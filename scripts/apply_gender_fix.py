"""
Cinsiyet atama hatalarını düzelten script
Yanlış listedeki isimleri siler
"""

# Erkek listesinden silinecek (sadece kız)
ERKEK_LISTESINDEN_SIL = {'Ahsen', 'Beyhan', 'Ebrar', 'Günay', 'Yüksel', 'İkbal'}

# Kız listesinden silinecek (sadece erkek)
KIZ_LISTESINDEN_SIL = {
    'Berke', 'Bora', 'Cemal', 'Emir', 'Ercan', 'Ferman', 'Görkem',
    'Nevzat', 'Polat', 'Semih', 'Suat', 'Taner', 'Tayfun', 'Tekin',
    'Vehbi', 'Zeynel', 'Çağrı', 'Çınar', 'Şeref'
}

print("turkish_names.py dosyası düzeltiliyor...")

with open('turkish_names.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
deleted_count = 0
current_list = None

for line in lines:
    skip_line = False

    # Hangi listede olduğumuzu takip et
    if 'ERKEK_ISIMLERI = [' in line:
        current_list = 'ERKEK'
    elif 'KIZ_ISIMLERI = [' in line:
        current_list = 'KIZ'
    elif line.strip().startswith('def ') or line.strip().startswith('# =='):
        current_list = None

    # Erkek listesindeyken silinecekleri kontrol et
    if current_list == 'ERKEK':
        for isim in ERKEK_LISTESINDEN_SIL:
            if f'("{isim}"' in line or f"('{isim}'" in line:
                print(f"  [ERKEK listesinden silindi]: {isim}")
                skip_line = True
                deleted_count += 1
                break

    # Kız listesindeyken silinecekleri kontrol et
    elif current_list == 'KIZ':
        for isim in KIZ_LISTESINDEN_SIL:
            if f'("{isim}"' in line or f"('{isim}'" in line:
                print(f"  [KIZ listesinden silindi]: {isim}")
                skip_line = True
                deleted_count += 1
                break

    if not skip_line:
        new_lines.append(line)

# Dosyayı yaz
with open('turkish_names.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print(f"\n✓ Toplam {deleted_count} yanlış atama düzeltildi.")
print("✓ turkish_names.py dosyası güncellendi.")
