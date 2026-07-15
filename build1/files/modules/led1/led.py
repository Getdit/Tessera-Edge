#LED V1
import uasyncio as asyncio

class LED:
    versao = "LED2-v1"

    def __init__(self, led, context):
        self.__cbf = None
        self._led = led

    def set_cbf(self, cbf):
        self.__cbf = cbf

    async def executar(self):
        await asyncio.sleep(2)

        try:
            self._led.value(not self._led.value())
        except Exception as e:
            print(f"Error executing led2 {self.versao}: {e}")
