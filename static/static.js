document.addEventListener("DOMContentLoaded", () => {
  // 1. Interactive Galaxy Starfield & Constellation Canvas
  const canvas = document.getElementById("cosmos-canvas");
  if (canvas) {
    const ctx = canvas.getContext("2d");
    let width = (canvas.width = window.innerWidth);
    let height = (canvas.height = window.innerHeight);
    const pointer = { x: -9999, y: -9999 };

    window.addEventListener("resize", () => {
      width = canvas.width = window.innerWidth;
      height = canvas.height = window.innerHeight;
    });

    window.addEventListener("mousemove", (e) => {
      pointer.x = e.clientX;
      pointer.y = e.clientY;
    });

    const starCount = Math.min(140, Math.floor((width * height) / 11000));
    const palette = ["#ffffff", "#ffe29a", "#c4b5fd", "#67e8f9", "#f9a8d4"];
    const stars = Array.from({ length: starCount }, () => ({
      x: Math.random() * width,
      y: Math.random() * height,
      r: Math.random() * 1.6 + 0.4,
      vx: (Math.random() - 0.5) * 0.12,
      vy: (Math.random() - 0.5) * 0.12,
      phase: Math.random() * Math.PI * 2,
      speed: Math.random() * 0.02 + 0.008,
      color: palette[Math.floor(Math.random() * palette.length)]
    }));

    const renderCosmos = () => {
      ctx.clearRect(0, 0, width, height);

      for (let i = 0; i < stars.length; i++) {
        const s = stars[i];
        s.x += s.vx;
        s.y += s.vy;
        s.phase += s.speed;

        if (s.x < 0) s.x = width;
        if (s.x > width) s.x = 0;
        if (s.y < 0) s.y = height;
        if (s.y > height) s.y = 0;

        const alpha = 0.35 + 0.65 * Math.abs(Math.sin(s.phase));
        ctx.beginPath();
        ctx.arc(s.x, s.y, s.r, 0, Math.PI * 2);
        ctx.fillStyle = s.color;
        ctx.globalAlpha = alpha;
        ctx.fill();

        // Draw subtle constellation threads near cursor
        const dx = s.x - pointer.x;
        const dy = s.y - pointer.y;
        const dist = Math.hypot(dx, dy);
        if (dist < 150) {
          ctx.beginPath();
          ctx.moveTo(s.x, s.y);
          ctx.lineTo(pointer.x, pointer.y);
          ctx.strokeStyle = "#e6b85c";
          ctx.globalAlpha = (1 - dist / 150) * 0.28;
          ctx.lineWidth = 0.8;
          ctx.stroke();
        }
      }

      ctx.globalAlpha = 1;
      requestAnimationFrame(renderCosmos);
    };

    renderCosmos();
  }

  // 2. Orbital Loading Overlay on Form Submit
  const loader = document.getElementById("orbital-loader");
  document.querySelectorAll("form[data-astral-loader]").forEach((form) => {
    form.addEventListener("submit", () => {
      if (loader) {
        loader.classList.add("is-visible");
      }
    });
  });

  // 3. Interactive Coordinate Selection (pick.html)
  const placeOptions = document.querySelectorAll(".place-option");
  const coordDisplay = document.getElementById("coord-readout");
  if (placeOptions.length > 0) {
    placeOptions.forEach((opt) => {
      const radio = opt.querySelector('input[type="radio"]');
      if (!radio) return;

      const selectPlace = () => {
        placeOptions.forEach((el) => el.classList.remove("is-selected"));
        opt.classList.add("is-selected");
        radio.checked = true;

        const form = radio.form;
        if (form) {
          form.lat.value = radio.dataset.lat || "";
          form.lon.value = radio.dataset.lon || "";
        }

        if (coordDisplay) {
          coordDisplay.textContent = `CELESTIAL LOCK: ${radio.dataset.lat}° N/S, ${radio.dataset.lon}° E/W`;
        }
      };

      opt.addEventListener("click", selectPlace);
      radio.addEventListener("change", selectPlace);
    });
  }

  // 4. Inject Astronomical & Zodiac Glyphs (result.html)
  const grahaGlyphs = {
    sun: "\u2609",
    surya: "\u2609",
    moon: "\u263D",
    chandra: "\u263D",
    mars: "\u2642",
    mangala: "\u2642",
    mercury: "\u263F",
    budha: "\u263F",
    jupiter: "\u2643",
    guru: "\u2643",
    venus: "\u2640",
    shukra: "\u2640",
    saturn: "\u2644",
    shani: "\u2644",
    rahu: "\u260A",
    ketu: "\u260B",
    ascendant: "\u2295",
    lagna: "\u2295"
  };

  const signGlyphs = {
    aries: "\u2648",
    mesha: "\u2648",
    taurus: "\u2649",
    vrishabha: "\u2649",
    gemini: "\u264A",
    mithuna: "\u264A",
    cancer: "\u264B",
    karka: "\u264B",
    leo: "\u264C",
    simha: "\u264C",
    virgo: "\u264D",
    kanya: "\u264D",
    libra: "\u264E",
    tula: "\u264E",
    scorpio: "\u264F",
    vrishchika: "\u264F",
    sagittarius: "\u2650",
    dhanu: "\u2650",
    capricorn: "\u2651",
    makara: "\u2651",
    aquarius: "\u2652",
    kumbha: "\u2652",
    pisces: "\u2653",
    meena: "\u2653"
  };

  document.querySelectorAll("[data-graha]").forEach((el) => {
    const key = el.dataset.graha.trim().toLowerCase();
    const glyph = grahaGlyphs[key] || "\u2726";
    const badge = el.querySelector(".glyph-orb");
    if (badge) {
      badge.textContent = glyph;
    }
  });

  document.querySelectorAll("[data-sign]").forEach((el) => {
    const raw = el.dataset.sign.trim().toLowerCase();
    for (const [k, symbol] of Object.entries(signGlyphs)) {
      if (raw.includes(k)) {
        el.textContent = `${symbol} ${el.textContent}`;
        break;
      }
    }
  });

  // 5. Highlight Active Mahadasha Period (result.html)
  const todayIso = new Date().toISOString().slice(0, 10);
  document.querySelectorAll("tr[data-start][data-end]").forEach((row) => {
    const start = row.dataset.start;
    const end = row.dataset.end;
    if (start && end && todayIso >= start && todayIso <= end) {
      row.classList.add("is-current-dasha");
      const firstCell = row.querySelector("td");
      if (firstCell && !firstCell.querySelector(".pill-active")) {
        const pill = document.createElement("span");
        pill.className = "pill-active";
        pill.textContent = "ACTIVE";
        firstCell.appendChild(pill);
      }
    }
  });

  // 6. Retrograde Graha Filter & Chart Night-Invert Toggle (result.html)
  const retroBtn = document.getElementById("toggle-retro");
  const grahaTable = document.getElementById("graha-table");
  if (retroBtn && grahaTable) {
    let retroOnly = false;
    retroBtn.addEventListener("click", () => {
      retroOnly = !retroOnly;
      retroBtn.classList.toggle("is-active", retroOnly);
      retroBtn.textContent = retroOnly ? "All Grahas" : "Retrograde Only";
      grahaTable.querySelectorAll("tbody tr").forEach((row) => {
        const isRetro = row.dataset.retro === "true";
        row.style.display = retroOnly && !isRetro ? "none" : "";
      });
    });
  }

  const invertBtn = document.getElementById("toggle-chart-invert");
  const chartBox = document.getElementById("kundali-viewport");
  if (invertBtn && chartBox) {
    const savedInvert = localStorage.getItem("astral_chart_invert");
    if (savedInvert === "on") {
      chartBox.classList.add("is-inverted");
      invertBtn.classList.add("is-active");
    }
    invertBtn.addEventListener("click", () => {
      chartBox.classList.toggle("is-inverted");
      const active = chartBox.classList.contains("is-inverted");
      invertBtn.classList.toggle("is-active", active);
      localStorage.setItem("astral_chart_invert", active ? "on" : "off");
    });
  }
});