from pymodbus.client.sync import ModbusTcpClient


client = ModbusTcpClient('192.168.0.52', port=502)
print(client.read_holding_registers(address=1, count=124, unit=1).registers)
client.close()
