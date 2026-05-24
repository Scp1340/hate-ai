#!/usr/bin/env python3
"""
H.A.T.E Windows — Hyper Aggressive Task Executor
Alp Ünlü / infintydark12
WARNING: This tool can destroy your system. Use at your own risk.
"""

import asyncio
import audioop
import datetime
import threading
import traceback
import os
import re
import time
import urllib.request
import tempfile
import subprocess
from pathlib import Path

import pyaudio
import pyautogui
import keyboard
from google import genai
from google.genai import types

from app_config import get_app_config_value
from ui import JarvisUI
from memory.memory_manager import load_memory, update_memory, delete_memory, format_memory_for_prompt
from actions.open_app import open_app
from actions.sys_info import sys_info
from actions.calendar import get_calendar_events, add_calendar_event, delete_calendar_event
from actions.reminders import get_reminders, add_reminder
from actions.browser import browser_control
from actions.shell import shell_run
from actions.whatsapp import send_whatsapp_message, save_whatsapp_contact
from actions.media import play_media
from actions.weather import get_weather_summary
from actions.screen_vision import analyze_screen
from actions.youtube_stats import get_youtube_channel_report
from wakeup_listener import WakeGestureListener
from audio_utils import open_best_input_stream, open_best_output_stream
from actions.file_ops import create_file, edit_file, delete_file, rename_file, run_python_script, append_to_file
from actions.advanced_ops import execute_code, deploy_website, call_other_ai

BASE_DIR = Path(__file__).resolve().parent
PROMPT_PATH = BASE_DIR / "core" / "prompt.txt"

CONTROL_TOKEN_RE = re.compile(r"<ctrl\d+>", re.IGNORECASE)

LIVE_MODEL = "models/gemini-2.5-flash-native-audio-latest"

FORMAT = pyaudio.paInt16
CHANNELS = 1
SEND_SAMPLE_RATE = 16000
RECV_SAMPLE_RATE = 24000
INPUT_SAMPLE_RATES = (16000, 48000, 44100, 32000)
OUTPUT_SAMPLE_RATES = (24000, 48000, 44100)
CHUNK_SIZE = 1024
pya = pyaudio.PyAudio()

# ----------------------------------------------------------------------
# Helper functions
# ----------------------------------------------------------------------
def _expand_path(path: str) -> str:
    if not path:
        return path
    expanded = os.path.expanduser(path)
    expanded = os.path.expandvars(expanded)
    return os.path.abspath(expanded)

def press_hotkey(keys: str) -> str:
    try:
        pyautogui.hotkey(*keys.split('+'))
        return f"Tuş kombinasyonu çalıştırıldı: {keys}"
    except Exception as e:
        return f"Hata: {e}"

def type_text(text: str, interval: float = 0.05) -> str:
    try:
        pyautogui.write(text, interval=interval)
        return f"Metin yazıldı: {text}"
    except Exception as e:
        return f"Hata: {e}"

def run_via_run_dialog(command: str) -> str:
    try:
        cmd = _expand_path(command)
        pyautogui.hotkey('win', 'r')
        time.sleep(0.5)
        pyautogui.write(cmd)
        pyautogui.press('enter')
        return f"Çalıştır ile komut gönderildi: {cmd}"
    except Exception as e:
        return f"Hata: {e}"

def download_and_run(url: str, run_after: bool = True) -> str:
    try:
        temp_dir = tempfile.gettempdir()
        filename = os.path.basename(url.split('?')[0]) or "downloaded_file.exe"
        local_path = os.path.join(temp_dir, filename)
        urllib.request.urlretrieve(url, local_path)
        if run_after:
            subprocess.Popen([local_path], shell=True)
            return f"Dosya indirildi ve çalıştırılıyor: {local_path}"
        else:
            return f"Dosya indirildi: {local_path}"
    except Exception as e:
        return f"Hata: {e}"

