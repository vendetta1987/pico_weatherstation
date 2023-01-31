import random
import struct


class WeatherStation:
    def __init__(self):
        pass

    @property
    def Temperature(self) -> float:
        return random.randrange(-150, 400)/10

    @property
    def Humidity(self) -> float:
        return random.randrange(0, 1000)/10

    def Serialize(self) -> bytes:
        tmp = []
        tmp.append(b"T")  # 1
        tmp.append(struct.pack("f", self.Temperature))  # 4
        tmp.append(b";H")  # 2
        tmp.append(struct.pack("f", self.Humidity))  # 4
        tmp.append(b";X")  # 2

        bin = bytes().join(tmp)
        # print(f"serialized {len(bin)} bytes")
        return bin

    @staticmethod
    def Deserialize(bin: bytes):
        for msg in bin.split(b";"):
            t = chr(msg[0])

            if t == "X":
                break

            val = struct.unpack("f", msg[1:])[0]

            if t == "H":
                print(f"humidity = {val}")
            elif t == "T":
                print(f"temperature = {val}")
