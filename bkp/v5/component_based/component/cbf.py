from .interface import ComponentInterface
from component_based.utils.ota_manager import OTAManager
from component_based.component.context import Context

import uasyncio as asyncio


class TesseraEdge():

    def __init__(self, update_url: str):
        self.__components = {}
        self.__stop = False
        self.__context: Context = Context()

        self.__ota_manager = OTAManager(update_url)

        self.__components_by_lib = {}

    def add_component(self, component: ComponentInterface):
        component.set_parent_component(self)
        component.set_context(self.__context)
        self.__components[component.get_component_name()] = component

    def remove_component(self, component: ComponentInterface):
        self.__components.pop(component.get_component_name())

    def get_components(self):
        return self.__components

    def stop(self):
        self.__stop = True

        for component in self.__components.values():
            component.stop()

    def start(self):
        self.__stop = False
        for component in self.__components.values():
            lib_name = component.get_component_lib()
            if not (lib_name in self.__components_by_lib.keys()):
                self.__components_by_lib[lib_name] = []
            self.__components_by_lib[lib_name].append(component)

            component.start()

        #self.__run()

    def set_context(self, name: str, value):
        self.__context.set(name, value)

    def set_initial_context(self, context: Context):
        self.__context = context

    def __run(self):

        while not self.__stop:
            asyncio.sleep_ms(10)

    async def update_components(self):
        component_libs = self.__ota_manager.verify_updates()

        for component_lib, filepaths in component_libs.items():
            for component in self.__components_by_lib[component_lib]:
                await component.stop()

            self.__ota_manager.update_lib(filepaths)

            for component in self.__components_by_lib[component_lib]:
                await component.start()
