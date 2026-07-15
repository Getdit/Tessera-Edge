import hashlib, sys, http.server, os, json, threading
from pathlib import Path
from typing import List, Optional


def generate_ota_manifest(
        target_dir: str,
        output_filename: str = "manifest.json",
        exclude_dirs: Optional[List[str]] = None
) -> None:
    """Gera um manifesto JSON com os hashes SHA-256 dos arquivos para OTA."""

    # Pastas padrão de desenvolvimento que não devem ir para o embarcado
    if exclude_dirs is None:
        exclude_dirs = [".git", "__pycache__", ".venv", "env"]

    base_path = Path(target_dir).resolve()
    manifest_path = base_path / output_filename

    manifest = {
        "version": "1.0.0",  # Idealmente injetado via pipeline (ex: Git tag ou timestamp)
        "files": {}
    }

    # Varredura recursiva
    for file_path in base_path.rglob("*"):
        if not file_path.is_file() or file_path.name == output_filename:
            continue

        # Ignora arquivos contidos nos diretórios excluídos
        if any(part in exclude_dirs for part in file_path.parts):
            continue

        # Calcula o hash SHA-256 em blocos (memory-safe)
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256.update(chunk)

        # Converte para caminho relativo padrão POSIX (ex: 'modules/bdi1/core.py')
        # Crucial para o MicroPython reconstruir a árvore de diretórios corretamente
        rel_path = file_path.relative_to(base_path).as_posix()

        manifest["files"][rel_path] = {
            "hash": sha256.hexdigest(),
            "size": file_path.stat().st_size
        }

    # Grava o manifesto no formato JSON
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=4)

    print(f"Manifesto gerado em: {manifest_path} | Arquivos: {len(manifest['files'])}")


def iniciar_servidor_estatico(porta: int, diretorio_alvo: str):
    """
    Inicializa um servidor HTTP não-bloqueante servindo um diretório específico.
    """
    # 1. Validação de path absoluto para segurança
    caminho_absoluto = os.path.abspath(diretorio_alvo)
    if not os.path.exists(caminho_absoluto):
        raise FileNotFoundError(f"Diretório não encontrado: {caminho_absoluto}")

    # 2. Customização do Handler para alterar o diretório raiz (CWD)
    class HandlerCustomizado(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            # Injeta o diretório antes de inicializar a classe pai
            super().__init__(*args, directory=caminho_absoluto, **kwargs)

        # Opcional: Sobrescrever log_message para silenciar logs padrão
        # ou redirecioná-los para o módulo logging que configuramos antes
        def log_message(self, format, *args):
            pass  # Silencia o output padrão do sys.stderr

    # 3. Criação do servidor multithread
    # Bind em "" (0.0.0.0) permite acesso externo na rede local
    httpd = http.server.ThreadingHTTPServer(("", porta), HandlerCustomizado)

    print(f"[Servidor] Rodando na porta {porta} | Diretório: {caminho_absoluto}")

    # 4. Loop de I/O bloqueante (deve rodar na sua própria thread)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()

if __name__ == "__main__":

    folder = sys.argv[1]
    #print(folder)
    generate_ota_manifest("./"+folder)

    PORTA = 8000

    # Executa o servidor em uma thread Daemon (morre quando o programa principal fechar)
    thread_servidor = threading.Thread(
        target=iniciar_servidor_estatico,
        args=(PORTA, "./"+folder),
        daemon=True,
        name="Thread-HTTPServer"
    )
    thread_servidor.start()

    # O seu script principal fica livre para continuar o processamento
    # Ex: Loop infinito do backend, monitoramento de arquivos, gerador de manifestos...
    import time

    try:
        while True:
            # Lógica principal do sistema rodando em paralelo...
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nEncerrando sistema...")