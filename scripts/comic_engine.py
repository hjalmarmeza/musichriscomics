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

STYLE_PROMPT = ", japanese manga style, high contrast, dramatic shadows, cinematic composition, bold lines, 4k"

class MusiChrisComicEngine:
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.assets_dir = self.base_dir / "assets/panels"
        self.renders_dir = self.base_dir / "renders"
        self.temp_dir = self.base_dir / "temp"
        self.catalog_path = self.base_dir / "data/catalog.json"
        
        for d in [self.assets_dir, self.renders_dir, self.temp_dir]:
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
        img = Image.open(BytesIO(image_bytes)).convert("RGB")
        img = img.resize((1280, 720), Image.Resampling.LANCZOS)
        draw = ImageDraw.Draw(img)
        rect_height = 100
        draw.rectangle([0, 720 - rect_height, 1280, 720], fill=(0, 0, 0))
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 35)
        except:
            font = ImageFont.load_default()
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (1280 - text_width) / 2
        y = 720 - (rect_height / 2) - (text_height / 2)
        draw.text((x, y), text, font=font, fill=(255, 255, 255))
        output = BytesIO()
        img.save(output, format="PNG")
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

    def render_motion_comic(self, panel_paths, audio_url, output_name="comic_master.mp4"):
        output_path = self.renders_dir / output_name
        audio_path = self.temp_dir / "bg_music.mp3"
        r = requests.get(audio_url)
        with open(audio_path, "wb") as f:
            f.write(r.content)
        concat_file = self.temp_dir / "panels.txt"
        with open(concat_file, "w") as f:
            for p in panel_paths:
                f.write(f"file '{Path(p).absolute()}'\nduration 6\n")
            f.write(f"file '{Path(panel_paths[-1]).absolute()}'\n")

        # Comando como LISTA para evitar problemas de escape en shell
        cmd = [
            "ffmpeg", "-y",
            "-f", "concat", "-safe", "0", "-i", str(concat_file),
            "-i", str(audio_path),
            "-vf", "zoompan=z='min(zoom+0.001,1.5)':d=150:s=1280x720,format=yuv420p",
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-shortest",
            "-c:a", "aac", "-b:a", "192k",
            str(output_path)
        ]
        
        print("🎬 Iniciando Renderizado...")
        subprocess.run(cmd, check=True)
        print(f"✅ ¡Video Finalizado! {output_path}")

if __name__ == "__main__":
    engine = MusiChrisComicEngine()
    historia = [
        {"prompt": "Simon of Cyrene walking tired, carrying a basket", "text": "SIMON CAMINABA CANSADO HACIA JERUSALEN..."},
        {"prompt": "Roman soldiers stopping a tall african man", "text": "TU! DETENTE! - GRITO EL SOLDADO ROMANO."},
        {"prompt": "Simon forced to carry the cross, sweat and blood", "text": "EL PESO DE LA MADERA ERA INSOPORTABLE..."},
        {"prompt": "Jesus looking at Simon with love and peace", "text": "PERO EN LOS OJOS DE JESUS, ENCONTRO UNA PAZ EXTRANA."},
        {"prompt": "Simon carrying the cross alongside Jesus up a hill", "text": "Y ASI, EL EXTRAÑO SE CONVIRTIO EN SU COMPANERO."},
        {"prompt": "A transformed Simon looking at the empty tomb later", "text": "AQUEL DIA, SIMON NO SOLO CARGO UNA CRUZ... CARGO LA ESPERANZA."}
    ]
    bg_song = engine.get_random_bg_music()
    p_paths = [str(engine.assets_dir / f"panel_{0:02d}.png".format(i)) for i in range(len(historia))]
    # Solo regenerar si no existen
    actual_p_paths = [str(engine.assets_dir / f"panel_{i:02d}.png") for i in range(len(historia))]
    if not all(os.path.exists(p) for p in actual_p_paths):
        actual_p_paths = engine.forge_panels(historia)
    
    if actual_p_paths:
        engine.render_motion_comic(actual_p_paths, bg_song['audio_url'], "Simon_Final_Premium.mp4")
