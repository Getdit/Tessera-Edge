# Tessera Edge 

**Tessera Edge** é um framework *lightweight* (leve) baseado em componentes, voltado para desenvolvimento de sistemas embarcados assíncronos utilizando **MicroPython** no microcontrolador **ESP32**. 

O objetivo principal do framework é modularizar o hardware e as regras de negócio em **componentes independentes**, com suporte integrado a execução assíncrona (`uasyncio`), comunicação por rede e atualizações OTA (*Over-The-Air* / Updater).

---

## Arquitetura de Componentes

O Tessera Edge baseia-se em uma interface comum (`ComponentInterface`) e em um orquestrador central (`TesseraEdge` / `ComponentFramework`). Cada funcionalidade (por exemplo, controle de LEDs, atuadores, sensores ou rotinas de atualização) é encapsulada em sua própria classe com um ciclo de vida gerenciado assincronamente.

### Exemplo de Estrutura (`main.py`)
```python
from component_based.component.te import TesseraEdge
from component_based.component.interface import ComponentInterface
import machine
import uasyncio as asyncio

# 1. Definir o Componente herdando de ComponentInterface
class CompLED(ComponentInterface):
    def instantiante_module(self):
        # Inicializa o módulo embutido (ex: controle de LED)
        self.led_execution = self.module.Led(machine.Pin(22, machine.Pin.OUT), {})

    async def loop(self):
        # Execução assíncrona contínua do componente
        await self.led_execution.executar()

# 2. Configurar o Framework e registrar componentes
async def main():
    cbf = TesseraEdge("[http://10.133.98.156:8000](http://10.133.98.156:8000)") # URL do servidor de controle/atualização
    
    comp_led = CompLED("comp_led_1", "led_module")
    cbf.add_component(comp_led)
    
    cbf.start()

    while True:
        await asyncio.sleep(1) # Cede tempo de CPU para as tasks assíncronas

asyncio.run(main())
```

# Pré-requisitos e Ferramentas
Para gerar a imagem do sistema de arquivos (VFS), mesclar com o firmware MicroPython e realizar o flash no ESP32, você precisará das seguintes ferramentas instaladas no seu ambiente de desenvolvimento (Linux/macOS):

Python 3.8+

esptool.py: Para manipulação e gravação da memória flash do ESP32.
```
pip install esptool
```
mpremote: Para acesso ao terminal REPL e gerenciamento do MicroPython.

```
pip install mpremote
```
mklittlefs: Ferramenta para criar imagens de sistema de arquivos LittleFS compatíveis com o MicroPython. (Deve estar disponível no seu $PATH).

Firmware base do MicroPython (firmware.bin): Binário base do ESP32 (compilado por você ou baixado diretamente do site oficial do MicroPython).

# Como Buildar o VFS e Gerar Binário Único
Em ambientes embarcados de produção, é altamente recomendável embarcar seu código diretamente na memória do chip de forma automatizada, sem precisar enviar arquivo por arquivo via serial.

O projeto utiliza um script automatizado (build.sh) para empacotar o código em um VFS (Virtual File System) LittleFS e mesclá-lo com o firmware base do MicroPython em um binário único (firmware_comb.bin).

Passo a Passo do Build (build.sh)
Preparação dos Arquivos: O script copia os scripts essenciais (boot.py, main.py, bibliotecas e módulos) para um diretório temporário (build/files/) e limpa arquivos de cache do Python (__pycache__).

Geração do LittleFS (VFS): Utiliza o mklittlefs para gerar uma partição LittleFS de 2MB contendo todo o projeto:

```
mklittlefs -c ~/component_based_v2/build/files/ -b 4096 -p 256 -s 2097152 ~/component_based_v2/build/vfs_novo.bin
```
-b 4096: Tamanho do bloco de flash (4KB).

-p 256: Tamanho da página (256 bytes).

-s 2097152: Tamanho total da partição (2MB ou 0x200000 bytes).

Unificação dos Binários (Merge): Com o comando merge_bin do esptool.py, o firmware base e a partição do sistema de arquivos são combinados em um único arquivo .bin:

```
esptool.py --chip esp32 merge_bin --output ~/component_based_v2/build/firmware_comb.bin \
  0x1000 ~/component_based_v2/build/firmware.bin \
  0x200000 ~/component_based_v2/build/vfs_novo.bin
```
Toque e execute o script para gerar a build:

```
chmod +x build.sh
./build.sh
```
Nota: Verifique se os caminhos no arquivo build.sh (como ~/cb_project/... e ~/component_based_v2/...) condizem com a estrutura atual de pastas no seu computador.

# Como gravar no ESP32 (Deploy)
Com o binário unificado (firmware_comb.bin) gerado, o deploy para a placa se torna simples e rápido, podendo ser executado a partir do offset 0x00.

O projeto disponibiliza o script deploy.sh que realiza a limpeza da flash do ESP32, grava o firmware gerado e abre imediatamente o REPL para monitorar os logs.

Executando o Deploy
Conecte o seu ESP32 via porta USB (geralmente reconhecido como /dev/ttyUSB0 no Linux ou /dev/cu.usbserial-... no macOS) e execute:

```
chmod +x deploy.sh
./deploy.sh
```
O que o script realiza por baixo dos panos:
Apaga a memória flash completamente (Erase):

```
esptool.py --chip esp32 --port /dev/ttyUSB0 erase_flash
```
Grava o binário combinado na posição inicial (0x00):

```
esptool.py --chip esp32 --port /dev/ttyUSB0 --baud 921600 write_flash -z --flash_mode dio --flash_freq 40m 0x00 ~/component_based_v2/build/firmware_comb.bin
```
Abre o Terminal Interativo (REPL):

```
mpremote repl
```