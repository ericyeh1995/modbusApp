from pymodbus.client.sync import ModbusTcpClient
import logging

logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.DEBUG)

client = ModbusTcpClient('192.168.11.51', port=502)
print(client.read_holding_registers(address=256, count=380, unit=1).registers)
client.close()
