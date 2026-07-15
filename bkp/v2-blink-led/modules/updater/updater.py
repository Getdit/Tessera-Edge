#Updater V1
import uasyncio as asyncio

class Updater:
    versao = "Updater-v1"

    def __init__(self):
        self.__cbf = None

    def set_cbf(self, cbf):
        self.__cbf = cbf

    async def executar(self):
        await asyncio.sleep(10)
        if self.__cbf is None:
            return

        try:
            print(f"Calling update {self.versao}")
            await self.__cbf.update_components()
        except Exception as e:
            print(f"Error executing update {self.versao}: {e}")
