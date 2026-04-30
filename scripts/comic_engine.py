import os
import requests
import json
import time
import subprocess
import random
from pathlib import Path
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

# Configuración Maestra
load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN")
MODEL_ID = "black-forest-labs/FLUX.1-schnell" 
client = InferenceClient(api_key=HF_TOKEN)

# Estilo Comic Premium: Modern Digital Art (No bubbles)
STYLE_PROMPT = ", professional digital comic art, cinematic lighting, sharp detail, 4k, vertical composition"

class MusiChrisComicEngine:
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.assets_dir = self.base_dir / "assets/panels"
        self.renders_dir = self.base_dir / "renders"
        self.temp_dir = self.base_dir / "temp"
        self.video_assets = self.base_dir / "assets/video"
        self.catalog_path = self.base_dir / "data/catalog.json"
        
        for d in [self.assets_dir, self.renders_dir, self.temp_dir, self.video_assets]:
            d.mkdir(parents=True, exist_ok=True)

    def get_random_bg_music(self):
        try:
            with open(self.catalog_path, 'r') as f:
                catalog = json.load(f)
            generic_songs = [s for s in catalog if "Descanso" in s.get("moments", [])]
            return random.choice(generic_songs if generic_songs else catalog)
        except Exception:
            return {"audio_url": "https://res.cloudinary.com/dveqs8f3n/video/upload/v1765360897/wi5649ngot0kzi9m7mwu.mp3"}

    def add_text_to_image(self, image_bytes, text):
        """Prepara la imagen para formato vertical 9:16 con texto quemado"""
        img = Image.open(BytesIO(image_bytes)).convert("RGB")
        # Redimensionar para llenar el ancho de 1080
        w, h = img.size
        new_w = 1080
        new_h = int(h * (new_w / w))
        img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        
        # Crear lienzo vertical 1080x1920
        canvas = Image.new("RGB", (1080, 1920), (10, 14, 20))
        # Centrar la imagen en el lienzo
        offset = (0, (1920 - new_h) // 2)
        canvas.paste(img, offset)
        
        draw = ImageDraw.Draw(canvas)
        
        # Caja de texto premium al fondo
        rect_height = 250
        draw.rectangle([0, 1920 - rect_height, 1080, 1920], fill=(0, 86, 179)) # Azul MusiChris
        
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 45)
        except:
            font = ImageFont.load_default()
            
        # Wrap text manual para que no se salga
        lines = []
        words = text.split()
        current_line = ""
        for word in words:
            if len(current_line + word) < 30:
                current_line += word + " "
            else:
                lines.append(current_line.strip())
                current_line = word + " "
        lines.append(current_line.strip())
        
        y_text = 1920 - rect_height + 40
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            line_w = bbox[2] - bbox[0]
            draw.text(((1080 - line_w) / 2, y_text), line, font=font, fill=(255, 215, 0)) # Oro
            y_text += 60
            
        output = BytesIO()
        canvas.save(output, format="PNG")
        return output.getvalue()

    def query_hf(self, prompt, retries=3):
        for i in range(retries):
            try:
                image = client.text_to_image(prompt + STYLE_PROMPT, model=MODEL_ID)
                img_byte_arr = BytesIO()
                image.save(img_byte_arr, format='PNG')
                return img_byte_arr.getvalue()
            except Exception as e:
                print(f"⚠️ Intento {i+1} falló: {e}")
                time.sleep(10)
        return None

    def forge_panels(self, story_data):
        panel_paths = []
        for i, entry in enumerate(story_data):
            print(f"🎨 Panel {i+1}/{len(story_data)}: {entry['prompt'][:40]}...")
            image_data = self.query_hf(entry['prompt'])
            if image_data:
                final_image_data = self.add_text_to_image(image_data, entry['text'])
                path = self.assets_dir / f"panel_{i:02d}.png"
                with open(path, "wb") as f:
                    f.write(final_image_data)
                panel_paths.append(str(path))
        return panel_paths

    def render_motion_comic(self, panel_paths, audio_url, output_name="comic_final.mp4"):
        output_path = self.renders_dir / output_name
        audio_path = self.temp_dir / "bg_music.mp3"
        outro_path = self.video_assets / "outro.mp4"
        
        # Descargar música
        r = requests.get(audio_url)
        with open(audio_path, "wb") as f:
            f.write(r.content)

        # Crear archivo de lista
        concat_file = self.temp_dir / "panels.txt"
        with open(concat_file, "w") as f:
            for p in panel_paths:
                f.write(f"file '{Path(p).absolute()}'\nduration 5\n")
            f.write(f"file '{Path(panel_paths[-1]).absolute()}'\n")

        # Paso 1: Renderizar Comic Base con Zoom
        temp_comic = self.temp_dir / "temp_comic.mp4"
        cmd_zoom = [
            "ffmpeg", "-y",
            "-f", "concat", "-safe", "0", "-i", str(concat_file),
            "-vf", "zoompan=z='min(zoom+0.001,1.5)':d=125:s=1080x1920,format=yuv420p",
            "-c:v", "libx264", "-pix_fmt", "yuv420p",
            str(temp_comic)
        ]
        subprocess.run(cmd_zoom, check=True)

        # Paso 2: Mezclar con Audio y añadir Outro
        # Si el outro existe, lo concatenamos
        if outro_path.exists():
            final_cmd = [
                "ffmpeg", "-y",
                "-i", str(temp_comic),
                "-i", str(audio_path),
                "-i", str(outro_path),
                "-filter_complex", 
                "[0:v]fade=t=out:st=24:d=1[v0]; [2:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fade=t=in:st=0:d=1[vout]; [v0][vout]concat=n=2:v=1:a=0[v]; [1:a]afade=t=out:st=24:d=1[a]",
                "-map", "[v]", "-map", "[a]",
                "-c:v", "libx264", "-shortest", str(output_path)
            ]
        else:
            final_cmd = [
                "ffmpeg", "-y", "-i", str(temp_comic), "-i", str(audio_path),
                "-c:v", "libx264", "-shortest", str(output_path)
            ]
            
        subprocess.run(final_cmd, check=True)
        print(f"✅ ¡Video Finalizado con Outro Ministerial! {output_path}")

if __name__ == "__main__":
    # Demo local
    engine = MusiChrisComicEngine()
    demo_story = [
        {"prompt": "Moses parting the red sea, epic cinematic", "text": "EL MAR SE ABRIO ANTE LA FE DE MOISES."},
        {"prompt": "People crossing the sea floor, fish on the sides", "text": "EL PUEBLO CAMINABA POR TIERRA SECA."},
        {"prompt": "Pharaoh army drowning in the distance", "text": "LA JUSTICIA DE DIOS SE MANIFESTO."}
    ]
    bg = engine.get_random_bg_music()
    p = engine.forge_panels(demo_story)
    if p:
        engine.render_motion_comic(p, bg['audio_url'], "Exodo_Demo.mp4")
