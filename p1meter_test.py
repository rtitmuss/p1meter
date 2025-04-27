import unittest
from p1meter import read_p1_meter


meter_sample = [
    '/ELL5\\253833635_A\r\n',
    '\r\n',
    '0-0:1.0.0(241030120019W)\r\n',
    '1-0:1.8.0(00042741.128*kWh)\r\n',
    '1-0:2.8.0(00000000.001*kWh)\r\n',
    '1-0:3.8.0(00000761.228*kvarh)\r\n',
    '1-0:4.8.0(00002826.285*kvarh)\r\n',
    '1-0:1.7.0(0000.268*kW)\r\n',
    '1-0:2.7.0(0000.000*kW)\r\n',
    '1-0:3.7.0(0000.000*kvar)\r\n',
    '1-0:4.7.0(0000.198*kvar)\r\n',
    '1-0:21.7.0(0000.200*kW)\r\n',
    '1-0:41.7.0(0000.035*kW)\r\n',
    '1-0:61.7.0(0000.032*kW)\r\n',
    '1-0:22.7.0(0000.000*kW)\r\n',
    '1-0:42.7.0(0000.000*kW)\r\n',
    '1-0:62.7.0(0000.000*kW)\r\n',
    '1-0:23.7.0(0000.000*kvar)\r\n',
    '1-0:43.7.0(0000.000*kvar)\r\n',
    '1-0:63.7.0(0000.000*kvar)\r\n',
    '1-0:24.7.0(0000.003*kvar)\r\n',
    '1-0:44.7.0(0000.121*kvar)\r\n',
    '1-0:64.7.0(0000.072*kvar)\r\n',
    '1-0:32.7.0(228.9*V)\r\n',
    '1-0:52.7.0(232.1*V)\r\n',
    '1-0:72.7.0(234.0*V)\r\n',
    '1-0:31.7.0(001.0*A)\r\n',
    '1-0:51.7.0(000.5*A)\r\n',
    '1-0:71.7.0(000.3*A)\r\n',
    '!F5D8\r\n'
]


def p1_test_readline(sample=meter_sample):
    pos = 0

    def readline():
        nonlocal pos
        if pos < len(sample):
            line = sample[pos].encode('utf-8') if isinstance(sample[pos], str) else sample[pos]
            pos += 1
            return line
        else:
            return None

    return readline


class P1MeterTest(unittest.TestCase):

    def test_meter_sample(self):
        s, error_type = read_p1_meter(p1_test_readline())
        self.assertIsNotNone(s)
        self.assertEqual(len(s), 27)
        self.assertIsNone(error_type)

    def test_timestamp(self):
        sample = [
            "/XMX5LGBBFFB231157879",
            "1-0:1.8.0(00042741.128*kWh)",
            "1-0:2.8.0(00000001.234*kWh)",
            "0-0:1.0.0(241030120019W)",
            "!8A57"
        ]
        s, error_type = read_p1_meter(p1_test_readline(sample))
        self.assertEqual(s['sensor.dsmr_timestamp']['state'], '241030120019W')
        self.assertIsNone(error_type)

    def test_total_energy_import(self):
        sample = [
            "/XMX5LGBBFFB231157879",
            "1-0:1.8.0(00042741.128*kWh)",
            "1-0:2.8.0(00000001.234*kWh)",
            "!39B3"
        ]
        s, error_type = read_p1_meter(p1_test_readline(sample))
        self.assertEqual(s['sensor.dsmr_total_energy_import']['state'], '00042741.128')
        self.assertEqual(s['sensor.dsmr_total_energy_import']['attributes']['unit_of_measurement'], 'kWh')
        self.assertEqual(s['sensor.dsmr_total_energy_import']['attributes']['friendly_name'], 'Total Energy Import')
        self.assertEqual(s['sensor.dsmr_total_energy_import']['attributes']['obis_code'], '1-0:1.8.0')
        self.assertEqual(s['sensor.dsmr_total_energy_import']['attributes']['device_class'], 'energy')
        self.assertEqual(s['sensor.dsmr_total_energy_import']['attributes']['state_class'], 'total')
        self.assertIsNone(error_type)

    def test_total_energy_import_with_timestamp(self):
        sample = [
            "/XMX5LGBBFFB231157879",
            "1-0:1.8.0(170124210000W)(00042741.128*kWh)",
            "1-0:2.8.0(00000001.234*kWh)",
            "!63F5"
        ]
        s, error_type = read_p1_meter(p1_test_readline(sample))
        self.assertEqual(s['sensor.dsmr_total_energy_import']['state'], '00042741.128')
        self.assertEqual(s['sensor.dsmr_total_energy_import']['attributes']['unit_of_measurement'], 'kWh')
        self.assertEqual(s['sensor.dsmr_total_energy_import']['attributes']['friendly_name'], 'Total Energy Import')
        self.assertEqual(s['sensor.dsmr_total_energy_import']['attributes']['obis_code'], '1-0:1.8.0')
        self.assertEqual(s['sensor.dsmr_total_energy_import']['attributes']['device_class'], 'energy')
        self.assertEqual(s['sensor.dsmr_total_energy_import']['attributes']['state_class'], 'total')
        self.assertEqual(s['sensor.dsmr_total_energy_import']['attributes']['timestamp'], '170124210000W')
        self.assertIsNone(error_type)

    def test_unknown_obis_code(self):
        sample = [
            "/XMX5LGBBFFB231157879",
            "1-0:99.9.9(00012345.678*kWh)",
            "!E0A3"
        ]
        s, error_type = read_p1_meter(p1_test_readline(sample))
        self.assertIn("sensor.dsmr_1_0_99_9_9", s)
        self.assertEqual(s["sensor.dsmr_1_0_99_9_9"]["state"], "00012345.678")
        self.assertIsNone(error_type)

    def test_crc_failure(self):
        sample = [
            "/XMX5LGBBFFB231157879",
            "1-0:1.8.0(00042741.128*kWh)",
            "1-0:2.8.0(00000001.234*kWh)",
            "0-0:1.0.0(241030120019W)",
            "!0000"
        ]
        s, error_type = read_p1_meter(p1_test_readline(sample))
        self.assertIsNone(s)
        self.assertEqual(error_type, "crc")
        
    def test_malformed_data(self):
        sample = [
            "/XMX5LGBBFFB231157879",
            "1-0:2.7.0(!@#$%^&*())",  # Malformed line
            "!8593"
        ]
        s, error_type = read_p1_meter(p1_test_readline(sample))
        self.assertIsNone(s)
        self.assertEqual(error_type, "format")

    def test_unicode_error(self):
        sample = [
            b'/XMX5LGBBFFB231157879\r\n',
            b'\xff\xfe\xfa\xfb',  # Invalid UTF-8 bytes
            b'1-0:2.8.0(00000001.234*kWh)\r\n',
            b'!52E4\r\n'
        ]
        s, error_type = read_p1_meter(p1_test_readline(sample))
        self.assertIsNone(s)
        self.assertEqual(error_type, "decode")

if __name__ == '__main__':
    unittest.main()
