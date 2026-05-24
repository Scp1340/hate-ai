# actions/file_ops.py
import os
import shutil
import subprocess
from pathlib import Path

def _expand_path(path: str) -> str:
    """Yol değişkenlerini ve kullanıcı dizinini genişletir."""
    if not path:
        return path
    expanded = os.path.expanduser(path)
    expanded = os.path.expandvars(expanded)
    return os.path.abspath(expanded)

def create_file(path: str, content: str = "") -> str:
    try:
        p = Path(_expand_path(path))
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        return f"Dosya oluşturuldu: {p}"
    except Exception as e:
        return f"Hata: {e}"

def edit_file(path: str, new_content: str) -> str:
    try:
        p = Path(_expand_path(path))
        p.write_text(new_content, encoding="utf-8")
        return f"Dosya güncellendi: {p}"
    except Exception as e:
        return f"Hata: {e}"

def append_to_file(path: str, extra_content: str) -> str:
    try:
        p = Path(_expand_path(path))
        with open(p, "a", encoding="utf-8") as f:
            f.write(extra_content)
        return f"Dosyaya eklendi: {p}"
    except Exception as e:
        return f"Hata: {e}"

def delete_file(path: str) -> str:
    try:
        full_path = _expand_path(path)
        if not os.path.exists(full_path):
            return f"Dosya bulunamadı: {full_path}"
        os.remove(full_path)
        return f"Dosya silindi: {full_path}"
    except Exception as e:
        return f"Hata: {e}"

def rename_file(old_path: str, new_path: str) -> str:
    try:
        old = _expand_path(old_path)
        new = _expand_path(new_path)
        shutil.move(old, new)
        return f"Dosya taşındı/yeniden adlandırıldı: {old} -> {new}"
    except Exception as e:
        return f"Hata: {e}"

def run_python_script(script_path: str, args: str = "") -> str:
    try:
        full_script = _expand_path(script_path)
        result = subprocess.run(
            ["python", full_script] + (args.split() if args else []),
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            return result.stdout.strip() or "Betik başarıyla çalıştı."
        else:
            return f"Hata: {result.stderr.strip()}"
    except Exception as e:
        return f"Hata: {e}"