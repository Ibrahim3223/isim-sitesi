"""
YAML Tırnak İşaretlerini Düzelt
anlam alanındaki iç tırnak işaretlerini temizler
"""

import os
import re
from pathlib import Path

# Content dizini
CONTENT_DIR = Path(__file__).parent.parent / "hugo-site" / "content" / "isim"

def fix_yaml_quotes(file_path):
    """Dosyadaki YAML tırnak sorunlarını düzelt"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content
        lines = content.split('\n')
        fixed_lines = []
        modified = False

        for line in lines:
            # anlam: "..." satırını kontrol et
            if line.startswith('anlam: "'):
                # İç tırnak işaretlerini temizle
                match = re.match(r'anlam: "(.*)"', line)
                if match:
                    inner_text = match.group(1)
                    # İç tırnak işaretlerini kaldır
                    cleaned_text = inner_text.replace('"', '').replace('"', '').replace('"', '')
                    new_line = f'anlam: "{cleaned_text}"'

                    if new_line != line:
                        fixed_lines.append(new_line)
                        modified = True
                    else:
                        fixed_lines.append(line)
                else:
                    fixed_lines.append(line)
            else:
                fixed_lines.append(line)

        if modified:
            # Dosyayı güncelle
            new_content = '\n'.join(fixed_lines)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            return True

        return False

    except Exception as e:
        print(f"Hata ({file_path.name}): {e}")
        return False

def main():
    """Ana fonksiyon"""
    if not CONTENT_DIR.exists():
        print(f"Hata: {CONTENT_DIR} bulunamadı!")
        return

    md_files = list(CONTENT_DIR.glob("*.md"))
    print(f"Toplam {len(md_files)} dosya bulundu.")

    fixed_count = 0

    for file_path in md_files:
        if fix_yaml_quotes(file_path):
            fixed_count += 1
            print(f"[OK] {file_path.name}")

    print(f"\n{'='*50}")
    print(f"Toplam {fixed_count} dosya düzeltildi.")
    print(f"{'='*50}")

if __name__ == "__main__":
    main()
