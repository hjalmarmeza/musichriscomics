import json
import os
from pathlib import Path

def manage_catalog():
    """
    Protocolo de Gestión de Catálogo MusiChris (v1.0)
    Este script permite añadir canciones al catálogo maestro de forma estructurada
    y asegura que todos los metadatos ministeriales estén presentes.
    """
    catalog_path = Path("data/catalog.json")
    
    if not catalog_path.exists():
        print("❌ Error: No se encontró data/catalog.json")
        return

    with open(catalog_path, 'r', encoding='utf-8') as f:
        catalog = json.load(f)

    print(f"📊 Catálogo actual: {len(catalog)} canciones.")
    print("\n--- AGREGAR NUEVA CANCIÓN ---")
    
    title = input("Título de la canción: ").upper()
    album = input("Álbum: ").upper()
    audio_url = input("URL de Cloudinary (mp3): ")
    thumbnail = input("URL de Portada (jpg/png): ")
    
    # Estructura Ministerial
    new_entry = {
        "title": title,
        "audio_url": audio_url,
        "duration_secs": 240, 
        "moments": ["Inspiración"],
        "context": {
            "verse": input("Versículo relacionado: "),
            "focus": input("Enfoque ministerial: ")
        },
        "album": album,
        "thumbnail": thumbnail
    }
    
    catalog.append(new_entry)

    with open(catalog_path, 'w', encoding='utf-8') as f:
        json.dump(catalog, f, indent=4, ensure_ascii=False)

    print(f"✅ Canción '{title}' añadida con éxito al catálogo maestro.")

if __name__ == "__main__":
    manage_catalog()
