# actions/advanced_ops.py
import os
import subprocess
import tempfile
import webbrowser
import http.server
import socketserver
import threading

def execute_code(code: str) -> str:
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
            f.write(code)
            temp_file = f.name
        result = subprocess.run(["python", temp_file], capture_output=True, text=True, timeout=30)
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