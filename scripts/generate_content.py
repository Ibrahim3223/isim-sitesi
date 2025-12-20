"""
İsim Sözlüğü - Groq API ile İçerik Üretimi
Her isim için detaylı sayfa oluşturur
"""

import os
import json
import time
import asyncio
import aiohttp
from datetime import datetime
from pathlib import Path
from slugify import slugify
from tqdm import tqdm
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

# İsim veritabanını import et
from turkish_names import get_all_names, get_names_by_gender

# ============================================
# YAPILANDIRMA
# ============================================

# API Ayarları
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.1-8b-instant"  # Hızlı ve ücretsiz model

# Dizinler
SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent
CONTENT_DIR = PROJECT_DIR / "hugo-site" / "content" / "isim"
PROGRESS_FILE = SCRIPT_DIR / "generation_progress.json"

# Rate limiting
REQUESTS_PER_MINUTE = 30
DELAY_BETWEEN_REQUESTS = 2.0  # saniye

# ============================================
# SYSTEM PROMPT
# ============================================

SYSTEM_PROMPT = """Sen Türkiye'nin en deneyimli bebek isim uzmanısın. İsimler hakkında detaylı, doğru ve ilgi çekici içerikler yazarsın.

Yazım kuralların:
1. Doğal, akıcı Türkçe kullan
2. SEO dostu içerik yaz (anahtar kelimeleri doğal şekilde kullan)
3. Bilgilendirici ve güvenilir ol
4. Ebeveynlere yardımcı olacak pratik bilgiler ver
5. Markdown formatında yaz (## başlıklar, - listeler)
6. Her bölümü detaylı yaz, minimum 150 kelime kullan
7. İsmin anlamını, kökenini ve karakter özelliklerini detaylandır"""

# ============================================
# İÇERİK ÜRETME FONKSİYONLARI
# ============================================

def get_user_prompt(name_data):
    """İsim için kullanıcı promptu oluştur"""
    isim = name_data["isim"]
    cinsiyet_raw = name_data["cinsiyet"]

    if cinsiyet_raw == "unisex":
        cinsiyet = "unisex (hem erkek hem kız için kullanılır)"
    elif cinsiyet_raw == "erkek":
        cinsiyet = "erkek"
    else:
        cinsiyet = "kız"

    koken = name_data["koken"]
    islami = "evet" if name_data["islami"] else "hayır"

    prompt = f""""{isim}" ismi hakkında detaylı bir içerik yaz.

ÖNEMLI: İlk cümle "{isim} isminin kısa anlamı:" ile başlamalı ve tek cümlede özet anlam verilmeli.
Örnek: "Ahmet isminin kısa anlamı: Övülmeye layık, çok övülen, şükredilen anlamına gelir."

Sonra devam et:

İsim Bilgileri:
- İsim: {isim}
- Cinsiyet: {cinsiyet}
- Köken: {koken}
- İslami/Dini İsim: {islami}

Aşağıdaki bölümleri içeren kapsamlı bir içerik oluştur:

## {isim} İsminin Anlamı
(İsmin anlamını detaylı açıkla, kökenine değin, varsa farklı anlamlarını belirt)

## {isim} İsminin Kökeni ve Tarihi
(İsmin hangi dilden geldiğini, tarihsel kullanımını, kültürel önemini anlat)

## {isim} İsminin Karakter Özellikleri
(Bu ismi taşıyan kişilerin genel karakter özelliklerini, kişilik analizini yaz)

## {isim} İsmi Hakkında Bilgiler
(İsmin harf sayısı, hece sayısı, numerolojik değeri gibi bilgiler)

## {isim} İsmi Neden Tercih Edilmeli?
(Ebeveynlere bu ismi seçmeleri için nedenler sun)

## {isim} İsmi ile Uyumlu İkinci İsimler
(Bu isimle uyumlu 5-6 ikinci isim öner, açıklamayla)

Dikkat:
- Sadece içeriği yaz, frontmatter veya metadata ekleme
- Markdown formatında yaz
- Minimum 400 kelime olsun
- Doğal ve akıcı bir dil kullan"""

    return prompt


async def generate_content_with_groq(session, name_data):
    """Groq API ile içerik üret"""
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": get_user_prompt(name_data)}
        ],
        "temperature": 0.7,
        "max_tokens": 2048,
        "top_p": 0.9
    }

    try:
        async with session.post(GROQ_API_URL, headers=headers, json=payload) as response:
            if response.status == 200:
                data = await response.json()
                content = data["choices"][0]["message"]["content"]
                return content
            elif response.status == 429:
                # Rate limit - bekle ve tekrar dene
                print(f"Rate limit aşıldı, 60 saniye bekleniyor...")
                await asyncio.sleep(60)
                return await generate_content_with_groq(session, name_data)
            else:
                error_text = await response.text()
                print(f"API Hatası ({response.status}): {error_text}")
                return None
    except Exception as e:
        print(f"İstek hatası: {e}")
        return None


