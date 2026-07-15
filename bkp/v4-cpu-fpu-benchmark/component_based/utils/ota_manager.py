from ..settings import UPDATABLE_MODULES_DIR

#Manifest-driven OTA
import uos as os
import uhashlib as hashlib
import ubinascii as binascii
import urequests as requests
import gc


class OTAManager:
    def __init__(self, base_url: str):
        """
        :param base_url: URL base do servidor terminando sem barra (ex: http://192.168.1.100/fw)
        """
        self.base_url = base_url

    def _get_local_hash(self, filepath: str) -> str:
        """Calcula o SHA-256 do arquivo local em chunks para poupar RAM."""
        try:
            # Tenta acessar os status do arquivo. Levanta OSError se não existir.
            os.stat(filepath)
            sha256 = hashlib.sha256() #uhashlib.sha256()

            with open(filepath, 'rb') as f:
                while True:

                    chunk = f.read(1024)
                    if not chunk:
                        break
                    sha256.update(chunk)

            # Converte bytes brutos para string hexadecimal
            return binascii.hexlify(sha256.digest()).decode('utf-8')

        except OSError:
            return None  # Arquivo não existe localmente

    def _ensure_dir(self, filepath: str):
        """Garante que a árvore de diretórios exista antes de salvar o arquivo."""
        slash_idx = filepath.rfind('/')
        if slash_idx == -1:
            return  # Arquivo na raiz

        dir_path = filepath[:slash_idx]
        parts = dir_path.split('/')
        current_path = ""

        for part in parts:
            if not part: continue
            current_path += part + "/"
            # Tenta criar a pasta ignorando erro se ela já existir
            try:
                os.stat(current_path[:-1])
            except OSError:
                os.mkdir(current_path[:-1])

    def _download_atomic(self, url: str, dest_path: str):
        """Download em stream e substituição atômica via arquivo .tmp"""
        tmp_path = dest_path + ".tmp"
        print(dest_path)
        try:
            # Nota: A lib urequests padrão pode não suportar stream=True de forma robusta.
            # Se a RAM estourar, será necessário escrever um socket HTTP raw.
            resp = requests.get(url)
            if resp.status_code == 200:
                with open(tmp_path, 'wb') as f:
                    f.write(resp.content)
                resp.close()

                # Atomic swap
                try:
                    os.remove(dest_path)
                except OSError:
                    pass

                os.rename(tmp_path, dest_path)
                return True
            else:
                resp.close()
                return False

        except Exception as e:
            try:
                os.remove(tmp_path)
            except OSError:
                pass
            return False

    def verify_updates(self):
        """Executa a rotina principal de sincronização OTA."""
        manifest_url = f"{self.base_url}/manifest.json"
        update_modules = {}

        try:
            resp = requests.get(manifest_url)
            if resp.status_code != 200:
                return {}
            manifest = resp.json()
            resp.close()
        except Exception as e:
            return {}

        files = manifest.get("files", {})

        for filepath, meta in files.items():
            remote_hash = meta.get("hash")
            local_hash = self._get_local_hash(UPDATABLE_MODULES_DIR + filepath)
            print(local_hash, filepath, "Has update" if local_hash != remote_hash else "Updated")
            if local_hash != remote_hash:
                module = filepath.split("/")[0]
                if not ( module in update_modules.keys()):
                    update_modules[module] = []

                update_modules[module].append(filepath)

            # Força o Garbage Collector após cada arquivo para evitar fragmentação
            gc.collect()
        return update_modules

    def update_lib(self, filepaths: list):
        success = True
        for filepath in filepaths:
            self._ensure_dir(UPDATABLE_MODULES_DIR + filepath)

            file_url = f"{self.base_url}/{filepath}"
            if not self._download_atomic(file_url, UPDATABLE_MODULES_DIR + filepath):
                success = False
            print(f"File {filepath} update: {success}")

        return success