// API 엔드포인트 URL (백엔드 Part에서 전달한 URL로 업데이트)
const API_ENDPOINT = "/api/controlnet";

// 스케치 기능 추가
const canvas = document.getElementById("sketchCanvas");
const ctx = canvas.getContext("2d");
let drawing = false;

canvas.addEventListener("mousedown", () => (drawing = true));
canvas.addEventListener("mouseup", () => (drawing = false));
canvas.addEventListener("mouseout", () => (drawing = false));
canvas.addEventListener("mousemove", (event) => {
  if (!drawing) return;
  const rect = canvas.getBoundingClientRect();
  const x = event.clientX - rect.left;
  const y = event.clientY - rect.top;
  ctx.fillStyle = "#000";
  ctx.fillRect(x, y, 2, 2);
});

// 모델 실행 버튼 이벤트
document.getElementById("runModel").addEventListener("click", async () => {
  const optionValue = document.getElementById("option").value.trim();
  const resultDiv = document.getElementById("result");

  resultDiv.innerHTML = '<div class="loading">모델 처리 중...</div>';

  const imageBlob = await new Promise((resolve) =>
    canvas.toBlob(resolve, "image/png")
  );
  const formData = new FormData();
  formData.append("image", imageBlob, "sketch.png");

  if (optionValue) {
    formData.append("option", optionValue);
  }

  try {
    const response = await fetch(API_ENDPOINT, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      throw new Error("서버 응답에 문제가 있습니다.");
    }

    const data = await response.json();
    if (data.imageUrl) {
      resultDiv.innerHTML = `<img src="${data.imageUrl}" alt="처리된 이미지">`;
    } else {
      resultDiv.innerHTML = "이미지 처리 결과를 불러오지 못했습니다.";
    }
  } catch (err) {
    console.error("오류 발생:", err);
    resultDiv.innerHTML = "오류가 발생했습니다. 콘솔 로그를 확인하세요.";
  }
});
