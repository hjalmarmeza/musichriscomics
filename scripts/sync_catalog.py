import csv
import json
from pathlib import Path

csv_path = "/Users/hjalmarmeza/.gemini/antigravity/brain/5014038f-4388-4cd5-8ea6-87ed182d2632/scratch/sheet2_catalog.csv"
json_path = "/Users/hjalmarmeza/Downloads/Antigravity/Musichris_Comic/data/catalog.json"

def sync_catalog():
    # 1. Cargar catálogo actual
    if Path(json_path).exists():
        with open(json_path, 'r', encoding='utf-8') as f:
            catalog = json.load(f)
    else:
        catalog = []

    # Crear set de URLs existentes para evitar duplicados
    existing_urls = {item['audio_url'] for item in catalog}
    
    new_entries_count = 0
    
    # 2. Leer CSV y procesar
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            audio_url = row.get('URL CANCIÓN', '').strip()
            title = row.get('TÍTULO DE CANCIÓN', '').strip()
            album = row.get('NOMBRE DE ALBUM', '').strip()
            thumbnail = row.get('URL IMAGEN', '').strip()
            
            if not audio_url or audio_url in existing_urls:
                continue
            
            # Crear nueva entrada
            entry = {
                "title": title,
                "audio_url": audio_url,
                "duration_secs": 240,
                "moments": ["Inspiración"],
                "context": {
                    "verse": "Salmos 23:1",
                    "focus": "Adoración y descanso"
                },
                "album": album,
                "thumbnail": thumbnail
            }
            
            catalog.append(entry)
            existing_urls.add(audio_url)
            new_entries_count += 1
            
    # 3. Guardar catálogo actualizado
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(catalog, f, indent=4, ensure_ascii=False)
        
    print(f"✅ Sincronización completada. Se añadieron {new_entries_count} canciones nuevas.")

if __name__ == "__main__":
    sync_catalog()
