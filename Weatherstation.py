import struct

try:
    from BME280.Manager import BMEManager
except:
    bme_available = False
else:
    bme_available = True

try:
    from CAPSHYG.Manager import SoilMoistureManager
except:
    soil_available = False
else:
    soil_available = True

try:
    from DS18B20.Manager import DS18B20Manager
except:
    ds18_available = False
else:
    ds18_available = True

try:
    from DS15901.WindVane import WindVane
    from DS15901.TriggerCounter import TriggerCounter
except:
    ds15_available = False
else:
    ds15_available = True


class WeatherStation:
    _temperature: float
    _humidity: float
    _pressure: float
    _soil_moisture: float
    _soil_temperature: float
    _wind_direction: str
    _wind_speed: float
    _rain: float

    def __init__(self):
        if bme_available:
            self._bme = BMEManager(0, 2, 3, 4, 1)
        else:
            self._bme = None
            self._temperature = -1
            self._humidity = -1
            self._pressure = -1

        if soil_available:
            self._soil_M = SoilMoistureManager(27)
        else:
            self._soil_M = None
            self._soil_moisture = -1

        if ds18_available:
            self._soil_T = DS18B20Manager(13)
        else:
            self._soil_T = None
            self._soil_temperature = -1

        if ds15_available:
            self._wind_vane = WindVane(26)
            self._wind_anemometer = TriggerCounter(2.4, 15)
            self._rain_gauge = TriggerCounter(0.2794, 14)
        else:
            self._wind_vane = None
            self._wind_anemometer = None
            self._rain_gauge = None
            self._wind_direction = "X"
            self._wind_speed = -1
            self._rain = -1

    @property
    def Temperature(self) -> float:
        if self._bme is not None:
            return self._bme.Temperature
        else:
            return self._temperature

    @Temperature.setter
    def Temperature(self, val: float):
        self._temperature = val

    @property
    def Humidity(self) -> float:
        if self._bme is not None:
            return self._bme.Humidity
        else:
            return self._humidity

    @Humidity.setter
    def Humidity(self, val: float):
        self._humidity = val

    @property
    def Pressure(self) -> float:
        if self._bme is not None:
            return self._bme.Pressure
        else:
            return self._pressure

    @Pressure.setter
    def Pressure(self, val: float):
        self._pressure = val

    @property
    def SoilMoisture(self) -> float:
        if self._soil_M is not None:
            return self._soil_M.Moisture
        else:
            return self._soil_moisture

    @SoilMoisture.setter
    def SoilMoisture(self, val: float):
        self._soil_moisture = val

    @property
    def SoilTemperature(self) -> float:
        if self._soil_T is not None:
            return self._soil_T.Temperature
        else:
            return self._soil_temperature

    @SoilTemperature.setter
    def SoilTemperature(self, val: float):
        self._soil_temperature = val

    @property
    def WindDirection(self) -> str:
        if self._wind_vane is not None:
            return self._wind_vane.Direction
        else:
            return self._wind_direction

    @WindDirection.setter
    def WindDirection(self, val: str):
        self._wind_direction = val

    @property
    def WindSpeed(self) -> float:
        if self._wind_anemometer is not None:
            return self._wind_anemometer.EvaluatedCount
        else:
            return self._wind_speed

    @WindSpeed.setter
    def WindSpeed(self, val: float):
        self._wind_speed = val

    @property
    def Rain(self) -> float:
        if self._rain_gauge is not None:
            return self._rain_gauge.EvaluatedCount
        else:
            return self._rain

    @Rain.setter
    def Rain(self, val: float):
        self._rain = val

    def Serialize(self) -> list[bytes]:
        packets = []

        tmp = []  # byte size of this line, summed up size in tmp
        tmp.append(b"T:")  # 2, 2
        tmp.append(struct.pack("f", self.Temperature))  # 4, 6
        tmp.append(b";H:")  # 3, 9
        tmp.append(struct.pack("f", self.Humidity))  # 4, 13
        tmp.append(b";P:")  # 3, 16
        tmp.append(struct.pack("f", self.Pressure))  # 4, 20
        tmp.append(b";SM:")  # 4, 24
        tmp.append(struct.pack("f", self.SoilMoisture))  # 4, 28
        tmp.append(b";")  # 1, 25

        packets.append(bytes().join(tmp))

        tmp = []
        tmp.append(b"ST:")  # 3, 3
        tmp.append(struct.pack("f", self.SoilTemperature))  # 4, 7
        tmp.append(b";WD:")  # 4, 11
        tmp.append(bytes(self.WindDirection, "ascii"))  # 1-3, 14
        tmp.append(b";WS:")  # 4, 18
        tmp.append(struct.pack("f", self.WindSpeed))  # 4, 22
        tmp.append(b";R:")  # 3, 25
        tmp.append(struct.pack("f", self.Rain))  # 4, 29
        tmp.append(b";")  # 1, 30

        packets.append(bytes().join(tmp))

        length = 0
        for p in packets:
            length += len(p)

        print(f"serialized {length} bytes in {len(packets)} packets")
        return packets

    def Deserialize(self, packet: bytes):
        for entry in packet.split(b";"):
            if b":" in entry:
                key, value = entry.split(b":")

                try:
                    if key == b"WD":
                        value = value.decode("ascii")
                    else:
                        value = struct.unpack("f", value)[0]

                    if key == b"H":
                        self.Humidity = value
                    elif key == b"T":
                        self.Temperature = value
                    elif key == b"P":
                        self.Pressure = value
                    elif key == b"SM":
                        self.SoilMoisture = value
                    elif key == b"ST":
                        self.SoilTemperature = value
                    elif key == "WD":
                        self.WindDirection = value
                    elif key == b"WS":
                        self.WindSpeed = value
                    elif key == b"R":
                        self.Rain = value
                    else:
                        pass
                except:
                    print(
                        f"error unpacking {key} with length {len(entry)} -> {entry}")
