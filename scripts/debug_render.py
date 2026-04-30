import subprocess
import os

panels = [
    {"path": "assets/panels/panel_00.png", "text": "SIMON CAMINABA CANSADO HACIA JERUSALEN..."},
    {"path": "assets/panels/panel_01.png", "text": "TU! DETENTE! - GRITO EL SOLDADO ROMANO."},
    {"path": "assets/panels/panel_02.png", "text": "EL PESO DE LA MADERA ERA INSOPORTABLE..."},
    {"path": "assets/panels/panel_03.png", "text": "PERO EN LOS OJOS DE JESUS, ENCONTRO UNA PAZ EXTRANA."},
    {"path": "assets/panels/panel_04.png", "text": "Y ASI, EL EXTRANO SE CONVIRTIO EN SU COMPANERO."},
    {"path": "assets/panels/panel_05.png", "text": "AQUEL DIA, SIMON NO SOLO CARGO UNA CRUZ... CARGO LA ESPERANZA."}
]

filter_complex = ""
inputs = ""
for i, panel in enumerate(panels):
    idx = i
    filter_complex += f"[{idx}:v]scale=1280:720,zoompan=z='min(zoom+0.001,1.5)':d=150:s=1280x720,fade=t=in:st=0:d=1,fade=t=out:st=5:d=1"
    # Simplificamos el drawtext quitando la fuente específica
    clean_text = panel['text'].replace("'", "")
    filter_complex += f",drawtext=text='{clean_text}':fontcolor=white:fontsize=40:box=1:boxcolor=black@0.6:boxborderw=10:x=(w-text_w)/2:y=h-80"
    filter_complex += f"[v{idx}];"
    inputs += f"-i {panel['path']} "

concat_filter = "".join([f"[v{i}]" for i in range(len(panels))])
filter_complex += f"{concat_filter}concat=n={len(panels)}:v=1:a=0[v]"

cmd = f"ffmpeg -y {inputs} -filter_complex \"{filter_complex}\" -map \"[v]\" -c:v libx264 -pix_fmt yuv420p renders/debug_render.mp4"

print("Comando Debug:", cmd)
subprocess.run(cmd, shell=True)