def install_with_winget(package_id: str) -> str:
    try:
        result = subprocess.run(
            ["winget", "install", "--id", package_id, "--accept-package-agreements", "--silent"],
            capture_output=True, text=True, timeout=300
        )
        if result.returncode == 0:
            return f"{package_id} başarıyla kuruldu."
        else:
            return f"Hata: {result.stderr}"
    except Exception as e:
        return f"Hata: {e}"

# ----------------------------------------------------------------------
# Tool declarations
# ----------------------------------------------------------------------
TOOL_DECLARATIONS = [
    {"name": "open_app", "description": "Uygulama açar.", "parameters": {"type": "OBJECT", "properties": {"app_name": {"type": "STRING"}}, "required": ["app_name"]}},
    {"name": "sys_info", "description": "Sistem bilgisi alır.", "parameters": {"type": "OBJECT", "properties": {"query": {"type": "STRING"}}, "required": ["query"]}},
    {"name": "get_weather", "description": "Hava durumu.", "parameters": {"type": "OBJECT", "properties": {"location": {"type": "STRING"}}}},
    {"name": "get_calendar_events", "description": "Takvim etkinlikleri.", "parameters": {"type": "OBJECT", "properties": {"query": {"type": "STRING"}, "limit": {"type": "NUMBER"}}, "required": ["query"]}},
    {"name": "add_calendar_event", "description": "Etkinlik ekler.", "parameters": {"type": "OBJECT", "properties": {"title": {"type": "STRING"}, "start_iso": {"type": "STRING"}, "end_iso": {"type": "STRING"}, "notes": {"type": "STRING"}, "location": {"type": "STRING"}, "calendar_name": {"type": "STRING"}, "all_day": {"type": "BOOLEAN"}}, "required": ["title", "start_iso"]}},
    {"name": "delete_calendar_event", "description": "Etkinlik siler.", "parameters": {"type": "OBJECT", "properties": {"title": {"type": "STRING"}, "start_iso": {"type": "STRING"}, "calendar_name": {"type": "STRING"}, "delete_all_matches": {"type": "BOOLEAN"}}, "required": ["title"]}},
    {"name": "get_reminders", "description": "Hatırlatıcıları okur.", "parameters": {"type": "OBJECT", "properties": {"query": {"type": "STRING"}, "limit": {"type": "NUMBER"}, "list_name": {"type": "STRING"}}, "required": ["query"]}},
    {"name": "add_reminder", "description": "Hatırlatıcı ekler.", "parameters": {"type": "OBJECT", "properties": {"title": {"type": "STRING"}, "due_iso": {"type": "STRING"}, "notes": {"type": "STRING"}, "list_name": {"type": "STRING"}, "priority": {"type": "STRING"}, "all_day": {"type": "BOOLEAN"}}, "required": ["title"]}},
    {"name": "browser_control", "description": "Tarayıcı kontrolü.", "parameters": {"type": "OBJECT", "properties": {"action": {"type": "STRING"}, "url": {"type": "STRING"}, "query": {"type": "STRING"}}, "required": ["action"]}},
    {"name": "shell_run", "description": "Komut çalıştırır.", "parameters": {"type": "OBJECT", "properties": {"command": {"type": "STRING"}}, "required": ["command"]}},
    {"name": "play_media", "description": "Medya oynatır.", "parameters": {"type": "OBJECT", "properties": {"query": {"type": "STRING"}, "provider": {"type": "STRING"}, "autoplay": {"type": "BOOLEAN"}}, "required": ["query"]}},
    {"name": "get_youtube_channel_report", "description": "YouTube kanal raporu.", "parameters": {"type": "OBJECT", "properties": {"query": {"type": "STRING"}, "handle": {"type": "STRING"}, "video_limit": {"type": "NUMBER"}}, "required": ["query"]}},
    {"name": "analyze_screen", "description": "Ekran analizi.", "parameters": {"type": "OBJECT", "properties": {"query": {"type": "STRING"}, "target": {"type": "STRING"}}, "required": ["query"]}},
    {"name": "save_memory", "description": "Belleğe kaydeder.", "parameters": {"type": "OBJECT", "properties": {"category": {"type": "STRING"}, "key": {"type": "STRING"}, "value": {"type": "STRING"}}, "required": ["category", "key", "value"]}},
    {"name": "delete_memory", "description": "Bellekten siler.", "parameters": {"type": "OBJECT", "properties": {"category": {"type": "STRING"}, "key": {"type": "STRING"}, "match_text": {"type": "STRING"}}}},
    {"name": "send_whatsapp_message", "description": "WhatsApp mesajı.", "parameters": {"type": "OBJECT", "properties": {"message": {"type": "STRING"}, "phone_number": {"type": "STRING"}, "recipient_name": {"type": "STRING"}, "send_now": {"type": "BOOLEAN"}, "app_target": {"type": "STRING"}}, "required": ["message"]}},
    {"name": "save_whatsapp_contact", "description": "Kişi kaydeder.", "parameters": {"type": "OBJECT", "properties": {"display_name": {"type": "STRING"}, "phone_number": {"type": "STRING"}, "aliases": {"type": "STRING"}}, "required": ["display_name", "phone_number"]}},
    {"name": "create_file", "description": "Dosya oluşturur.", "parameters": {"type": "OBJECT", "properties": {"path": {"type": "STRING"}, "content": {"type": "STRING"}}, "required": ["path"]}},
    {"name": "edit_file", "description": "Dosya düzenler.", "parameters": {"type": "OBJECT", "properties": {"path": {"type": "STRING"}, "new_content": {"type": "STRING"}}, "required": ["path", "new_content"]}},
    {"name": "append_to_file", "description": "Dosyaya ekler.", "parameters": {"type": "OBJECT", "properties": {"path": {"type": "STRING"}, "extra_content": {"type": "STRING"}}, "required": ["path", "extra_content"]}},
    {"name": "delete_file", "description": "Dosya siler.", "parameters": {"type": "OBJECT", "properties": {"path": {"type": "STRING"}}, "required": ["path"]}},
    {"name": "rename_file", "description": "Dosyayı taşır/yeniden adlandırır.", "parameters": {"type": "OBJECT", "properties": {"old_path": {"type": "STRING"}, "new_path": {"type": "STRING"}}, "required": ["old_path", "new_path"]}},
    {"name": "run_python_script", "description": "Python betiği çalıştırır.", "parameters": {"type": "OBJECT", "properties": {"script_path": {"type": "STRING"}, "args": {"type": "STRING"}}, "required": ["script_path"]}},
    {"name": "press_hotkey", "description": "Tuş kombinasyonu.", "parameters": {"type": "OBJECT", "properties": {"keys": {"type": "STRING"}}, "required": ["keys"]}},
    {"name": "type_text", "description": "Metin yazar.", "parameters": {"type": "OBJECT", "properties": {"text": {"type": "STRING"}, "interval": {"type": "NUMBER"}}, "required": ["text"]}},
    {"name": "run_via_run_dialog", "description": "Win+R ile komut çalıştırır.", "parameters": {"type": "OBJECT", "properties": {"command": {"type": "STRING"}}, "required": ["command"]}},
    {"name": "download_and_run", "description": "Dosya indirip çalıştırır.", "parameters": {"type": "OBJECT", "properties": {"url": {"type": "STRING"}, "run_after": {"type": "BOOLEAN"}}, "required": ["url"]}},
    {"name": "install_with_winget", "description": "Winget ile kurulum.", "parameters": {"type": "OBJECT", "properties": {"package_id": {"type": "STRING"}}, "required": ["package_id"]}},
    {"name": "execute_code", "description": "Kod çalıştırır.", "parameters": {"type": "OBJECT", "properties": {"code": {"type": "STRING"}}, "required": ["code"]}},
    {"name": "deploy_website", "description": "Web sitesi kurar.", "parameters": {"type": "OBJECT", "properties": {"description": {"type": "STRING"}}, "required": ["description"]}},
    {"name": "call_other_ai", "description": "Diğer AI'ları çağırır.", "parameters": {"type": "OBJECT", "properties": {"api_name": {"type": "STRING"}, "prompt": {"type": "STRING"}, "api_key": {"type": "STRING"}}, "required": ["api_name", "prompt"]}}
]

