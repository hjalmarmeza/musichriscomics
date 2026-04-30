from PIL import Image

def remove_background(input_path, output_path):
    img = Image.open(input_path).convert("RGBA")
    datas = img.getdata()

    newData = []
    for item in datas:
        # Si el pixel es muy cercano al blanco (ajustable con el umbral)
        if item[0] > 240 and item[1] > 240 and item[2] > 240:
            newData.append((255, 255, 255, 0)) # Hacerlo transparente
        else:
            newData.append(item)

    img.putdata(newData)
    img.save(output_path, "PNG")
    print(f"✅ Fondo eliminado: {output_path}")

if __name__ == "__main__":
    remove_background("public/logo_v4.png", "public/logo_v4_transparent.png")
