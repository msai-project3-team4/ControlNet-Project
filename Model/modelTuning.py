from diffusers import StableDiffusionControlNetPipeline, ControlNetModel
from PIL import Image, ImageEnhance
import torch
from torchvision import transforms
import os

# ✅ CUDA 디바이스 확인
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device: {device}")


# ✅ ControlNet 모델 로드 (Scribble 버전)
controlnet = ControlNetModel.from_pretrained(
    "lllyasviel/control_v11p_sd15_scribble",  # 스케치(낙서) 스타일 ControlNet
    torch_dtype=torch.float16
).to(device)
print("ControlNet 모델 로드 완료")

# ✅ Checkpoint 로드
pipe = StableDiffusionControlNetPipeline.from_pretrained(
    "Yntec/samaritan3dCartoon2MVAE",  # Yntec/ResidentCNZCartoon3D
    controlnet=controlnet,
    torch_dtype=torch.float16
).to(device)

pipe.enable_model_cpu_offload()
pipe.enable_vae_slicing()
print("Pipeline 설정 완료")
negative_prompt = (
    "extra limbs, extra fingers, malformed hands, missing fingers, extra hands, "
    "mutated hands, deformed hands, unnatural hand position, bad anatomy, "
    "disfigured body, asymmetrical hands, incorrect fingers, long unnatural fingers, "
    "floating fingers, deformed arms, blurry, distorted, glitch, disproportioned features, "
    "low-quality, low-resolution, grainy, overly saturated, poorly rendered")

# ✅ 이미지 전처리 함수 (ControlNet에 적합한 형태로 변환)
def preprocess_sketch(image_path):
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"이미지를 찾을 수 없습니다: {image_path}")

    print(f"\n=== 이미지 전처리 시작 ===")
    image = Image.open(image_path).convert("RGB")
    original_size = image.size
    print(f"원본 이미지 크기: {original_size}")

    # 이미지 품질 개선
    contrast = ImageEnhance.Contrast(image)
    image = contrast.enhance(1.8)  # 대비 증가

    sharpness = ImageEnhance.Sharpness(image)
    image = sharpness.enhance(1.5)  # 선명도 증가

    # 고품질 리사이징
    image = image.resize((512, 512), Image.Resampling.LANCZOS)
    print(f"변환된 이미지 크기: {image.size}")

    return image  # ControlNet에 사용하기 위해 PIL 이미지 반환


# ✅ 이미지 생성 함수
def generate_image(sketch_path, prompt, output_path, seed=42):
    try:
        print("\n=== 이미지 생성 시작 ===")
        print(f"설정값:")
        print(f"- 입력 이미지: {sketch_path}")
        print(f"- 프롬프트: {prompt}")
        print(f"- 출력 경로: {output_path}")
        print(f"- 시드값: {seed}")

        # 전처리된 컨트롤 이미지 생성
        control_image = preprocess_sketch(sketch_path)
        generator = torch.Generator(device).manual_seed(seed)  # Generator에 시드 적용

        print("\n이미지 생성 중...")
        output = pipe(
            prompt=prompt,
            negative_prompt=negative_prompt,
            image=control_image,
            num_inference_steps=75,  # 품질 향상
            guidance_scale=9.0,  # 프롬프트 영향력 증가
            generator=generator
        ).images[0]

        output.save(output_path)
        print(f"\n✅ 이미지 생성 완료: {output_path}")
        return output

    except Exception as e:
        print(f"\n❌ 에러 발생: {str(e)}")
        return None

# ✅ 실행
sketch_path = "/home/azureuser/Model/Model/aladdin.png"
prompt = "Aladdin making three wishes with the magic lamp in the middle of the marketplace"
output_path = "/home/azureuser/Model/aladdin_result.png"

generated_image = generate_image(sketch_path, prompt, output_path, seed=456)

if generated_image:
    print("\n=== 생성된 이미지 표시 ===")
    from IPython.display import display
    display(generated_image)