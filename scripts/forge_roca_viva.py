
import sys
import os
from pathlib import Path
from scripts.comic_engine import MusiChrisComicEngine

def forge_roca_viva():
    print("🔥 INICIANDO FORJA MINISTERIAL: ROCA VIVA")
    engine = MusiChrisComicEngine()
    
    # 1. Narrativa Bíblica Pura (Salmo 78:15-20)
    story_panels = [
        {
            "text": "El desierto era un valle de sed, donde la esperanza parecía secarse.",
            "prompt": "Cinematic wide shot of a vast, scorching biblical desert, heat haze, golden hour, comic art style, 9:16 vertical"
        },
        {
            "text": "Pero allí se alzaba la peña, firme bajo el cielo abrasador.",
            "prompt": "A massive, ancient monolithic rock in the middle of the desert, sharp edges, divine light from above, epic composition, 9:16 vertical"
        },
        {
            "text": "Él hendió las peñas en la soledad y les dio a beber en abundancia.",
            "prompt": "A divine hand or a staff touching a massive rock, magical energy, cracks forming on the stone surface, biblical epic style, 9:16 vertical"
        },
        {
            "text": "De la piedra sacó corrientes, e hizo descender aguas como ríos.",
            "prompt": "Crystal clear water bursting forth from a cracked rock in the desert, powerful splash, sunlight reflecting on water, 9:16 vertical"
        },
        {
            "text": "Los torrentes inundaron la tierra seca, trayendo vida donde no la había.",
            "prompt": "Rivers of water flowing through desert sand dunes, small green plants starting to sprout, beautiful landscape, 9:16 vertical"
        },
        {
            "text": "El pueblo bebió del gran abismo, saciando su alma con Su bondad.",
            "prompt": "Ancient Hebrew people kneeling and drinking water from a clear stream with joy and wonder, soft cinematic lighting, 9:16 vertical"
        },
        {
            "text": "Su poder es la fuente que nunca se agota en medio de nuestra prueba.",
            "prompt": "A majestic waterfall coming from a mountain in the desert, rainbows in the mist, divine atmosphere, 9:16 vertical"
        },
        {
            "text": "Cristo es nuestra Roca Viva, la base eterna de nuestra salvación.",
            "prompt": "Symbolic image of a cross glowing with light on top of a mountain, ethereal background, spiritual victory, comic art masterpiece, 9:16 vertical"
        }
    ]
    
    title = "ROCA VIVA"
    audio_url = "https://res.cloudinary.com/dveqs8f3n/video/upload/v1777587831/Roca_Viva_fkdsaa.mp3"
    teaching = "Confía en Su provisión: Él hace brotar agua de la roca y vida en tu desierto."
    
    # 2. Generar y Procesar Paneles
    panel_vids = []
    for i, p in enumerate(story_panels):
        # Reutilizar imagen si ya existe (Evitar gasto de IA en ajustes de render)
        img_path = engine.temp_dir / f"roca_viva_panel_{i}.jpg"
        if img_path.exists():
            print(f"♻️ Reutilizando imagen de Panel {i+1}...")
            with open(img_path, "rb") as f: img_data = f.read()
        else:
            print(f"🎨 Panel {i+1}/8: Generando nueva imagen...")
            img_data = engine.generate_image_hf(p['prompt'])
        
        if not img_data:
            print(f"⚠️ Error en panel {i}, reintentando...")
            continue
            
        # Horneado de texto (Inferior-Central según nuevos estándares)
        baked_data = engine.add_text_to_image(img_data, p['text'])
        img_path = engine.temp_dir / f"roca_viva_panel_{i}.jpg"
        with open(img_path, "wb") as f: f.write(baked_data)
        
        vid_path = engine.assets_dir / f"roca_viva_panel_{i}.mp4"
        
        # Efecto Zoom-In (Hacia adentro)
        zoom_filter = (
            "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,"
            "zoompan=z='zoom+0.0015':d=180:s=1080x1920:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
        )
        
        import subprocess
        subprocess.run([
            "ffmpeg", "-y", "-loop", "1", "-i", str(img_path),
            "-vf", f"{zoom_filter},fade=t=in:st=0:d=0.5",
            "-t", "6", "-c:v", "libx264", "-pix_fmt", "yuv420p", str(vid_path)
        ], check=True)
        panel_vids.append(str(vid_path))
    
    # 3. Renderizar Video Final
    output_filename = "ROCA_VIVA_FINAL.mp4"
    story_data = {
        'teaching': teaching
    }
    
    print("🎬 Iniciando ensamblaje final: Intro + Paneles + Enseñanza + Outro")
    final_path = engine.render_motion_comic(panel_vids, title, audio_url, output_filename, story_data)
    
    print(f"✨ ¡GLORIA A DIOS! Video completado en: {final_path}")

if __name__ == "__main__":
    forge_roca_viva()
