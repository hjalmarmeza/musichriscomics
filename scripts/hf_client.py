import requests
import time
import os

# API_URL = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-schnell"
API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"

def query_hf(prompt, api_token):
    headers = {"Authorization": f"Bearer {api_token}"}
    payload = {
        "inputs": prompt,
        "parameters": {
            "negative_prompt": "blurry, low quality, distorted, extra limbs, bad anatomy, text, watermark",
            "num_inference_steps": 30,
            "guidance_scale": 7.5
        }
    }
    
    print(f"🎨 [IA] Generando imagen para: {prompt[:50]}...")
    
    max_retries = 3
    for attempt in range(max_retries):
        response = requests.post(API_URL, headers=headers, json=payload)
        
        if response.status_code == 200:
            return response.content
        elif response.status_code == 503:
            # El modelo se está cargando
            wait_time = response.json().get('estimated_time', 20)
            print(f"⏳ [IA] El modelo se está cargando, esperando {wait_time}s...")
            time.sleep(wait_time)
        else:
            print(f"❌ [IA] Error {response.status_code}: {response.text}")
            time.sleep(5)
            
    return None

def save_image(content, path):
    if content:
        with open(path, "wb") as f:
            f.write(content)
        return True
    return False
