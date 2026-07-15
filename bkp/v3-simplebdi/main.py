import time
time.sleep(2)

from component_based.component.cbf import TesseraEdge
from component_based.component.interface import ComponentInterface
from motor_bdi import Agente
import machine, network, mip
import uasyncio as asyncio


wlan = network.WLAN(network.STA_IF)
wlan.active(False)
wlan.active(True)
wlan.connect('Galaxy_Eduardo', '123quatro')

mip.install("urequests")

led_status = machine.Pin(2, machine.Pin.OUT)
agente = Agente("Robo_01")

class CrencaTemp(ComponentInterface):

    def instantiante_module(self):
        agente.registrar_plano("crenca_temperatura_alterada", self.module.plano_tratar_temperatura)

    async def loop(self):
        led_status.value(not led_status.value())
        await asyncio.sleep(1)

class SensorDummy(ComponentInterface):

    def instantiante_module(self):
        pass

    async def loop(self):
        await self.module.sensor_dummy(agente)
        await asyncio.sleep(1)


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

comp1 = CrencaTemp("comp1", "plan_tratar_temp")
comp2 = SensorDummy("comp2", "sensor_dummy")
#comp3 = AgentComp("agent")
updater = CompUpdater("updater", "updater")


async def main():
    # Injeção de Dependências


    # Executa o Motor BDI e os Sensores concorrentemente
    task_motor = asyncio.create_task(agente.iniciar_raciocinio())

    await asyncio.sleep(5)  # Deixa rodar por 5 segundos
    agente.parar()


    print("Starting main")
    cbf = ComponentFramework("http://10.199.225.156:8000")

    print("Settings components")
    cbf.add_component(comp1)
    cbf.add_component(comp2)
    cbf.add_component(updater)

    print("Running")
    cbf.start()

    #await asyncio.Event().wait()
    while True:
        # Substitua o Event().wait() por sleep.
        # Mantém o sistema vivo e cede a CPU para as Tasks a cada ciclo.
        await asyncio.sleep(1)

asyncio.run(main())
