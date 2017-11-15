import sys
import os
import time
import math
from decimal import Decimal
from pymodbus.client.sync import ModbusTcpClient
from pymodbus.exceptions import ConnectionException
from multiprocessing import Pool, TimeoutError

DEBUG = True
start_time = time.time()
ip = '192.168.0.52'
ports = range(502,508)
clients = list([ModbusTcpClient(ip, port=port) for port in ports])


def runner(client):
    global start_time
    next_time = math.floor(time.time())

    # testting data: time elapsed, num cycle, error, data rate, error rate
    num_cycle = 0
    num_error = 0
    elap_time = 0
    error = ''
    
    while True:
        time.sleep(0)
        error = 'None'
        elap_time = time.time()-start_time
        
        if (elap_time > 60*60*10): # terminate test
            break
        if time.time() > next_time:
            next_time += 1
        else:
            sleep_time = max(0.2, next_time - time.time())
            time.sleep(sleep_time)
            continue
        
        try:
            reg = client.read_holding_registers(address=0, count=124, unit=1).registers
        except ConnectionException:
            error = 'Connection Exception'
            num_error += 1

        
        num_cycle += 1
        info = ('time elap:{:1.3f} | port:{} | pid:{} | tot cycle:{} - {:1.1f}/sec | tot err:{} - {:.2E}/cyc | error:{}').format
        print(info(elap_time, client.port, os.getpid(), num_cycle,
                   num_cycle/elap_time, num_error, Decimal(num_error/num_cycle), error))


if __name__ == "__main__":
    pool = Pool(6)
    
    while True:
        try:
            results = pool.map_async(runner, clients)
            results.get()
        except KeyboardInterrupt:
            pool.terminate()
            break
        except: # other errors
            e = sys.exc_info()[0]
            print('Other error: {}'.format(e))
            pool.terminate()
            if DEBUG:
                break
            else:
                continue

    print('Closing pools')
    pool.close()
    pool.join()
    print('Closing clients')
    for client in clients:
        client.close()
