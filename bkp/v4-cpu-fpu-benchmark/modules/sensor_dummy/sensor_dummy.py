import uasyncio as asyncio

async def sensor_dummy(agente):
    await asyncio.sleep(1)
    print("\n[Sensor] Nova leitura recebida.")
    # A atualização da crença gera automaticamente o evento 'crenca_temperatura_alterada'
    agente.atualizar_crenca("temperatura", 35.5)