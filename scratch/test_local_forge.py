import os
import json
import requests
from pathlib import Path
from dotenv import load_dotenv
from scripts.comic_engine import MusiChrisComicEngine

# Cargar llaves
load_dotenv()

def run_local_test():
    print("🚀 INICIANDO PRUEBA LOCAL DE FORJA MINISTERIAL...")
    
    # 1. Simular Selección de Canción ( ADN: Siete Vueltas - Josué 6)
    # Aunque el usuario dijo que no quería usarla, para el test es un ADN fuerte.
    # Usemos "Soplo de Vida" mejor.
    
    song_title = "Soplo de Vida"
    song_focus = "Restauración espiritual y el poder del Espíritu Santo en el valle de los huesos secos."
    song_verse = "Ezequiel 37:9"
    song_url = "https://res.cloudinary.com/dveqs8f3n/video/upload/v1765360897/wi5649ngot0kzi9m7mwu.mp3"

    print(f"🎵 Canción: {song_title}")
    
    # 2. Obtener Guion Expandido via Cerebras (Mock o Real)
    # Para esta prueba usaremos una estructura ya expandida para ahorrar tiempo de API, 
    # pero el motor la procesará como si fuera real.
    
    story_data = {
        "creative_title": "EL DESPERTAR DEL VALLE",
        "story": [
            {"prompt": "A desolate valley filled with dry white bones, cinematic lighting, epic scale", "text": "Un valle de huesos secos, donde la esperanza parecía haber muerto."},
            {"prompt": "A prophet standing in the middle of the valley, looking at the sky, divine light", "text": "Pero una voz del cielo ordenó profetizar sobre la vida."},
            {"prompt": "A powerful wind rushing through the valley, dust and light swirling", "text": "El Soplo de Vida comenzó a soplar desde los cuatro vientos."},
            {"prompt": "Bones coming together, skeletons rising, spiritual energy", "text": "Lo que estaba muerto comenzó a cobrar forma y fuerza."},
            {"prompt": "A great army of people standing up, alive and strong, sunrise background", "text": "Un ejército inmenso se puso en pie, lleno del Espíritu."},
            {"prompt": "The prophet with hands raised, surrounded by a restored people", "text": "Porque no hay valle que el Espíritu de Dios no pueda restaurar."}
        ],
        "lesson": "No importa cuán secos estén tus sueños, el Soplo de Dios puede darles vida otra vez.",
        "reference": "Ezequiel 37:9"
    }

    engine = MusiChrisComicEngine()
    
    print("🎨 Generando Paneles con IA (Flux)...")
    panel_paths = engine.forge_panels(story_data['story'])
    
    if panel_paths:
        print("🎬 Renderizando Video Final...")
        output_name = "test_local_comic.mp4"
        engine.render_motion_comic(
            panel_paths, 
            story_data['creative_title'], 
            song_url, 
            output_name, 
            story_data
        )
        print(f"✅ ¡PRUEBA COMPLETADA! Video guardado en: renders/{output_name}")
    else:
        print("❌ Error al generar los paneles.")

if __name__ == "__main__":
    run_local_test()
