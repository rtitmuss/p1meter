import re

from obis_codes import OBIS_CODES

PARSE_TIMESTAMP = re.compile(r'([\d\.\-:]+)\((\d+[SW]?)\)\(([\w.]*)\*?([\w%]*)\)')
PARSE_NO_TIMESTAMP = match = re.compile(r'([\d\.\-:]+)\(([\w.]*)\*?([\w%]*)\)')


def obis_to_description(obis_code):
    description = OBIS_CODES.get(obis_code)
    if description:
        description['id'] = f'sensor.dsmr_{description["friendly_name"].lower().replace(" ", "_")}'
        return description
    else:
        unique_id = obis_code.replace("-", "_").replace(".", "_").replace(":", "_")
        return {
            'id': f'sensor.dsmr_{unique_id}',
            'friendly_name': obis_code
        }


def parse_line(line):
    match = PARSE_TIMESTAMP.match(line)
    if match:
        return match.group(1), match.group(3), match.group(4), match.group(2)
    
    match = PARSE_NO_TIMESTAMP.match(line)
    if match:
        return match.group(1), match.group(2), match.group(3), None

    return None, None, None, None


def calculate_crc(crc, buf):
    for c in buf:
        crc ^= c
        for i in range(8):
            if crc & 0x01:
                crc >>= 1
                crc ^= 0xA001
            else:
                crc >>= 1
    return crc


def read_p1_meter(readline):
    header = None
    crc = 0
    data = {}

    while True:
        uart_line = readline()
        
        if uart_line is None:
            continue  # timeout

        try:
            line = uart_line.decode().strip()
        except BaseException as error:
            print(f'decode error: {uart_line}')
            continue  # uart error

        print(line)

        if not line:
            crc = calculate_crc(crc, uart_line)
            continue  # blank line

        if not header and line[0] == '/':
            header = line
            crc = calculate_crc(0, uart_line)
            data = {}            
            continue  # header

        if line[0] == '!':
            crc = calculate_crc(crc, b'!')
            if line != f'!{crc:04X}':
                print(f'CRC error: {line} !{crc:04X}')
                return None
            return data

        crc = calculate_crc(crc, uart_line)
        
        obis_code, value, unit, timestamp = parse_line(line)
        if obis_code:
            description = obis_to_description(obis_code)

            attributes = {
                "unit_of_measurement": unit,
                "friendly_name": description['friendly_name'],
                "obis_code": obis_code
            }
            if 'device_class' in description:
                attributes["device_class"] = description['device_class']
            if 'state_class' in description:
                attributes["state_class"] = description['state_class']
            if timestamp:
                attributes["timestamp"] = timestamp

            data[description['id']] = {
                "state": value,
                "attributes": attributes
            }
            #print(data)
        else:
            print(f"Line format is incorrect: {line}")
