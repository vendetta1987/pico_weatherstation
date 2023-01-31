import random

import ustruct as struct
import utime
from machine import SPI, Pin

from NRF24L01 import NRF24L01, POWER_3, SPEED_250K

if __name__ == "__main__":
    spi = SPI(0, sck=Pin(2), mosi=Pin(3), miso=Pin(4))
    cfg = {"spi": spi, "csn": 5, "ce": 6}

    csn = Pin(cfg["csn"], mode=Pin.OUT)
    ce = Pin(cfg["ce"], mode=Pin.OUT)

    nrf = NRF24L01(cfg["spi"], csn, ce, channel=100, payload_size=32)
    nrf.set_power_speed(POWER_3, SPEED_250K)
    print(spi)

    # 57 == ASCII W; 77 == ASCII w
    addresses = (b"\x57\x57\x57\x57\x57", b"\x77\x77\x77\x77\x77")

    nrf.open_tx_pipe(addresses[0])
    nrf.open_rx_pipe(1, addresses[1])

    words = ["Lorem ipsum dolor sit amet cras.",
             "Donec vel viverra ante volutpat.",
             "Cras posuere efficitur pharetra.",
             "Cras iaculis arcu id dolor quis."]
    ascii_words = []

    for word_idx in range(len(words)):
        ascii_words.append(list((ord(l) for l in words[word_idx])))

    while True:
        millis = utime.ticks_ms()
        try:
            rand = random.randrange(len(words))
            bin = bytes()
            bin = bin.join(struct.pack("B", l) for l in ascii_words[rand])
            nrf.send(bin)
        except OSError:
            pass
        else:
            print("sending "+words[rand])

        nrf.recv

        utime.sleep_ms(100)
