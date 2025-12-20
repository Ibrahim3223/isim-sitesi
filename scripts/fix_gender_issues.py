"""
Cinsiyet atama hatalarını düzelten script
Gerçek unisex isimleri belirler ve yanlış atamaları düzeltir
"""

# Gerçek unisex isimler (hem erkek hem kız için kullanılabilir)
GERCEK_UNISEX = {
    "Deniz", "Bilge", "Umut", "Özgür", "Evren", "Şafak",
    "Güneş", "Işık", "Ufuk", "Ece", "Anıl", "Cihan",
    "Yıldız", "İlkay", "Burçin"
}

# Sadece ERKEK olması gereken isimler (yanlışlıkla kız listesine eklenmiş)
SADECE_ERKEK = {
    "Berke", "Bora", "Emir", "Cemal", "Semih", "Suat",
    "Taner", "Tayfun", "Tekin", "Vehbi", "Zeynel", "Polat",
    "Nevzat", "Ercan", "Görkem", "Ferman", "Çağrı", "Çınar",
    "Şeref", "Afşin"  # Afşin genelde erkek
}

# Sadece KIZ olması gereken isimler (yanlışlıkla erkek listesine eklenmiş)
SADECE_KIZ = {
    "Beyhan", "Ahsen", "Ebrar", "Günay", "İkbal", "Yüksel"
}

import turkish_names

print("Cinsiyet atamaları kontrol ediliyor...\n")

# Her iki listede de bulunan isimleri bul
erkek_set = set([name[0] for name in turkish_names.ERKEK_ISIMLERI])
kiz_set = set([name[0] for name in turkish_names.KIZ_ISIMLERI])
duplicates = erkek_set.intersection(kiz_set)

print(f"Toplam {len(duplicates)} isim her iki listede de bulundu:\n")

# Kategorilere ayır
gercek_unisex_bulundu = []
sadece_erkek_olacak = []
sadece_kiz_olacak = []
belirsiz = []

for isim in sorted(duplicates):
    if isim in GERCEK_UNISEX:
        gercek_unisex_bulundu.append(isim)
    elif isim in SADECE_ERKEK:
        sadece_erkek_olacak.append(isim)
    elif isim in SADECE_KIZ:
        sadece_kiz_olacak.append(isim)
    else:
        belirsiz.append(isim)

print("[OK] Gercek Unisex Isimler (her iki listede kalacak):")
for isim in gercek_unisex_bulundu:
    print(f"  - {isim}")

print(f"\n[X] Sadece ERKEK listesinde olmali (kiz listesinden silinecek):")
for isim in sadece_erkek_olacak:
    print(f"  - {isim}")

print(f"\n[X] Sadece KIZ listesinde olmali (erkek listesinden silinecek):")
for isim in sadece_kiz_olacak:
    print(f"  - {isim}")

if belirsiz:
    print(f"\n? Belirsiz (manuel kontrol gerekli):")
    for isim in belirsiz:
        print(f"  - {isim}")

print(f"\n\nÖzet:")
print(f"  Unisex: {len(gercek_unisex_bulundu)} isim")
print(f"  Sadece Erkek: {len(sadece_erkek_olacak)} isim")
print(f"  Sadece Kız: {len(sadece_kiz_olacak)} isim")
print(f"  Belirsiz: {len(belirsiz)} isim")
