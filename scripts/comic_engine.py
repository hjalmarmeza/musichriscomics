import os
import requests
import json
import time
import subprocess
import random
import numpy as np
from pathlib import Path
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageStat

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

    def generate_title_video(self, title):
        """Genera el video inicial animado basado en video_pantalla_inicio.mp4"""
        input_video = self.public_dir / "video_pantalla_inicio.mp4"
        output_video = self.assets_dir / "intro_rendered.mp4"
        font_path = "/System/Library/Fonts/Helvetica.ttc"
        
        # Escapar caracteres para FFmpeg drawtext
        clean_title = title.upper().replace(":", "\\:").replace("'", "")
        
        # Lógica de líneas dinámica: Si es corto, 1 línea. Si es largo, 2.
        words = clean_title.split()
        if len(clean_title) < 20:
            line1, line2 = clean_title, ""
        else:
            mid = len(words) // 2
            line1, line2 = " ".join(words[:mid]), " ".join(words[mid:])
        
        # Filtro: Ralentizar + Fades + Texto
        # Título arriba (y=350), Branding DEBAJO del pergamino (y=1400) para evitar UI YouTube
        # Fade In al inicio (t,0,1) y Fade Out al final (t,7,1)
        filter_str = (
            f"setpts=2.0*PTS,fade=t=in:st=0:d=1,fade=t=out:st=7:d=1,"
            f"drawtext=fontfile='{font_path}':text='{line1}':fontcolor=white:fontsize=95:x=(w-text_w)/2:y=350:shadowcolor=black:shadowx=4:shadowy=4:alpha='if(lt(t,1.5),t-0.5,1)',"
            f"drawtext=fontfile='{font_path}':text='{line2}':fontcolor=white:fontsize=95:x=(w-text_w)/2:y=470:shadowcolor=black:shadowx=4:shadowy=4:alpha='if(lt(t,1.5),t-0.5,1)',"
            f"drawtext=fontfile='{font_path}':text='MUSICHRIS_STUDIO':fontcolor=0xFFD700:fontsize=60:x=(w-text_w)/2:y=1400:alpha='if(lt(t,2.5),t-1.5,1)',"
            f"drawtext=fontfile='{font_path}':text='EL ESTÁNDAR DE LA FORJA':fontcolor=white@0.8:fontsize=38:x=(w-text_w)/2:y=1480:alpha='if(lt(t,3),t-2,1)'"
        )

        cmd = [
            "ffmpeg", "-y", "-i", str(input_video),
            "-vf", filter_str,
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "30",
            str(output_video)
        ]
        
        subprocess.run(cmd, check=True)
        return str(output_video)

    def analyze_best_corner(self, img, box_w, box_h):
        """Analiza la complejidad visual para decidir si poner el texto a la izq o der"""
        margin = 40
        # Cuadrante Izquierdo Superior vs Derecho Superior
        left_area = img.crop((margin, margin, margin + box_w, margin + box_h))
        right_area = img.crop((1080 - margin - box_w, margin, 1080 - margin, margin + box_h))
        
        # Calculamos la desviación estándar (complejidad)
        left_stat = ImageStat.Stat(left_area).stddev
        right_stat = ImageStat.Stat(right_area).stddev
        
        # Sumamos las desviaciones de los canales R, G, B
        left_score = sum(left_stat)
        right_score = sum(right_stat)
        
        # Preferimos la izquierda si la diferencia no es mucha, 
        # pero si la derecha está MUCHO más vacía, vamos a la derecha.
        # YouTube UI suele estar más cargada a la derecha, así que sesgamos a la izquierda.
        if right_score < (left_score * 0.7): # Solo si la derecha es notablemente más simple
            return 1080 - margin - box_w, margin
        return margin, margin

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
        padding = 40
        
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 45)
        except:
            font = ImageFont.load_default()
            
        lines = []
        words = text.split()
        curr = ""
        for w in words:
            if len(curr + w) < 25: curr += w + " "
            else: lines.append(curr.strip()); curr = w + " "
        lines.append(curr.strip())
        
        max_w = 0
        for l in lines:
            bbox = draw.textbbox((0, 0), l, font=font)
            max_w = max(max_w, bbox[2] - bbox[0])
        
        box_w, box_h = max_w + (padding * 2), (len(lines) * 60) + (padding)
        
        # Inteligencia de Posicionamiento
        pos_x, pos_y = self.analyze_best_corner(canvas, box_w, box_h)
        
        overlay = Image.new('RGBA', (1080, 1920), (0,0,0,0))
        overlay_draw = ImageDraw.Draw(overlay)
        overlay_draw.rectangle([pos_x, pos_y, pos_x + box_w, pos_y + box_h], fill=(0, 0, 0, 180))
        canvas.paste(overlay, (0,0), overlay)
        
        y_text = pos_y + 30
        for l in lines:
            draw.text((pos_x + padding, y_text), l, font=font, fill=(255, 215, 0))
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
        panel_vids = []
        for i, entry in enumerate(story_data):
            print(f"🎨 Panel {i+1}/{len(story_data)}...")
            image_data = self.query_hf(entry['prompt'])
            if not image_data: continue
            
            # Guardar imagen base para zoom
            img_path = self.temp_dir / f"raw_panel_{i}.png"
            with open(img_path, "wb") as f: f.write(image_data)
            
            # Preparar imagen para análisis de texto (resize/canvas)
            img = Image.open(BytesIO(image_data)).convert("RGB")
            new_w, new_h = 1080, int(img.height * (1080 / img.width))
            img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
            canvas = Image.new("RGB", (1080, 1920), (10, 14, 20))
            canvas.paste(img, (0, (1920 - new_h) // 2))
            
            # Inteligencia de Posicionamiento
            font_path = "/System/Library/Fonts/Helvetica.ttc"
            font_size = 45
            padding = 40
            
            # Wrap y medida de texto
            words = entry['text'].split()
            lines = []
            curr = ""
            for w in words:
                if len(curr + w) < 25: curr += w + " "
                else: lines.append(curr.strip()); curr = w + " "
            lines.append(curr.strip())
            
            # Medir caja para Cápsula (Pill)
            box_w = 750
            box_h = (len(lines) * 60) + (padding * 1.5)
            pos_x, pos_y = self.analyze_best_corner(canvas, box_w, box_h)
            
            # Crear overlay de la CÁPSULA (Pill Shape) en PIL
            pill_overlay = Image.new('RGBA', (1080, 1920), (0,0,0,0))
            p_draw = ImageDraw.Draw(pill_overlay)
            # Dibujar rectángulo redondeado (Pill)
            p_draw.rounded_rectangle([pos_x, pos_y, pos_x + box_w, pos_y + box_h], radius=box_h//2, fill=(0, 0, 0, 190))
            
            # Guardar overlay temporal
            pill_path = self.temp_dir / f"pill_{i}.png"
            pill_overlay.save(pill_path)
            
            # Generar video individual con Zoom + Cápsula + Texto + Bullet
            vid_path = self.assets_dir / f"panel_vid_{i}.mp4"
            
            drawtext_filters = []
            # Agregar Bullet Dorado
            drawtext_filters.append(
                f"drawtext=fontfile='{font_path}':text='•':fontcolor=0xFFD700:fontsize=60:x={pos_x+padding}:y={pos_y+padding-10}:enable='between(t,0.5,5)'"
            )
            
            for j, line in enumerate(lines):
                line_clean = line.replace("'", "").replace(":", "\\:")
                x_off = pos_x + padding + 40 # Espacio para el bullet
                drawtext_filters.append(
                    f"drawtext=fontfile='{font_path}':text='{line_clean}':fontcolor=white:fontsize={font_size}:x={x_off}:y={pos_y+padding+(j*60)}:enable='between(t,0.5,5)'"
                )
            
            # Filtro: Zoom + Overlay de Cápsula + Textos
            filters = [
                f"zoompan=z='min(zoom+0.001,1.5)':d=150:s=1080x1920", # 150 frames = 5s @ 30fps? No, d=180 para 6s
                f"overlay=enable='between(t,0.5,5)'"
            ]
            
            # Re-ajustar d para 6 segundos @ 25fps o 30fps. Usaremos 30fps -> d=180
            zoom_filter = f"zoompan=z='min(zoom+0.001,1.5)':d=180:s=1080x1920"
            
            subprocess.run([
                "ffmpeg", "-y", "-loop", "1", "-i", str(img_path),
                "-i", str(pill_path),
                "-filter_complex", f"[0:v]{zoom_filter}[z]; [z][1:v]overlay=enable='between(t,0.5,5)'[o]; [o]{','.join(drawtext_filters)}[v]",
                "-map", "[v]", "-t", "6", "-c:v", "libx264", "-pix_fmt", "yuv420p", str(vid_path)
            ], check=True)
            
            panel_vids.append(str(vid_path))
        return panel_vids

        intro_path = self.generate_title_video(title)
        
        r = requests.get(audio_url)
        with open(audio_path, "wb") as f: f.write(r.content)

        # 1. Generar video de los PANELES (imágenes)
        panels_concat_file = self.temp_dir / "panels_only.txt"
        with open(panels_concat_file, "w") as f:
            for p in panel_paths:
                f.write(f"file '{Path(p).absolute()}'\nduration 5\n")
            f.write(f"file '{Path(panel_paths[-1]).absolute()}'\n")

        panels_video = self.temp_dir / "panels_only.mp4"
        subprocess.run([
            "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(panels_concat_file),
            "-vf", "zoompan=z='min(zoom+0.001,1.5)':d=125:s=1080x1920,format=yuv420p",
            "-c:v", "libx264", "-pix_fmt", "yuv420p", str(panels_video)
        ], check=True)

        # 2. Unir INTRO + PANELES con XFADE (0.5s)
        # Usamos filter_complex para encadenar xfades
        # Intro(8s) + P1(5s) + P2(5s)... 
        # Cada xfade reduce 0.5s la duración total
        vids = [intro_path] + panel_paths
        filter_complex = ""
        last_out = "[v0]"
        # Pre-preparar los inputs para el filter_complex
        for i in range(len(vids)):
            filter_complex += f"[{i}:v]settb=AVTB,setpts=PTS-STARTPTS[v{i}];"
        
        offset = 7.5 # Intro termina en 8s, xfade de 0.5s empieza en 7.5s
        for i in range(1, len(vids)):
            next_out = f"cx{i}"
            filter_complex += f"{last_out}[v{i}]xfade=transition=fade:duration=0.5:offset={offset}[{next_out}];"
            last_out = f"[{next_out}]"
            offset += 5.5 # Cada panel dura 6s, con solape de 0.5s, el offset avanza 5.5s
            
        final_input_args = []
        for v in vids:
            final_input_args.extend(["-i", str(v)])
            
        sequence_video = self.temp_dir / "full_sequence.mp4"
        subprocess.run([
            "ffmpeg", "-y"] + final_input_args + [
            "-filter_complex", filter_complex,
            "-map", last_out, "-c:v", "libx264", str(sequence_video)
        ], check=True)

        comic_duration = 8 + (len(panel_paths) * 5.5) # Duración ajustada por solapes (6s - 0.5s solape)
        if outro_path.exists():
            final_cmd = [
                "ffmpeg", "-y",
                "-i", str(sequence_video),
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
            final_cmd = ["ffmpeg", "-y", "-i", str(sequence_video), "-i", str(audio_path), "-c:v", "libx264", "-shortest", str(output_path)]
            
        subprocess.run(final_cmd, check=True)
        print(f"✅ ¡Video Finalizado! {output_path}")

if __name__ == "__main__":
    engine = MusiChrisComicEngine()
