import argparse
import json
import random
import sys
import time
import traceback
import math

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


def ForwardWeatherStationData(ws: WeatherStation, mqtt_client: MQTTCLient, received_packets: list[bytes]):
    for packet in received_packets:
        ws.Deserialize(packet)

    print(f"T={ws.Temperature:.2f}\tH={ws.Humidity:.2f}\t\
            P={ws.Pressure:.2f}\tSM={ws.SoilMoisture:.2f}\t\
            ST={ws.SoilTemperature:.2f}\tWD={ws.WindDirection}\t\
            WS={ws.WindSpeed:.2f}\tR={ws.Rain:.2f}")

    if not math.isnan(ws.Temperature):
        mqtt_client.Publish("temperature", str(ws.Temperature))
    if not math.isnan(ws.Humidity):
        mqtt_client.Publish("humidity", str(ws.Humidity))
    if not math.isnan(ws.Pressure):
        mqtt_client.Publish("pressure", str(ws.Pressure))
    if not math.isnan(ws.Rain):
        mqtt_client.Publish("rain", str(ws.Rain))

    soil = {}

    if not math.isnan(ws.SoilMoisture):
        soil["moisture"] = ws.SoilMoisture
    if not math.isnan(ws.SoilTemperature):
        soil["temperature"] = ws.SoilTemperature

    if len(soil) > 0:
        mqtt_client.Publish("soil", json.dumps(soil))

    wind = {}

    if ws.WindDirection != "X":
        wind["direction"] = ws.WindDirection
    if not math.isnan(ws.WindSpeed):
        wind["speed"] = ws.WindSpeed

    if len(wind) > 0:
        mqtt_client.Publish("wind", json.dumps(wind))

    mqtt_client.Publish("last_update", time.strftime("%c"))


def WakePicoAndReceive(nrf: RF24, timeout_ms: int = 100) -> list[bytes]:
    # wake up call
    nrf.listen = False
    nrf.write(b"wake_up")
    # wait for reaction
    nrf.listen = True

    received_packets = []
    target_time = time.process_time_ns() + (timeout_ms * 1000000)

    while target_time > time.process_time_ns():
        has_payload, _ = nrf.available_pipe()
        if has_payload:
            packet = nrf.read(nrf.payload_size)
            received_packets.append(packet)

    unique_packets = {}
    for packet in received_packets:
        unique_packets[str(packet)] = packet

    return list(unique_packets.values())


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(
        prog="Hub.py", description="WeatherStation hub application with MQTT connection")
    arg_parser.add_argument('-n', '--hostname', type=str, default='raspberrypi4.fritz.box',
                            help="Hostname for MQTT server.")
    arg_parser.add_argument('-ce', type=int, nargs='?', default=23,
                            help="NRF chip enbale pin")
    arg_parser.add_argument('--channel', type=int, nargs='?', default=100,
                            help="NRF channel")
    arg_parser.add_argument('--receive_addr', type=str, nargs='?', default='WSone',
                            help="NRF receiving pipe address (5 ASCII characters)")
    arg_parser.add_argument('--send_addr', type=str, nargs='?', default='WStwo',
                            help="NRF sending pipe address (5 ASCII characters)")

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

    retry_limit = 100

    try:
        i = 0
        while i < retry_limit:
            received_packets = WakePicoAndReceive(nrf, 500)

            if len(received_packets) > 0:
                ForwardWeatherStationData(ws, mqtt_client, received_packets)
                print(f"took {i} attempts, received {len(received_packets)} packets")
                break
            else:
                i += 1
                time.sleep(0.01*random.randrange(1, 10))

        if i >= retry_limit:
            print("retry limit exceeded")
    except:
        traceback.print_exc()

    Shutdown()
