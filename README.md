```markdown
# H.A.T.E - Windows 10/11 Kurulum Rehberi

## Adım 1 - Python 3.12'yi Yükleme

1.  **İndir**: [python.org/downloads/](https://python.org/downloads/) adresine gidip `Python 3.12.x` sürümünü indirin.
2.  **Başlat**: İndirilen dosyaya çift tıklayın.
3.  **ÖNEMLİ**: Kurulum sihirbazının **EN ALTINDAKİ** "Add Python 3.12 to PATH" yazan kutucuğu mutlaka işaretleyin.
4.  **Kur**: "Install Now" seçeneğine tıklayın ve kurulumun tamamlanmasını bekleyin.
5.  **Doğrula**: `Win + R` tuşlarına basın, `cmd` yazıp Enter'a basarak Komut İstemi'ni açın. Aşağıdaki komutu yazıp Enter'a basın:
    ```bash
    python --version
    ```
    Eğer "Python 3.12.x" yazısını görüyorsanız, Python başarıyla kurulmuş demektir.

## Adım 2 - Projeyi İndirme ve Sanal Ortam Oluşturma

1.  **Klasör Oluşturun**: Masaüstüne yeni bir klasör oluşturun ve ismini `hate-ai` olarak belirleyin.
2.  **Komut İstemi'ni Açın**: Arama çubuğuna `cmd` yazın, "Komut İstemi" uygulamasına sağ tıklayıp "Yönetici olarak çalıştır" seçeneğini seçin.
3.  **Klasöre Gidin**: Açılan siyah ekrana sırayla aşağıdaki komutları yazın ve her birinden sonra Enter'a basın:
    ```bash
    cd Desktop
    cd hate-ai
    ```
4.  **Sanal Ortam Oluşturun**:
    ```bash
    py -3.12 -m venv venv
    ```
    Bu komut, projenize özel, izole bir Python ortamı yaratacaktır. (Eğer `py -3.12` çalışmazsa, `python -m venv venv` komutunu deneyin).

## Adım 3 - Gerekli Kütüphaneleri Yükleme

1.  **Komut İstemi'nde hala `C:\Users\...\Desktop\hate-ai` klasöründe olduğunuzdan emin olun.**
2.  **Sanal Ortamı Aktifleştirin**:
    ```bash
    venv\Scripts\activate
    ```
    Komut satırının başında `(venv)` yazısını görmelisiniz. Bu, sanal ortamın aktif olduğunu gösterir.
3.  **Pip'i Güncelleyin**:
    ```bash
    py -3.12 -m pip install --upgrade pip
    ```
4.  **Kütüphaneleri Yükleyin**: Projenin ihtiyacı olan tüm kütüphaneleri tek seferde kurmak için şu komutu çalıştırın:
    ```bash
    py -3.12 -m pip install -r requirements.txt
    ```
    (Eğer `py -3.12` çalışmazsa, `python -m pip install -r requirements.txt` komutunu kullanın).

## Adım 4 - API Anahtarını Yapılandırma

1.  **Dosya Gezgini** ile `C:\Users\...\Desktop\hate-ai\config` klasörüne gidin.
2.  İçinde `api_keys.example.json` isimli bir dosya göreceksiniz. Bu dosyaya sağ tıklayıp **Kopyala**'ya tıklayın.
3.  Aynı klasörün içinde boş bir alana sağ tıklayıp **Yapıştır**'a tıklayın.
4.  Yapıştırdığınız bu yeni dosyaya sağ tıklayın, "Yeniden Adlandır" seçeneğini seçin ve ismini `api_keys.json` olarak değiştirin.
5.  Yeni oluşturduğunuz `api_keys.json` dosyasını Notepad veya herhangi bir metin düzenleyicisi ile açın.
6.  [Google AI Studio](https://aistudio.google.com/app/apikey) adresine giderek bir **Google Gemini API anahtarı** oluşturun ve kopyalayın.
7.  Metin düzenleyicisinde `"AIzaSy..."` yazan yeri silin ve kopyaladığınız API anahtarınızı buraya yapıştırın. Dosyayı kaydedip kapatın.
    ```json
    {
      "gemini_api_key": "BURAYA_API_ANAHTARINIZI_YAPISTIRIN",
      "voice": "Charon",
      "recognition_language": "tr-TR"
    }
    ```

## Adım 5 - Asistanı Çalıştırmak

1.  **Komut İstemi'nde hala `(venv)` yazısını görüyor olmanız ve `C:\...\Desktop\hate-ai` klasöründe bulunmanız gerekiyor.** Eğer kapattıysanız, Komut İstemi'ni tekrar yönetici olarak açın, sırayla `cd Desktop`, `cd hate-ai` ve `venv\Scripts\activate` komutlarını tekrar girin.
2.  **Ana Programı Başlatın**:
    ```bash
    py main.py
    ```
    (Eğer `py` çalışmazsa, `python main.py` komutunu deneyin).

## Adım 6 - Sorun Giderme (SSS)

**1. `'python' is not recognized...` hatası alıyorum (Python tanınmıyor).**
- **Nedeni:** Python kurulumu sırasında "Add Python to PATH" kutucuğu işaretlenmemiş olabilir.
- **Çözüm 1:** Python'u kaldırın ve bu kılavuzdaki **Adım 1**'i tekrar uygulayarak **en alttaki kutucuğu işaretlemeyi unutmayın**.
- **Çözüm 2:** "Komut İstemi"ni kapatıp tekrar yönetici olarak açmayı deneyin.

**2. `pip` bir komut olarak tanınmıyor.**
- **Nedeni:** Python PATH'e eklenmemiş olabilir veya Pip kurulu değildir.
- **Çözüm:** Her `pip install ...` komutu yerine `py -3.12 -m pip install ...` formatını kullanın. Örneğin: `py -3.12 -m pip install -r requirements.txt`

**3. `pip install -r requirements.txt` sırasında hata alıyorum.**
- **Nedeni:** Bazı kütüphaneler (örn: `pyaudio`) kurulum için ek araçlara ihtiyaç duyabilir.
- **Çözüm:** [Microsoft C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) sayfasına gidin, "Build Tools for Visual Studio 2022" başlığı altındaki "Download" butonuna tıklayın. Kurulumu başlatın, "C++ ile masaüstü geliştirme" iş yükünü seçip yükleyin. Bilgisayarınızı yeniden başlatın ve **Adım 3**'ü tekrar uygulayın.

**4. `venv\Scripts\activate` komutu çalışmıyor.**
- **Nedeni:** Bilgisayarınızda PowerShell çalıştırma politikaları, betiklerin çalışmasını engelliyor olabilir.
- **Çözüm:** Yönetici olarak açtığınız Komut İstemi (CMD) penceresinde bu komutu tekrar deneyin. CMD, genellikle PowerShell'e göre bu konuda daha sorunsuzdur.

**5. Mikrofon çalışmıyor veya asistan beni duymuyor.**
- **Çözüm:** Windows Ayarları > Gizlilik ve Güvenlik > Mikrofon menüsüne gidin. "Masaüstü uygulamalarının mikrofonunuza erişmesine izin ver" seçeneğinin açık olduğundan emin olun.
```
