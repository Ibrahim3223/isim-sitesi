"""
Groq API ile Yeni Türkçe İsimler Üret
Veritabanına otomatik olarak ekler
"""

import os
import json
import time
import asyncio
import aiohttp
from pathlib import Path
from dotenv import load_dotenv
from slugify import slugify

# .env dosyasını yükle
load_dotenv()

# ============================================
# YAPILANDIRMA
# ============================================

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.1-8b-instant"

SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent
NAMES_FILE = SCRIPT_DIR / "turkish_names.py"
BACKUP_FILE = SCRIPT_DIR / "turkish_names_backup.py"

# Rate limiting
DELAY_BETWEEN_REQUESTS = 2.0

# ============================================
# İSİM ÜRETME
# ============================================

SYSTEM_PROMPT = """Sen Türkiye'nin en kapsamlı isim uzmanısın. Türkçe, Arapça, Farsça kökenli gerçek Türk isimleri hakkında derin bilgiye sahipsin.

Görevin: Türkiye'de gerçekten kullanılan, otantik Türk isimleri üretmek.

Kurallar:
1. SADECE Türkiye'de gerçekten kullanılan isimler
2. Modern ve geleneksel isimlerin karışımı
3. Popüler, nadir ve orta seviye isimler
4. Her isim için doğru köken belirt (Türkçe/Arapça/Farsça/Kürtçe)
5. İslami ve seküler isimlerin dengeli dağılımı
6. JSON formatında çıktı ver"""


async def generate_names_batch(session, gender, count=50):
    """Groq API ile isim batch'i üret"""

    gender_tr = "erkek" if gender == "erkek" else "kız"

    user_prompt = f"""Türkiye'de kullanılan {count} adet {gender_tr} ismi üret.

İsimler şu kategorilerden olabilir:
- Modern Türk isimleri (Ece, Emir, Zeynep, Mert vb.)
- Geleneksel Türk isimleri (Ayşe, Fatma, Mehmet, Ali vb.)
- Türkçe kökenli isimler (Alp, Aslan, Gökçe, Deniz vb.)
- Arapça kökenli isimler (Zehra, Yusuf, Rabia vb.)
- Farsça kökenli isimler (Gülsüm, Pervane vb.)
- Nadir ama gerçek isimler

Her isim için:
1. İsmin tam hali
2. Cinsiyet (erkek/kiz/unisex)
3. Köken (Türkçe/Arapça/Farsça/Kürtçe)
4. Popülerlik (true/false)
5. İslami isim mi? (true/false)

JSON array formatında ver:
[
  {{"isim": "Elif", "cinsiyet": "kiz", "koken": "Arapça", "populer": true, "islami": true}},
  {{"isim": "Arda", "cinsiyet": "erkek", "koken": "Türkçe", "populer": true, "islami": false}},
  ...
]

SADECE JSON array dön, başka açıklama ekleme."""

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.9,  # Yüksek çeşitlilik için
        "max_tokens": 4096,
        "top_p": 0.95
    }

    try:
        async with session.post(GROQ_API_URL, headers=headers, json=payload) as response:
            if response.status == 200:
                data = await response.json()
                content = data["choices"][0]["message"]["content"]

                # JSON'ı parse et
                # Bazen AI markdown formatında verir, temizle
                content = content.strip()
                if content.startswith("```json"):
                    content = content[7:]
                if content.startswith("```"):
                    content = content[3:]
                if content.endswith("```"):
                    content = content[:-3]
                content = content.strip()

                names_data = json.loads(content)
                return names_data

            elif response.status == 429:
                print("Rate limit, 60 saniye bekleniyor...")
                await asyncio.sleep(60)
                return await generate_names_batch(session, gender, count)
            else:
                error_text = await response.text()
                print(f"API Hatası ({response.status}): {error_text}")
                return None

    except json.JSONDecodeError as e:
        print(f"JSON parse hatası: {e}")
        print(f"Content: {content[:200]}...")
        return None
    except Exception as e:
        print(f"Hata: {e}")
        return None


def load_existing_names():
    """Mevcut isimleri yükle"""
    try:
        # turkish_names modülünü import et
        import sys
        sys.path.insert(0, str(SCRIPT_DIR))
        from turkish_names import get_all_names

        existing = get_all_names()
        existing_set = {slugify(n["isim"].lower()) for n in existing}

        return existing, existing_set

    except Exception as e:
        print(f"Mevcut isimler yüklenemedi: {e}")
        return [], set()


def backup_names_file():
    """Mevcut dosyayı yedekle"""
    if NAMES_FILE.exists():
        import shutil
        shutil.copy(NAMES_FILE, BACKUP_FILE)
        print(f"Yedek oluşturuldu: {BACKUP_FILE}")


