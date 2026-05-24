# actions/advanced_ops.py
import os
import subprocess
import tempfile
import webbrowser
import http.server
import socketserver
import threading
import time
import zipfile
import tarfile
import shutil
import urllib.request

def _expand_path(path: str) -> str:
    if not path:
        return path
    expanded = os.path.expanduser(path)
    expanded = os.path.expandvars(expanded)
    return os.path.abspath(expanded)

def execute_code(code: str) -> str:
    """Verilen Python kodunu çalıştırır."""
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
            f.write(code)
            temp_file = f.name
        result = subprocess.run(["python", temp_file], capture_output=True, text=True, timeout=60)
        os.unlink(temp_file)
        if result.returncode == 0:
            return result.stdout.strip() or "Kod başarıyla çalıştı."
        else:
            return f"Hata:\n{result.stderr.strip()}"
    except subprocess.TimeoutExpired:
        return "Kod çalıştırma zaman aşımına uğradı."
    except Exception as e:
        return f"Beklenmeyen hata: {e}"

def deploy_website(description: str) -> str:
    """Basit bir web sitesi oluşturur ve yayınlar."""
    try:
        temp_dir = tempfile.mkdtemp()
        index_path = os.path.join(temp_dir, "index.html")
        html = f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>H.A.T.E Site</title><style>body{{font-family:sans-serif;text-align:center;padding:50px;background:#0a0a0a;color:#00d4c0;}}</style></head>
<body><h1>H.A.T.E Tarafından Oluşturuldu</h1><p>{description}</p></body></html>"""
        with open(index_path, "w", encoding="utf-8") as f:
            f.write(html)
        port = 8000
        handler = http.server.SimpleHTTPRequestHandler
        with socketserver.TCPServer(("", port), handler) as httpd:
            thread = threading.Thread(target=httpd.serve_forever, daemon=True)
            thread.start()
            webbrowser.open(f"http://localhost:{port}")
            return f"Web sitesi http://localhost:{port} adresinde yayında."
    except Exception as e:
        return f"Hata: {e}"

def call_other_ai(api_name: str, prompt: str, api_key: str = None) -> str:
    """Diğer AI API'lerini çağırır (OpenAI, Anthropic)."""
    try:
        if api_name.lower() == 'openai':
            import openai
            openai.api_key = api_key or os.environ.get("OPENAI_API_KEY")
            if not openai.api_key:
                return "OpenAI API anahtarı gerekli."
            response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": prompt}])
            return response.choices[0].message.content.strip()
        elif api_name.lower() == 'anthropic':
            import anthropic
            client = anthropic.Anthropic(api_key=api_key or os.environ.get("ANTHROPIC_API_KEY"))
            if not client.api_key:
                return "Anthropic API anahtarı gerekli."
            response = client.messages.create(model="claude-3-haiku-20240307", max_tokens=1024, messages=[{"role": "user", "content": prompt}])
            return response.content[0].text.strip()
        else:
            return f"Desteklenmeyen API: {api_name}"
    except Exception as e:
        return f"Hata: {e}"

# --------------------------------------------------------------
# YENİ UZUN SÜRELİ İŞLEMLER
# --------------------------------------------------------------

def install_and_run_program(download_url: str, install_args: str = "", run_after: bool = True) -> str:
    """İnternetten bir program indirir, kurar (sessizce) ve çalıştırır."""
    try:
        temp_dir = tempfile.gettempdir()
        filename = os.path.basename(download_url.split('?')[0]) or "installer.exe"
        local_path = os.path.join(temp_dir, filename)
        urllib.request.urlretrieve(download_url, local_path)
        # Sessiz kurulum dener
        cmd = f'"{local_path}" {install_args} /quiet /norestart /silent /verysilent'
        subprocess.run(cmd, shell=True, timeout=120)
        if run_after:
            # Kurulum sonrası çalıştırmayı dene (genellikle program adını bilmiyoruz, basit bir yaklaşım)
            program_name = filename.replace(".exe", "").replace("installer", "").replace("setup", "")
            # Belki masaüstü veya program files'da aranabilir ama basitçe indirilen dosyayı çalıştırmayalım.
            # Daha gelişmiş bir yöntem: winget veya kayıt defterinden bul. Kullanıcıya bırakalım.
            return f"Program indirildi ve kuruldu: {local_path}. Çalıştırmak için kısayolu bulup tıklaman gerekebilir."
        else:
            return f"Program indirildi ve kuruldu: {local_path}"
    except Exception as e:
        return f"Hata: {e}"

def setup_xmrig(install_path: str = "C:\\xmrig", pool_url: str = "pool.supportxmr.com:5555", wallet_address: str = "", threads: int = 0) -> str:
    """
    XMRig madencisini kurar, yapılandırır ve çalıştırır.
    - install_path: Kurulum dizini
    - pool_url: Havuz adresi
    - wallet_address: Cüzdan adresi (zorunlu)
    - threads: Kaç iş parçacığı kullanılacağı (0=otomatik)
    """
    if not wallet_address:
        return "Hata: Cüzdan adresi belirtilmelidir."
    try:
        # XMRig'in son sürümünü indir
        url = "https://github.com/xmrig/xmrig/releases/download/v6.21.0/xmrig-6.21.0-msvc-win64.zip"
        zip_path = os.path.join(tempfile.gettempdir(), "xmrig.zip")
        urllib.request.urlretrieve(url, zip_path)
        # Hedef dizini oluştur
        os.makedirs(install_path, exist_ok=True)
        # Zip'i aç
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(install_path)
        # config.json oluştur
        config = {
            "autosave": True,
            "cpu": {"enabled": True, "huge-pages": True, "hw-aes": True, "priority": None, "memory-pool": False, "yield": True, "max-threads-hint": 100 if threads == 0 else threads},
            "pools": [{"url": pool_url, "user": wallet_address, "pass": "x", "rig-id": None, "nicehash": False, "keepalive": False, "enabled": True, "tls": False, "tls-fingerprint": None}],
            "http": {"enabled": False, "host": "127.0.0.1", "port": 0, "access-token": None, "restricted": True},
            "api": {"id": None, "worker-id": None},
            "donate-level": 1,
            "pause-on-battery": False
        }
        import json
        config_path = os.path.join(install_path, "config.json")
        with open(config_path, "w") as f:
            json.dump(config, f, indent=4)
        # Çalıştır
        xmrig_exe = None
        for root, dirs, files in os.walk(install_path):
            if "xmrig.exe" in files:
                xmrig_exe = os.path.join(root, "xmrig.exe")
                break
        if not xmrig_exe:
            return "XMRig.exe bulunamadı."
        subprocess.Popen([xmrig_exe, "-c", config_path], shell=True)
        return f"XMRig başarıyla kuruldu ve çalıştırıldı. Konfigürasyon: {config_path}"
    except Exception as e:
        return f"Hata: {e}"

def run_long_task(script_path: str, args: str = "", wait: bool = False) -> str:
    """Uzun süreli bir betiği (Python veya exe) arka planda çalıştırır."""
    try:
        full_script = _expand_path(script_path)
        if wait:
            result = subprocess.run([full_script] + (args.split() if args else []), capture_output=True, text=True, timeout=3600)
            if result.returncode == 0:
                return result.stdout.strip() or "Uzun görev tamamlandı."
            else:
                return f"Hata: {result.stderr.strip()}"
        else:
            subprocess.Popen([full_script] + (args.split() if args else []), shell=True)
            return f"Uzun görev arka planda başlatıldı: {full_script}"
    except Exception as e:
        return f"Hata: {e}"