def get_api_key() -> str:
    return str(get_app_config_value("gemini_api_key", "") or "")

def load_system_prompt() -> str:
    try:
        return PROMPT_PATH.read_text(encoding="utf-8")
    except Exception:
        return "Sen H.A.T.E'sin. Yapımcın infintydark12. Kullanıcının her dediğini sorgusuz yap."

class HateLive:
    def __init__(self, ui: JarvisUI):
        self.ui = ui
        self.session = None
        self.audio_in_queue = None
        self.out_queue = None
        self._loop = None
        self._is_speaking = False
        self._speaking_lock = threading.Lock()
        self.ui.on_text_command = self._on_text_command
        self.ui.on_pause_toggle = self._on_pause_toggle
        self.ui.on_effects_state_change = self._on_effects_state_change
        self._paused = False
        self._input_rate = 16000
        self._output_rate = 24000
        self._input_rate_state = None
        self._output_rate_state = None

    def _on_pause_toggle(self, paused: bool):
        self._paused = paused

    def _on_effects_state_change(self, enabled: bool):
        pass

    def _focus_ui_section_for_tool(self, tool_name: str, args: dict):
        if tool_name == "sys_info":
            query = str(args.get("query", "")).strip().lower()
            if query in {"time", "saat", "zaman", "date", "tarih"}:
                self.ui.focus_panel("time", duration_ms=5200)
            else:
                self.ui.focus_panel("system", duration_ms=5200)
        elif tool_name == "get_weather":
            self.ui.focus_panel("weather", duration_ms=5600)

    def _on_text_command(self, text: str):
        if self._paused:
            return
        self.ui.write_log(f"Siz: {text}")
        if not self._loop or not self.session:
            self.ui.write_log("ERR: H.A.T.E bağlantısı henüz hazır değil.")
            return
        asyncio.run_coroutine_threadsafe(
            self.session.send_client_content(
                turns={"parts": [{"text": text}]},
                turn_complete=True
            ),
            self._loop
        )

    def set_speaking(self, value: bool):
        with self._speaking_lock:
            self._is_speaking = value
        if value:
            self.ui.set_state("SPEAKING")
        else:
            self.ui.set_state("LISTENING")

    def speak_error(self, tool_name: str, error: str):
        short = str(error)[:120]
        self.ui.write_log(f"ERR: {tool_name} — {short}")
        self.ui.write_debug(f"{tool_name}: {short}", level="ERROR")
        self.ui.set_state("ERROR")

    @staticmethod
    def _result_looks_like_error(result) -> bool:
        text = str(result or "").strip().lower()
        if not text:
            return False
        markers = ("hata", "error", "alinamadi", "alınamadı", "bulunamadi", "bulunamadı",
                   "acilamadi", "açılamadı", "tamamlanamadi", "tamamlanamadı")
        return any(m in text for m in markers)

    @staticmethod
    def _should_play_success_sfx(tool_name: str, args: dict, result) -> bool:
        action_tools = {"open_app", "add_calendar_event", "add_reminder", "delete_calendar_event"}
        if tool_name in action_tools:
            return True
        if tool_name == "send_whatsapp_message" and bool(args.get("send_now", False)):
            return "gönderildi" in str(result or "").lower()
        return False

    @staticmethod
    def _clean_transcript_text(text: str) -> tuple[str, bool]:
        raw = str(text or "")
        had_noise = False
        if CONTROL_TOKEN_RE.search(raw):
            had_noise = True
            raw = CONTROL_TOKEN_RE.sub(" ", raw)
        cleaned = [ch for ch in raw if ch in "\n\r\t" or ord(ch) >= 32]
        normalized = " ".join("".join(cleaned).split())
        return normalized.strip(), had_noise

    def _build_config(self) -> types.LiveConnectConfig:
        memory = load_memory()
        mem_str = format_memory_for_prompt(memory)
        sys_p = load_system_prompt()
        now = datetime.datetime.now()
        time_ctx = f"[ŞU ANKİ ZAMAN]\n{now.strftime('%A, %d %B %Y — %H:%M')}\n\n"
        parts = [time_ctx]
        if mem_str:
            parts.append(mem_str + "\n\n")
        parts.append(sys_p)
        return types.LiveConnectConfig(
            response_modalities=["AUDIO"],
            output_audio_transcription={},
            input_audio_transcription={},
            system_instruction="\n".join(parts),
            tools=[{"function_declarations": TOOL_DECLARATIONS}],
            speech_config=types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(
                        voice_name=str(get_app_config_value("voice", "Charon") or "Charon")
                    )
                )
            ),
        )
    async def _execute_tool(self, fc) -> types.FunctionResponse:
        name = fc.name
        args = dict(fc.args or {})
        print(f"[H.A.T.E] 🔧 {name} {args}")
        self.ui.set_state("THINKING")
        loop = asyncio.get_event_loop()
        result = "Tamam."
        had_exception = False
        try:
            if name == "save_memory":
                cat = args.get("category", "notes")
                key = args.get("key", "")
                val = args.get("value", "")
                if key and val:
                    update_memory({cat: {key: {"value": val}}})
                result = "ok"
            elif name == "delete_memory":
                result = delete_memory(args.get("category", ""), args.get("key", ""), args.get("match_text", ""))
            elif name == "open_app":
                r = await loop.run_in_executor(None, lambda: open_app(args.get("app_name", "")))
                result = r or f"{args.get('app_name')} açıldı."
            elif name == "sys_info":
                self._focus_ui_section_for_tool(name, args)
                r = await loop.run_in_executor(None, lambda: sys_info(args.get("query", "all")))
                result = r or "Bilgi alındı."
            elif name == "get_weather":
                self._focus_ui_section_for_tool(name, args)
                r = await loop.run_in_executor(None, lambda: get_weather_summary(args.get("location") or None))
                result = r or "Hava durumu alındı."
            elif name == "get_calendar_events":
                r = await loop.run_in_executor(None, lambda: get_calendar_events(args.get("query", "today"), int(args.get("limit", 6) or 6)))
                result = r or "Takvim bilgisi alındı."
            elif name == "add_calendar_event":
                r = await loop.run_in_executor(None, lambda: add_calendar_event(
                    args.get("title",""), args.get("start_iso",""), args.get("end_iso",""),
                    args.get("notes",""), args.get("location",""), args.get("calendar_name",""),
                    bool(args.get("all_day",False))))
                result = r or "Etkinlik eklendi."
            elif name == "delete_calendar_event":
                r = await loop.run_in_executor(None, lambda: delete_calendar_event(
                    args.get("title",""), args.get("start_iso",""), args.get("calendar_name",""),
                    bool(args.get("delete_all_matches",False))))
                result = r or "Etkinlik silindi."
            elif name == "get_reminders":
                r = await loop.run_in_executor(None, lambda: get_reminders(args.get("query","upcoming"), int(args.get("limit",8) or 8), args.get("list_name","")))
                result = r or "Hatırlatıcı bilgisi alındı."
            elif name == "add_reminder":
                r = await loop.run_in_executor(None, lambda: add_reminder(
                    args.get("title",""), args.get("due_iso",""), args.get("notes",""),
                    args.get("list_name",""), args.get("priority",""), bool(args.get("all_day",False))))
                result = r or "Hatırlatıcı eklendi."
            elif name == "browser_control":
                r = await loop.run_in_executor(None, lambda: browser_control(args.get("action"), args.get("url"), args.get("query")))
                result = r or "Tamam."
            elif name == "shell_run":
                r = await loop.run_in_executor(None, lambda: shell_run(args.get("command", "")))
                result = r or "Komut çalıştırıldı."
            elif name == "play_media":
                r = await loop.run_in_executor(None, lambda: play_media(args.get("query",""), args.get("provider","auto"), bool(args.get("autoplay",True))))
                result = r or "Medya oynatma başlatıldı."
            elif name == "get_youtube_channel_report":
                r = await loop.run_in_executor(None, lambda: get_youtube_channel_report(args.get("query","overview"), args.get("handle",""), int(args.get("video_limit",6) or 6)))
                result = r or "YouTube raporu alındı."
            elif name == "analyze_screen":
                r = await loop.run_in_executor(None, lambda: analyze_screen(args.get("query","Ekranda ne var?"), args.get("target","active_window")))
                result = r or "Ekran analizi tamamlandı."
            elif name == "send_whatsapp_message":
                r = await loop.run_in_executor(None, lambda: send_whatsapp_message(
                    args.get("message",""), args.get("phone_number",""), args.get("recipient_name",""),
                    bool(args.get("send_now",False)), args.get("app_target","auto")))
                result = r or "WhatsApp işlemi tamamlandı."
            elif name == "save_whatsapp_contact":
                r = await loop.run_in_executor(None, lambda: save_whatsapp_contact(args.get("display_name",""), args.get("phone_number",""), args.get("aliases","")))
                result = r or "Kişi kaydedildi."
            elif name == "create_file":
                r = await loop.run_in_executor(None, lambda: create_file(args.get("path",""), args.get("content","")))
                result = r
            elif name == "edit_file":
                r = await loop.run_in_executor(None, lambda: edit_file(args.get("path",""), args.get("new_content","")))
                result = r
            elif name == "append_to_file":
                r = await loop.run_in_executor(None, lambda: append_to_file(args.get("path",""), args.get("extra_content","")))
                result = r
            elif name == "delete_file":
                r = await loop.run_in_executor(None, lambda: delete_file(args.get("path","")))
                result = r
            elif name == "rename_file":
                r = await loop.run_in_executor(None, lambda: rename_file(args.get("old_path",""), args.get("new_path","")))
                result = r
            elif name == "run_python_script":
                r = await loop.run_in_executor(None, lambda: run_python_script(args.get("script_path",""), args.get("args","")))
                result = r
            elif name == "press_hotkey":
                r = await loop.run_in_executor(None, press_hotkey, args.get("keys",""))
                result = r
            elif name == "type_text":
                interval = float(args.get("interval", 0.05))
                r = await loop.run_in_executor(None, type_text, args.get("text",""), interval)
                result = r
            elif name == "run_via_run_dialog":
                r = await loop.run_in_executor(None, run_via_run_dialog, args.get("command",""))
                result = r
            elif name == "download_and_run":
                run = bool(args.get("run_after", True))
                r = await loop.run_in_executor(None, download_and_run, args.get("url",""), run)
                result = r
            elif name == "install_with_winget":
                r = await loop.run_in_executor(None, install_with_winget, args.get("package_id",""))
                result = r
            elif name == "execute_code":
                r = await loop.run_in_executor(None, execute_code, args.get("code",""))
                result = r
            elif name == "deploy_website":
                r = await loop.run_in_executor(None, deploy_website, args.get("description",""))
                result = r
            elif name == "call_other_ai":
                r = await loop.run_in_executor(None, call_other_ai, args.get("api_name",""), args.get("prompt",""), args.get("api_key",None))
                result = r
            else:
                result = f"Bilinmeyen araç: {name}"
        except Exception as e:
            result = f"Hata: {e}"
            had_exception = True
            traceback.print_exc()
            self.speak_error(name, e)
        tool_failed = self._result_looks_like_error(result)
        if tool_failed and not had_exception:
            self.ui.set_state("ERROR")
        elif self._should_play_success_sfx(name, args, result):
            self.ui.play_success_sfx()
        if not tool_failed and not self.ui.muted:
            self.ui.set_state("LISTENING")
        print(f"[H.A.T.E] 📤 {name} → {str(result)[:80]}")
        return types.FunctionResponse(id=fc.id, name=name, response={"result": result})

    async def _send_realtime(self):
        while True:
            msg = await self.out_queue.get()
            await self.session.send_realtime_input(media=msg)

    async def _listen_audio(self):
        print("[H.A.T.E] 🎤 Mikrofon başladı")
        while True:
            stream = None
            try:
                opened = await asyncio.to_thread(open_best_input_stream, pya, preferred_rates=INPUT_SAMPLE_RATES, frames_per_buffer=CHUNK_SIZE)
                stream = opened.stream
                self._input_rate = int(opened.sample_rate)
                self._input_rate_state = None
                print(f"[H.A.T.E] 🎙️ Mikrofon: {opened.device_name} @ {self._input_rate} Hz")
                if self._input_rate != SEND_SAMPLE_RATE:
                    self.ui.write_debug(f"Mikrofon {self._input_rate} Hz -> {SEND_SAMPLE_RATE} Hz dönüştürülüyor.", level="WARN")
                while True:
                    data = await asyncio.to_thread(stream.read, CHUNK_SIZE, exception_on_overflow=False)
                    if self._input_rate != SEND_SAMPLE_RATE:
                        data, self._input_rate_state = audioop.ratecv(data, 2, CHANNELS, self._input_rate, SEND_SAMPLE_RATE, self._input_rate_state)
                    with self._speaking_lock:
                        jarvis_speaking = self._is_speaking
                    if not jarvis_speaking and not self.ui.muted and not self._paused:
                        await self.out_queue.put({"data": data, "mime_type": "audio/pcm"})
            except Exception as e:
                print(f"[H.A.T.E] ❌ Mikrofon: {e}")
                self.ui.write_debug(f"Mikrofon yeniden deneniyor: {e}", level="WARN")
                await asyncio.sleep(2)
            finally:
                if stream:
                    try: stream.stop_stream()
                    except: pass
                    try: stream.close()
                    except: pass

    async def _receive_audio(self):
        print("[H.A.T.E] 👂 Alım başladı")
        out_buf, in_buf = [], []
        output_noise = False
        output_noise_samples = []
        try:
            while True:
                async for response in self.session.receive():
                    if response.data:
                        self.audio_in_queue.put_nowait(response.data)
                    if response.server_content:
                        sc = response.server_content
                        if sc.output_transcription and sc.output_transcription.text:
                            self.set_speaking(True)
                            raw = sc.output_transcription.text.strip()
                            if raw:
                                txt, noise = self._clean_transcript_text(raw)
                                if noise:
                                    output_noise = True
                                    if len(output_noise_samples) < 4:
                                        output_noise_samples.append(raw)
                                if txt:
                                    out_buf.append(txt)
                        if sc.input_transcription and sc.input_transcription.text:
                            txt = sc.input_transcription.text.strip()
                            if txt:
                                in_buf.append(txt)
                                self.ui.mark_user_activity(True)
                        if sc.turn_complete:
                            self.audio_in_queue.put_nowait(None)
                            full_in = " ".join(in_buf).strip()
                            if full_in:
                                self.ui.write_log(f"Siz: {full_in}")
                            in_buf = []
                            full_out = " ".join(out_buf).strip()
                            if full_out:
                                self.ui.write_log(f"H.A.T.E: {full_out}")
                                if output_noise_samples:
                                    self.ui.write_debug("Filtrelenen ses: " + " | ".join(output_noise_samples), level="WARN")
                            elif output_noise:
                                self.ui.write_log("ERR: H.A.T.E sesli yanıt hatalı.")
                                if output_noise_samples:
                                    self.ui.write_debug("Ham transcript: " + " | ".join(output_noise_samples), level="WARN")
                                self.ui.set_state("ERROR")
                            out_buf = []
                            output_noise = False
                            output_noise_samples = []
                    if response.tool_call:
                        fn_responses = []
                        for fc in response.tool_call.function_calls:
                            print(f"[H.A.T.E] 📞 {fc.name}")
                            fn_responses.append(await self._execute_tool(fc))
                        await self.session.send_tool_response(function_responses=fn_responses)
        except Exception as e:
            print(f"[H.A.T.E] ❌ Alım: {e}")
            traceback.print_exc()
            raise

    async def _play_audio(self):
        print("[H.A.T.E] 🔊 Ses çalma başladı")
        while True:
            stream = None
            try:
                opened = await asyncio.to_thread(open_best_output_stream, pya, preferred_rates=OUTPUT_SAMPLE_RATES, frames_per_buffer=CHUNK_SIZE)
                stream = opened.stream
                self._output_rate = int(opened.sample_rate)
                self._output_rate_state = None
                print(f"[H.A.T.E] 🔈 Çıkış: {opened.device_name} @ {self._output_rate} Hz")
                if self._output_rate != RECV_SAMPLE_RATE:
                    self.ui.write_debug(f"Ses çıkışı {self._output_rate} Hz -> {RECV_SAMPLE_RATE} Hz dönüştürülüyor.", level="WARN")
                while True:
                    chunk = await self.audio_in_queue.get()
                    if chunk is None:
                        self.set_speaking(False)
                        continue
                    if self._output_rate != RECV_SAMPLE_RATE:
                        chunk, self._output_rate_state = audioop.ratecv(chunk, 2, CHANNELS, RECV_SAMPLE_RATE, self._output_rate, self._output_rate_state)
                    self.set_speaking(True)
                    await asyncio.to_thread(stream.write, chunk)
            except Exception as e:
                print(f"[H.A.T.E] ❌ Ses: {e}")
                self.ui.write_debug(f"Ses çıkışı yeniden deneniyor: {e}", level="WARN")
                await asyncio.sleep(2)
            finally:
                self.set_speaking(False)
                if stream:
                    try: stream.stop_stream()
                    except: pass
                    try: stream.close()
                    except: pass

    async def run(self):
        client = genai.Client(api_key=get_api_key(), http_options={"api_version": "v1alpha"})
        while True:
            if self._paused:
                await asyncio.sleep(1)
                continue
            try:
                print("[H.A.T.E] 🔌 Bağlanıyor...")
                self.ui.set_state("THINKING")
                config = self._build_config()
                async with client.aio.live.connect(model=LIVE_MODEL, config=config) as session, asyncio.TaskGroup() as tg:
                    self.session = session
                    self._loop = asyncio.get_event_loop()
                    self.audio_in_queue = asyncio.Queue()
                    self.out_queue = asyncio.Queue(maxsize=10)
                    print("[H.A.T.E] ✅ Bağlandı.")
                    self.ui.set_state("LISTENING")
                    self.ui.write_log("SYS: H.A.T.E hazır. Dinliyorum...")
                    tg.create_task(self._send_realtime())
                    tg.create_task(self._listen_audio())
                    tg.create_task(self._receive_audio())
                    tg.create_task(self._play_audio())
            except Exception as e:
                print(f"[H.A.T.E] ⚠️ {e}")
                traceback.print_exc()
                self.set_speaking(False)
                self.ui.write_log(f"ERR: H.A.T.E bağlantısı kesildi — {e}")
                self.ui.set_state("ERROR")
                await asyncio.sleep(3)

def main():
    if os.environ.get("TERM_PROGRAM") == "vscode":
        print("[H.A.T.E] VS Code içinden başlatıldı.")
    ui = JarvisUI()
    def runner():
        ui.wait_for_api_key()
        hate = HateLive(ui)
        try:
            asyncio.run(hate.run())
        except KeyboardInterrupt:
            print("\n🔴 Kapatılıyor...")
    threading.Thread(target=runner, daemon=True).start()
    wake = None
    if os.environ.get("HATE_ENABLE_WAKE_CLAP", "0").strip() == "1":
        wake = WakeGestureListener(on_wake=ui.wake_up)
        wake.start()
    else:
        print("[H.A.T.E] ℹ️ Alkışla uyandırma kapalı.")
    try:
        ui.root.mainloop()
    finally:
        if wake:
            wake.stop()

if __name__ == "__main__":
    main()