def create_markdown_file(name_data, content):
    """Markdown dosyası oluştur"""
    isim = name_data["isim"]
    slug = slugify(isim, lowercase=True)
    cinsiyet = name_data["cinsiyet"]
    koken = name_data["koken"]
    populer = name_data["populer"]
    islami = name_data["islami"]

    # Tarih
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%dT%H:%M:%S+03:00")

    # Harf ve hece sayısı
    harf_sayisi = len(isim)
    # Basit hece sayısı hesaplama (sesli harf sayısı)
    sesli_harfler = "aeıioöuüAEIİOÖUÜ"
    hece_sayisi = sum(1 for c in isim if c in sesli_harfler)
    if hece_sayisi == 0:
        hece_sayisi = 1

    # Kısa anlam çıkar (içeriğin ilk paragraflarından akıllıca çıkar)
    kisa_anlam = f"{isim} isminin anlamı"
    try:
        # Önce özel formatlı başlangıcı ara
        if f"{isim} isminin kısa anlamı:" in content:
            anlam_baslangic = content.find(f"{isim} isminin kısa anlamı:")
            anlam_bitis = content.find("\n", anlam_baslangic)
            if anlam_bitis != -1:
                kisa_anlam_line = content[anlam_baslangic:anlam_bitis]
                kisa_anlam = kisa_anlam_line.replace(f"{isim} isminin kısa anlamı:", "").strip()
        else:
            # İçeriği satırlara böl ve anlam içeren ilk cümleyi bul
            lines = content.split('\n')
            for line in lines:
                # Boş satırları ve başlıkları atla
                if not line.strip() or line.strip().startswith('#'):
                    continue

                # Anlam belirten ifadeleri ara
                anlam_belirtecler = [
                    'anlamına gelir', 'demektir', 'anlamındadır',
                    'manasına gelir', 'ifade eder', 'karşılık gelir'
                ]

                if any(belirtec in line.lower() for belirtec in anlam_belirtecler):
                    # Bu satırdan anlamı çıkar
                    # "İsmin anlamı, " veya "İsim, " gibi başlangıçları temizle
                    clean_line = line.strip()
                    for prefix in [f"{isim} ismi,", f"{isim},", "İsmin anlamı,", "Anlamı,"]:
                        if clean_line.startswith(prefix):
                            clean_line = clean_line[len(prefix):].strip()

                    # İlk cümleyi al (nokta veya virgüle kadar)
                    first_sentence = clean_line.split('.')[0].strip()
                    if len(first_sentence) < 200 and first_sentence:
                        kisa_anlam = first_sentence
                        # Baştaki ve sondaki tırnak işaretlerini temizle
                        kisa_anlam = kisa_anlam.strip('"\'')
                        break
    except:
        pass

    # Benzer isimler (aynı harfle başlayan, aynı cinsiyetten)
    all_names = get_names_by_gender(cinsiyet)
    ilk_harf = isim[0].upper()
    benzer_isimler = [n["isim"] for n in all_names
                      if n["isim"][0].upper() == ilk_harf and n["isim"] != isim][:6]

    # Cinsiyet açıklaması
    if cinsiyet == "unisex":
        cinsiyet_aciklama = "unisex (hem erkek hem kız)"
        categories_list = ["erkek-isimleri", "kiz-isimleri"]
        tags_cinsiyet = "unisex isimleri"
    elif cinsiyet == "erkek":
        cinsiyet_aciklama = "erkek"
        categories_list = ["erkek-isimleri"]
        tags_cinsiyet = "erkek isimleri"
    else:
        cinsiyet_aciklama = "kız"
        categories_list = ["kiz-isimleri"]
        tags_cinsiyet = "kız isimleri"

    # Frontmatter
    frontmatter = f"""---
title: "{isim}"
slug: "{slug}"
date: {date_str}
lastmod: {date_str}
description: "{isim} isminin anlamı, kökeni ve özellikleri. {isim} ismi {koken} kökenli {cinsiyet_aciklama} bebek ismidir."
keywords: ["{isim}", "{isim} ismi", "{isim} isminin anlamı", "{isim} ne demek", "{isim} ismi anlamı"]
categories: {json.dumps(categories_list, ensure_ascii=False)}
tags: ["{isim}", "{koken} isimler", "{tags_cinsiyet}", "bebek isimleri"]
cinsiyet: "{cinsiyet}"
koken: "{koken}"
populer: {str(populer).lower()}
islami: {str(islami).lower()}
harf_sayisi: {harf_sayisi}
hece_sayisi: {hece_sayisi}
anlam: "{kisa_anlam}"
benzer_isimler: {json.dumps(benzer_isimler, ensure_ascii=False)}
draft: false
---

"""

    # Dosya içeriği
    full_content = frontmatter + content

    # Dosya yolu
    file_path = CONTENT_DIR / f"{slug}.md"

    # Dosyayı yaz
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(full_content)

    return file_path


