import argparse
import json
import random
import sys
import time
import traceback

import pigpio
from nrf24 import *

from MQTTClient import MQTTCLient
from Weatherstation import WeatherStation


def RunWeatherStation(payload):
    global ws
    ws.Deserialize(payload)

    print(f"T={ws.Temperature:.2f}\tH={ws.Humidity:.2f}\t\
            P={ws.Pressure:.2f}\tSM={ws.SoilMoisture:.2f}\t\
            ST={ws.SoilTemperature:.2f}\tWD={ws.WindDirection}\t\
            WS={ws.WindSpeed:.2f}\tR={ws.Rain:.2f}")

    global mqtt_client
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


def WakePico(nrf: NRF24, timeout_ms: int = 100):
    start=time.process_time_ns()
    nrf.reset_packages_lost()
    # wake up call
    print("sending wake up")
    nrf.send(b"wake_up")

    try:
        nrf.wait_until_sent()
    except TimeoutError:
        print("Timeout waiting for transmission to complete.")

    # wait for reaction
    woke_up = False
    target_time = time.process_time_ns()+(timeout_ms*1000000)

    while not woke_up and (target_time > time.process_time_ns()):
        if nrf.data_ready():
            while nrf.data_ready():
                payload = nrf.get_payload()
                print("received "+str(payload))
            woke_up = True
            print(f"roundtrip time = {(time.process_time_ns()-start)/1000000}ms")
        else:
            time.sleep(0.001)


if __name__ == "__main__":
    print("Python NRF24 Simple Receiver Example.")
    # Parse command line argument.
    arg_parser = argparse.ArgumentParser(
        prog="Hub.py", description="WeatherStation hub application with MQTT connection")
    arg_parser.add_argument('-n', '--hostname', type=str, default='localhost',
                            help="Hostname for the device running the pigpio daemon.")
    arg_parser.add_argument('-p', '--port', type=int, default=8888,
                            help="Port number of the pigpio daemon.")
    arg_parser.add_argument('--receive_addr', type=str, nargs='?', default='WSone',
                            help="receiving pipe address (5 ASCII characters)")
    arg_parser.add_argument('--send_addr', type=str, nargs='?', default='WStwo',
                            help="sending pipe address (5 ASCII characters)")
    arg_parser.add_argument('-ce', type=int, nargs='?', default=23,
                            help="chip enbale pin")
    arg_parser.add_argument('--channel', type=int, nargs='?', default=100,
                            help="NRF channel")

    args = arg_parser.parse_args()
    hostname = args.hostname
    port = args.port
    address_rcv = args.receive_addr
    address_snd = args.send_addr
    ce_pin = args.ce
    nrf_channel = args.channel
    # Verify that address is between 3 and 5 characters.
    if (not (2 < len(address_rcv) < 6)) or (not (2 < len(address_snd) < 6)):
        print(
            f'Addresses must be between 3 and 5 ASCII characters. receive={address_rcv} send={address_snd}')
        sys.exit(1)

    print(f'Connecting to GPIO daemon on {hostname}:{port} ...')
    pi_gpio_d = pigpio.pi(hostname, port)

    if not pi_gpio_d.connected:
        print("Not connected to Raspberry Pi ... goodbye.")
        sys.exit()

    nrf = NRF24(pi_gpio_d, ce=ce_pin, payload_size=RF24_PAYLOAD.MAX, channel=nrf_channel,
                data_rate=RF24_DATA_RATE.RATE_250KBPS, pa_level=RF24_PA.MAX, address_bytes=len(address_rcv))
    nrf.open_reading_pipe(RF24_RX_ADDR.P1, address_rcv)
    nrf.open_writing_pipe(address_snd)
    nrf.show_registers()

    # ws = WeatherStation()

    # mqtt_client = MQTTCLient()
    # mqtt_client.Connect()

    try:
        i = 0
        while True:
            WakePico(nrf, 200)
            time.sleep(random.random())

        # print(f'Receiving from {nrf_address} on channel {nrf_channel}')
        #
        # while True:
        #    while nrf.data_ready():
        #        payload = nrf.get_payload()
        #
        #        # DEBUG
        #        # print(f"{i}_{payload}")
        #        # i+=1
        #
        #        # RunWeatherStation(payload)
        #
        #    time.sleep(0.01)
    except:
        traceback.print_exc()
        print("powering down")
        mqtt_client.Publish("status", "disconnected")
        nrf.power_down()
        pi_gpio_d.stop()
