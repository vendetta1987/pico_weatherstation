import argparse
import json
import random
import sys
import time
import traceback

from pyrf24 import RF24, RF24_PA_MAX, RF24_250KBPS, RF24_CRC_16

from MQTTClient import MQTTCLient
from Weatherstation import WeatherStation


def RegisterSignalHandler():
    import signal

    def signal_handler(sig_num, frame):
        signame = signal.Signals(sig_num).name
        print(
            f'Stop by Signal <{signame}> ({sig_num}) at: {time.strftime("%d.%m.%Y %H:%M:%S")}')
        Shutdown()

    # Interrupt from keyboard (CTRL + C)
    signal.signal(signal.SIGINT,  signal_handler)
    # Signal Handler from terminating processes
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGHUP,  signal_handler)
    # signal.signal(signal.SIGKILL,  signal_handler) #cant be catched anyway


def InitNRF(ce_pin: int, spi: int, address_snd, address_rcv, channel: int) -> RF24:
    radio = RF24(ce_pin, spi)

    if not radio.begin():
        raise OSError("nRF24L01 hardware isn't responding")

    radio.set_pa_level(RF24_PA_MAX)
    radio.open_tx_pipe(address_snd.encode())
    radio.open_rx_pipe(1, address_rcv.encode())
    radio.payload_size = 32
    radio.channel = channel
    radio.data_rate = RF24_250KBPS
    radio.crc_length = RF24_CRC_16
    radio.print_details()

    return radio


def Shutdown():
    print("powering down")

    global do_run
    do_run = False
    mqtt_client.Publish("status", "disconnected")
    nrf.power = False
    sys.exit(0)


def ForwardWeatherStationData(ws: WeatherStation, mqtt_client: MQTTCLient, ws_data: bytes):
    ws.Deserialize(ws_data)

    print(f"T={ws.Temperature:.2f}\tH={ws.Humidity:.2f}\t\
            P={ws.Pressure:.2f}\tSM={ws.SoilMoisture:.2f}\t\
            ST={ws.SoilTemperature:.2f}\tWD={ws.WindDirection}\t\
            WS={ws.WindSpeed:.2f}\tR={ws.Rain:.2f}")

    mqtt_client.Publish("temperature", str(ws.Temperature))
    mqtt_client.Publish("humidity", str(ws.Humidity))
    mqtt_client.Publish("pressure", str(ws.Pressure))
    mqtt_client.Publish("rain", str(ws.Rain))

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


def WakePico(nrf: RF24, timeout_ms: int = 100) -> list[bytes]:
    # wake up call
    # print("sending wake up")
    nrf.listen = False
    result = nrf.write(b"wake_up")

    if not result:
        print("Timeout waiting for transmission to complete.")
    # wait for reaction
    target_time = time.process_time_ns()+(timeout_ms*1000000)

    payload = []
    nrf.listen = True

    while target_time > time.process_time_ns():
        has_payload, _ = nrf.available_pipe()
        if has_payload:
            payload.append(nrf.read(nrf.payload_size))
            break

    return payload


if __name__ == "__main__":
    print("Python NRF24 Simple Receiver Example.")
    # Parse command line argument.
    arg_parser = argparse.ArgumentParser(
        prog="Hub.py", description="WeatherStation hub application with MQTT connection")
    arg_parser.add_argument('-n', '--hostname', type=str, default='raspberrypi4.fritz.box',
                            help="Hostname for MQTT server.")
    arg_parser.add_argument('-ce', type=int, nargs='?', default=23,
                            help="chip enbale pin")
    arg_parser.add_argument('--channel', type=int, nargs='?', default=100,
                            help="NRF channel")
    arg_parser.add_argument('--receive_addr', type=str, nargs='?', default='WSone',
                            help="receiving pipe address (5 ASCII characters)")
    arg_parser.add_argument('--send_addr', type=str, nargs='?', default='WStwo',
                            help="sending pipe address (5 ASCII characters)")

    args = arg_parser.parse_args()
    mqtt_hostname = args.hostname
    address_rcv = args.receive_addr
    address_snd = args.send_addr
    ce_pin = args.ce
    nrf_channel = args.channel
    # Verify that address is between 3 and 5 characters.
    if (not (2 < len(address_rcv) < 6)) or (not (2 < len(address_snd) < 6)):
        print(
            f'Addresses must be between 3 and 5 ASCII characters. receive={address_rcv} send={address_snd}')
        sys.exit(1)

    RegisterSignalHandler()

    nrf = InitNRF(ce_pin, 0, address_snd, address_rcv, nrf_channel)
    ws = WeatherStation()

    mqtt_client = MQTTCLient(mqtt_hostname)
    mqtt_client.Connect()

    do_run = True

    try:
        i = 0
        while do_run:
            payload = WakePico(nrf, 200)

            if len(payload) > 0:
                for packet in payload:
                    print(f"received {packet}")
                    ForwardWeatherStationData(ws, mqtt_client, packet)
                print(f"took {i} attempts")
                i = 0
                time.sleep(3)
            else:
                i += 1
                time.sleep(0.01*random.randrange(1, 10))
    except:
        #traceback.print_exc()
        Shutdown()
