import paho.mqtt.client as mqtt


class MQTTCLient:
    _TOPIC: str = "Weatherstation"
    _client: mqtt.Client
    _address: str
    _port: int
    is_connected: bool

    def __init__(self, address: str = "localhost", port: int = 1883) -> None:
        self.is_connected = False

        self._address = address
        self._port = port

        self._client = mqtt.Client(client_id="weatherstation")
        self._client.on_connect = self._OnConnect
        self._client.on_message = self._OnMessage

    def __del__(self):
        self._client.disconnect()
        self._client.loop_stop()

    def Connect(self):
        self._client.connect(self._address, self._port)
        self._client.loop_start()

    def Publish(self, topic: str, msg: str):
        if self.is_connected:
            res = self._client.publish(f"{self._TOPIC}/{topic}", msg)
            res.wait_for_publish(3)
        else:
            print("not connected to broker")

    def _OnConnect(self, client, userdata, flags, rc):
        print("connected to MQTT broker")
        self.is_connected = rc == 0

        if self.is_connected:
            self._client.will_set(
                f"{self._TOPIC}/status", "disconnected unexpectedly")
            self._client.publish(f"{self._TOPIC}/status", "connected")

    def _OnMessage(self, client, userdata, msg):
        print(msg.topic+" "+str(msg.payload))
