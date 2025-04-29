from machine import UART, Pin, Timer, WDT
import network
import ntptime
import re
import time
import urequests

from p1meter import read_p1_meter

from config import WIFI_SSID, WIFI_PASSWORD, HOME_ASSISTANT_SENSOR_API, HOME_ASSISTANT_ACCESS_TOKEN

# Initialize watchdog with 8388ms timeout
wdt = WDT(timeout=8388)

wlan = network.WLAN(network.STA_IF)
print("Reset WiFi")
wlan.disconnect()
wlan.active(False)

uart = UART(1, tx=Pin(4), rx=Pin(5),
            baudrate=115200, bits=8, parity=None,
            stop=1, invert=UART.INV_RX | UART.INV_TX,
            timeout=1000, timeout_char=1000,
            txbuf=2048, rxbuf=2048)

# Solid LED WiFi is connecting, blinking LED WiFi is connected
led = Pin('LED', Pin.OUT)

def tick(timer):
    global led
    if wlan.isconnected():
        led.toggle()
    else:
        led.on()

tim = Timer()
tim.init(freq=2.5, mode=Timer.PERIODIC, callback=tick)

epoch = time.time()
wifi_connections = 0
http_400_errors = 0
http_500_errors = 0
p1_timeout_errors = 0
p1_decode_errors = 0
p1_crc_errors = 0
p1_format_errors = 0
exception_counts = {}  # Track counts of different exception types
MAX_RETRIES = 3


def get_utc_time_string():
    current_time = time.localtime()
    return "{:04}-{:02}-{:02} {:02}:{:02}:{:02}".format(
        current_time[0], current_time[1], current_time[2],  # Year, Month, Day
        current_time[3], current_time[4], current_time[5]   # Hour, Minute, Second
    )


status_sensors = {
    'sensor.smartmeter_http_400_errors': {
        "state": lambda: str(http_400_errors),
        "attributes": {
            "unit_of_measurement": "",
            "friendly_name": "HTTP 400 errors"
            }
        },
    'sensor.smartmeter_http_500_errors': {
        "state": lambda: str(http_500_errors),
        "attributes": {
            "unit_of_measurement": "",
            "friendly_name": "HTTP 500 errors"
            }
        },
    'sensor.smartmeter_p1_timeout_errors': {
        "state": lambda: str(p1_timeout_errors),
        "attributes": {
            "unit_of_measurement": "",
            "friendly_name": "P1 Timeout errors"
            }
        },
    'sensor.smartmeter_p1_decode_errors': {
        "state": lambda: str(p1_decode_errors),
        "attributes": {
            "unit_of_measurement": "",
            "friendly_name": "P1 Decode errors"
            }
        },
    'sensor.smartmeter_p1_crc_errors': {
        "state": lambda: str(p1_crc_errors),
        "attributes": {
            "unit_of_measurement": "",
            "friendly_name": "P1 CRC errors"
            }
        },
    'sensor.smartmeter_p1_format_errors': {
        "state": lambda: str(p1_format_errors),
        "attributes": {
            "unit_of_measurement": "",
            "friendly_name": "P1 Format errors"
            }
        },
    'sensor.smartmeter_wifi_connections': {
        "state": lambda: str(wifi_connections),
        "attributes": {
            "unit_of_measurement": "",
            "friendly_name": "Wifi connections"
            }
        },
    'sensor.smartmeter_wifi_rssi': {
        "state": lambda: str(wlan.status('rssi')),
        "attributes": {
            "unit_of_measurement": "dbm",
            "friendly_name": "Wifi rssi"
            }
        },
    'sensor.smartmeter_last_update': {
        "state": get_utc_time_string,
        "attributes": {
            "unit_of_measurement": "time",
            "friendly_name": "Last update"
            }
        },
    'sensor.smartmeter_uptime': {
        "state": lambda: str(time.time() - epoch),
        "attributes": {
            "unit_of_measurement": "s",
            "friendly_name": "Uptime"
            }
        },
}


