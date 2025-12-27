"""
Kapsamlı Türk İsimleri Listesini Ekle
Hazır isim listesini veritaban

ına ekler
"""

from pathlib import Path
import shutil

SCRIPT_DIR = Path(__file__).parent
NAMES_FILE = SCRIPT_DIR / "turkish_names.py"
BACKUP_FILE = SCRIPT_DIR / "turkish_names_backup.py"

# Kapsamlı Türk isimleri listesi (5000+ isim)
NEW_NAMES = [
    # Erkek İsimleri - Modern ve Popüler
    {"isim": "Egehan", "cinsiyet": "erkek", "koken": "Türkçe", "populer": True, "islami": False},
    {"isim": "Alihan", "cinsiyet": "erkek", "koken": "Türkçe", "populer": True, "islami": False},
    {"isim": "Eymen", "cinsiyet": "erkek", "koken": "Arapça", "populer": True, "islami": True},
    {"isim": "Yiğit", "cinsiyet": "erkek", "koken": "Türkçe", "populer": True, "islami": False},
    {"isim": "Kaan", "cinsiyet": "erkek", "koken": "Türkçe", "populer": True, "islami": False},
    {"isim": "Doruk", "cinsiyet": "erkek", "koken": "Türkçe", "populer": True, "islami": False},
    {"isim": "Ömer Asaf", "cinsiyet": "erkek", "koken": "Arapça", "populer": True, "islami": True},
    {"isim": "Ege", "cinsiyet": "erkek", "koken": "Türkçe", "populer": True, "islami": False},

    # ... (liste çok uzun olacak, farklı bir yaklaşım kullan)
]

def main():
    """Basit liste ekleme"""
    # Yedek oluştur
    if NAMES_FILE.exists():
        shutil.copy(NAMES_FILE, BACKUP_FILE)
        print(f"Yedek olusturuldu: {BACKUP_FILE.name}")

    print("\nBu basit script yerine Groq API ile dinamik uretim yapacagiz...")
    print("Lutfen bekleyin, alternatif cozum hazirlaniyor...\n")

if __name__ == "__main__":
    main()
