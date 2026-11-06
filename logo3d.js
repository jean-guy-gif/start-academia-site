// Le « A » du logo en 3D dans la section manifeste (ordinateur uniquement), sans bibliothèque.
// Reprend la mise en scène de StoryScene, calée sur les 6 pages du paperboard (progression 0 → 1) :
// pages 1 à 4 : un tour complet, lent ; page 5 « On la fait tourner plus vite » : il s'emballe
// (plusieurs tours) et le triangle orange (« l'IA ») se détache en s'illuminant ;
// page 6 « Ceci est Start Academia » : il revient de face, triangle en place. La souris l'incline.
(() => {
  const boite = document.querySelector('.manifeste-a');
  if (!boite) return;
  const section = boite.closest('section');
  const zone = document.querySelector('.defile-pb') || section;
  const ok = matchMedia('(min-width: 1001px) and (prefers-reduced-motion: no-preference)');
  if (!ok.matches) return;
  const canvas = boite.querySelector('canvas');
  const gl = canvas.getContext('webgl', { alpha: true, antialias: true, premultipliedAlpha: true });
  if (!gl) return;

  // ---------- Réglages (équivalents de StoryScene.tsx) ----------
  const R = {
    taille: 1.0,              // taille du A (1 = 2 unités de haut)
    tourLent: [0.0, 0.62],    // pages 1 à 4 : un tour complet
    emballe: [0.66, 0.83],    // page 5 : les tours rapides
    toursRapides: 3,          // nombre de tours à la page 5
    ecartTriangle: 0.55,      // distance du triangle orange quand il s'échappe
    souris: [0.25, 0.2],      // influence de la souris (y, x)
  };

  // ---------- Petites maths ----------
  const lerp = (a, b, t) => a + (b - a) * t;
  const borne = (v, a = 0, b = 1) => Math.min(b, Math.max(a, v));
  const smooth = (x, a, b) => { const t = borne((x - a) / (b - a)); return t * t * (3 - 2 * t); };
  const damp = (a, b, l, dt) => lerp(a, b, 1 - Math.exp(-l * dt));
  const mul = (a, b) => { const o = new Float32Array(16); for (let i = 0; i < 4; i++) for (let j = 0; j < 4; j++) { let s = 0; for (let k = 0; k < 4; k++) s += a[k * 4 + j] * b[i * 4 + k]; o[i * 4 + j] = s; } return o; };
  const ident = () => new Float32Array([1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]);
  const trans = (x, y, z) => { const m = ident(); m[12] = x; m[13] = y; m[14] = z; return m; };
  const echelle = (s) => { const m = ident(); m[0] = m[5] = m[10] = s; return m; };
  const rotX = (a) => { const c = Math.cos(a), s = Math.sin(a), m = ident(); m[5] = c; m[6] = s; m[9] = -s; m[10] = c; return m; };
  const rotY = (a) => { const c = Math.cos(a), s = Math.sin(a), m = ident(); m[0] = c; m[2] = -s; m[8] = s; m[10] = c; return m; };
  const rotZ = (a) => { const c = Math.cos(a), s = Math.sin(a), m = ident(); m[0] = c; m[1] = s; m[4] = -s; m[5] = c; return m; };
  const persp = (fov, asp, n, f) => { const t = 1 / Math.tan(fov / 2), m = new Float32Array(16); m[0] = t / asp; m[5] = t; m[10] = (f + n) / (n - f); m[11] = -1; m[14] = 2 * f * n / (n - f); return m; };

  // ---------- Shaders : lumières de StoryScene + environnement simulé (Lightformers) ----------
  const vs = `
    attribute vec3 aP; attribute vec3 aN;
    uniform mat4 uM; uniform mat4 uVP;
    varying vec3 vN; varying vec3 vW;
    void main(){ vec4 w = uM * vec4(aP,1.0); vW = w.xyz; vN = mat3(uM) * aN; gl_Position = uVP * w; }`;
  const fs = `
    precision highp float;
    varying vec3 vN; varying vec3 vW;
    uniform vec3 uCouleur; uniform vec3 uEmissif; uniform float uEmi; uniform float uRug; uniform float uSpec; uniform float uExpo;
    vec3 env(vec3 r){
      vec3 c = vec3(0.10,0.12,0.22);
      c += vec3(0.92,0.95,1.0) * 5.0 * smoothstep(0.55,0.95,r.y) * 0.35;      // bande blanche en haut
      c += vec3(0.75,0.83,1.0) * 4.0 * smoothstep(0.35,0.9,-r.x) * 0.25;      // reflet bleuté à gauche
      c += vec3(1.0,0.60,0.40) * 2.5 * smoothstep(0.35,0.9, r.x) * 0.3;       // reflet chaud à droite
      c += vec3(1.0,0.42,0.17) * 1.0 * smoothstep(0.4,0.95,-r.y) * 0.5;       // orange par en dessous
      return c;
    }
    vec3 ponctuelle(vec3 pos, vec3 col, float I, float dist, vec3 N, vec3 V){
      vec3 L = pos - vW; float d = length(L); L /= d;
      float att = I * pow(clamp(1.0 - d/dist, 0.0, 1.0), 2.0) / (d*d + 1.0);
      vec3 H = normalize(L+V);
      return col * att * (max(dot(N,L),0.0) * uCouleur + pow(max(dot(N,H),0.0), 60.0) * 0.6);
    }
    void main(){
      vec3 N = normalize(vN); vec3 V = normalize(vec3(0.0,0.0,7.0) - vW);
      if (dot(N,V) < 0.0) N = -N;
      vec3 c = uCouleur * 0.7 * vec3(0.55,0.6,0.75);                             // ambiante
      vec3 L1 = normalize(vec3(4.0,6.0,6.0)); vec3 L2 = normalize(vec3(-3.0,2.0,5.0));
      float sh = mix(220.0, 50.0, uRug);
      c += vec3(0.93,0.95,1.0) * 2.4 * (max(dot(N,L1),0.0) * uCouleur * 0.42 + pow(max(dot(N,normalize(L1+V)),0.0), sh) * 0.9 * uSpec);
      c += vec3(1.0) * 1.2 * (max(dot(N,L2),0.0) * uCouleur * 0.42 + pow(max(dot(N,normalize(L2+V)),0.0), sh) * 0.5 * uSpec);
      c += ponctuelle(vec3(-4.0,-3.0,3.0), vec3(1.0,0.48,0.24), 18.0, 12.0, N, V);
      c += ponctuelle(vec3(3.0,-4.0,2.0), vec3(1.0,0.42,0.17), 10.0, 10.0, N, V);
      float fr = pow(1.0 - max(dot(N,V),0.0), 4.0);                              // vernis (clearcoat)
      vec3 R = reflect(-V, N);
      c += env(R) * mix(0.10, 0.85, fr) * uSpec;
      c += uEmissif * uEmi;
      c *= uExpo;
      c = (c*(2.51*c+0.03))/(c*(2.43*c+0.59)+0.14);                               // tonemapping ACES
      gl_FragColor = vec4(pow(clamp(c,0.0,1.0), vec3(1.0/2.2)), 1.0);
    }`;
  const shader = (t, s) => { const o = gl.createShader(t); gl.shaderSource(o, s); gl.compileShader(o); if (!gl.getShaderParameter(o, gl.COMPILE_STATUS)) throw new Error(gl.getShaderInfoLog(o)); return o; };
  let prog;
  try {
    prog = gl.createProgram();
    gl.attachShader(prog, shader(gl.VERTEX_SHADER, vs)); gl.attachShader(prog, shader(gl.FRAGMENT_SHADER, fs));
    gl.linkProgram(prog); gl.useProgram(prog);
  } catch (e) { return; }
  const U = (n) => gl.getUniformLocation(prog, n);
  const aP = gl.getAttribLocation(prog, 'aP'), aN = gl.getAttribLocation(prog, 'aN');

  const piece = (d) => {
    const bin = Uint8Array.from(atob(d.b64), (c) => c.charCodeAt(0)).buffer;
    const pos = new Int16Array(bin, 0, d.n * 3), nor = new Int8Array(bin, d.n * 6, d.n * 3);
    const bp = gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER, bp); gl.bufferData(gl.ARRAY_BUFFER, pos, gl.STATIC_DRAW);
    const bn = gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER, bn); gl.bufferData(gl.ARRAY_BUFFER, nor, gl.STATIC_DRAW);
    return { bp, bn, n: d.n };
  };
  const dessine = (p, M, coul, emi, emiI, rug) => {
    gl.bindBuffer(gl.ARRAY_BUFFER, p.bp); gl.enableVertexAttribArray(aP); gl.vertexAttribPointer(aP, 3, gl.SHORT, false, 0, 0);
    gl.bindBuffer(gl.ARRAY_BUFFER, p.bn); gl.enableVertexAttribArray(aN); gl.vertexAttribPointer(aN, 3, gl.BYTE, true, 0, 0);
    gl.uniformMatrix4fv(U('uM'), false, M);
    gl.uniform3fv(U('uCouleur'), coul); gl.uniform3fv(U('uEmissif'), emi); gl.uniform1f(U('uEmi'), emiI); gl.uniform1f(U('uRug'), rug); gl.uniform1f(U('uSpec'), rug > 0.2 ? 0.35 : 1.0); gl.uniform1f(U('uExpo'), rug > 0.2 ? 0.42 : 1.0);
    gl.drawArrays(gl.TRIANGLES, 0, p.n);
  };

  const demarrer = () => {
    const G = window.LOGO3D; if (!G) return;
    const blanc = piece(G.blanc), orange = piece(G.orange);
    const Q = 1 / 16000;                                  // les positions sont stockées en entiers
    const co = G.co;
    gl.enable(gl.DEPTH_TEST); gl.clearColor(0, 0, 0, 0);
    const blancC = new Float32Array([1, 1, 1]), orangeC = new Float32Array([0.9, 0.22, 0.04]), orangeE = new Float32Array([1, 0.26, 0]), zero = new Float32Array([0, 0, 0]);
    let w = 0, h = 0;
    const taille = () => {
      const r = canvas.getBoundingClientRect(), dpr = Math.min(devicePixelRatio || 1, 1.6);
      w = Math.round(r.width * dpr); h = Math.round(r.height * dpr);
      if (canvas.width !== w || canvas.height !== h) { canvas.width = w; canvas.height = h; }
      gl.viewport(0, 0, w, h);
    };
    new ResizeObserver(taille).observe(canvas); taille();

    let px = 0, py = 0;
    addEventListener('pointermove', (e) => { px = (e.clientX / innerWidth) * 2 - 1; py = -((e.clientY / innerHeight) * 2 - 1); }, { passive: true });
    const g = { x: 0, y: 0, ry: 0.15, rx: 0, s: R.taille };
    let t = 0, avant = performance.now(), actif = false, boucle = 0;

    const image = (now) => {
      const dt = Math.min(0.05, (now - avant) / 1000); avant = now; t += dt;
      const r = zone.getBoundingClientRect();
      const p = borne(-r.top / (r.height - innerHeight));
      const lent = smooth(p, R.tourLent[0], R.tourLent[1]);
      const vite = smooth(p, R.emballe[0], R.emballe[1]);
      const c2 = smooth(p, 0.64, 0.74) - smooth(p, 0.84, 0.95);     // le triangle part puis revient
      const fin = smooth(p, 0.86, 1);
      g.x = damp(g.x, 0, 5, dt); g.y = damp(g.y, Math.sin(t * 0.9) * 0.08, 5, dt);
      g.ry = damp(g.ry, 0.15 * (1 - fin) - lent * Math.PI * 2 - vite * Math.PI * 2 * R.toursRapides + px * R.souris[0], vite > 0 && vite < 1 ? 9 : 5, dt);
      g.rx = damp(g.rx, -0.35 * c2 - py * R.souris[1], 5, dt);
      g.s = damp(g.s, R.taille * (1 + 0.12 * c2 + 0.06 * fin), 5, dt);
      boite.style.setProperty('--lueur', (0.12 + c2 * 0.6 + fin * 0.2).toFixed(3));

      gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT);
      const VP = mul(persp(30 * Math.PI / 180, w / h, 0.1, 50), trans(0, 0, -7));
      gl.uniformMatrix4fv(U('uVP'), false, VP);
      const groupe = mul(mul(mul(trans(g.x, g.y, 0), rotY(g.ry)), rotX(g.rx)), echelle(g.s * Q));
      dessine(blanc, groupe, blancC, zero, 0, 0.15);
      const off = c2 * R.ecartTriangle / Q;
      const mo = mul(mul(groupe, trans(co[0] / Q + off * 0.9, co[1] / Q - off * 0.6, off * 0.8)), rotZ(-c2 * 0.6));
      dessine(orange, mo, orangeC, orangeE, 0.35 + c2 * 1.1 + fin * 0.3 + Math.sin(t * 3) * 0.1 * c2, 0.22);
      boucle = actif ? requestAnimationFrame(image) : 0;
    };
    new IntersectionObserver(([e]) => {
      actif = e.isIntersecting;
      if (actif && !boucle) { avant = performance.now(); boucle = requestAnimationFrame(image); }
    }).observe(zone);
    boite.classList.add('en-3d');
  };

  // la géométrie (≈ 120 Ko) n'est chargée qu'à l'approche de la section
  new IntersectionObserver(([e], o) => {
    if (!e.isIntersecting) return; o.disconnect();
    const s = document.createElement('script'); s.src = '/logo3d-geo.js'; s.onload = demarrer; document.head.appendChild(s);
  }, { rootMargin: '600px 0px' }).observe(section);
})();
