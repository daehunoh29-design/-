const canvas = document.getElementById("roomCanvas");
const ctx = canvas.getContext("2d");
const azimuthValue = document.getElementById("azimuthValue");
const distanceValue = document.getElementById("distanceValue");
const positionReadout = document.getElementById("positionReadout");
const soundSelect = document.getElementById("soundSelect");
const replayButton = document.getElementById("replayButton");
const centerButton = document.getElementById("centerButton");
const statusDot = document.getElementById("statusDot");
const statusText = document.getElementById("statusText");

let config = {
  room: { width: 7, depth: 7 },
  listener: { x: 3.5, y: 3.5, earDistance: 0.18 },
};
let selected = { x: 3.5, y: 4.5, azimuth: 0, distance: 1 };
let lastAudioUrl = null;
let renderToken = 0;

function setStatus(text, mode = "ready") {
  statusText.textContent = text;
  statusDot.className = mode === "ready" ? "" : mode;
}

function resizeCanvas() {
  const rect = canvas.getBoundingClientRect();
  const ratio = window.devicePixelRatio || 1;
  canvas.width = Math.max(1, Math.floor(rect.width * ratio));
  canvas.height = Math.max(1, Math.floor(rect.height * ratio));
  ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
  draw();
}

function layout() {
  const rect = canvas.getBoundingClientRect();
  const pad = Math.min(rect.width, rect.height) * 0.08;
  const roomRatio = config.room.width / config.room.depth;
  let width = rect.width - pad * 2;
  let height = rect.height - pad * 2;
  if (width / height > roomRatio) {
    width = height * roomRatio;
  } else {
    height = width / roomRatio;
  }
  return {
    x: (rect.width - width) / 2,
    y: (rect.height - height) / 2,
    width,
    height,
  };
}

function roomToCanvas(point) {
  const box = layout();
  return {
    x: box.x + (point.x / config.room.width) * box.width,
    y: box.y + ((config.room.depth - point.y) / config.room.depth) * box.height,
  };
}

function canvasToRoom(clientX, clientY) {
  const rect = canvas.getBoundingClientRect();
  const box = layout();
  const x = Math.min(Math.max(clientX - rect.left, box.x), box.x + box.width);
  const y = Math.min(Math.max(clientY - rect.top, box.y), box.y + box.height);
  return {
    x: ((x - box.x) / box.width) * config.room.width,
    y: config.room.depth - ((y - box.y) / box.height) * config.room.depth,
  };
}

function metricsFromRoom(point) {
  const dx = point.x - config.listener.x;
  const dyFront = point.y - config.listener.y;
  const distance = Math.hypot(dx, dyFront);
  const azimuth = (Math.atan2(-dx, dyFront) * 180) / Math.PI;
  return {
    azimuth: Number.isFinite(azimuth) ? azimuth : 0,
    distance: Math.min(Math.max(distance, 0.35), 3.25),
  };
}

function updateSelection(point) {
  const metrics = metricsFromRoom(point);
  selected = { ...point, ...metrics };
  azimuthValue.textContent = `${selected.azimuth.toFixed(1)}°`;
  distanceValue.textContent = `${selected.distance.toFixed(2)}m`;
  positionReadout.textContent = `${selected.azimuth.toFixed(1)}도 · ${selected.distance.toFixed(2)}m`;
  draw();
}

function drawGrid(box) {
  ctx.save();
  ctx.strokeStyle = "rgba(23, 33, 31, 0.12)";
  ctx.lineWidth = 1;
  for (let i = 1; i < config.room.width; i += 1) {
    const x = box.x + (i / config.room.width) * box.width;
    ctx.beginPath();
    ctx.moveTo(x, box.y);
    ctx.lineTo(x, box.y + box.height);
    ctx.stroke();
  }
  for (let i = 1; i < config.room.depth; i += 1) {
    const y = box.y + (i / config.room.depth) * box.height;
    ctx.beginPath();
    ctx.moveTo(box.x, y);
    ctx.lineTo(box.x + box.width, y);
    ctx.stroke();
  }
  ctx.restore();
}