def count_exception(e):
    global exception_counts, status_sensors
    exception_name = type(e).__name__.lower()

    if isinstance(e, OSError):
        match = re.search(r'([A-Z_][A-Z_]+)', str(e))
        if match:
            error_name = match.group(0).lower()
            exception_type = f"{exception_name}_{error_name}"
        else:
            exception_type = f"{exception_name}_{e.errno}"
    else:
        exception_type = exception_name

    exception_counts[exception_type] = exception_counts.get(exception_type, 0) + 1

    # Add new sensor type if this is the first time we've seen this exception
    if exception_type not in [s.split('_')[-1] for s in status_sensors.keys() if s.startswith('sensor.smartmeter_exception_')]:
        status_sensors[f'sensor.smartmeter_exception_{exception_type}'] = {
            "state": lambda t=exception_type: str(exception_counts.get(t, 0)),
            "attributes": {
                "unit_of_measurement": "",
                "friendly_name": f"Exception: {exception_type}"
            }
        }


def safe_sleep(seconds):
    """Sleep while keeping the watchdog fed"""
    start = time.time()
    while time.time() - start < seconds:
        wdt.feed()
        time.sleep(0.1)


def sync_time_with_ntp():
    global epoch

    for attempt in range(MAX_RETRIES):
        try:
            uptime = time.time() - epoch
            ntptime.settime()
            epoch = time.time() - uptime # adjust uptime due to RTC change
            break
        except Exception as e:
            print(f"ntp failed {e}")
            count_exception(e)
            safe_sleep(1)


def wifi_connect():
    global wifi_connections
    
    if not wlan.isconnected():
        # Reset wifi module
        wlan.active(False)
        safe_sleep(0.2)
        wlan.active(True)

        print("Connecting to WiFi...")
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        
        timeout_time = time.time() + 10
        while not wlan.isconnected():
            if time.time() > timeout_time:
                print("Failed to connect to WiFi: Timeout")
                return False
            safe_sleep(1)

        sync_time_with_ntp()

        print(f"Connected to WiFi with RSSI: {wlan.status('rssi')}")
        wifi_connections += 1        
        return True
    return True


def post_sensor(sensor_id, sensor_data):
    global http_400_errors, http_500_errors
    
    url = f"{HOME_ASSISTANT_SENSOR_API}/{sensor_id}"
    headers = {
        "Authorization": f"Bearer {HOME_ASSISTANT_ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "state": sensor_data["state"]() if callable(sensor_data["state"]) else sensor_data["state"],
        "attributes": sensor_data["attributes"]
    }

    response = None
    try:
        response = urequests.post(url, json=payload, headers=headers, timeout=1)
        if response.status_code == 200 or response.status_code == 201:
            print(f"Successfully updated {sensor_id}")
        elif response.status_code >= 400 and response.status_code < 500:
            print(f"Client error updating {sensor_id}: {response.status_code} {response.text}")
            http_400_errors += 1
        else:
            print(f"Server error updating {sensor_id}: {response.status_code} {response.text}")
            http_500_errors += 1
    finally:
        if response:
            response.close()


def publish_sensors(sensors):
    for sensor_id, sensor_data in sensors.items():
        for attempt in range(MAX_RETRIES):
            try:
                wdt.feed()
                post_sensor(sensor_id, sensor_data)
                break # Break if publish is successful
            except Exception as e:
                print(f"Publish error for sensor '{sensor_id}': {e}")
                count_exception(e)
                if not wifi_connect():
                    return False
    return True


# Set to allow immediate publishing on the first iteration
last_publish_time = time.ticks_ms() - 60000
last_known_good_values = {}

while True:
    try:
        wdt.feed()
        loop_time = time.ticks_ms()

        print("Reading meter...")
        p1_sensors, error_type = read_p1_meter(uart.readline)

        if error_type is None and p1_sensors is not None:
            last_known_good_values = p1_sensors
        else:
            p1_sensors = last_known_good_values
            if error_type == "timeout":
                p1_timeout_errors += 1
            elif error_type == "decode":
                p1_decode_errors += 1
            elif error_type == "crc":
                p1_crc_errors += 1
            elif error_type == "format":
                p1_format_errors += 1

        current_time = time.ticks_ms()
        if time.ticks_diff(current_time, last_publish_time) >= 60000:
            last_publish_time = current_time
            p1_sensors.update(status_sensors)
            if not publish_sensors(p1_sensors):
                print("Publishing failed")
    except Exception as e:
        print(f"Error in main loop: {e}")
        count_exception(e)
        safe_sleep(1)
        continue
