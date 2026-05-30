H.A.T.E – Hyper Aggressive Task Executor

Windows için Google Gemini destekli, tamamen sesle kontrol edilen bir masaüstü asistanı. Gereksiz selamlaşma yok, sadece komutlarını çalıştırır.

Sistem gereksinimleri:
- Windows 10 veya 11 (64-bit)
- Python 3.12.x (64-bit) – https://python.org/downloads/ adresinden indir
- İnternet bağlantısı
- Google Gemini API anahtarı – https://aistudio.google.com/app/apikey adresinden ücretsiz al

TEK KOMUT İLE OTOMATİK KURULUM (önerilen):
Yönetici PowerShell'i aç ve aşağıdaki kodu yapıştır:
git clone https://github.com/Scp1340/hate-ai.git ; cd hate-ai ; py -3.12 -m venv venv ; venv\Scripts\activate ; py -3.12 -m pip install --upgrade pip ; py -3.12 -m pip install -r requirements.txt
Sonra config/api_keys.example.json dosyasını config/api_keys.json olarak kopyala, içine kendi Gemini API anahtarını yapıştır.

MANUEL KURULUM (adım adım):
1. Depoyu indir:
   git clone https://github.com/Scp1340/hate-ai.git
   cd hate-ai
2. Sanal ortam oluştur:
   py -3.12 -m venv venv
3. Sanal ortamı aktifleştir:
   venv\Scripts\activate
4. Pip'i güncelle ve bağımlılıkları yükle:
   py -3.12 -m pip install --upgrade pip
   py -3.12 -m pip install -r requirements.txt
5. API anahtarını ayarla:
   - config/api_keys.example.json dosyasını kopyala, yeni dosyaya api_keys.json adını ver.
   - Notepad ile aç, "gemini_api_key" alanına kendi anahtarını yaz. Örnek:
     {
       "gemini_api_key": "AIzaSy...",
       "voice": "Charon",
       "recognition_language": "tr-TR"
     }
   - Kaydet.
6. Asistanı başlat (sanal ortam aktifken):
   py main.py

KULLANIM:
- Uyandırma: Yüksek sesle konuş veya iki kez el çırp.
- Örnek komutlar:
  "Saat kaç?"
  "Hava durumu nasıl?"
  "Not Defteri'ni aç"
  "Dosya oluştur"
  "WhatsApp'tan Ali'ye merhaba de"
- Çıkış: "kapat" de veya terminali kapat.

SIK KARŞILAŞILAN SORUNLAR:
- 'py' tanınmıyor: Python 3.12'yi PATH'e ekleyerek yeniden kur (kurulumda en alttaki kutucuğu işaretle)
- Microsoft Visual C++ 14.0 hatası: https://visualstudio.microsoft.com/visual-cpp-build-tools/ adresinden "C++ ile masaüstü geliştirme" iş yükünü yükle
- Mikrofon çalışmıyor: Ayarlar > Gizlilik > Mikrofon > "Masaüstü uygulamalarının erişmesine izin ver" AÇ
- API key invalid: Anahtarını kontrol et. Eğer geçmişse Google AI Studio'dan yenisi oluştur.
- ModuleNotFoundError: Sanal ortamı aktif et (venv\Scripts\activate), tekrar py -3.12 -m pip install -r requirements.txt

UYARI – HERKESE AÇIK DEPO:
Bu depo public'tir. config/api_keys.json dosyasını asla gerçek anahtarınla pushlama. Eğer yanlışlıkla pushladıysan, anahtarını hemen iptal et ve yenisi oluştur.

İletişim: esatayar7@gmail.co
