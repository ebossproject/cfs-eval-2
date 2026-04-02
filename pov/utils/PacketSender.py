import socket
from utils.CommandList import CfeCmds
from spacepackets.ccsds.spacepacket import SpHeader, PacketType

class PacketSender:
    def __init__(self):
        self.cmds = CfeCmds()

    def compute_checksum(self, packet: bytearray) -> int:
        """Compute 1-byte XOR checksum for cFS command packets (skip byte 7)."""
        checksum = 0
        for i, byte in enumerate(packet):
            if i == 7:
                continue
            checksum ^= byte
        return checksum

    def parse_params(self, parameters, **kwargs):
        payload = bytearray()
        if not parameters:
            return payload

        for p in parameters:
            name = p['name']
            p_type = p['type']

            if name not in kwargs:
                raise ValueError(f"No value provided for parameter: {name}")
            val = kwargs[name]

            # integer types
            if p_type.startswith('uint') or p_type.startswith('int'):
                byte_len = int(''.join(filter(str.isdigit, p_type))) // 8
                signed = p_type.startswith('int')
                payload.extend(int(val).to_bytes(byte_len, byteorder='little', signed=signed))

            # strings
            elif p_type == 'string':
                max_len = p['length']
                if val is None or val == "":
                    val_bytes = b''
                else:
                    val_bytes = val.encode()
                if len(val_bytes) > max_len:
                    raise ValueError(f"String too long for {name}: {val}")
                # Only pad to max_len if the spec requires
                fixed_bytes = val_bytes.ljust(max_len, b'\x00')
                payload.extend(fixed_bytes)

        return payload

    def create_ccsds_command(self, apid: int, sequence_count: int, cmd_code: int, cmd_args: bytes = b'') -> bytes:
        """Create a CCSDS command packet."""
        user_data = bytes([cmd_code, 0x00]) + cmd_args

        sp_header = SpHeader(
            packet_type=PacketType.TC,
            apid=apid,
            seq_count=sequence_count,
            data_len=len(user_data) - 1,
            sec_header_flag=True,
            ccsds_version=0
        )

        packet = bytearray(sp_header.pack() + user_data)
        packet[7] = self.compute_checksum(packet)
        return bytes(packet)

    def send_ccsds_packet(self, ip: str, port: int, packet: bytes):
        """Send packet over UDP."""
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.sendto(packet, (ip, port))
            print(f"Packet sent to {ip}:{port} ({len(packet)} bytes)")

    def send_command(self, cmd_name: str, sequence_count: int = 0, **kwargs):
        """Send a command using the CfeCmds templates and runtime parameters."""
        cmd_template = self.cmds.get_command(cmd_name)

        cmd_args = self.parse_params(cmd_template.get('parameters'), **kwargs)
        apid = int(cmd_template['pkt_id'], 16) & 0x07FF
        cmd_code = int(cmd_template['cc'])
        packet = self.create_ccsds_command(apid, sequence_count, cmd_code, cmd_args)

        self.send_ccsds_packet(cmd_template['target_ip'], int(cmd_template['target_port']), packet)
        return True

