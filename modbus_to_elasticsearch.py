import csv
import math
import struct
import json
import datetime
from collections import OrderedDict
from pymodbus.client.sync import ModbusTcpClient
from pymodbus.exceptions import ConnectionException



def decimals_to_float32(int1, int2):
    """Convert to float
    
    Note:
        Orders in big endian
    Args:
        int1, int2 (int)
    Return:
        float: decoded value
    """
    f = int('{:016b}{:016b}'.format(int1, int2), 2)
    return struct.unpack('f', struct.pack('I', f))[0]


def unpack_bool(data):
    """Extract list of boolean from integer
    
    Args:
        data (int)
    Return:
        list: in bool
    """
    return [bool(int(i)) for i in '{:016b}'.format(data)]


def twos_comp(val, bits):
    """compute the 2's complement of int value val"""
    if (val & (1 << (bits - 1))) != 0:
        val = val - (1 << bits)
    return val


def csv_to_dict(tag_csv):
    """ create a parsing dictionary """
    tags = OrderedDict()
    with open(tag_csv, 'r') as f:
        reader = csv.reader(f, doublequote=True, quoting=csv.QUOTE_ALL, escapechar='\\')
        header = next(reader)
        header[0] = 'Name' # manually adjust from \ufeffName to Name
        tags = {row[0]:{header[i]:row[i] for i in range(0,len(header))} for row in reader}
    return tags



# -----

def insert_data(tags, data):
    """ process from a list of data and insert to its tags accordingly 
    
    TODO: Word datatype parsing
    """
    data_iter = iter(data)
    for tag in tags:
        val = next(data_iter)
        if tags[tag]["Data Type"] == "Real":
            val = decimals_to_float32(val, next(data_iter))
        elif tags[tag]["Data Type"] == "Word":
            pass
        elif tags[tag]["Data Type"] == "Int":
            val = twos_comp(val, 16)
        if tags[tag]['scale'] == 'x10':
            val /= 10
        tags[tag]['value'] = val

    return tags



tags = csv_to_dict('plc_tags.csv')
client = ModbusTcpClient('192.168.0.52', port=502, retries=3, timeout=3)
client.connect()
time = datetime.datetime.now()

try:
    rr = client.read_holding_registers(address=0,count=103,unit=1)
    assert(rr.function_code < 0x80), "register error"

    tags = insert_data(tags, rr.registers)
    formatted_data = {tag:tags[tag]['value'] for tag in tags if tags[tag]['Data Type'] != "Word"}
    print(json.dumps(formatted_data, indent=4))

except ConnectionException:
    print('connection error')

finally:
    client.close()
