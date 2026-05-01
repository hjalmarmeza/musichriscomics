import json
import random
import os
import subprocess
from pathlib import Path
from scripts.comic_engine import MusiChrisComicEngine

def run_real_test():
    print("🚀 INICIANDO PRUEBA REAL EN LOCALHOST...")
    engine = MusiChrisComicEngine()
    
    # 1. Cargar Catálogo Real
    catalog_path = Path("data/catalog.json")
    with open(catalog_path, 'r') as f:
        catalog = json.load(f)
    
    # 2. Seleccionar la canción CIELO CLARO para coherencia
    song = next((s for s in catalog if "CIELO CLARO" in s['title'].upper()), catalog[0])
    print(f"🎵 Canción Seleccionada: {song['title']}")
    
    # 3. Historia Coherente (Basada en Cielo Claro)
    story_data = {
        "title": "LA PROMESA TRAS LA TORMENTA",
        "panels": [
            {"text": "Bajo la lluvia más densa, mi fe se mantiene firme.", "prompt": "Young man walking in heavy rain, cinematic lighting, biblical style, 9:16"},
            {"text": "De pronto, la mano de Dios aparta las nubes.", "prompt": "Hand of light opening dark clouds in the sky, divine rays, 9:16"},
            {"text": "Un rayo de sol desciende, bañando la tierra de oro.", "prompt": "Golden sunlight hitting a green field, cinematic, biblical, 9:16"},
            {"text": "El cielo se vuelve claro, como un cristal azul.", "prompt": "Perfectly clear blue sky with a single white dove, 9:16"},
            {"text": "La paz inunda mi alma al ver Su gloria manifiesta.", "prompt": "Man praying under a bright clear sky, peaceful, 9:16"},
            {"text": "¡Gloria a Dios por Su luz eterna!", "prompt": "Bright divine light from the heavens, cinematic explosion of light, 9:16"}
        ],
        "teaching": "Confía en que Dios despejará tus nubes; Su luz siempre prevalece.",
        "reference": "Salmos 30:5"
    }

    # 4. Forjar Paneles (Bypass si ya existen para ahorrar créditos HF)
    existing_panels = [Path(f"assets/panels/panel_{i:02d}.png") for i in range(6)]
    if all(p.exists() for p in existing_panels):
        print("♻️ Reusando paneles existentes para ahorrar créditos HF...")
        # Pero aún debemos procesarlos a video si no existen los vids
        panel_paths = []
        for i, img_p in enumerate(existing_panels):
            vid_p = Path(f"assets/panels/panel_vid_{i}.mp4")
            if not vid_p.exists():
                # Forzar recreación del video desde la imagen
                with open(img_p, "rb") as f: img_data = f.read()
                baked_data = engine.add_text_to_image(img_data, story_data['panels'][i]['text'])
                baked_p = Path(f"temp/baked_panel_{i}.png")
                with open(baked_p, "wb") as f: f.write(baked_data)
                
                zoom_filter = f"zoompan=z='min(zoom+0.001,1.5)':d=180:s=1080x1920"
                subprocess.run([
                    "ffmpeg", "-y", "-loop", "1", "-i", str(baked_p),
                    "-vf", f"{zoom_filter},fade=t=in:st=0:d=0.5",
                    "-t", "6", "-c:v", "libx264", "-pix_fmt", "yuv420p", str(vid_p)
                ], check=True)
            panel_paths.append(str(vid_p))
    else:
        panel_paths = engine.forge_panels(story_data['panels'])
    
    # 5. Renderizar Video Final
    output_name = "test_forja_localhost.mp4"
    engine.render_motion_comic(
        panel_paths, 
        story_data['title'], 
        song['audio_url'], 
        output_name, 
        story_data
    )

    # 6. Mover a Scratch
    final_video = Path("renders") / output_name
    scratch_dest = Path("scratch") / output_name
    Path("scratch").mkdir(exist_ok=True)
    
    if final_video.exists():
        import shutil
        shutil.copy(final_video, scratch_dest)
        print(f"✅ PRUEBA COMPLETADA. Video guardado en: {scratch_dest}")
    else:
        print("❌ Error: El video no se generó correctamente.")

if __name__ == "__main__":
    run_real_test()
