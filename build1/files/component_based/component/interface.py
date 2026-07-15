from component_based.component.context import Context
import component_based.settings as settings

import urandom as random
import uasyncio as asyncio
import uos as os
import binascii
import sys
import gc, machine


def generate_uuid4():
    # Gera 16 bytes de hardware RNG
    b = bytearray(random.getrandbits(8) for _ in range(16))
    b[6] = (b[6] & 0x0f) | 0x40  # Versão 4
    b[8] = (b[8] & 0x3f) | 0x80  # Variante RFC 4122
    h = binascii.hexlify(b).decode()
    return f"{h[:8]}-{h[8:12]}-{h[12:16]}-{h[16:20]}-{h[20:]}"


class ComponentInterface():

    def __init__(self, component_name: str, component_lib: str):
        print(f"Instantiating Component {component_name}, with lib {component_lib}")
        self.__context = None
        self.__parent_component = None
        self.__running = False
        self.__module = None
        self.__first_run = True
        self.__id = generate_uuid4()

        print(f"Component {component_name}: setting up the lib path")
        base_path = ("/" + settings.UPDATABLE_MODULES_DIR + component_lib)

        # Se for um diretório, o spec precisa do caminho do __init__.py
        if (os.stat(base_path)[0] & 0x4000) != 0:
            self.__path = base_path + "/__init__.py"
        else:
            self.__path = base_path

        self.__component_name = component_name
        self.__component_lib = component_lib

        print(f"Component {component_name}: creating task")
        self.__task_ref = None

        print(f"Component {component_name}: loading module")
        self.__load_module()
        print(f"Component {component_name}: instantiate module")
        self.instantiante_module()
        print(f"Component {component_name}: Pronto")

    def __load_module(self):
        try:
            # 1. Resolver diretório raiz via string split (mais leve que pathlib)
            # Exemplo: de '/lib/modules/bdi1/__init__.py' extraímos '/lib/modules'
            parts = self.__path.rsplit('/', 2)
            root_modules_dir = parts[0] if len(parts) >= 3 else '/'

            if root_modules_dir not in sys.path:
                # sys.path funciona perfeitamente no MicroPython
                sys.path.insert(0, root_modules_dir)

            # 2. Importação Dinâmica
            # Ela injeta no sys.modules e executa o __init__.py automaticamente.
            self.module = __import__(self.__component_lib)

        except Exception as e:
            raise ImportError(f"{self.get_component_name()}: Erro ao importar: {e}")

    def __reload_total(self):
        # 1. Identifica submódulos (sys.modules é um dicionário no MicroPython)
        prefixo = self.__component_lib + "."
        submodulos = [m for m in sys.modules.keys() if type(m) is str and m.startswith(prefixo)]

        # 2. Remove do cache global
        for m in submodulos:
            del sys.modules[m]

        # 3. Remove o módulo principal
        if self.__component_lib in sys.modules:
            del sys.modules[self.__component_lib]

        # 4. CRÍTICO PARA EMBARCADOS: Limpeza de RAM.
        # Ao deletar as referências do sys.modules, os objetos de código ficam órfãos.
        # O Garbage Collector deve ser chamado imediatamente para evitar MemoryError e fragmentação de Heap.
        gc.collect()

        # 5. Faz o load do zero
        return self.__load_module()

    def start(self):
        t = machine.RTC().datetime()

        # Formatando a string (ignoramos t[3] que é o dia da semana)
        print("-- Starting: {:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}.{:06d}".format(
            t[0], t[1], t[2], t[4], t[5], t[6], t[7]
        ))
        if not self.__first_run:
            self.__reload_total()
            self.instantiante_module()
        else:
            self.__first_run = False


        if not (self.__parent_component and self.__context):
            raise AttributeError("Could not start component because there is no parent or context")

        if self.is_running():
            print("Component is already running")
            return
        print(f"Component {self.get_component_name()}: Start")
        self.__task_ref = asyncio.create_task(self.__execution())

    async def stop(self):
        print(f"Component {self.get_component_name()}: Stop")
        self.__task_ref.cancel()

        try:
            # Aguarda bloqueando (assincronamente) até que a task termine o seu ciclo
            await self.__task_ref
        except asyncio.CancelledError:
            # O erro propaga-se até aqui quando a task finalmente morre
            pass

            # Aqui, task.done() é 100% garantido como True
        print(f"[{self.__component_name}] Encerrado com segurança. done={self.__task_ref.done()}")

    def is_running(self) -> bool:
        print(self.__task_ref is not None)
        if self.__task_ref is not None:
            print(self.__task_ref.done())
        else:
            print(False)
        return self.__task_ref is not None and not self.__task_ref.done()

    def set_context(self, context: Context):
        print(f"Component {self.get_component_name()}: Settings context")
        self.__context = context

    def get_context(self) -> Context:
        return self.__context

    def set_parent_component(self, parent_component):
        self.__parent_component = parent_component

    def get_parent_component(self):
        return self.__parent_component

    def get_component_name(self) -> str:
        return self.__component_name

    def get_component_lib(self) -> str:
        return self.__component_lib

    async def __execution(self):
        try:
            while True:
                await self.loop()
        except asyncio.CancelledError:
            # Tratamento limpo de parada (equivalente a checar um Event() de stop)
            print(f"[{self.__component_name}] Desligamento seguro executado.")
            raise
        except Exception as e:
            # SE A TASK MORRER, O ERRO VAZA AQUI
            print(f"[{self.__component_name}] FATAL ERROR NA TASK: {e}")
            import sys
            sys.print_exception(e)
            raise



    def loop(self):
        """
        Deve implementar a rotina de uma execução deste componente.
        Aqui devem ser chamados todos
        """
        raise NotImplementedError("Subclasses devem implementar este método")

    def instantiante_module(self):
        """
        Deve implementar a instanciação do módulo. Lembre de que será reexecutado caso o módulo seja reiniciado
        :return:
        """
        raise NotImplementedError("Subclasses devem implementar este método")