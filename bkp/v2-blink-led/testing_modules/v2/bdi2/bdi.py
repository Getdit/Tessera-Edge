#BDI 2 V2
import uasyncio as asyncio

class AgenteBDI:
    """
    # --- Simulação do Contexto Compartilhado ---
    # Este dicionário funciona como a "memória central"
    memoria_global = {
        "bateria": 25,
        "vitima_detectada": True
    }

    # Criando o agente com o "ponteiro" para a memória
    robo_resgate = AgenteBDI("Alpha-1", memoria_global)

    # Executando o ciclo BDI
    robo_resgate.perceber()
    robo_resgate.deliberar()
    robo_resgate.planejar()
    robo_resgate.executar()
    """
    versao = "BDI2-v2"

    def __init__(self, nome, contexto_compartilhado):
        self.nome = nome
        # 'believes' é a nossa referência ao dicionário global (o "ponteiro")
        self.crenças = contexto_compartilhado
        self.desejos = []  # Objetivos abstratos
        self.intenções = []  # Plano de ação imediato

    def perceber(self):
        print(f"\n--- [1. PERCEPÇÃO] ---    {self.versao}")
        # Simula a leitura de sensores alterando o dicionário compartilhado
        print(f"Lendo sensores... Bateria: {self.crenças['bateria']}% | Vítima: {self.crenças['vitima_detectada']}    {self.versao}")
        pass

    def deliberar(self):
        print(f"--- [2. DELIBERAÇÃO (Desejos)] ---    {self.versao}")
        self.desejos = []

        # Define desejos baseados nas crenças
        if self.crenças['bateria'] < 30:
            self.desejos.append("RECARREGAR_ENERGIA")

        if self.crenças['vitima_detectada']:
            self.desejos.append("SALVAR_VITIMA")

        print(f"Desejos atuais: {self.desejos}    {self.versao}")

    def planejar(self):
        print(f"--- [3. PLANEJAMENTO (Intenções)] ---    {self.versao}")
        # Transforma o desejo prioritário em intenção (compromisso)
        if "RECARREGAR_ENERGIA" in self.desejos:
            self.intenções = ["LOCALIZAR_TOMADA", "CONECTAR"]
        elif "SALVAR_VITIMA" in self.desejos:
            self.intenções = ["MOVER_ATE_VITIMA", "PRESTAR_SOCORRO"]
        else:
            self.intenções = ["PATRULHAR"]

        print(f"Intenções confirmadas: {self.intenções}    {self.versao}")

    async def executar(self):
        print(f"--- [4. EXECUÇÃO] ---    {self.versao}")
        for acao in self.intenções:
            print(f"Executando: {acao}...    {self.versao}")

            # Consequências das ações nas crenças
            if acao == "CONECTAR":
                self.crenças['bateria'] = 100
            if acao == "PRESTAR_SOCORRO":
                self.crenças['vitima_detectada'] = False

        print("Ciclo finalizado.")
