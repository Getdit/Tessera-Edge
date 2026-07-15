import time
time.sleep(2)

from component_based.component.cbf import TesseraEdge
from component_based.component.interface import ComponentInterface
import machine, network, mip, gc
import uasyncio as asyncio

import machine

TEST_PIN = 2
ITERATIONS_CPU = 50000
ITERATIONS_IO = 500000
pin = machine.Pin(TEST_PIN, machine.Pin.OUT)

# 1. Ler a frequência atual da CPU
freq_atual = machine.freq()
print(f"Frequência atual: {freq_atual / 1_000_000} MHz")

# 2. Alterar a frequência da CPU (Exemplo: 240 MHz)
machine.freq(240_000_000)




def test_fpu_pi_calc():
    pi = 0.0
    for i in range(ITERATIONS_CPU):
        # Evitando ternários complexos para reduzir overhead de parsing do bytecode
        if i % 2 == 0:
            pi += 1.0 / (2.0 * i + 1.0)
        else:
            pi -= 1.0 / (2.0 * i + 1.0)
    return pi

def test_io_toggle():
    # Cache local do objeto e método.
    # Isso evita a busca no dicionário de atributos do Python em cada iteração,
    # medindo o I/O mais puro possível que o interpretador consegue entregar.
    p = pin
    val = p.value
    for _ in range(ITERATIONS_IO):
        val(1)
        val(0)

class C1(ComponentInterface):

    def instantiante_module(self):
        pass

    async def loop(self):
        time.sleep(1)  # Estabiliza serial

        print("Iniciando Benchmark (MicroPython)...")
        print("Frequencia CPU: {} MHz".format(machine.freq() // 1000000))

        # Fase 1: Calibração / Warm-up
        # Força o interpretador a fazer o parsing inicial e compilar o bytecode
        test_fpu_pi_calc()
        test_io_toggle()

        # Fase 2: Execução Crítica

        # --- Teste CPU (FPU) ---
        gc.collect()  # Limpa a RAM fragmentada para iniciar do estado zero
        start_time = time.ticks_us()
        test_fpu_pi_calc()
        cpu_time = time.ticks_diff(time.ticks_us(), start_time)

        time.sleep_ms(10)  # Yield para o RTOS subjacente (WDT)

        # --- Teste I/O (HAL) ---
        gc.collect()
        start_time = time.ticks_us()
        test_io_toggle()
        io_time = time.ticks_diff(time.ticks_us(), start_time)

        # Exportação de Telemetria (CSV)
        print("\n--- Resultados (microssegundos) ---")
        print("TESTE,ITERACOES,TEMPO_TOTAL_US")
        print("CPU_FPU,{},{}".format(ITERATIONS_CPU, cpu_time))
        print("IO_TOGGLE,{},{}".format(ITERATIONS_IO, io_time))
        await asyncio.sleep(1)

class ComponentFramework(TesseraEdge):
    pass

comp1 = C1("comp1", "plan_tratar_temp")


async def main():


    print("Starting main")
    cbf = ComponentFramework("http://10.199.225.156:8000")

    print("Settings components")
    cbf.add_component(comp1)

    print("Running")
    cbf.start()

    #await asyncio.Event().wait()
    while True:
        # Substitua o Event().wait() por sleep.
        # Mantém o sistema vivo e cede a CPU para as Tasks a cada ciclo.
        await asyncio.sleep(1)

asyncio.run(main())
