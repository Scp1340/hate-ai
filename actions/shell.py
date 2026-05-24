# actions/shell.py
import subprocess
import os

def _expand_path(path: str) -> str:
    if not path:
        return path
    expanded = os.path.expanduser(path)
    expanded = os.path.expandvars(expanded)
    return os.path.abspath(expanded)

def shell_run(command: str) -> str:
    try:
        expanded_cmd = _expand_path(command)
        result = subprocess.run(
            expanded_cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            return result.stdout.strip() or "Komut başarıyla çalıştı."
        else:
            return f"Hata: {result.stderr.strip()}"
    except subprocess.TimeoutExpired:
        return "Komut zaman aşımına uğradı."
    except Exception as e:
        return f"Hata: {e}"