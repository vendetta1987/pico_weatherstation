import math
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
    from DS15901.TriggerCounter import TriggerCounter
    from DS15901.WindVane import WindVane
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
        self._bme_mngr = None
        self._temperature = math.nan
        self._humidity = math.nan
        self._pressure = math.nan

        if bme_available:
            self._bme_mngr = BMEManager(0, 2, 3, 4, 1)
        #
        self._soil_moist_mngr = None
        self._soil_moisture = math.nan

        if soil_available:
            self._soil_moist_mngr = SoilMoistureManager(27)
        #
        self._soil_temp_mngr = None
        self._soil_temperature = math.nan

        if ds18_available:
            self._soil_temp_mngr = DS18B20Manager(13)
        #
        self._wind_vane = None
        self._wind_anemometer = None
        self._rain_gauge = None
        self._wind_direction = "X"
        self._wind_speed = math.nan
        self._rain = math.nan

        if ds15_available:
            self._wind_vane = WindVane(26)
            # equals 2.4km/h for one trigger per second
            self._wind_anemometer = TriggerCounter(2.4, 22, True)
            # equals 0.2794mm per trigger
            self._rain_gauge = TriggerCounter(0.2794, 16, False)

    @property
    def Temperature(self) -> float:
        if self._bme_mngr is not None:
            return self._bme_mngr.Temperature
        else:
            return self._temperature

    @Temperature.setter
    def Temperature(self, val: float):
        self._temperature = val

    @property
    def Humidity(self) -> float:
        if self._bme_mngr is not None:
            return self._bme_mngr.Humidity
        else:
            return self._humidity

    @Humidity.setter
    def Humidity(self, val: float):
        self._humidity = val

    @property
    def Pressure(self) -> float:
        if self._bme_mngr is not None:
            return self._bme_mngr.Pressure
        else:
            return self._pressure

    @Pressure.setter
    def Pressure(self, val: float):
        self._pressure = val

    @property
    def SoilMoisture(self) -> float:
        if self._soil_moist_mngr is not None:
            return self._soil_moist_mngr.Moisture
        else:
            return self._soil_moisture

    @SoilMoisture.setter
    def SoilMoisture(self, val: float):
        self._soil_moisture = val

    @property
    def SoilTemperature(self) -> float:
        if self._soil_temp_mngr is not None:
            return self._soil_temp_mngr.Temperature
        else:
            return self._soil_temperature

    @SoilTemperature.setter
    def SoilTemperature(self, val: float):
        self._soil_temperature = val

    @property
    def WindDirection(self) -> str:
        if self._wind_vane is not None:
            return self._wind_vane.AverageDirection
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

    def Update(self):
        if self._wind_vane is not None:
            self._wind_vane.UpdateHistogram()

    def Reset(self):
        if self._wind_vane is not None:
            self._wind_vane.ResetHistogram()

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

        wind_dir = self.WindDirection
        wind_dir_len = len(wind_dir)
        packed_structs.append(struct.pack(f"!B2sB{wind_dir_len}s", 2, b"WD", wind_dir_len,
                                          wind_dir.encode("ascii")))

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
                # float value
                value = struct.unpack("!f", packet[:value_byte_cnt])[0]
            else:
                # some string
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
            elif property_type == b"WD":
                self.WindDirection = value.decode("ascii")
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
