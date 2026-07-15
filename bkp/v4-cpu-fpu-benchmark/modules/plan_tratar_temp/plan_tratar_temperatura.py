import uasyncio as asyncio


# 1. Definimos o Plano (Pode vir de um ficheiro externo)
async def plano_tratar_temperatura(agente, contexto):
    temp_atual = agente.ler_crenca("temperatura")

    # Avaliação do Contexto (Context Condition BDI)
    if temp_atual > 30.0:
        print("[Atuador] Ligando refrigeração assíncrona...")
        await asyncio.sleep(2)  # Simula atuação de I/O de hardware

        # Ação altera crenças resultantes
        agente.atualizar_crenca("sistema_resfriado", True)
        print("[Atuador] Refrigeração concluída.")
    else:
        print("[Lógica] Temperatura aceitável. Plano abortado.")