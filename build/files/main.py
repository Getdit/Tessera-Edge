import time

time.sleep(2)

from component_based.component.cbf import TesseraEdge
from component_based.component.interface import ComponentInterface
import machine
import uasyncio as asyncio

led2_status = machine.Pin(22, machine.Pin.OUT)
led10_status = machine.Pin(23, machine.Pin.OUT)


class Comp(ComponentInterface):

    def instantiante_module(self):
        self.led_execution = self.module.Led(led2_status, {})

    async def loop(self):
        await self.led_execution.executar()


class Comp1(ComponentInterface):

    def instantiante_module(self):
        self.led_execution = self.module.Led(led10_status, {})

    async def loop(self):
        await self.led_execution.executar()


class CompUpdater(ComponentInterface):

    def instantiante_module(self):
        self.updater = self.module.Updater()

    def start(self):
        self.updater.set_cbf(self.get_parent_component())
        super().start()

    async def loop(self):
        await self.updater.executar()


class ComponentFramework(TesseraEdge):
    pass


comp1 = Comp1("comp1", "led1")
comp2 = Comp("comp2", "led2")
comp3 = CompUpdater("comp3", "updater")


async def main():
    print("Starting main")
    cbf = ComponentFramework("http://10.133.98.156:8000")

    print("Settings components")
    cbf.add_component(comp1)
    cbf.add_component(comp2)
    cbf.add_component(comp3)

    print("Running")
    cbf.start()

    # await asyncio.Event().wait()
    while True:
        # Substitua o Event().wait() por sleep.
        # Mantém o sistema vivo e cede a CPU para as Tasks a cada ciclo.
        await asyncio.sleep(1)


asyncio.run(main())
