
import sys
import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from scripts.comic_engine import MusiChrisComicEngine

def generate_static_thumb(title, output_name="thumb_pergamino.jpg"):
    engine = MusiChrisComicEngine()
    
    # Base path for assets
    bg_image_path = engine.public_dir / "master_intro_bg.png"
    if not bg_image_path.exists():
        # Fallback if png doesn't exist, try to extract from video
        print("⚠️ Background image not found, extracting from video...")
        input_video = engine.public_dir / "video_pantalla_inicio.mp4"
        os.system(f"ffmpeg -y -i {input_video} -ss 00:00:01 -vframes 1 {engine.temp_dir}/temp_bg.jpg")
        bg = Image.open(engine.temp_dir / "temp_bg.jpg").convert('RGBA')
    else:
        bg = Image.open(bg_image_path).convert('RGBA')
        
    # Resize to 1080x1920
    bg = bg.resize((1080, 1920), Image.Resampling.LANCZOS)
    
    # Create overlay
    overlay = Image.new('RGBA', (1080, 1920), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    
    font_path = "/System/Library/Fonts/Helvetica.ttc"
    try:
        f_title = ImageFont.truetype(font_path, 80)
        f_brand = ImageFont.truetype(font_path, 50)
    except:
        f_title = f_brand = ImageFont.load_default()

    def draw_premium_text(draw_obj, y, text, font, color, max_width=18):
        words = text.split()
        lines = []
        curr = ""
        for w in words:
            if len(curr + w) < max_width: curr += w + " "
            else:
                lines.append(curr.strip())
                curr = w + " "
        lines.append(curr.strip())
        
        curr_y = y
        for line in lines:
            bbox = draw_obj.textbbox((0, 0), line, font=font)
            w = bbox[2] - bbox[0]
            # Sombra Profunda
            draw_obj.text(((1080-w)/2 + 4, curr_y + 4), line, font=font, fill=(0,0,0,220))
            draw_obj.text(((1080-w)/2, curr_y), line, font=font, fill=color)
            curr_y += 95

    # Dibujar título y marca (igual que en el video)
    draw_premium_text(draw, 650, title.upper(), f_title, (255, 215, 0))
    draw_premium_text(draw, 1050, "MUSICHRIS_STUDIO", f_brand, (255, 255, 255))
    
    # Combinar
    final_img = Image.alpha_composite(bg, overlay)
    output_path = engine.renders_dir / output_name
    final_img.convert('RGB').save(output_path, "JPEG", quality=95)
    print(f"✨ Miniatura generada en: {output_path}")
    return output_path

if __name__ == "__main__":
    title = sys.argv[1] if len(sys.argv) > 1 else "ROCA VIVA"
    generate_static_thumb(title)
