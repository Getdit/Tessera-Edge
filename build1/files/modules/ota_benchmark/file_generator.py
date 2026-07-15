import os
import sys


def create_dummy_file(filepath: str, size_kb: int):
    """
    Gera um arquivo de texto com o tamanho exato em KB via I/O em blocos.
    """
    chunk_size = 1024  # 1 KB

    # Utilizando um caractere repetido. Em testes de throughput TCP cru,
    # a entropia do dado importa menos que o tamanho do buffer enviado.
    chunk = "A" * chunk_size

    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            for _ in range(size_kb):
                f.write(chunk)

        tamanho_real = os.path.getsize(filepath)
        print(f"[OK] {filepath:<20} | Alvo: {size_kb} KB | Real: {tamanho_real} bytes")

    except IOError as e:
        print(f"[ERRO] Falha ao acessar disco para {filepath}: {e}")


if __name__ == "__main__":
    # Escopo de tamanhos baseados no seu mapa de Flash (256KB até 1.5MB)
    tamanhos_benchmark_kb = [0, 1, 50, 100, 150, 200, 250, 300, 350, 400]

    print("Iniciando alocacao de payloads para OTA...\n")

    for size in tamanhos_benchmark_kb:
        filename = f"dummy_{size}.py"
        create_dummy_file(filename, size)

    print("\nConcluido. Você pode servir esta pasta usando:")
    print("python -m http.server 8000")