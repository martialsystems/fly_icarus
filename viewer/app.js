/* Two-body replay. Not the finding. */
(function () {
  const app = document.getElementById("app");
  const condsEl = document.getElementById("conds");
  const canvas = document.getElementById("arena");
  const ctx = canvas.getContext("2d");
  const p1El = document.getElementById("p1");
  const p1v = document.getElementById("p1v");
  const hud = document.getElementById("hud");

  const LABELS = {
    1: "1 female",
    2: "2 male",
    3: "3 Icarus male",
    4: "4 body only",
    5: "5 odor only",
  };

  let pack = null;
  let cond = 3;
  let i = 0;
  let timer = 0;

  function current() {
    return (pack.conditions || []).find((c) => c.condition === cond);
  }

  function draw(frame, obj) {
    const w = canvas.width;
    const h = canvas.height;
    ctx.fillStyle = "#10141c";
    ctx.fillRect(0, 0, w, h);
    const sx = w / 2;
    const sy = h / 2;
    const scale = 18;
    const ox = sx;
    const oy = sy;
    const x = sx + (frame.sx || 0) * scale;
    const y = sy - (frame.sy || 0) * scale;
    ctx.fillStyle = obj.abdomen === "female" ? "#e8c07a" : "#5a6a7a";
    const r = obj.icarus ? 14 : obj.abdomen === "female" ? 11 : 8;
    ctx.beginPath();
    ctx.arc(ox, oy, r, 0, Math.PI * 2);
    ctx.fill();
    if (obj.wings) {
      ctx.strokeStyle = "#8ab0c8";
      ctx.beginPath();
      ctx.ellipse(ox - 10, oy, 8, 4, -0.4, 0, Math.PI * 2);
      ctx.ellipse(ox + 10, oy, 8, 4, 0.4, 0, Math.PI * 2);
      ctx.stroke();
    }
    ctx.fillStyle = "#c41e3a";
    ctx.beginPath();
    ctx.arc(x, y, 7, 0, Math.PI * 2);
    ctx.fill();
    const hdg = frame.sh || 0;
    ctx.strokeStyle = "#e8e4d9";
    ctx.beginPath();
    ctx.moveTo(x, y);
    ctx.lineTo(x + Math.cos(hdg) * 16, y - Math.sin(hdg) * 16);
    ctx.stroke();
  }

  function show(frame, row) {
    const obj = row.object || {};
    draw(frame, obj);
    const p1 = Number(frame.p1 || 0);
    p1El.value = p1;
    p1v.textContent = p1.toFixed(2);
    hud.textContent =
      "condition " +
      row.condition +
      " " +
      row.name +
      "\nobject wiring_sex=" +
      obj.wiring_sex +
      " wings=" +
      obj.wings +
      " abdomen=" +
      obj.abdomen +
      " odor=" +
      obj.odor +
      " frozen=" +
      obj.frozen +
      "\nP1 " +
      p1.toFixed(3) +
      (frame.song ? " song" : "");
  }

  function tick() {
    const row = current();
    if (!row || !row.frames || !row.frames.length) return;
    const frame = row.frames[i % row.frames.length];
    show(frame, row);
    i += 1;
  }

  function select(c) {
    cond = c;
    i = 0;
    [...condsEl.querySelectorAll("button")].forEach((b) => {
      b.setAttribute("aria-selected", b.dataset.cond === String(c) ? "true" : "false");
    });
    tick();
  }

  function buildButtons(conditions) {
    condsEl.innerHTML = "";
    conditions.forEach((row) => {
      const b = document.createElement("button");
      b.type = "button";
      b.dataset.cond = String(row.condition);
      b.textContent = LABELS[row.condition] || String(row.condition);
      b.setAttribute("aria-selected", row.condition === cond ? "true" : "false");
      b.addEventListener("click", () => select(row.condition));
      condsEl.appendChild(b);
    });
  }

  fetch("frames.json")
    .then((r) => r.json())
    .then((data) => {
      pack = data;
      buildButtons(data.conditions || []);
      app.dataset.ready = "1";
      tick();
      timer = setInterval(tick, 80);
    })
    .catch((err) => {
      hud.textContent = String(err);
      app.dataset.ready = "0";
    });

  window.FlyIcarus = {
    select,
    currentCondition: () => cond,
    ready: () => app.dataset.ready === "1",
  };
})();
