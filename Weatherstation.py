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
        packed_structs = []
        # !  network byte order
        # B  number of bytes denoting the type
        # ns n digits as an array/string
        # B  number of bytes denoting the value
        # f  a float value
        packed_structs.append(struct.pack(
            "!B1sBf", 1, b"T", 4, self.Temperature))
        packed_structs.append(struct.pack("!B1sBf", 1, b"H", 4, self.Humidity))
        packed_structs.append(struct.pack("!B1sBf", 1, b"P", 4, self.Pressure))
        packed_structs.append(struct.pack(
            "!B2sBf", 2, b"SM", 4, self.SoilMoisture))
        packed_structs.append(struct.pack(
            "!B2sBf", 2, b"ST", 4, self.SoilTemperature))
        packed_structs.append(struct.pack("!B2sB3s", 2, b"WD", 3,
                                          self.WindDirection.encode("ascii")))
        packed_structs.append(struct.pack(
            "!B2sBf", 2, b"WS", 4, self.WindSpeed))
        packed_structs.append(struct.pack("!B1sBf", 1, b"R", 4, self.Rain))

        packets = []
        idx = 0
        struct_cnt = len(packed_structs)
        while idx < struct_cnt:
            packet = bytes()
            while (idx < struct_cnt) and ((len(packed_structs[idx])+len(packet)) < 31):
                packet = bytes().join([packet, packed_structs[idx]])
                idx += 1
            packet = bytes().join([struct.pack("!B", len(packet)), packet])
            packets.append(packet)

        length = 0
        for p in packets:
            length += len(p)

        print(f"serialized {length} bytes in {len(packets)} packets")
        return packets

    def Deserialize(self, packet: bytes):
        packet_byte_cnt = struct.unpack("!B", packet[:1])[0]
        packet = packet[1:]
        consumed_cnt = 0
        while consumed_cnt < packet_byte_cnt:
            type_byte_cnt = struct.unpack("!B", packet[:1])[0]
            packet = packet[1:]
            consumed_cnt += 1

            property_type = struct.unpack(
                f"!{type_byte_cnt}s", packet[:type_byte_cnt])[0]
            packet = packet[type_byte_cnt:]
            consumed_cnt += type_byte_cnt

            value_byte_cnt = struct.unpack("!B", packet[:1])[0]
            packet = packet[1:]
            consumed_cnt += 1

            if value_byte_cnt == 4:
                value = struct.unpack("!f", packet[:value_byte_cnt])[0]
            else:
                value = struct.unpack(
                    f"!{value_byte_cnt}s", packet[:value_byte_cnt])[0]

            packet = packet[value_byte_cnt:]
            consumed_cnt += value_byte_cnt

            if property_type == b"H":
                self.Humidity = value
            elif property_type == b"T":
                self.Temperature = value
            elif property_type == b"P":
                self.Pressure = value
            elif property_type == b"SM":
                self.SoilMoisture = value
            elif property_type == b"ST":
                self.SoilTemperature = value
            elif property_type == "WD":
                self.WindDirection = value
            elif property_type == b"WS":
                self.WindSpeed = value
            elif property_type == b"R":
                self.Rain = value
            else:
                pass


if __name__ == "__main__":
    ws = WeatherStation()
    packets = ws.Serialize()
    ws.Deserialize(packets[0])
