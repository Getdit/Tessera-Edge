"""
Classe contexto para ser utilizada em interface
"""
import uasyncio as asyncio


class Context():
    """
    classe contexto padrão
    """
    __context = None
    __lock = None

    def __init__(self, default_context: dict = None):
        if default_context is None:
            self.__context = default_context
        self.__lock = asyncio.Lock()

    def get(self, value):
        with self.__lock:
            return self.__context.get(value)

    def set(self, key, value):
        with self.__lock:
            self.__context[key] = value


