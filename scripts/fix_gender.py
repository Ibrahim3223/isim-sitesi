"""
Cinsiyet hatalarını düzelt
Kız ismi olan isimleri erkek listesinden çıkar
"""

# Kesinlikle kız ismi olanlar - erkek listesinden silinmeli
KESINLIKLE_KIZ = [
    "Alev",
    "Arzu",
    "Bahar",
    "Burçin",
    "Ebrar",
    "Ece",
    "Eslem",
    "Evren",
    "Işık",
    "Nevzat",
    "Polat",
    "Şafak",
    "Şeref",
    "İkbal",
]

# Unisex isimler - hem erkek hem kız listesinde kalabilir
UNISEX = [
    "Ahsen",
    "Anıl",
    "Ayhan",
    "Berke",
    "Beyhan",
    "Bilge",
    "Bora",
    "Cemal",
    "Cihan",
    "Deniz",
    "Emir",
    "Ercan",
    "Ferman",
    "Görkem",
    "Günay",
    "Güneş",
    "Semih",
    "Suat",
    "Taner",
    "Tayfun",
    "Tekin",
    "Ufuk",
    "Umut",
    "Vehbi",
    "Yüksel",
    "Yıldız",
    "Zeynel",
    "Çağrı",
    "Çınar",
    "Özgür",
    "İlkay",
]

print("Kesinlikle kız ismi olanlar (erkek listesinden silinmeli):")
for isim in sorted(KESINLIKLE_KIZ):
    print(f"  - {isim}")

print("\nUnisex isimler (her iki listede de kalabilir):")
for isim in sorted(UNISEX):
    print(f"  - {isim}")

print(f"\nToplam düzeltilecek: {len(KESINLIKLE_KIZ)} isim")
