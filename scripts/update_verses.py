import json
import csv
import io
import re
import unicodedata
from pathlib import Path

json_path = "/Users/hjalmarmeza/Downloads/Antigravity/Musichris_Comic/data/catalog.json"
scratchpads = [
    "/Users/hjalmarmeza/.gemini/antigravity/brain/5014038f-4388-4cd5-8ea6-87ed182d2632/browser/scratchpad_kqfpoavd.md",
    "/Users/hjalmarmeza/.gemini/antigravity/brain/5014038f-4388-4cd5-8ea6-87ed182d2632/browser/scratchpad_1yfqdwlp.md",
    "/Users/hjalmarmeza/.gemini/antigravity/brain/5014038f-4388-4cd5-8ea6-87ed182d2632/browser/scratchpad_6i0ap1te.md"
]

def normalize_title(title):
    if not title: return ""
    # Convertir a mayúsculas y quitar espacios extra
    t = title.strip().upper()
    # Quitar acentos
    t = "".join(c for c in unicodedata.normalize('NFD', t)
               if unicodedata.category(c) != 'Mn')
    # Quitar "v2", "v3", etc. al final
    t = re.sub(r'\s+V\d+$', '', t)
    # Quitar artículos al inicio (EL, LA, LOS, LAS, UN, UNA)
    t = re.sub(r'^(EL|LA|LOS|LAS|UN|UNA)\s+', '', t)
    # Quitar signos de puntuación comunes
    t = re.sub(r'[¡!¿?]', '', t)
    return t

def get_csv_data():
    verse_map = {}
    for path in scratchpads:
        if not Path(path).exists(): continue
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extraer bloques CSV
        csv_blocks = re.findall(r'```csv\n(.*?)\n```', content, re.DOTALL)
        if not csv_blocks:
            # Si no hay bloques, intentar buscar la cabecera directamente
            if "Title," in content or "Título," in content:
                csv_blocks = [content]
        
        for block in csv_blocks:
            reader = csv.DictReader(io.StringIO(block.strip()))
            for row in reader:
                # Normalizar nombres de columnas (pueden variar entre sheets)
                title_val = row.get('Title') or row.get('Título') or row.get('TÍTULO')
                verse_val = row.get('Verse') or row.get('Verso') or row.get('Versículo') or row.get('Salmos') or row.get('Verso Bíblico')
                focus_val = row.get('Focus') or row.get('Enfoque') or row.get('MENSAJE/ENFOQUE') or row.get('Temática') or row.get('ENFOQUE TEMÁTICO') or row.get('Temática Central')
                
                if title_val and verse_val:
                    norm_t = normalize_title(title_val)
                    verse_map[norm_t] = {
                        "verse": verse_val.strip(),
                        "focus": focus_val.strip() if focus_val else "Adoración y descanso"
                    }
    return verse_map

def update_verses():
    if not Path(json_path).exists(): return
    with open(json_path, 'r', encoding='utf-8') as f:
        catalog = json.load(f)

    verse_map = get_csv_data()
    updated_count = 0
    
    for item in catalog:
        title = item['title']
        norm_t = normalize_title(title)
        
        if norm_t in verse_map:
            item['context']['verse'] = verse_map[norm_t]['verse']
            item['context']['focus'] = verse_map[norm_t]['focus']
            updated_count += 1
        else:
            # Intento de coincidencia parcial
            matched = False
            for mapped_title in verse_map:
                if mapped_title in norm_t or norm_t in mapped_title:
                    item['context']['verse'] = verse_map[mapped_title]['verse']
                    item['context']['focus'] = verse_map[mapped_title]['focus']
                    updated_count += 1
                    matched = True
                    break
            
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(catalog, f, indent=4, ensure_ascii=False)
        
    print(f"✅ Catálogo actualizado con normalización. Se corrigieron {updated_count} canciones.")
    print(f"⚠️ {len(catalog) - updated_count} canciones siguen sin coincidencia.")

if __name__ == "__main__":
    update_verses()
