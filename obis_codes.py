OBIS_CODES = {
    '0-0:1.0.0': {  # Timestamp
        'friendly_name': 'Timestamp',
        'device_class': None,  # No device class for timestamp
        'state_class': None
    },
    '1-0:1.8.0': {  # Total Energy Import
        'friendly_name': 'Total Energy Import',
        'device_class': 'energy',  # Total energy in kWh
        'state_class': 'total'
    },
    '1-0:2.8.0': {  # Total Energy Export
        'friendly_name': 'Total Energy Export',
        'device_class': 'energy',  # Total energy in kWh
        'state_class': 'total'
    },
    '1-0:3.8.0': {  # Total Reactive Energy Import
        'friendly_name': 'Total Reactive Energy Import',
        'device_class': 'energy',  # Total reactive energy in kvarh
        'state_class': 'total'
    },
    '1-0:4.8.0': {  # Total Reactive Energy Export
        'friendly_name': 'Total Reactive Energy Export',
        'device_class': 'energy',  # Total reactive energy in kvarh
        'state_class': 'total'
    },
    '1-0:1.7.0': {  # Instantaneous Power
        'friendly_name': 'Instantaneous Power',
        'device_class': 'power',  # Power in kW
        'state_class': 'measurement'
    },
    '1-0:2.7.0': {  # Instantaneous Power Export
        'friendly_name': 'Instantaneous Power Export',
        'device_class': 'power',  # Power in kW
        'state_class': 'measurement'
    },
    '1-0:3.7.0': {  # Instantaneous Reactive Power
        'friendly_name': 'Instantaneous Reactive Power',
        'device_class': 'power',  # Reactive power in kvar
        'state_class': 'measurement'
    },
    '1-0:4.7.0': {  # Instantaneous Reactive Power Export
        'friendly_name': 'Instantaneous Reactive Power Export',
        'device_class': 'power',  # Reactive power in kvar
        'state_class': 'measurement'
    },
    '1-0:21.7.0': {  # Current Power L1
        'friendly_name': 'Current Power L1',
        'device_class': 'power',  # Power in kW
        'state_class': 'measurement'
    },
    '1-0:41.7.0': {  # Current Power L2
        'friendly_name': 'Current Power L2',
        'device_class': 'power',  # Power in kW
        'state_class': 'measurement'
    },
    '1-0:61.7.0': {  # Current Power L3
        'friendly_name': 'Current Power L3',
        'device_class': 'power',  # Power in kW
        'state_class': 'measurement'
    },
    '1-0:22.7.0': {  # Current Power Export L1
        'friendly_name': 'Current Power Export L1',
        'device_class': 'power',  # Power in kW
        'state_class': 'measurement'
    },
    '1-0:42.7.0': {  # Current Power Export L2
        'friendly_name': 'Current Power Export L2',
        'device_class': 'power',  # Power in kW
        'state_class': 'measurement'
    },
    '1-0:62.7.0': {  # Current Power Export L3
        'friendly_name': 'Current Power Export L3',
        'device_class': 'power',  # Power in kW
        'state_class': 'measurement'
    },
    '1-0:23.7.0': {  # Current Reactive Power L1
        'friendly_name': 'Current Reactive Power L1',
        'device_class': 'power',  # Reactive power in kvar
        'state_class': 'measurement'
    },
    '1-0:43.7.0': {  # Current Reactive Power L2
        'friendly_name': 'Current Reactive Power L2',
        'device_class': 'power',  # Reactive power in kvar
        'state_class': 'measurement'
    },
    '1-0:63.7.0': {  # Current Reactive Power L3
        'friendly_name': 'Current Reactive Power L3',
        'device_class': 'power',  # Reactive power in kvar
        'state_class': 'measurement'
    },
    '1-0:24.7.0': {  # Current Reactive Power Export L1
        'friendly_name': 'Current Reactive Power Export L1',
        'device_class': 'power',  # Reactive power in kvar
        'state_class': 'measurement'
    },
    '1-0:44.7.0': {  # Current Reactive Power Export L2
        'friendly_name': 'Current Reactive Power Export L2',
        'device_class': 'power',  # Reactive power in kvar
        'state_class': 'measurement'
    },
    '1-0:64.7.0': {  # Current Reactive Power Export L3
        'friendly_name': 'Current Reactive Power Export L3',
        'device_class': 'power',  # Reactive power in kvar
        'state_class': 'measurement'
    },
    '1-0:32.7.0': {  # Current Voltage L1
        'friendly_name': 'Current Voltage L1',
        'device_class': 'voltage',  # Voltage in V
        'state_class': 'measurement'
    },
    '1-0:52.7.0': {  # Current Voltage L2
        'friendly_name': 'Current Voltage L2',
        'device_class': 'voltage',  # Voltage in V
        'state_class': 'measurement'
    },
    '1-0:72.7.0': {  # Current Voltage L3
        'friendly_name': 'Current Voltage L3',
        'device_class': 'voltage',  # Voltage in V
        'state_class': 'measurement'
    },
    '1-0:31.7.0': {  # Current Current L1
        'friendly_name': 'Current Current L1',
        'device_class': 'current',  # Current in A
        'state_class': 'measurement'
    },
    '1-0:51.7.0': {  # Current Current L2
        'friendly_name': 'Current Current L2',
        'device_class': 'current',  # Current in A
        'state_class': 'measurement'
    },
    '1-0:71.7.0': {  # Current Current L3
        'friendly_name': 'Current Current L3',
        'device_class': 'current',  # Current in A
        'state_class': 'measurement'
    },
}
