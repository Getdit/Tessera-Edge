import asyncio


class Agente:
    def __init__(self, nome):
        self.nome = nome

        # Base de Crenças (Beliefs): Estado atual percebido do mundo
        self.crencas = {}

        # Fila de Desejos (Desires/Events): Eventos internos ou externos pendentes
        self.desejos = []

        # Pilha de Intenções (Intentions): Tarefas (Tasks) ativas no Event Loop
        self.intencoes = set()

        # Biblioteca de Planos (Plan Library): Mapeamento de Eventos -> Corrotinas
        self.biblioteca_planos = {}

        self._loop_ativo = False

    # ==========================================
    # GESTÃO DE CRENÇAS E EVENTOS
    # ==========================================
    def atualizar_crenca(self, chave, valor):
        """Atualiza o estado e dispara um evento (desejo) se houver mudança."""
        if self.crencas.get(chave) != valor:
            self.crencas[chave] = valor
            self.adicionar_desejo(f"crenca_{chave}_alterada")

    def ler_crenca(self, chave, default=None):
        return self.crencas.get(chave, default)

    def adicionar_desejo(self, evento, payload=None):
        """Adiciona um novo objetivo ou evento à fila de deliberação."""
        self.desejos.append({"evento": evento, "payload": payload})

    # ==========================================
    # GESTÃO DE PLANOS (MODULARIDADE)
    # ==========================================
    def registrar_plano(self, gatilho_evento, corrotina_plano):
        """Regista uma função assíncrona para responder a um evento específico."""
        if gatilho_evento not in self.biblioteca_planos:
            self.biblioteca_planos[gatilho_evento] = []
        self.biblioteca_planos[gatilho_evento].append(corrotina_plano)

    # ==========================================
    # O MOTOR DE DELIBERAÇÃO (AGENT LOOP)
    # ==========================================
    async def _executar_intencao(self, plano, contexto):
        """Wrapper de ciclo de vida para garantir a limpeza da Task (Intenção)."""
        try:
            # A checagem de contexto (Condition) ocorre dentro do próprio plano
            await plano(self, contexto)
        except Exception as e:
            print(f"[{self.nome}] Falha Crítica na Intenção: {e}")
        finally:
            task_atual = asyncio.current_task()
            if task_atual in self.intencoes:
                self.intencoes.remove(task_atual)

    async def iniciar_raciocinio(self, tick_ms=50):
        """Laço principal do agente. Deve rodar como uma Task contínua."""
        self._loop_ativo = True
        print(f"[{self.nome}] Motor BDI Inicializado.")

        while self._loop_ativo:
            if self.desejos:
                desejo_atual = self.desejos.pop(0)
                evento = desejo_atual["evento"]

                # Busca planos registados para este evento
                planos_candidatos = self.biblioteca_planos.get(evento, [])

                for plano in planos_candidatos:
                    # Instancia a Intenção despachando-a para o RTOS/Event Loop
                    task = asyncio.create_task(self._executar_intencao(plano, desejo_atual))
                    self.intencoes.add(task)

                    # Em BDI clássico, escolhemos apenas o primeiro plano aplicável.
                    # Pode-se remover o 'break' caso queira disparar múltiplos planos em paralelo.
                    break

                    # Cede processamento para que as Intenções e o Hardware operem
            await asyncio.sleep(tick_ms / 1000.0)

    def parar(self):
        """Mata o ciclo de raciocínio e cancela todas as intenções ativas."""
        self._loop_ativo = False
        for task in list(self.intencoes):
            task.cancel()
        print(f"[{self.nome}] Agente Desligado.")