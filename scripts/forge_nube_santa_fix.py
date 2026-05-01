
import sys
import os
from pathlib import Path
from scripts.comic_engine import MusiChrisComicEngine

def forge_nube_santa_correct():
    print("🔥 INICIANDO RE-FORJA MINISTERIAL: NUBE SANTA")
    engine = MusiChrisComicEngine()
    
    # 1. Guion Bíblico Real (Salmo 78:14)
    story_panels = [
        {
            "text": "El desierto era implacable, pero Su fidelidad era mayor.",
            "prompt": "Ancient Hebrew people walking through a vast desert, sand dunes, cinematic lighting, biblical style, 9:16 vertical"
        },
        {
            "text": "De día, una nube santa nos cubría del sol abrasador.",
            "prompt": "A giant, majestic divine cloud providing shade over a biblical camp in the desert, rays of sun filtering through, epic, 9:16 vertical"
        },
        {
            "text": "Era el abrazo de Dios hecho sombra y descanso.",
            "prompt": "Close up of a biblical child looking up at a cool divine cloud with wonder, soft cinematic lighting, 9:16 vertical"
        },
        {
            "text": "Al llegar la noche, el fuego de Su presencia se encendía.",
            "prompt": "A colossal pillar of fire rising from a desert camp into the starry night sky, illuminating the dunes, 9:16 vertical"
        },
        {
            "text": "No había oscuridad que pudiera apagar Su resplandor.",
            "prompt": "Biblical families sitting around tents at night, illuminated by a warm orange glow from a heavenly fire above, peaceful, 9:16 vertical"
        },
        {
            "text": "En la luz o en la sombra, Él es nuestra guía eterna.",
            "prompt": "Silhouette of a prophet with a staff looking at a pillar of fire in the desert, starry night, epic cinematic composition, 9:16 vertical"
        }
    ]
    
    title = "NUBE SANTA"
    audio_url = "https://res.cloudinary.com/dveqs8f3n/video/upload/v1777587823/Nube_Santa_og9kiw.mp3"
    teaching = "Confía en Su guía: Él es tu sombra en el calor y tu luz en la oscuridad."
    
    # 2. Procesar Paneles (Reutilizar imágenes si existen para no gastar cuota)
    panel_vids = []
    for i, p in enumerate(story_panels):
        img_path = engine.temp_dir / f"panel_{i}.jpg"
        
        # Si la imagen ya existe, la leemos. Si no, la generamos.
        if img_path.exists():
            print(f"♻️ Reutilizando imagen de Panel {i+1}...")
            with open(img_path, "rb") as f: img_data = f.read()
        else:
            print(f"🎨 Generando nueva imagen para Panel {i+1}...")
            img_data = engine.generate_image_hf(p['prompt'])
        
        if not img_data: continue
        
        # Volver a hornear el texto (ahora saldrá centrado)
        baked_data = engine.add_text_to_image(img_data, p['text'])
        with open(img_path, "wb") as f: f.write(baked_data)
        
        vid_path = engine.assets_dir / f"panel_{i}.mp4"
        
        # Zoom-In Cinematográfico (Empieza normal y se acerca al centro)
        zoom_filter = (
            "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,"
            "zoompan=z='zoom+0.002':d=180:s=1080x1920:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
        )
        
        import subprocess
        subprocess.run([
            "ffmpeg", "-y", "-loop", "1", "-i", str(img_path),
            "-vf", f"{zoom_filter},fade=t=in:st=0:d=0.5",
            "-t", "6", "-c:v", "libx264", "-pix_fmt", "yuv420p", str(vid_path)
        ], check=True)
        panel_vids.append(str(vid_path))
    
    # 3. Renderizar Video Final
    output_filename = "NUBE_SANTA_PERFECTO.mp4"
    story_data = {
        'teaching': teaching
    }
    
    print("🎬 Iniciando ensamblaje final con narrativa bíblica y Zoom-In...")
    engine.render_motion_comic(panel_vids, title, audio_url, output_filename, story_data)
    
    print(f"✨ ¡GLORIA A DIOS! Video corregido en: renders/{output_filename}")

if __name__ == "__main__":
    forge_nube_santa_correct()
