import struct


class WeatherStation:
    _temperature: float
    _humidity: float

    def __init__(self):
        pass

    @property
    def Temperature(self) -> float:
        return self._temperature

    @Temperature.setter
    def Temperature(self, val: float):
        self._temperature = val

    @property
    def Humidity(self) -> float:
        return self._humidity

    @Humidity.setter
    def Humidity(self, val: float):
        self._humidity = val

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

    def Deserialize(self, bin: bytes):
        for msg in bin.split(b";"):
            if len(msg) > 0:
                t = chr(msg[0])

                if t == "X":
                    break

                try:
                    val = struct.unpack("f", msg[1:])[0]

                    if t == "H":
                        self.Humidity = val
                    elif t == "T":
                        self.Temperature = val
                    else:
                        pass
                except:
                    msg = msg[1:]
                    print(
                        f"error unpacking {t} with length {len(msg)} -> {msg}")
