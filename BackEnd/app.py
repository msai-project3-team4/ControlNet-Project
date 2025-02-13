import os
import torch
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from diffusers import StableDiffusionControlNetPipeline, ControlNetModel
from PIL import Image, ImageEnhance

# ✅ Flask 설정
app = Flask(__name__, static_url_path="/static")
CORS(app)

# ✅ 폴더 설정
UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "static/output"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# ✅ CUDA 디바이스 확인
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device: {device}")

# ✅ ControlNet 모델 로드
controlnet = ControlNetModel.from_pretrained(
    "lllyasviel/control_v11p_sd15_scribble",  
    torch_dtype=torch.float16
).to(device)

# ✅ Stable Diffusion 모델 로드
pipe = StableDiffusionControlNetPipeline.from_pretrained(
    "Yntec/samaritan3dCartoon2MVAE",
    controlnet=controlnet,
    torch_dtype=torch.float16
).to(device)

pipe.enable_model_cpu_offload()
pipe.enable_vae_slicing()

negative_prompt = (
    "extra limbs, extra fingers, malformed hands, missing fingers, extra hands, "
    "mutated hands, deformed hands, unnatural hand position, bad anatomy, "
    "disfigured body, asymmetrical hands, incorrect fingers, long unnatural fingers, "
    "floating fingers, deformed arms, blurry, distorted, glitch, disproportioned features, "
    "low-quality, low-resolution, grainy, overly saturated, poorly rendered"
)

# ✅ 이미지 전처리
def preprocess_sketch(image_path):
    image = Image.open(image_path).convert("RGB")
    contrast = ImageEnhance.Contrast(image).enhance(1.8)
    sharpness = ImageEnhance.Sharpness(contrast).enhance(1.5)
    return sharpness.resize((512, 512), Image.Resampling.LANCZOS)

# ✅ API 엔드포인트: 3개의 이미지 생성
@app.route('/api/controlnet', methods=['POST'])
def process():
    if 'image' not in request.files:
        return jsonify({"error": "이미지가 업로드되지 않았습니다."}), 400

    file = request.files['image']
    prompt = request.form.get("prompt", "A digital sketch converted by ControlNet")
    seed = int(request.form.get("seed", 42))

    # ✅ 업로드된 이미지 저장
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    try:
        control_image = preprocess_sketch(file_path)
        generator = torch.Generator(device).manual_seed(seed)

        # ✅ 3개의 이미지 생성
        output_paths = []
        for i in range(3):
            output = pipe(
                prompt=prompt,
                negative_prompt=negative_prompt,
                image=control_image,
                num_inference_steps=75,
                guidance_scale=9.0,
                generator=generator
            ).images[0]

            output_filename = f"output_{i+1}_{file.filename}"
            output_path = os.path.join(OUTPUT_FOLDER, output_filename)
            output.save(output_path)
            output_paths.append(f"/static/output/{output_filename}")

        return jsonify({"imageUrls": output_paths})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
