(() => {
  const canvas = document.getElementById('game');
  const ctx = canvas.getContext('2d');
  const scoreEl = document.getElementById('score');
  const livesEl = document.getElementById('lives');

  const W = canvas.width;
  const H = canvas.height;
  const TAU = Math.PI * 2;
  const keys = new Set();

  let ship, rocks, shots, sparks, stars, score, lives, paused, over, lastShot, lastTime;

  const rand = (min, max) => min + Math.random() * (max - min);
  const wrap = o => {
    if (o.x < -40) o.x = W + 40;
    if (o.x > W + 40) o.x = -40;
    if (o.y < -40) o.y = H + 40;
    if (o.y > H + 40) o.y = -40;
  };
  const dist = (a, b) => Math.hypot(a.x - b.x, a.y - b.y);

  function reset() {
    ship = { x: W / 2, y: H / 2, vx: 0, vy: 0, a: -Math.PI / 2, r: 15, inv: 120 };
    rocks = [];
    shots = [];
    sparks = [];
    stars = Array.from({ length: 140 }, () => ({ x: rand(0, W), y: rand(0, H), z: rand(.2, 1), tw: rand(0, TAU) }));
    score = 0;
    lives = 3;
    paused = false;
    over = false;
    lastShot = 0;
    lastTime = performance.now();
    for (let i = 0; i < 5; i++) spawnRock(3);
    updateHud();
  }

  function updateHud() {
    scoreEl.textContent = `SCORE ${String(score).padStart(6, '0')}`;
    livesEl.textContent = `LIVES ${lives}`;
  }

  function spawnRock(size, x, y) {
    const r = size === 3 ? rand(36, 54) : size === 2 ? rand(22, 32) : rand(12, 18);
    let rx = x ?? rand(0, W);
    let ry = y ?? rand(0, H);
    if (x == null && dist({ x: rx, y: ry }, ship) < 170) { rx = rand(0, W); ry = rand(0, H); }
    const pts = Array.from({ length: 10 }, (_, i) => {
      const ang = i / 10 * TAU;
      return { a: ang, m: rand(.68, 1.22) };
    });
    rocks.push({ x: rx, y: ry, vx: rand(-1.4, 1.4), vy: rand(-1.4, 1.4), a: rand(0, TAU), spin: rand(-.025, .025), r, size, pts });
  }

  function fire() {
    const now = performance.now();
    if (now - lastShot < 150 || over) return;
    lastShot = now;
    const noseX = ship.x + Math.cos(ship.a) * 18;
    const noseY = ship.y + Math.sin(ship.a) * 18;
    shots.push({ x: noseX, y: noseY, vx: ship.vx + Math.cos(ship.a) * 8, vy: ship.vy + Math.sin(ship.a) * 8, life: 54 });
  }

  function burst(x, y, n = 18) {
    for (let i = 0; i < n; i++) sparks.push({ x, y, vx: rand(-3, 3), vy: rand(-3, 3), life: rand(18, 45) });
  }

  function breakRock(rock) {
    score += rock.size === 3 ? 20 : rock.size === 2 ? 50 : 100;
    burst(rock.x, rock.y, rock.size * 10);
    if (rock.size > 1) {
      spawnRock(rock.size - 1, rock.x, rock.y);
      spawnRock(rock.size - 1, rock.x, rock.y);
    }
    updateHud();
  }

  function loseLife() {
    if (ship.inv > 0 || over) return;
    lives -= 1;
    burst(ship.x, ship.y, 42);
    updateHud();
    if (lives <= 0) {
      over = true;
      return;
    }
    ship.x = W / 2; ship.y = H / 2; ship.vx = 0; ship.vy = 0; ship.a = -Math.PI / 2; ship.inv = 150;
  }

  function update() {
    if (paused) return;

    if (!over) {
      if (keys.has('ArrowLeft') || keys.has('a')) ship.a -= .075;
      if (keys.has('ArrowRight') || keys.has('d')) ship.a += .075;
      if (keys.has('ArrowUp') || keys.has('w')) {
        ship.vx += Math.cos(ship.a) * .16;
        ship.vy += Math.sin(ship.a) * .16;
        if (Math.random() < .7) sparks.push({ x: ship.x - Math.cos(ship.a) * 16, y: ship.y - Math.sin(ship.a) * 16, vx: -Math.cos(ship.a) * rand(1, 3), vy: -Math.sin(ship.a) * rand(1, 3), life: 16 });
      }
      if (keys.has(' ')) fire();
      ship.x += ship.vx;
      ship.y += ship.vy;
      ship.vx *= .992;
      ship.vy *= .992;
      ship.inv = Math.max(0, ship.inv - 1);
      wrap(ship);
    }

    shots.forEach(s => { s.x += s.vx; s.y += s.vy; s.life--; wrap(s); });
    shots = shots.filter(s => s.life > 0);

    rocks.forEach(r => { r.x += r.vx; r.y += r.vy; r.a += r.spin; wrap(r); });
    sparks.forEach(p => { p.x += p.vx; p.y += p.vy; p.vx *= .97; p.vy *= .97; p.life--; });
    sparks = sparks.filter(p => p.life > 0);

    for (let i = rocks.length - 1; i >= 0; i--) {
      const r = rocks[i];
      for (let j = shots.length - 1; j >= 0; j--) {
        if (dist(r, shots[j]) < r.r) {
          shots.splice(j, 1);
          rocks.splice(i, 1);
          breakRock(r);
          break;
        }
      }
    }

    if (!over) rocks.forEach(r => { if (dist(r, ship) < r.r + ship.r) loseLife(); });
    if (rocks.length === 0) for (let i = 0; i < 5 + Math.floor(score / 500); i++) spawnRock(3);
  }

  function drawShip() {
    if (over) return;
    if (ship.inv && Math.floor(ship.inv / 8) % 2) return;
    ctx.save();
    ctx.translate(ship.x, ship.y);
    ctx.rotate(ship.a);
    ctx.strokeStyle = '#69f7ff';
    ctx.lineWidth = 2;
    ctx.shadowBlur = 12;
    ctx.shadowColor = '#69f7ff';
    ctx.beginPath();
    ctx.moveTo(20, 0);
    ctx.lineTo(-13, -12);
    ctx.lineTo(-7, 0);
    ctx.lineTo(-13, 12);
    ctx.closePath();
    ctx.stroke();
    ctx.restore();
  }

  function drawRock(r) {
    ctx.save();
    ctx.translate(r.x, r.y);
    ctx.rotate(r.a);
    ctx.strokeStyle = '#d8fbff';
    ctx.lineWidth = 2;
    ctx.shadowBlur = 8;
    ctx.shadowColor = '#ff4fd8';
    ctx.beginPath();
    r.pts.forEach((p, i) => {
      const x = Math.cos(p.a) * r.r * p.m;
      const y = Math.sin(p.a) * r.r * p.m;
      i ? ctx.lineTo(x, y) : ctx.moveTo(x, y);
    });
    ctx.closePath();
    ctx.stroke();
    ctx.restore();
  }

  function draw() {
    ctx.clearRect(0, 0, W, H);
    ctx.fillStyle = '#02030a';
    ctx.fillRect(0, 0, W, H);

    stars.forEach(s => {
      s.tw += .015 * s.z;
      ctx.globalAlpha = .35 + Math.sin(s.tw) * .25 + s.z * .4;
      ctx.fillStyle = '#d8fbff';
      ctx.fillRect(s.x, s.y, Math.max(1, s.z * 2), Math.max(1, s.z * 2));
      s.x -= .08 * s.z;
      if (s.x < 0) s.x = W;
    });
    ctx.globalAlpha = 1;

    rocks.forEach(drawRock);

    ctx.strokeStyle = '#ffe66d';
    ctx.lineWidth = 3;
    shots.forEach(s => {
      ctx.beginPath();
      ctx.moveTo(s.x, s.y);
      ctx.lineTo(s.x - s.vx * .8, s.y - s.vy * .8);
      ctx.stroke();
    });

    sparks.forEach(p => {
      ctx.globalAlpha = Math.max(0, p.life / 45);
      ctx.fillStyle = '#ff4fd8';
      ctx.fillRect(p.x, p.y, 3, 3);
    });
    ctx.globalAlpha = 1;

    drawShip();

    ctx.strokeStyle = 'rgba(105,247,255,.08)';
    for (let y = 0; y < H; y += 4) { ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(W, y); ctx.stroke(); }

    if (paused || over) {
      ctx.fillStyle = 'rgba(2,3,10,.72)';
      ctx.fillRect(0, 0, W, H);
      ctx.textAlign = 'center';
      ctx.fillStyle = over ? '#ff4fd8' : '#ffe66d';
      ctx.font = '42px ui-monospace, monospace';
      ctx.fillText(over ? 'GAME OVER' : 'PAUSED', W / 2, H / 2 - 12);
      ctx.fillStyle = '#d8fbff';
      ctx.font = '18px ui-monospace, monospace';
      ctx.fillText('Press R to restart', W / 2, H / 2 + 26);
      ctx.textAlign = 'start';
    }
  }

  function loop(t) {
    const dt = t - lastTime;
    lastTime = t;
    if (dt < 80) update();
    draw();
    requestAnimationFrame(loop);
  }

  window.addEventListener('keydown', e => {
    const k = e.key.length === 1 ? e.key.toLowerCase() : e.key;
    if (['ArrowUp','ArrowDown','ArrowLeft','ArrowRight',' '].includes(e.key)) e.preventDefault();
    if (k === 'p') paused = !paused;
    if (k === 'r') reset();
    keys.add(k);
  });

  window.addEventListener('keyup', e => keys.delete(e.key.length === 1 ? e.key.toLowerCase() : e.key));

  reset();
  requestAnimationFrame(loop);
})();
