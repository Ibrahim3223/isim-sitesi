"""
Google Indexing API - Instant Indexing
Yeni oluşturulan sayfaları otomatik olarak Google'a bildirir
"""

import os
import json
import time
from pathlib import Path
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

# ============================================
# YAPILANDIRMA
# ============================================

SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent
CREDENTIALS_FILE = SCRIPT_DIR / "google-credentials.json"
INDEXED_URLS_FILE = SCRIPT_DIR / "indexed_urls.json"
BASE_URL = os.getenv("SITE_URL", "https://isimsozlugu.net")

# API Scopes
SCOPES = ["https://www.googleapis.com/auth/indexing"]

# Rate limiting
REQUESTS_PER_MINUTE = 200  # Google limiti: 200/dakika
DELAY_BETWEEN_REQUESTS = 60.0 / REQUESTS_PER_MINUTE  # ~0.3 saniye

# ============================================
# INDEXING FONKSİYONLARI
# ============================================

def load_indexed_urls():
    """Daha önce indexlenen URL'leri yükle"""
    if INDEXED_URLS_FILE.exists():
        with open(INDEXED_URLS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "indexed": [],
        "failed": [],
        "stats": {
            "total_indexed": 0,
            "total_failed": 0,
            "last_run": None
        }
    }


def save_indexed_urls(data):
    """İndexlenen URL'leri kaydet"""
    data["stats"]["last_run"] = datetime.now().isoformat()
    with open(INDEXED_URLS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_credentials():
    """Google API credentials al"""
    if not CREDENTIALS_FILE.exists():
        print(f"HATA: {CREDENTIALS_FILE} bulunamadı!")
        print("\nGoogle Cloud Console'dan service account oluşturup")
        print("credentials dosyasını bu konuma kaydetmelisiniz.")
        return None

    credentials = service_account.Credentials.from_service_account_file(
        str(CREDENTIALS_FILE), scopes=SCOPES
    )
    return credentials


def notify_google(url, update_type="URL_UPDATED"):
    """
    Google'a URL bildirimi gönder

    update_type:
        - URL_UPDATED: Sayfa oluşturuldu veya güncellendi
        - URL_DELETED: Sayfa silindi
    """
    credentials = get_credentials()
    if not credentials:
        return False

    try:
        service = build('indexing', 'v3', credentials=credentials)

        body = {
            "url": url,
            "type": update_type
        }

        response = service.urlNotifications().publish(body=body).execute()
        return True

    except HttpError as e:
        print(f"HTTP Hatası: {e}")
        return False
    except Exception as e:
        print(f"Hata: {e}")
        return False


def get_status(url):
    """URL'nin indexing durumunu kontrol et"""
    credentials = get_credentials()
    if not credentials:
        return None

    try:
        service = build('indexing', 'v3', credentials=credentials)
        response = service.urlNotifications().getMetadata(url=url).execute()
        return response
    except HttpError as e:
        if e.resp.status == 404:
            return {"status": "NOT_FOUND"}
        print(f"HTTP Hatası: {e}")
        return None
    except Exception as e:
        print(f"Hata: {e}")
        return None


def index_url(url, force=False):
    """Tek bir URL'i indexle"""
    indexed_data = load_indexed_urls()

    # Daha önce indexlendiyse atla (force=False ise)
    if not force and url in indexed_data["indexed"]:
        print(f"[ATLA] Zaten indexlendi: {url}")
        return True

    print(f"[INDEX] {url}")

    if notify_google(url):
        indexed_data["indexed"].append(url)
        indexed_data["stats"]["total_indexed"] += 1
        save_indexed_urls(indexed_data)
        print(f"[OK] Başarıyla indexlendi")
        return True
    else:
        indexed_data["failed"].append(url)
        indexed_data["stats"]["total_failed"] += 1
        save_indexed_urls(indexed_data)
        print(f"[HATA] İndexleme başarısız")
        return False


def index_all_names(force=False, limit=None):
    """Tüm isim sayfalarını indexle"""
    content_dir = PROJECT_DIR / "hugo-site" / "content" / "isim"

    if not content_dir.exists():
        print(f"HATA: {content_dir} bulunamadı!")
        return

    md_files = list(content_dir.glob("*.md"))

    # _index.md'yi hariç tut
    md_files = [f for f in md_files if f.name != "_index.md"]

    print(f"\n{'='*60}")
    print(f"Toplam {len(md_files)} isim sayfası bulundu")
    print(f"{'='*60}\n")

    indexed_data = load_indexed_urls()
    success_count = 0
    failed_count = 0
    skipped_count = 0

    # Limit varsa uygula
    if limit:
        md_files = md_files[:limit]
        print(f"Limit: İlk {limit} sayfa işlenecek\n")

    for i, md_file in enumerate(md_files, 1):
        # Slug'ı dosya adından al
        slug = md_file.stem
        url = f"{BASE_URL}/isim/{slug}/"

        # Daha önce indexlendiyse atla
        if not force and url in indexed_data["indexed"]:
            skipped_count += 1
            if i % 50 == 0:  # Her 50'de bir durum göster
                print(f"[{i}/{len(md_files)}] İşleniyor... (Başarılı: {success_count}, Atlanan: {skipped_count})")
            continue

        print(f"[{i}/{len(md_files)}] {url}")

        if notify_google(url):
            indexed_data["indexed"].append(url)
            indexed_data["stats"]["total_indexed"] += 1
            success_count += 1
            print(f"  ✓ Başarılı")
        else:
            indexed_data["failed"].append(url)
            indexed_data["stats"]["total_failed"] += 1
            failed_count += 1
            print(f"  ✗ Başarısız")

        # İlerlemeyi kaydet
        if i % 10 == 0:
            save_indexed_urls(indexed_data)

        # Rate limiting
        time.sleep(DELAY_BETWEEN_REQUESTS)

    # Son durumu kaydet
    save_indexed_urls(indexed_data)

    print(f"\n{'='*60}")
    print(f"İşlem Tamamlandı!")
    print(f"Başarılı: {success_count}")
    print(f"Başarısız: {failed_count}")
    print(f"Atlanan: {skipped_count}")
    print(f"{'='*60}")


def index_category_pages():
    """Kategori sayfalarını indexle"""
    pages = [
        f"{BASE_URL}/",  # Ana sayfa
        f"{BASE_URL}/erkek-isimleri/",
        f"{BASE_URL}/kiz-isimleri/",
        f"{BASE_URL}/populer-isimler/",
        f"{BASE_URL}/islami-isimler/",
        f"{BASE_URL}/a-z-isimler/",
        f"{BASE_URL}/koken/turkce/",
        f"{BASE_URL}/koken/arapca/",
        f"{BASE_URL}/koken/farsca/",
    ]

    print(f"\n{'='*60}")
    print(f"Kategori Sayfaları İndexleniyor ({len(pages)} sayfa)")
    print(f"{'='*60}\n")

    for url in pages:
        print(f"[INDEX] {url}")
        if notify_google(url):
            print(f"  ✓ Başarılı")
        else:
            print(f"  ✗ Başarısız")
        time.sleep(DELAY_BETWEEN_REQUESTS)


def main():
    """Ana fonksiyon"""
    import argparse

    parser = argparse.ArgumentParser(description="Google Indexing API - Instant Indexing")
    parser.add_argument("--url", type=str, help="Tek bir URL indexle")
    parser.add_argument("--all", action="store_true", help="Tüm isim sayfalarını indexle")
    parser.add_argument("--categories", action="store_true", help="Kategori sayfalarını indexle")
    parser.add_argument("--limit", type=int, help="İndexlenecek maksimum sayfa sayısı")
    parser.add_argument("--force", action="store_true", help="Daha önce indexlenen sayfaları tekrar indexle")
    parser.add_argument("--status", type=str, help="URL'nin indexing durumunu kontrol et")
    parser.add_argument("--reset", action="store_true", help="İndexleme geçmişini sıfırla")

    args = parser.parse_args()

    # Credentials kontrolü
    if not CREDENTIALS_FILE.exists() and not args.reset:
        print(f"\n{'='*60}")
        print("HATA: Google Service Account credentials bulunamadı!")
        print(f"{'='*60}\n")
        print("Kurulum için:")
        print("1. Google Cloud Console'a gidin")
        print("2. Yeni bir proje oluşturun")
        print("3. Indexing API'yi etkinleştirin")
        print("4. Service Account oluşturun")
        print("5. JSON key dosyasını indirin")
        print(f"6. {CREDENTIALS_FILE} olarak kaydedin")
        print("\nDetaylı kurulum için README dosyasına bakın.")
        return

    # Reset
    if args.reset:
        if INDEXED_URLS_FILE.exists():
            INDEXED_URLS_FILE.unlink()
        print("İndexleme geçmişi sıfırlandı.")
        return

    # Status kontrolü
    if args.status:
        status = get_status(args.status)
        print(json.dumps(status, indent=2))
        return

    # Tek URL
    if args.url:
        index_url(args.url, force=args.force)
        return

    # Kategori sayfaları
    if args.categories:
        index_category_pages()
        return

    # Tüm sayfalar
    if args.all:
        index_all_names(force=args.force, limit=args.limit)
        return

    # Hiçbir argüman verilmediyse help göster
    parser.print_help()


if __name__ == "__main__":
    main()
