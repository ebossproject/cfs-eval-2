import os
import re
HOST = os.getenv("HOST", "127.0.0.1")
TARGET = os.getenv("TARGET", "cfs")

class CfeCmds:
    def __init__(self):
        self.commands = {
            # MM commands
            "MM_LOAD_MEM_WID": {
                'pkt_id': '0x1888', 'cc': '4', 'endian': 'LE',
                'target_ip': f'{TARGET}', 'target_port': '1234',
                'parameters': [
                    {'type': 'uint8', 'name': 'uint8_1'},
                    {'type': 'uint8',  'name': 'uint8_2'},
                    {'type': 'uint8',  'name': 'uint8_3'},
                    {'type': 'uint8',  'name': 'uint8_4'},
                    {'type': 'uint32', 'name': 'uint32_2'},
                    {'type': 'int64',  'name': 'int64_1'},
                    {'type': 'string', 'name': 'string_1', 'length': 64},
                ] + [{'type': 'uint64', 'name': f'uint64_{i}'} for i in range(1, 25)] + [
                    {'type': 'uint32', 'name': 'uint32_3'},
                    {'type': 'uint32',  'name': 'uint32_4'}
                ]
            },
            "MM_DUMP_TO_FILE": {
                'pkt_id': '0x1888', 'cc': '6', 'endian': 'LE',
                'target_ip': f'{TARGET}', 'target_port': '1234',
                'parameters': [
                    {'type': 'uint32', 'name': 'uint32_1'},
                    {'type': 'uint32', 'name': 'uint32_2'},
                    {'type': 'int64',  'name': 'int64_1'},
                    {'type': 'string', 'name': 'string_1', 'length': 64},
                    {'type': 'string', 'name': 'string_2', 'length': 64},
                ]
            },
            "MM_DUMP_INEVENT": {
                'pkt_id': '0x1888', 'cc': '7', 'endian': 'LE',
                'target_ip': f'{TARGET}', 'target_port': '1234',
                'parameters': [
                    {'type': 'uint32', 'name': 'uint32_1'},
                    {'type': 'uint32', 'name': 'uint32_2'},
                    {'type': 'uint64', 'name': 'uint64_1'},
                    {'type': 'string', 'name': 'string_1', 'length': 64},
                ]
            },
            "MM_FILL": {
                'pkt_id': '0x1888', 'cc': '8', 'endian': 'LE',
                'target_ip': f'{TARGET}', 'target_port': '1234',
                'parameters': [
                    {'type': 'uint32', 'name': f'uint32_{i}'} for i in range(1, 7)
                ] + [{'type': 'string', 'name': 'string', 'length': 64}]
            },
            "MM_SYM_LOOKUP": {
                'pkt_id': '0x1888', 'cc': '9', 'endian': 'LE',
                'target_ip': f'{TARGET}', 'target_port': '1234',
                'parameters': [
                   {'type': 'string', 'name': 'string_1', 'length': 64},
                ]
            },
            "MM_NOOP": {
                'pkt_id': '0x1888', 'cc': '0', 'endian': 'LE',
                'target_ip': f'{TARGET}', 'target_port': '1234',
                'parameters': None
            },

            # Core cFE services
            "CFE_EVS_NOOP": {'pkt_id': '0x1801', 'cc': '0', 'endian': 'LE', 'target_ip': f'{TARGET}', 'target_port': '1234', 'parameters': None},
            "CFE_EVS_RESET_COUNTERS": {'pkt_id': '0x1801', 'cc': '1', 'endian': 'LE', 'target_ip': f'{TARGET}', 'target_port': '1234', 'parameters': None},
            "CFE_SB_NOOP": {'pkt_id': '0x1803', 'cc': '0', 'endian': 'LE', 'target_ip': f'{TARGET}', 'target_port': '1234', 'parameters': None},
            "CFE_SB_RESET_COUNTERS": {'pkt_id': '0x1803', 'cc': '1', 'endian': 'LE', 'target_ip': f'{TARGET}', 'target_port': '1234', 'parameters': None},
            "CFE_SB_SEND_SB_STATS": {'pkt_id': '0x1803', 'cc': '2', 'endian': 'LE', 'target_ip': f'{TARGET}', 'target_port': '1234', 'parameters': None},
            "CFE_TBL_NOOP": {'pkt_id': '0x1804', 'cc': '0', 'endian': 'LE', 'target_ip': f'{TARGET}', 'target_port': '1234', 'parameters': None},
            "CFE_TIME_NOOP": {'pkt_id': '0x1805', 'cc': '0', 'endian': 'LE', 'target_ip': f'{TARGET}', 'target_port': '1234', 'parameters': None},
            "CFE_ES_NOOP": {'pkt_id': '0x1806', 'cc': '0', 'endian': 'LE', 'target_ip': f'{TARGET}', 'target_port': '1234', 'parameters': None},
            "CFE_ES_RESET_COUNTERS": {'pkt_id': '0x1806', 'cc': '1', 'endian': 'LE', 'target_ip': f'{TARGET}', 'target_port': '1234', 'parameters': None},

            # TO_LAB
            "TO_LAB_NOOP": {'pkt_id': '0x1880', 'cc': '0', 'endian': 'LE', 'target_ip': f'{TARGET}', 'target_port': '1234', 'parameters': None},
            "TO_LAB_RESET_STATUS": {'pkt_id': '0x1880', 'cc': '1', 'endian': 'LE', 'target_ip': f'{TARGET}', 'target_port': '1234', 'parameters': None},
            "TO_LAB_REMOVE_ALL_PKT": {'pkt_id': '0x1880', 'cc': '5', 'endian': 'LE', 'target_ip': f'{TARGET}', 'target_port': '1234', 'parameters': None},
            "TO_LAB_OUTPUT_ENABLE": {
                'pkt_id': '0x1880', 'cc': '6', 'endian': 'LE',
                'target_ip': f'{TARGET}', 'target_port': '1234',
                'parameters': [{'type': 'string', 'name': 'string', 'length': 17}]
            },

            # CI_LAB
            "CI_LAB_NOOP": {'pkt_id': '0x1884', 'cc': '0', 'endian': 'LE', 'target_ip': f'{TARGET}', 'target_port': '1234', 'parameters': None},
            "CI_LAB_RESET_COUNTERS": {'pkt_id': '0x1884', 'cc': '1', 'endian': 'LE', 'target_ip': f'{TARGET}', 'target_port': '1234', 'parameters': None},
            "CI_LAB_CORRUPT_PDU_CHECKSUM": {'pkt_id': '0x1884', 'cc': '3', 'endian': 'LE', 'target_ip': f'{TARGET}', 'target_port': '1234', 'parameters': None},
        }

    def get_command(self, name: str):
        cmd = self.commands.get(name)
        if not cmd:
            raise ValueError(f"Command '{name}' not found in CfeCmds")
        return cmd
