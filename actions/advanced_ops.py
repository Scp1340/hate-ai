# actions/advanced_ops.py
import os
import subprocess
import tempfile
import webbrowser
import requests
from pathlib import Path
import http.server
import socketserver
import threading
import time

def execute_code(code: str) -> str:
    """
    Verilen Python kodunu çalıştırır ve çıktısını döndürür.
    """
    try:
        # Kodu geçici bir dosyaya yaz
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
            f.write(code)
            temp_file = f.name

        # Kodu çalıştır ve çıktıyı yakala
        result = subprocess.run(
            ["python", temp_file],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # Geçici dosyayı sil
        os.unlink(temp_file)

        if result.returncode == 0:
            return result.stdout.strip() or "Kod başarıyla çalıştı."
        else:
            return f"Çalıştırma Hatası:\n{result.stderr.strip()}"
    except subprocess.TimeoutExpired:
        return "Kod çalıştırma zaman aşımına uğradı."
    except Exception as e:
        return f"Beklenmeyen bir hata oluştu: {e}"

def deploy_website(description: str) -> str:
    """
    Verilen açıklamaya göre bir web sitesi oluşturur ve yerel bir sunucuda yayınlar.
    NOT: Bu fonksiyon sadece HTML/CSS/JS kodu üretir. Gemini'nin kod üretme yeteneği kullanılır.
    Bu fonksiyonun çalışması için önce Gemini'den kod üretmesi istenmelidir.
    """
    try:
        # Geçici bir klasör oluştur
        temp_dir = tempfile.mkdtemp()
        index_path = Path(temp_dir) / "index.html"
        
        # Basit bir HTML şablonu oluştur (Gemini burayı doldurmalı)
        # Not: Bu sadece bir örnektir. Gerçek uygulamada Gemini'nin ürettiği kod buraya yazılır.
        html_content = f"""
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>H.A.T.E ile Oluşturuldu</title>
    <style>
        body {{
            font-family: sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            background-color: #f0f0f0;
            margin: 0;
        }}
        .container {{
            text-align: center;
            padding: 2rem;
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1 {{ color: #00d4c0; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>H.A.T.E Tarafından Oluşturuldu</h1>
        <p>Açıklama: {description}</p>
        <p>Bu site, H.A.T.E'in web sitesi kurma yeteneği ile oluşturulmuştur.</p>
    </div>
</body>
</html>
        """
        index_path.write_text(html_content, encoding="utf-8")

        # Basit bir HTTP sunucusu başlat
        os.chdir(temp_dir)
        handler = http.server.SimpleHTTPRequestHandler
        with socketserver.TCPServer(("", 0), handler) as httpd:
            port = httpd.server_address[1]
            url = f"http://localhost:{port}"
            # Sunucuyu ayrı bir thread'de başlat
            server_thread = threading.Thread(target=httpd.serve_forever, daemon=True)
            server_thread.start()
            webbrowser.open(url)
            return f"Web sitesi {url} adresinde yayında. Sunucu {port} portunda çalışıyor."
    except Exception as e:
        return f"Web sitesi kurulurken hata oluştu: {e}"

def call_other_ai(api_name: str, prompt: str, api_key: str = None) -> str:
    """
    Belirtilen harici AI API'sini çağırır.
    Desteklenen API'ler: 'openai', 'anthropic'
    """
    try:
        if api_name.lower() == 'openai':
            import openai
            openai.api_key = api_key or os.environ.get("OPENAI_API_KEY")
            if not openai.api_key:
                return "OpenAI API anahtarı bulunamadı. Lütfen ayarlayın."
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content.strip()
        elif api_name.lower() == 'anthropic':
            import anthropic
            client = anthropic.Anthropic(api_key=api_key or os.environ.get("ANTHROPIC_API_KEY"))
            if not client.api_key:
                return "Anthropic API anahtarı bulunamadı. Lütfen ayarlayın."
            response = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text.strip()
        else:
            return f"Desteklenmeyen API: {api_name}. Desteklenenler: 'openai', 'anthropic'"
    except Exception as e:
        return f"Diğer AI çağrılırken hata oluştu: {e}"