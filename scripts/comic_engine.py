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

STYLE_PROMPT = ", professional digital comic art, cinematic lighting, sharp detail, 4k, vertical composition"

class MusiChrisComicEngine:
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.assets_dir = self.base_dir / "assets/panels"
        self.renders_dir = self.base_dir / "renders"
        self.temp_dir = self.base_dir / "temp"
        self.video_assets = self.base_dir / "assets/video"
        self.public_dir = self.base_dir / "public"
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

    def generate_title_card(self, title):
        """Genera una pantalla inicial premium"""
        canvas = Image.new("RGB", (1080, 1920), (10, 14, 20))
        draw = ImageDraw.Draw(canvas)
        
        # Cargar logo transparente
        try:
            logo = Image.open(self.public_dir / "logo_v4.png").convert("RGBA")
            logo = logo.resize((600, int(600 * logo.height / logo.width)), Image.Resampling.LANCZOS)
            canvas.paste(logo, ((1080 - 600) // 2, 400), logo)
        except: pass

        try:
            font_title = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 80)
            font_sub = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 40)
        except:
            font_title = font_sub = ImageFont.load_default()

        # Texto del título
        draw.text((540, 1000), "MUSICHRIS COMIC", font=font_sub, fill=(255, 215, 0), anchor="mm")
        draw.text((540, 1150), title.upper(), font=font_title, fill=(255, 255, 255), anchor="mm")
        draw.text((540, 1300), "PRESENTA", font=font_sub, fill=(255, 215, 0), anchor="mm")
        
        path = self.assets_dir / "title_card.png"
        canvas.save(path)
        return str(path)

    def add_text_to_image(self, image_bytes, text):
        img = Image.open(BytesIO(image_bytes)).convert("RGB")
        w, h = img.size
        new_w = 1080
        new_h = int(h * (new_w / w))
        img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        
        canvas = Image.new("RGB", (1080, 1920), (10, 14, 20))
        offset = (0, (1920 - new_h) // 2)
        canvas.paste(img, offset)
        
        draw = ImageDraw.Draw(canvas)
        padding, rect_margin = 40, 20
        
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 45)
        except:
            font = ImageFont.load_default()
            
        lines = []
        words = text.split()
        current_line = ""
        for word in words:
            if len(current_line + word) < 30:
                current_line += word + " "
            else:
                lines.append(current_line.strip()); current_line = word + " "
        lines.append(current_line.strip())
        
        max_line_width = 0
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            max_line_width = max(max_line_width, bbox[2] - bbox[0])
        
        box_w, box_h = max_line_width + (padding * 2), (len(lines) * 60) + (padding)
        
        overlay = Image.new('RGBA', (1080, 1920), (0,0,0,0))
        overlay_draw = ImageDraw.Draw(overlay)
        overlay_draw.rectangle([rect_margin, rect_margin, rect_margin + box_w, rect_margin + box_h], fill=(0, 0, 0, 180))
        canvas.paste(overlay, (0,0), overlay)
        
        y_text = rect_margin + 30
        for line in lines:
            draw.text((rect_margin + padding, y_text), line, font=font, fill=(255, 215, 0))
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
                print(f"⚠️ Intento {i+1} falló: {e}"); time.sleep(10)
        return None

    def forge_panels(self, story_data):
        panel_paths = []
        for i, entry in enumerate(story_data):
            print(f"🎨 Panel {i+1}/{len(story_data)}...")
            image_data = self.query_hf(entry['prompt'])
            if image_data:
                final_image_data = self.add_text_to_image(image_data, entry['text'])
                path = self.assets_dir / f"panel_{i:02d}.png"
                with open(path, "wb") as f: f.write(final_image_data)
                panel_paths.append(str(path))
        return panel_paths

    def render_motion_comic(self, panel_paths, title, audio_url, output_name="comic_final.mp4"):
        output_path = self.renders_dir / output_name
        audio_path = self.temp_dir / "bg_music.mp3"
        outro_path = self.video_assets / "outro.mp4"
        
        title_path = self.generate_title_card(title)
        full_sequence = [title_path] + panel_paths

        r = requests.get(audio_url)
        with open(audio_path, "wb") as f: f.write(r.content)

        concat_file = self.temp_dir / "panels.txt"
        with open(concat_file, "w") as f:
            for p in full_sequence:
                f.write(f"file '{Path(p).absolute()}'\nduration 5\n")
            f.write(f"file '{Path(full_sequence[-1]).absolute()}'\n")

        temp_comic = self.temp_dir / "temp_comic.mp4"
        subprocess.run([
            "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_file),
            "-vf", "zoompan=z='min(zoom+0.001,1.5)':d=125:s=1080x1920,format=yuv420p",
            "-c:v", "libx264", "-pix_fmt", "yuv420p", str(temp_comic)
        ], check=True)

        comic_duration = len(full_sequence) * 5
        if outro_path.exists():
            # Filtro para Cierre Circular sin fondo negro
            final_cmd = [
                "ffmpeg", "-y",
                "-i", str(temp_comic),
                "-i", str(audio_path),
                "-i", str(outro_path),
                "-filter_complex", 
                f"[0:v]fade=t=out:st={comic_duration-1}:d=1[v0]; "
                f"[2:v]setpts=1.25*PTS,scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920, "
                f"geq=r='r(X,Y)':g='g(X,Y)':b='b(X,Y)':a='if(lt(hypot(X-W/2,Y-H/2),H/2.2),255,0)', "
                f"fade=t=in:st=0:d=1[vout]; "
                f"[v0][vout]concat=n=2:v=1:a=0[v]; "
                f"[1:a]afade=t=out:st={comic_duration+9}:d=1[a]",
                "-map", "[v]", "-map", "[a]",
                "-c:v", "libx264", "-shortest", str(output_path)
            ]
        else:
            final_cmd = ["ffmpeg", "-y", "-i", str(temp_comic), "-i", str(audio_path), "-c:v", "libx264", "-shortest", str(output_path)]
            
        subprocess.run(final_cmd, check=True)
        print(f"✅ ¡Video Finalizado! {output_path}")

if __name__ == "__main__":
    engine = MusiChrisComicEngine()
    # Demo local no necesaria, se usa vía Workflow
