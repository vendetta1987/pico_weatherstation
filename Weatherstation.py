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

        if soil_available:
            self._soil_M = SoilMoistureManager(27)
        else:
            self._soil_M = None

        if ds18_available:
            self._soil_T = DS18B20Manager(13)
        else:
            self._soil_T = None

        if ds15_available:
            self._wind_vane = WindVane(26)
            self._wind_anemometer = TriggerCounter(2.4, 15)
            self._rain_gauge = TriggerCounter(0.2794, 14)
        else:
            self._wind_vane = None
            self._wind_anemometer = None
            self._rain_gauge = None

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

    def Serialize(self) -> bytes:
        tmp = []
        tmp.append(b"T")  # 1
        tmp.append(struct.pack("f", self.Temperature))  # 4
        tmp.append(b";H")  # 2
        tmp.append(struct.pack("f", self.Humidity))  # 4
        tmp.append(b";P")  # 2
        tmp.append(struct.pack("f", self.Pressure))  # 4

        # TODO: two letter properties?
        # tmp.append(b";SM")  # 3
        # tmp.append(struct.pack("f", self.SoilMoisture))  # 4
        # tmp.append(b";ST")  # 3
        # tmp.append(struct.pack("f", self.SoilTemperature))  # 4

        # TODO: string property?
        # tmp.append(b";WD")  # 3
        # tmp.append(struct.pack("f", self.WindDirection))  # 4
        # tmp.append(b";WS")  # 3
        # tmp.append(struct.pack("f", self.WindSpeed))  # 4

        # tmp.append(b";R")  # 2
        # tmp.append(struct.pack("f", self.Rain))  # 4

        tmp.append(b";X")  # 2

        bin = bytes().join(tmp)
        print(f"serialized {len(bin)} bytes")
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
                    elif t == "SM":
                        self.SoilMoisture = val
                    elif t == "ST":
                        self.SoilTemperature = val
                    elif t == "WD":
                        self.WindDirection = val
                    elif t == "WS":
                        self.WindSpeed = val
                    elif t == "R":
                        self.Rain = val
                    else:
                        pass
                except:
                    msg = msg[1:]
                    print(
                        f"error unpacking {t} with length {len(msg)} -> {msg}")
