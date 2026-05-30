H.A.T.E – Hyper Aggressive Task Executor

Windows için Google Gemini destekli, tamamen sesle kontrol edilen bir masaüstü asistanı. Gereksiz selamlaşma yok, sadece komutlarını çalıştırır.

Sistem gereksinimleri:
- Windows 10 veya 11 (64-bit)
- Python 3.12.x (64-bit) – https://python.org/downloads/ adresinden indir
- İnternet bağlantısı
- Google Gemini API anahtarı – https://aistudio.google.com/app/apikey adresinden ücretsiz al

TEK KOMUT İLE OTOMATİK KURULUM:
Yönetici PowerShell'i aç ve aşağıdaki kodu yapıştır:
git clone https://github.com/Scp1340/hate-ai.git ; cd hate-ai ; py -3.12 -m venv venv ; venv\Scripts\activate ; py -3.12 -m pip install --upgrade pip ; py -3.12 -m pip install -r requirements.txt

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

API ANAHTARI AYARI:
Hate'i ilk kez çalıştırdığınızda program sizden Gemini API anahtarınızı isteyecektir. Daha önce https://aistudio.google.com/app/apikey adresinden aldığınız anahtarı kopyalayın, programın istediği yere yapıştırın ve Enter'a basın. Anahtarınız config/api_keys.json dosyasına kaydedilecektir. Tekrar sormaz.

ÇALIŞTIRMA (sanal ortam aktifken):
py main.py

ASİSTANIN YAPABİLECEKLERİ (tüm yetenekler):
- Dosya ve klasör işlemleri: oluşturma, silme, düzenleme, yeniden adlandırma, kopyalama, taşıma, içerik arama
- Uygulama yönetimi: uygulama açma/kapama (Notepad, Chrome, Spotify gibi popüler uygulamaları tanır)
- Sistem bilgisi: RAM kullanımı, CPU yükü, batarya seviyesi, işletim sistemi sürümü
- Shell komutları: PowerShell veya CMD komutlarını çalıştırma
- İnternet işlemleri: Google'da arama yapma, belirtilen linki açma, YouTube'da video arama ve oynatma
- Hava durumu: konuma göre güncel hava durumu ve tahmin
- Takvim ve hatırlatıcılar: etkinlik ekleme/listeleme/silme, hatırlatıcı kurma
- WhatsApp mesaj gönderme: rehberdeki kişilere veya numaraya direkt mesaj atma (önce rehbere eklemek gerekir)
- Medya kontrolü: ses seviyesini ayarlama, müzik/video oynatıcıyı kontrol etme, şarkı sözü bulma
- Ekran işlemleri: ekran görüntüsü alma, ekrandaki yazıyı okuma (OCR), fare ve klavye kontrolü
- Not tutma: hızlı not al, notları oku, notları listele
- Sağlık ve adımsayar: (Windows Health uygulaması varsa) adım sayısı, kalori, uyku süresi sorgulama
- YouTube istatistikleri: kanalın abone sayısı, video izlenme sayısı (belirli kanallar için)
- Hatırlatıcılar: zamanlı veya tarihli hatırlatıcılar kurma, hatırlatıcıları listeleme/silme
- Hızlı hesaplamalar: matematik işlemleri, birim dönüştürme
- Sesli yanıt: cevapları yüksek sesle okuma (Text-to-Speech)

KULLANIM:
- Uyandırma: Yüksek sesle konuş veya iki kez el çırp.
- Örnek komutlar:
  "Saat kaç?"
  "Hava durumu nasıl?"
  "Not Defteri'ni aç"
  "Yeni bir dosya oluştur masaüstüne"
  "WhatsApp'tan Ayşe'ye 'Geliyorum' yaz"
  "Hatırlat bana saat 15'te toplantı var"
  "Ekran görüntüsü al"
  "Bilgisayarımın RAM'i ne kadar"
  "YouTube'da 'Python eğitimi' ara ve aç"
  "Sesimi yüzde 70 yap"
  "Not al: bugün marketten süt al"
- Çıkış: "kapat" de veya terminali kapat.

SIK KARŞILAŞILAN SORUNLAR:
- 'py' tanınmıyor: Python 3.12'yi PATH'e ekleyerek yeniden kur (kurulumda en alttaki kutucuğu işaretle)
- Microsoft Visual C++ 14.0 hatası: https://visualstudio.microsoft.com/visual-cpp-build-tools/ adresinden "C++ ile masaüstü geliştirme" iş yükünü yükle
- Mikrofon çalışmıyor: Ayarlar > Gizlilik > Mikrofon > "Masaüstü uygulamalarının erişmesine izin ver" AÇ
- API key geçersiz hatası: Yanlış veya geçersiz anahtar girildiyse, config/api_keys.json dosyasını silip programı tekrar başlatın, yeni anahtarı girin.
- WhatsApp mesaj göndermiyor: Rehbere kişiyi eklemek için "memory/phone_book.json" dosyasını düzenleyin: {"isim": "905551234567"} formatında.
- Sesli yanıt gelmiyor: Sistem ses ayarlarını kontrol edin, varsayılan çıkış cihazının çalıştığından emin olun.
- ModuleNotFoundError: Sanal ortamı aktif et (venv\Scripts\activate), tekrar py -3.12 -m pip install -r requirements.txt

UYARI:
Bu depo herkese açıktır (public). API anahtarınız config/api_keys.json içinde saklanır, bu dosyayı asla paylaşmayın veya pushlamayın. .gitignore dosyası zaten bu dosyayı engeller.

İletişim: esatayar7@gmail.com