def load_progress():
    """İlerleme dosyasını yükle"""
    if PROGRESS_FILE.exists():
        with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "completed_slugs": [],
        "failed_slugs": [],
        "stats": {
            "total_generated": 0,
            "total_failed": 0,
            "last_run": None
        }
    }


def save_progress(progress):
    """İlerleme dosyasını kaydet"""
    progress["stats"]["last_run"] = datetime.now().isoformat()
    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        json.dump(progress, f, ensure_ascii=False, indent=2)


async def generate_batch(names, batch_size=10):
    """Bir grup isim için içerik üret"""
    progress = load_progress()
    completed = set(progress["completed_slugs"])

    # Henüz oluşturulmamış isimleri filtrele
    pending_names = [n for n in names if slugify(n["isim"]) not in completed]

    if not pending_names:
        print("Tüm isimler zaten oluşturulmuş!")
        return

    print(f"\n{'='*50}")
    print(f"Toplam isim: {len(names)}")
    print(f"Tamamlanan: {len(completed)}")
    print(f"Bekleyen: {len(pending_names)}")
    print(f"{'='*50}\n")

    # Content dizinini oluştur
    CONTENT_DIR.mkdir(parents=True, exist_ok=True)

    async with aiohttp.ClientSession() as session:
        for i, name_data in enumerate(tqdm(pending_names[:batch_size], desc="İçerik üretiliyor")):
            isim = name_data["isim"]
            slug = slugify(isim)

            try:
                # İçerik üret
                content = await generate_content_with_groq(session, name_data)

                if content:
                    # Markdown dosyası oluştur
                    file_path = create_markdown_file(name_data, content)
                    progress["completed_slugs"].append(slug)
                    progress["stats"]["total_generated"] += 1
                    print(f"[OK] {isim} olusturuldu: {file_path.name}")
                else:
                    progress["failed_slugs"].append(slug)
                    progress["stats"]["total_failed"] += 1
                    print(f"[HATA] {isim} basarisiz!")

                # İlerlemeyi kaydet
                save_progress(progress)

                # Rate limiting
                await asyncio.sleep(DELAY_BETWEEN_REQUESTS)

            except Exception as e:
                progress["failed_slugs"].append(slug)
                progress["stats"]["total_failed"] += 1
                print(f"[HATA] {isim} hata: {e}")
                save_progress(progress)

    print(f"\n{'='*50}")
    print(f"Tamamlanan: {progress['stats']['total_generated']}")
    print(f"Başarısız: {progress['stats']['total_failed']}")
    print(f"{'='*50}")


async def main():
    """Ana fonksiyon"""
    import argparse

    parser = argparse.ArgumentParser(description="İsim içeriği üret")
    parser.add_argument("--count", type=int, default=100, help="Üretilecek isim sayısı")
    parser.add_argument("--gender", choices=["erkek", "kiz", "all"], default="all", help="Cinsiyet filtresi")
    parser.add_argument("--reset", action="store_true", help="İlerlemeyi sıfırla")
    args = parser.parse_args()

    # API key kontrolü
    if not GROQ_API_KEY:
        print("HATA: GROQ_API_KEY bulunamadı!")
        print("Lütfen .env dosyasını kontrol edin.")
        return

    # İlerlemeyi sıfırla
    if args.reset:
        if PROGRESS_FILE.exists():
            PROGRESS_FILE.unlink()
        print("İlerleme sıfırlandı.")

    # İsimleri al
    if args.gender == "all":
        names = get_all_names()
    else:
        names = get_names_by_gender(args.gender)

    print(f"Toplam {len(names)} isim bulundu.")
    print(f"İlk {args.count} isim için içerik üretilecek.")

    # İçerik üret
    await generate_batch(names, batch_size=args.count)


if __name__ == "__main__":
    asyncio.run(main())
