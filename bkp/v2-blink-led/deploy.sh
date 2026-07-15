#!/bin/bash

# Aborta o script imediatamente se qualquer comando falhar
set -e

# ==========================================
# Configurações de Hardware e Diretórios
# ==========================================
PORT="/dev/ttyUSB0"
BAUD="921600"
PROJECT_ROOT="$HOME/cb_project"
SRC_FRAMEWORK="$HOME/component_based_v2"
VFS_DIR="$PROJECT_ROOT/src_producao"
VFS_BIN="vfs_novo.bin"

# ==========================================
# Pipeline de Deploy
# ==========================================

echo "[1/6] Acedendo ao diretório do projeto..."
cd $PROJECT_ROOT

echo "[2/6] Sincronizando código fonte do framework..."
mkdir -p $VFS_DIR
# Limpeza prévia para garantir que ficheiros removidos no source não fiquem órfãos no VFS
rm -rf $VFS_DIR/*
cp -r $SRC_FRAMEWORK/{boot.py,main.py,component_based,modules} $VFS_DIR/

echo "[3/6] Purgando binários incompatíveis (CPython cache)..."
find $VFS_DIR/ -type d -name "__pycache__" -exec rm -rf {} +

echo "[4/6] Compilando imagem LittleFS..."
mklittlefs -c $VFS_DIR/ -b 4096 -p 256 -s 2097152 $VFS_BIN

echo "[5/6] Gravando partição VFS no ESP32..."
# A flag no_reset é obrigatória para impedir que o esptool trave o chip
esptool.py --chip esp32 --port $PORT --baud $BAUD --after no_reset write_flash 0x200000 $VFS_BIN

echo "[6/6] Executando Hard Reset controlado e anexando REPL..."
sleep 1

# Abre o monitor serial para acompanhar a ignição do main.py e das tasks
mpremote repl