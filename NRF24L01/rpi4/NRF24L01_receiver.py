import argparse
import struct
import sys
import time
import traceback
from Weatherstation import WeatherStation

import pigpio
from nrf24 import *

if __name__ == "__main__":

    print("Python NRF24 Simple Receiver Example.")

    # Parse command line argument.
    arg_parser = argparse.ArgumentParser(
        prog="simple-receiver.py", description="Simple NRF24 Receiver Example.")
    arg_parser.add_argument('-n', '--hostname', type=str, default='localhost',
                            help="Hostname for the Raspberry running the pigpio daemon.")
    arg_parser.add_argument('-p', '--port', type=int, default=8888,
                            help="Port number of the pigpio daemon.")
    arg_parser.add_argument('address', type=str, nargs='?', default='WWWWW',
                            help="Address to listen to (3 to 5 ASCII characters)")

    args = arg_parser.parse_args()
    hostname = args.hostname
    port = args.port
    nrf_address = args.address

    # Verify that address is between 3 and 5 characters.
    if not (2 < len(nrf_address) < 6):
        print(
            f'Invalid address {nrf_address}. Addresses must be between 3 and 5 ASCII characters.')
        sys.exit(1)

    # Connect to pigpiod
    print(f'Connecting to GPIO daemon on {hostname}:{port} ...')
    pi_gpio_d = pigpio.pi(hostname, port)
    if not pi_gpio_d.connected:
        print("Not connected to Raspberry Pi ... goodbye.")
        sys.exit()

    nrf = NRF24(pi_gpio_d, ce=24, payload_size=RF24_PAYLOAD.MAX, channel=100,
                data_rate=RF24_DATA_RATE.RATE_250KBPS, pa_level=RF24_PA.MAX)
    nrf.set_address_bytes(len(nrf_address))
    nrf.open_reading_pipe(RF24_RX_ADDR.P1, nrf_address)
    # nrf.show_registers()

    ws = WeatherStation()

    try:
        print(f'Receive from {nrf_address}')
        count = 0
        while True:
            while nrf.data_ready():
                payload = nrf.get_payload()

                # print(f"cnt={struct.unpack('i', payload[:4])}")
                # ws.Deserialize(payload[4:])

                ws.Deserialize(payload)

                print(f"T={ws.Temperature:.2f}\tH={ws.Humidity:.2f}\tP={ws.Pressure:.2f}")

            time.sleep(0.001)
    except:
        traceback.print_exc()
        nrf.power_down()
        pi_gpio_d.stop()
