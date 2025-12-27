# Google Instant Indexing Kurulumu

Bu rehber, Google Indexing API kullanarak sitenize instant indexing özelliği eklemenizi sağlar.

## 🎯 Amaç

Google Indexing API, yeni veya güncellenmiş sayfalarınızı Google'a anında bildirmenizi sağlar. Normal crawling'i beklemek yerine, sayfa URL'lerinizi doğrudan Google'a gönderebilirsiniz.

**Faydalar:**
- ✅ Yeni sayfalar dakikalar içinde indexlenir
- ✅ Güncellemeler hemen Google'a bildirilir
- ✅ Search Console'da manuel gönderim gereksiz
- ✅ 200 URL/dakika hızla toplu gönderim

## 📋 Gereksinimler

1. Google Cloud hesabı (ücretsiz)
2. Domain'in Google Search Console'da doğrulanmış olması
3. Python 3.7+

## 🚀 Kurulum Adımları

### 1. Google Cloud Projesi Oluşturma

1. **Google Cloud Console'a gidin:**
   - https://console.cloud.google.com/

2. **Yeni proje oluşturun:**
   - Sol üstteki "Proje Seçin" > "Yeni Proje"
   - Proje adı: `isim-sitesi-indexing`
   - Oluştur butonuna tıklayın

3. **Indexing API'yi etkinleştirin:**
   - Sol menüden "API'ler ve Hizmetler" > "API'leri ve hizmetleri etkinleştir"
   - "Indexing API" araması yapın
   - "Web Search Indexing API"yi seçin
   - "Etkinleştir" butonuna tıklayın

### 2. Service Account Oluşturma

1. **Service Account oluşturun:**
   - "API'ler ve Hizmetler" > "Kimlik Bilgileri"
   - "Kimlik bilgisi oluştur" > "Hizmet hesabı"
   - Hizmet hesabı adı: `indexing-bot`
   - Hizmet hesabı ID: `indexing-bot` (otomatik)
   - "Oluştur ve devam et" butonuna tıklayın
   - Rol: **Owner** (veya en azından "Viewer")
   - "Devam" > "Bitti"

2. **JSON Key dosyası indirin:**
   - Oluşturduğunuz service account'a tıklayın
   - "Anahtarlar" sekmesine gidin
   - "Anahtar ekle" > "Yeni anahtar oluştur"
   - Tür: **JSON**
   - "Oluştur" butonuna tıklayın
   - JSON dosyası bilgisayarınıza indirilecek

3. **JSON dosyasını kaydedin:**
   - İndirilen dosyayı `scripts/google-credentials.json` olarak kaydedin
   ```bash
   # Dosyayı doğru konuma taşıyın
   mv ~/Downloads/isim-sitesi-indexing-*.json scripts/google-credentials.json
   ```

### 3. Search Console'da Service Account'u Yetkilendirme

1. **Service Account email'ini kopyalayın:**
   - JSON dosyasını açın
   - `client_email` alanındaki email'i kopyalayın
   - Örnek: `indexing-bot@isim-sitesi-indexing.iam.gserviceaccount.com`

2. **Search Console'a gidin:**
   - https://search.google.com/search-console/

3. **Service Account'u ekleyin:**
   - Sitenizi seçin (isimsozlugu.net)
   - Sol menüden "Ayarlar" > "Kullanıcılar ve izinler"
   - "Kullanıcı ekle" butonuna tıklayın
   - Email: Service account email'inizi yapıştırın
   - İzin: **Owner** (veya Full)
   - "Ekle" butonuna tıklayın

### 4. Python Bağımlılıklarını Yükleme

```bash
cd c:\Users\Dante\Desktop\Yeniden\WebSite\isim-sitesi
pip install -r requirements.txt
```

Bu şu paketleri yükler:
- `google-api-python-client` - Google API client
- `google-auth` - Authentication
- `google-auth-oauthlib` - OAuth
- `google-auth-httplib2` - HTTP client

## 💻 Kullanım

### Tek URL İndexleme

```bash
python scripts/instant_indexing.py --url https://isimsozlugu.net/isim/ahmet/
```

### Kategori Sayfalarını İndexleme

