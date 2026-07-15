import time

time.sleep(2)

from component_based.component.cbf import TesseraEdge
from component_based.component.interface import ComponentInterface
import machine
import uasyncio as asyncio

led_status = machine.Pin(2, machine.Pin.OUT)


# class Comp(ComponentInterface):
#
#     def instantiante_module(self):
#         self.bdi = self.module.AgenteBDI(self.get_component_name(), {})
#
#     async def loop(self):
#         await asyncio.sleep(10)
#         await self.bdi.executar()


class Comp1(ComponentInterface):

    def instantiante_module(self):
        pass

    async def loop(self):
        #print com microsegundos
        t = machine.RTC().datetime()

        # Formatando a string (ignoramos t[3] que é o dia da semana)
        print("-- Started: {:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}.{:06d}".format(
            t[0], t[1], t[2], t[4], t[5], t[6], t[7]
        ))
        led_status.value(not led_status.value())
        await asyncio.sleep(100)



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


comp1 = Comp1("comp1", "ota_benchmark")
# comp2 = Comp("comp2", "bdi2")
comp3 = CompUpdater("comp3", "updater")


async def main():
    print("Starting main")
    cbf = ComponentFramework("http://192.168.0.12:8000")

    print("Settings components")
    cbf.add_component(comp1)
    # cbf.add_component(comp2)
    cbf.add_component(comp3)

    print("Running")
    cbf.start()

    # await asyncio.Event().wait()
    while True:
        # Substitua o Event().wait() por sleep.
        # Mantém o sistema vivo e cede a CPU para as Tasks a cada ciclo.
        await asyncio.sleep(1)


asyncio.run(main())
