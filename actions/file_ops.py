# actions/file_ops.py
import os
import shutil
import subprocess
from pathlib import Path

def create_file(path: str, content: str = "") -> str:
    try:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        return f"Dosya oluşturuldu: {path}"
    except Exception as e:
        return f"Hata: {e}"

def edit_file(path: str, new_content: str) -> str:
    try:
        Path(path).write_text(new_content, encoding="utf-8")
        return f"Dosya güncellendi: {path}"
    except Exception as e:
        return f"Hata: {e}"

def append_to_file(path: str, extra_content: str) -> str:
    try:
        with open(path, "a", encoding="utf-8") as f:
            f.write(extra_content)
        return f"Dosyaya eklendi: {path}"
    except Exception as e:
        return f"Hata: {e}"

def delete_file(path: str) -> str:
    try:
        os.remove(path)
        return f"Dosya silindi: {path}"
    except Exception as e:
        return f"Hata: {e}"

def rename_file(old_path: str, new_path: str) -> str:
    try:
        shutil.move(old_path, new_path)
        return f"Dosya taşındı/yeniden adlandırıldı: {old_path} -> {new_path}"
    except Exception as e:
        return f"Hata: {e}"

def run_python_script(script_path: str, args: str = "") -> str:
    try:
        result = subprocess.run(
            ["python", script_path] + (args.split() if args else []),
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            return result.stdout.strip() or "Betik başarıyla çalıştı."
        else:
            return f"Hata: {result.stderr.strip()}"
    except Exception as e:
        return f"Hata: {e}"