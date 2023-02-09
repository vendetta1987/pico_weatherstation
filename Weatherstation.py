import struct

try:
    from BME280.Manager import BMEManager
except:
    bme_available = False
else:
    bme_available = True


class WeatherStation:
    _temperature: float
    _humidity: float
    _pressure: float

    def __init__(self):
        if bme_available:
            self.bme_mngr = BMEManager()
        else:
            self.bme_mngr = None

    @property
    def Temperature(self) -> float:
        if bme_available:
            return self.bme_mngr.sensor.temperature
        else:
            return self._temperature

    @Temperature.setter
    def Temperature(self, val: float):
        self._temperature = val

    @property
    def Humidity(self) -> float:
        if bme_available:
            return self.bme_mngr.sensor.humidity
        else:
            return self._humidity

    @Humidity.setter
    def Humidity(self, val: float):
        self._humidity = val

    @property
    def Pressure(self) -> float:
        if bme_available:
            return self.bme_mngr.sensor.pressure
        else:
            return self._pressure

    @Pressure.setter
    def Pressure(self, val: float):
        self._pressure = val

    def Serialize(self) -> bytes:
        tmp = []
        tmp.append(b"T")  # 1
        tmp.append(struct.pack("f", self.Temperature))  # 4
        tmp.append(b";H")  # 2
        tmp.append(struct.pack("f", self.Humidity))  # 4
        tmp.append(b";P")  # 2
        tmp.append(struct.pack("f", self.Pressure))  # 4
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
                    elif t == "P":
                        self.Pressure = val
                    else:
                        pass
                except:
                    msg = msg[1:]
                    print(
                        f"error unpacking {t} with length {len(msg)} -> {msg}")