```bash
python scripts/instant_indexing.py --categories
```

Bu komut şu sayfaları indexler:
- Ana sayfa
- Erkek isimleri
- Kız isimleri
- Popüler isimler
- İslami isimler
- A-Z listesi
- Köken sayfaları

### Tüm İsim Sayfalarını İndexleme

```bash
# Tüm sayfaları indexle (1245 sayfa)
python scripts/instant_indexing.py --all

# İlk 100 sayfayı indexle
python scripts/instant_indexing.py --all --limit 100

# Daha önce indexlenenler dahil tümünü tekrar indexle
python scripts/instant_indexing.py --all --force
```

### URL Durumunu Kontrol Etme

```bash
python scripts/instant_indexing.py --status https://isimsozlugu.net/isim/ahmet/
```

### İndexleme Geçmişini Sıfırlama

```bash
python scripts/instant_indexing.py --reset
```

## 📊 İzleme ve Takip

### İndexleme Geçmişi

Script otomatik olarak `scripts/indexed_urls.json` dosyasında:
- İndexlenen URL'leri
- Başarısız URL'leri
- İstatistikleri

saklar.

### Progress Tracking

Script çalışırken:
```
[1/1245] https://isimsozlugu.net/isim/ahmet/
  ✓ Başarılı
[2/1245] https://isimsozlugu.net/isim/mehmet/
  ✓ Başarılı
...
```

### Rate Limiting

Script otomatik olarak:
- Dakikada 200 istek sınırına uyar
- İstekler arasında ~0.3 saniye bekler
- Her 10 istekte bir ilerlemeyi kaydeder

## 🔄 Otomatik İndexleme (İleride Eklenebilir)

### Yeni İçerik Üretiminde Otomatik İndexleme

`generate_content.py` dosyasına entegrasyon:

```python
# generate_content.py içine eklenebilir
from instant_indexing import index_url

# Yeni sayfa oluşturulduğunda
if file_path:
    url = f"https://isimsozlugu.net/isim/{slug}/"
    index_url(url)
```

### GitHub Actions ile Otomatik İndexleme

`.github/workflows/index-pages.yml`:

```yaml
name: Index New Pages

on:
  push:
    branches: [main]
    paths:
      - 'hugo-site/content/isim/**'

jobs:
  index:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Index new pages
        env:
          GOOGLE_CREDENTIALS: ${{ secrets.GOOGLE_CREDENTIALS }}
        run: |
          echo "$GOOGLE_CREDENTIALS" > scripts/google-credentials.json
          python scripts/instant_indexing.py --all --limit 50
```

## ❓ Sorun Giderme

### "credentials not found" hatası

**Çözüm:**
```bash
# Dosyanın doğru konumda olduğunu kontrol edin
ls scripts/google-credentials.json

# Dosya yoksa Google Cloud'dan tekrar indirin
```

### "Permission denied" hatası

**Çözüm:**
- Search Console'da service account'un Owner izni olduğunu kontrol edin
- Service account email'inin doğru olduğunu kontrol edin

### "Quota exceeded" hatası

**Çözüm:**
- Dakikada 200 URL limiti aşılmış
- Script otomatik olarak bekler, endişelenmeyin
- Veya `--limit` parametresiyle daha az URL gönderin

### "API not enabled" hatası

**Çözüm:**
- Google Cloud Console'da Indexing API'nin etkinleştirildiğini kontrol edin

## 📚 Kaynaklar

- [Google Indexing API Dokümantasyonu](https://developers.google.com/search/apis/indexing-api/v3/quickstart)
- [Google Cloud Console](https://console.cloud.google.com/)
- [Search Console](https://search.google.com/search-console/)

## 🎉 İlk Test

Kurulum tamamlandıktan sonra test edin:

```bash
# 1. Kategori sayfalarını indexle
python scripts/instant_indexing.py --categories

# 2. İlk 10 isim sayfasını indexle
python scripts/instant_indexing.py --all --limit 10

# 3. Sonuçları kontrol et
cat scripts/indexed_urls.json
```

Search Console'da **Coverage** raporunu kontrol edin - birkaç dakika içinde yeni URL'ler görünmeye başlayacak!
