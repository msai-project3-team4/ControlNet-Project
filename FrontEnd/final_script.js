const canvas = document.getElementById("sketchCanvas");
const ctx = canvas.getContext("2d");
let drawing = false;

// ✅ 기본 설정 (선 두께, 색상)
ctx.lineWidth = 3;
ctx.lineCap = "round";
ctx.strokeStyle = "#000";

// ✅ 좌표 가져오기 (마우스 & 터치 지원)
function getCoordinates(event) {
  const rect = canvas.getBoundingClientRect();
  return {
    x: (event.touches ? event.touches[0].clientX : event.clientX) - rect.left,
    y: (event.touches ? event.touches[0].clientY : event.clientY) - rect.top,
  };
}

// ✅ 마우스 이벤트 처리
canvas.addEventListener("mousedown", (event) => {
  drawing = true;
  ctx.beginPath();
  const { x, y } = getCoordinates(event);
  ctx.moveTo(x, y);
});

canvas.addEventListener("mousemove", (event) => {
  if (!drawing) return;
  const { x, y } = getCoordinates(event);
  ctx.lineTo(x, y);
  ctx.stroke();
});

canvas.addEventListener("mouseup", () => {
  drawing = false;
  ctx.closePath();
});

canvas.addEventListener("mouseout", () => {
  drawing = false;
  ctx.closePath();
});

// ✅ 터치 이벤트 처리 (모바일 지원)
canvas.addEventListener("touchstart", (event) => {
  drawing = true;
  ctx.beginPath();
  const { x, y } = getCoordinates(event);
  ctx.moveTo(x, y);
  event.preventDefault();
});

canvas.addEventListener("touchmove", (event) => {
  if (!drawing) return;
  const { x, y } = getCoordinates(event);
  ctx.lineTo(x, y);
  ctx.stroke();
  event.preventDefault();
});

canvas.addEventListener("touchend", () => {
  drawing = false;
  ctx.closePath();
});

// ✅ 지우기 버튼 추가 (클리어 기능)
document.getElementById("clearCanvas").addEventListener("click", () => {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
});

// ✅ "모델 실행" 버튼 클릭 시 Flask로 이미지 업로드
const API_ENDPOINT = "http://20.41.118.218:5000/api/controlnet";  // Flask 서버 주소

document.getElementById("runModel").addEventListener("click", async () => {
  const optionValue = document.getElementById("option").value.trim();
  const resultDiv = document.getElementById("result");
  resultDiv.innerHTML = '<div class="loading">모델 처리 중...</div>';

  // ✅ 캔버스를 PNG 이미지로 변환
  const imageBlob = await new Promise((resolve) =>
    canvas.toBlob(resolve, "image/png")
  );

  const formData = new FormData();
  formData.append("image", imageBlob, "sketch.png");
  if (optionValue) formData.append("prompt", optionValue);

  try {
    const response = await fetch(API_ENDPOINT, { method: "POST", body: formData });

    if (!response.ok) throw new Error("서버 응답 오류");

    const data = await response.json();
    
    if (data.imageUrls && data.imageUrls.length > 0) {
      console.log("📌 변환된 이미지 URL:", data.imageUrls);

      // ✅ 변환된 이미지 URL을 localStorage에 저장
      localStorage.setItem("generatedImages", JSON.stringify(data.imageUrls));

      // ✅ 결과 페이지(result.html)로 이동
      window.location.href = "result.html";
    } else {
      resultDiv.innerHTML = "이미지 처리를 실패했습니다.";
    }
  } catch (err) {
    console.error("오류 발생:", err);
    resultDiv.innerHTML = "오류가 발생했습니다.";
  }
});