function drawListener(point) {
  ctx.save();
  ctx.translate(point.x, point.y);
  ctx.fillStyle = "#17211f";
  ctx.beginPath();
  ctx.arc(0, 0, 14, 0, Math.PI * 2);
  ctx.fill();
  ctx.fillStyle = "#ffffff";
  ctx.beginPath();
  ctx.arc(-5, -2, 2.2, 0, Math.PI * 2);
  ctx.arc(5, -2, 2.2, 0, Math.PI * 2);
  ctx.fill();
  ctx.strokeStyle = "#16827a";
  ctx.lineWidth = 3;
  ctx.beginPath();
  ctx.moveTo(0, -24);
  ctx.lineTo(0, -42);
  ctx.stroke();
  ctx.restore();
}

function drawSource(point) {
  ctx.save();
  ctx.fillStyle = "#e45d43";
  ctx.strokeStyle = "#ffffff";
  ctx.lineWidth = 4;
  ctx.beginPath();
  ctx.arc(point.x, point.y, 13, 0, Math.PI * 2);
  ctx.fill();
  ctx.stroke();
  ctx.strokeStyle = "rgba(228, 93, 67, 0.28)";
  ctx.lineWidth = 2;
  for (const radius of [26, 40, 54]) {
    ctx.beginPath();
    ctx.arc(point.x, point.y, radius, -0.7, 0.7);
    ctx.stroke();
  }
  ctx.restore();
}

function draw() {
  const rect = canvas.getBoundingClientRect();
  ctx.clearRect(0, 0, rect.width, rect.height);
  const box = layout();

  ctx.save();
  ctx.fillStyle = "#fafdfe";
  ctx.strokeStyle = "#17211f";
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.roundRect(box.x, box.y, box.width, box.height, 8);
  ctx.fill();
  ctx.stroke();
  drawGrid(box);
  ctx.restore();

  const listenerCanvas = roomToCanvas(config.listener);
  const sourceCanvas = roomToCanvas(selected);

  ctx.save();
  ctx.strokeStyle = "#3e6da8";
  ctx.lineWidth = 2.5;
  ctx.setLineDash([8, 8]);
  ctx.beginPath();
  ctx.moveTo(listenerCanvas.x, listenerCanvas.y);
  ctx.lineTo(sourceCanvas.x, sourceCanvas.y);
  ctx.stroke();
  ctx.restore();

  drawListener(listenerCanvas);
  drawSource(sourceCanvas);
}

async function playSelected() {
  const token = ++renderToken;
  setStatus("렌더링", "busy");

  try {
    const response = await fetch("/api/render", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        azimuth: selected.azimuth,
        distance: selected.distance,
        sound: soundSelect.value,
      }),
    });

    if (!response.ok) {
      const body = await response.json().catch(() => ({}));
      throw new Error(body.error || `HTTP ${response.status}`);
    }

    const blob = await response.blob();
    if (token !== renderToken) return;

    if (lastAudioUrl) URL.revokeObjectURL(lastAudioUrl);
    lastAudioUrl = URL.createObjectURL(blob);
    const audio = new Audio(lastAudioUrl);
    await audio.play();
    setStatus("재생 중");
    audio.addEventListener("ended", () => setStatus("준비"), { once: true });
  } catch (error) {
    setStatus(error.message || "오류", "error");
  }
}

canvas.addEventListener("pointerdown", (event) => {
  const point = canvasToRoom(event.clientX, event.clientY);
  updateSelection(point);
  playSelected();
});

replayButton.addEventListener("click", playSelected);

centerButton.addEventListener("click", () => {
  updateSelection({
    x: config.listener.x,
    y: Math.min(config.room.depth - 0.35, config.listener.y + 1),
  });
});

window.addEventListener("resize", resizeCanvas);

async function boot() {
  try {
    const response = await fetch("/api/config");
    if (response.ok) {
      config = await response.json();
    }
  } catch {
    setStatus("설정 오류", "error");
  }
  updateSelection(selected);
  resizeCanvas();
}

boot();