def add_names_to_database(new_names):
    """Yeni isimleri veritabanına ekle"""

    # Mevcut dosyayı oku
    with open(NAMES_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    # NAMES listesinin sonunu bul
    # "# İsim listesi" satırından sonraki NAMES = [ ... ] kısmını bul
    names_start = content.find("NAMES = [")
    if names_start == -1:
        print("HATA: NAMES listesi bulunamadı!")
        return False

    # Son ] işaretini bul
    bracket_count = 0
    in_names_list = False
    names_end = -1

    for i in range(names_start, len(content)):
        if content[i] == '[':
            bracket_count += 1
            in_names_list = True
        elif content[i] == ']':
            bracket_count -= 1
            if in_names_list and bracket_count == 0:
                names_end = i
                break

    if names_end == -1:
        print("HATA: NAMES listesinin sonu bulunamadı!")
        return False

    # Yeni isimleri ekle
    # Son ] den önce virgül ve yeni satır ekle
    before_bracket = content[:names_end]
    after_bracket = content[names_end:]

    # Eğer son eleman virgülle bitmiyorsa virgül ekle
    if not before_bracket.rstrip().endswith(','):
        before_bracket = before_bracket.rstrip() + ','

    # Yeni isimleri ekle
    new_entries = []
    for name in new_names:
        entry = f"""
    {{
        "isim": "{name['isim']}",
        "cinsiyet": "{name['cinsiyet']}",
        "koken": "{name['koken']}",
        "populer": {str(name['populer']).lower()},
        "islami": {str(name['islami']).lower()}
    }}"""
        new_entries.append(entry)

    new_content = before_bracket + ",".join(new_entries) + "\n" + after_bracket

    # Dosyayı güncelle
    with open(NAMES_FILE, "w", encoding="utf-8") as f:
        f.write(new_content)

    return True


async def main():
    """Ana fonksiyon"""
    import argparse

    parser = argparse.ArgumentParser(description="Groq ile yeni isimler üret")
    parser.add_argument("--target", type=int, default=5000, help="Hedef toplam isim sayısı")
    parser.add_argument("--batch-size", type=int, default=50, help="Her batch'te üretilecek isim sayısı")
    args = parser.parse_args()

    if not GROQ_API_KEY:
        print("HATA: GROQ_API_KEY bulunamadı!")
        return

    # Mevcut isimleri yükle
    existing_names, existing_slugs = load_existing_names()
    current_count = len(existing_names)

    print(f"\n{'='*60}")
    print(f"Mevcut isim sayısı: {current_count}")
    print(f"Hedef isim sayısı: {args.target}")
    print(f"Üretilecek isim sayısı: {args.target - current_count}")
    print(f"{'='*60}\n")

    if current_count >= args.target:
        print("Hedef sayıya zaten ulaşılmış!")
        return

    # Yedek oluştur
    backup_names_file()

    needed = args.target - current_count
    batches_needed = (needed + args.batch_size - 1) // args.batch_size

    total_added = 0
    total_duplicates = 0

    async with aiohttp.ClientSession() as session:
        for batch_num in range(batches_needed):
            # Erkek ve kız isimleri dengeli üret
            gender = "erkek" if batch_num % 2 == 0 else "kiz"

            print(f"\n[Batch {batch_num + 1}/{batches_needed}] {gender.capitalize()} isimleri üretiliyor...")

            names = await generate_names_batch(session, gender, args.batch_size)

            if not names:
                print("Batch üretilemedi, atlanıyor...")
                continue

            # Duplicate kontrolü
            new_names = []
            duplicates = 0

            for name in names:
                slug = slugify(name["isim"].lower())
                if slug not in existing_slugs:
                    new_names.append(name)
                    existing_slugs.add(slug)
                else:
                    duplicates += 1

            if new_names:
                # Veritabanına ekle
                if add_names_to_database(new_names):
                    total_added += len(new_names)
                    total_duplicates += duplicates
                    print(f"  ✓ {len(new_names)} yeni isim eklendi")
                    print(f"  ↷ {duplicates} duplicate atlandı")
                    print(f"  Toplam: {current_count + total_added}/{args.target}")
                else:
                    print("  ✗ Veritabanına eklenemedi!")

            # Rate limiting
            await asyncio.sleep(DELAY_BETWEEN_REQUESTS)

            # Hedefe ulaştıysak dur
            if current_count + total_added >= args.target:
                break

    print(f"\n{'='*60}")
    print(f"İşlem Tamamlandı!")
    print(f"Başlangıç: {current_count} isim")
    print(f"Eklenen: {total_added} isim")
    print(f"Duplicate: {total_duplicates}")
    print(f"Toplam: {current_count + total_added} isim")
    print(f"{'='*60}\n")

    if BACKUP_FILE.exists():
        print(f"Yedek dosya: {BACKUP_FILE}")
        print("Bir sorun olursa bu dosyayı kullanabilirsiniz.")


if __name__ == "__main__":
    asyncio.run(main())
