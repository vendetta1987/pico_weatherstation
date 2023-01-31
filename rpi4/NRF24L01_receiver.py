import argparse
import struct
import sys
import time
import traceback
from datetime import datetime
from Weatherstation import WeatherStation

import pigpio
from nrf24 import *

if __name__ == "__main__":

    print("Python NRF24 Simple Receiver Example.")

    # Parse command line argument.
    parser = argparse.ArgumentParser(
        prog="simple-receiver.py", description="Simple NRF24 Receiver Example.")
    parser.add_argument('-n', '--hostname', type=str, default='localhost',
                        help="Hostname for the Raspberry running the pigpio daemon.")
    parser.add_argument('-p', '--port', type=int, default=8888,
                        help="Port number of the pigpio daemon.")
    parser.add_argument('address', type=str, nargs='?', default='1SNSR',
                        help="Address to listen to (3 to 5 ASCII characters)")

    args = parser.parse_args()
    hostname = args.hostname
    port = args.port
    address = args.address

    # Verify that address is between 3 and 5 characters.
    if not (2 < len(address) < 6):
        print(
            f'Invalid address {address}. Addresses must be between 3 and 5 ASCII characters.')
        sys.exit(1)

    # Connect to pigpiod
    print(f'Connecting to GPIO daemon on {hostname}:{port} ...')
    pi = pigpio.pi(hostname, port)
    if not pi.connected:
        print("Not connected to Raspberry Pi ... goodbye.")
        sys.exit()

    nrf = NRF24(pi, ce=24, payload_size=RF24_PAYLOAD.MAX, channel=100,
                data_rate=RF24_DATA_RATE.RATE_250KBPS, pa_level=RF24_PA.MAX)
    nrf.set_address_bytes(len(address))
    nrf.open_reading_pipe(RF24_RX_ADDR.P1, address)
    # nrf.show_registers()

    try:
        print(f'Receive from {address}')
        count = 0
        while True:
            while nrf.data_ready():
                pipe = nrf.data_pipe()
                payload = nrf.get_payload()

                WeatherStation.Deserialize(payload)

            time.sleep(0.01)
    except:
        traceback.print_exc()
        nrf.power_down()
        pi.stop()
