import argparse
import json
import sys
import time
import traceback

import pigpio
from nrf24 import *

from MQTTClient import MQTTCLient
from Weatherstation import WeatherStation

if __name__ == "__main__":
    print("Python NRF24 Simple Receiver Example.")
    # Parse command line argument.
    arg_parser = argparse.ArgumentParser(
        prog="simple-receiver.py", description="Simple NRF24 Receiver Example.")
    arg_parser.add_argument('-n', '--hostname', type=str, default='localhost',
                            help="Hostname for the Raspberry running the pigpio daemon.")
    arg_parser.add_argument('-p', '--port', type=int, default=8888,
                            help="Port number of the pigpio daemon.")
    arg_parser.add_argument('--address', type=str, nargs='?', default='WWWWW',
                            help="Address to listen to (3 to 5 ASCII characters)")
    arg_parser.add_argument('-ce', type=int, nargs='?', default=23,
                            help="chip enbale pin")
    arg_parser.add_argument('--channel', type=int, nargs='?', default=100,
                            help="NRF channel")

    args = arg_parser.parse_args()
    hostname = args.hostname
    port = args.port
    nrf_address = args.address
    ce_pin = args.ce
    nrf_channel = args.channel

    mqtt_client = MQTTCLient()
    mqtt_client.Connect()

    # Verify that address is between 3 and 5 characters.
    if not (2 < len(nrf_address) < 6):
        print(
            f'Invalid address {nrf_address}. Addresses must be between 3 and 5 ASCII characters.')
        sys.exit(1)

    print(f'Connecting to GPIO daemon on {hostname}:{port} ...')
    pi_gpio_d = pigpio.pi(hostname, port)
    if not pi_gpio_d.connected:
        print("Not connected to Raspberry Pi ... goodbye.")
        sys.exit()

    nrf = NRF24(pi_gpio_d, ce=ce_pin, payload_size=RF24_PAYLOAD.MAX, channel=nrf_channel,
                data_rate=RF24_DATA_RATE.RATE_250KBPS, pa_level=RF24_PA.MAX, address_bytes=len(nrf_address))
    nrf.open_reading_pipe(RF24_RX_ADDR.P1, nrf_address)
    nrf.show_registers()

    ws = WeatherStation()

    try:
        print(f'Receiving from {nrf_address} on channel {nrf_channel}')

        while True:
            while nrf.data_ready():
                payload = nrf.get_payload()
                # print(payload)
                ws.Deserialize(payload)

                print(f"T={ws.Temperature:.2f}\tH={ws.Humidity:.2f}\t\
                      P={ws.Pressure:.2f}\tSM={ws.SoilMoisture:.2f}\t\
                      ST={ws.SoilTemperature:.2f}\tWD={ws.WindDirection}\t\
                      WS={ws.WindSpeed:.2f}\tR={ws.Rain:.2f}")

                mqtt_client.Publish("temperature", ws.Temperature)
                mqtt_client.Publish("humidity", ws.Humidity)
                mqtt_client.Publish("pressure", ws.Pressure)
                mqtt_client.Publish("rain", ws.Rain)

                soil = {
                    "moisture": ws.SoilMoisture,
                    "temperature": ws.SoilTemperature
                }
                mqtt_client.Publish("soil", json.dumps(soil))

                wind = {
                    "direction": ws.WindDirection,
                    "speed": ws.WindSpeed,
                }
                mqtt_client.Publish("wind", json.dumps(wind))

                mqtt_client.Publish("last_update", time.strftime("%c"))

            time.sleep(0.01)
    except:
        traceback.print_exc()
        print("powering down")
        mqtt_client.Publish("status", "disconnected")
        nrf.power_down()
        pi_gpio_d.stop()
