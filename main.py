from machine import UART, Pin, Timer
import network
import ntptime
import time
import urequests

from p1meter import read_p1_meter

from config import WIFI_SSID, WIFI_PASSWORD, HOME_ASSISTANT_SENSOR_API, HOME_ASSISTANT_ACCESS_TOKEN


wlan = network.WLAN(network.STA_IF)
print("Reset WiFi")
wlan.disconnect()
wlan.active(False)

uart = UART(1, tx=Pin(4), rx=Pin(5),
            baudrate=115200, bits=8, parity=None,
            stop=1, invert=UART.INV_RX | UART.INV_TX,
            timeout=1000, timeout_char=1000,
            txbuf=2048, rxbuf=2048)

# Blinking LED WiFi is connecting, solid LED WiFi is connected
led = Pin('LED', Pin.OUT)

def tick(timer):
    global led
    if not wlan.isconnected():
        led.toggle()
    else:
        led.on()

tim = Timer()
tim.init(freq=2.5, mode=Timer.PERIODIC, callback=tick)


epoch = time.time()
wifi_connections = 0
http_errors = 0
uart_errors = 0
MAX_RETRIES = 3


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
            time.sleep(1)


def wifi_connect():
    global wifi_connections
    
    if not wlan.isconnected():
        # Reset wifi module
        wlan.active(False)
        time.sleep_ms(200)
        wlan.active(True)

        print("Connecting to WiFi...")
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        
        timeout_time = time.time() + 10
        while not wlan.isconnected():
            if time.time() > timeout_time:
                print("Failed to connect to WiFi: Timeout")
                return False
            time.sleep(1)

        sync_time_with_ntp()

        print(f"Connected to WiFi with RSSI: {wlan.status('rssi')}")
        wifi_connections += 1        
        return True
    return True


def post_sensor(sensor_id, sensor_data):
    global http_errors
    
    url = f"{HOME_ASSISTANT_SENSOR_API}/{sensor_id}"
    headers = {
        "Authorization": f"Bearer {HOME_ASSISTANT_ACCESS_TOKEN}",  # Replace with your token
        "Content-Type": "application/json",
    }
    payload = {
        "state": sensor_data["state"]() if callable(sensor_data["state"]) else sensor_data["state"],
        "attributes": sensor_data["attributes"]
    }

    try:
        response = urequests.post(url, json=payload, headers=headers)
        if response.status_code == 200 or response.status_code == 201:
            print(f"Successfully updated {sensor_id}")
            return True
        else:
            print(f"Failed to update {sensor_id}: {response.status_code} {response.text}")
            http_errors += 1
            return False
    except Exception as e:
        print(f"Error posting to {sensor_id}: {e}")
        http_errors += 1
        return False
    finally:
        if response:
            response.close()


def publish_sensors(sensors):
    for sensor_id, sensor_data in sensors.items():
        for attempt in range(MAX_RETRIES):
            try:
                post_sensor(sensor_id, sensor_data)
                break # Break if publish is successful
            except Exception as e:
                print(f"Publish error for sensor '{sensor_id}': {e}")
                
                if not wifi_connect():
                    return False
    return True


def get_utc_time_string():
    current_time = time.localtime()
    return "{:04}-{:02}-{:02} {:02}:{:02}:{:02}".format(
        current_time[0], current_time[1], current_time[2],  # Year, Month, Day
        current_time[3], current_time[4], current_time[5]   # Hour, Minute, Second
    )


status_sensors = {
    'sensor.smartmeter_http_errors': {
        "state": lambda: str(http_errors),
        "attributes": {
            "unit_of_measurement": "",
            "friendly_name": "HTTP errors"
            }
        },
    'sensor.smartmeter_uart_errors': {
        "state": lambda: str(uart_errors),
        "attributes": {
            "unit_of_measurement": "",
            "friendly_name": "UART errors"
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


# Set to allow immediate publishing on the first iteration
last_publish_time = time.ticks_ms() - 60000

while True:
    loop_time = time.ticks_ms()
    
    print("Reading meter...")
    p1_sensors = read_p1_meter(uart.readline)

    if not p1_sensors:
        uart_errors += 1
        p1_sensors = {}
    
    current_time = time.ticks_ms()
    if time.ticks_diff(current_time, last_publish_time) >= 60000:
        last_publish_time = current_time
        p1_sensors.update(status_sensors)
        if not publish_sensors(p1_sensors):
            print("Publishing failed")
