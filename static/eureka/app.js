/* Eureka - static, no build, no tracking. All user state lives in localStorage. */
(() => {
"use strict";

const $ = (s, r = document) => r.querySelector(s);
const $$ = (s, r = document) => [...r.querySelectorAll(s)];
const esc = s => String(s ?? "").replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const app = $("#app");

/* ---------- persistent state ---------- */
const KEY = "eureka:v1";
const blank = () => ({ seen: {}, saved: [], hidden: [], notes: {}, ui: { tp: "all", dp: 2, len: "any", sort: "foryou", spark: false } });
let S = (() => { try { return Object.assign(blank(), JSON.parse(localStorage.getItem(KEY)) || {}); } catch { return blank(); } })();
S.ui = Object.assign(blank().ui, S.ui);
let saveTimer;
const persist = () => { clearTimeout(saveTimer); saveTimer = setTimeout(() => { try { localStorage.setItem(KEY, JSON.stringify(S)); } catch {} }, 150); };

/* ---------- data ---------- */
let DATA, BY, TOPICS, TOPIC_BY;
const DEPTH = {
  1: ["Spark", "Gets you curious. Treat it as a doorway, not as learning."],
  2: ["Mental model", "Builds a real mental model of the idea."],
  3: ["Deep dive", "Full technical detail: derivations, code, proofs, data."],
  4: ["Lecture / primary", "A real course lecture, or the researchers explaining their own work."],
};
const FORMAT = { lecture: "Lecture", talk: "Talk", explainer: "Explainer", build: "Build-along", interview: "Interview", doc: "Documentary" };

fetch("videos.json").then(r => r.json()).then(d => {
  DATA = d; BY = Object.fromEntries(d.v.map(v => [v.id, v]));
  TOPICS = d.meta.topics; TOPIC_BY = Object.fromEntries(TOPICS.map(t => [t.id, t]));
  route();
}).catch(() => { app.innerHTML = `<p class="empty">Could not load the video list.</p>`; });

/* ---------- helpers ---------- */
const fmtLen = s => { const h = Math.floor(s / 3600), m = Math.floor(s % 3600 / 60), x = s % 60; return h ? `${h}:${String(m).padStart(2, "0")}:${String(x).padStart(2, "0")}` : `${m}:${String(x).padStart(2, "0")}`; };
const fmtViews = n => n >= 1e6 ? (n / 1e6).toFixed(n >= 1e7 ? 0 : 1) + "M views" : n >= 1e3 ? Math.round(n / 1e3) + "K views" : n + " views";
const thumb = id => `https://i.ytimg.com/vi/${id}/hq2.jpg`;
const thumbFallback = id => `https://i.ytimg.com/vi/${id}/hqdefault.jpg`;
const hnYears = v => v.y0 === v.y1 ? `${v.y0}` : `${v.y0}-${v.y1}`;
const DAY = 864e5;
const seenOf = id => S.seen[id];
const pct = id => { const s = seenOf(id); return s && s.dur ? Math.min(1, s.pos / s.dur) : 0; };
const isDone = id => !!(seenOf(id) && seenOf(id).done);
const toggleIn = (arr, id) => { const i = arr.indexOf(id); i >= 0 ? arr.splice(i, 1) : arr.push(id); persist(); return i < 0; };

/* ---------- recommendation: quality + taste learned locally + a nudge toward the unfamiliar ---------- */
function affinity() {
  const tp = {}, ch = {}, total = {};
  for (const [id, s] of Object.entries(S.seen)) {
    const v = BY[id]; if (!v) continue;
    const n = S.notes[id]; const r = n && n.rating;
    const w = (r === "new" || r === "deep" ? 1.5 : r === "fluff" ? -1.5 : r === "knew" ? -0.4 : 0) + (s.done ? 0.8 : pct(id) > .3 ? 0.4 : 0);
    tp[v.tp] = (tp[v.tp] || 0) + w; ch[v.c] = (ch[v.c] || 0) + w; total[v.tp] = (total[v.tp] || 0) + 1;
  }
  for (const id of S.saved) { const v = BY[id]; if (v) { tp[v.tp] = (tp[v.tp] || 0) + .4; ch[v.c] = (ch[v.c] || 0) + .3; } }
  const norm = o => Object.fromEntries(Object.entries(o).map(([k, x]) => [k, Math.tanh(x / 3)]));
  const seenN = Object.values(total).reduce((a, b) => a + b, 0) || 1;
  return { tp: norm(tp), ch: norm(ch), exposure: Object.fromEntries(Object.entries(total).map(([k, x]) => [k, x / seenN])) };
}
const hash01 = str => { let h = 2166136261; for (let i = 0; i < str.length; i++) { h ^= str.charCodeAt(i); h = Math.imul(h, 16777619); } return ((h >>> 0) % 10000) / 10000; };
function foryou(list) {
  const a = affinity(), day = Math.floor(Date.now() / DAY);
  const sc = v => {
    let x = v.sc * 1.0 + 0.28 * (a.tp[v.tp] || 0) + 0.32 * (a.ch[v.c] || 0);
    x += 0.12 * (1 - (a.exposure[v.tp] || 0));
    x += 0.30 * hash01(v.id + day);
    if (v.tp === "sw") x -= 0.22; // Hacker News skews to software craft; keep the default feed on science and AI
    if (isDone(v.id)) x -= 2; else if (pct(v.id) > .05) x += .15;
    return x;
  };
  const ranked = list.map(v => [sc(v), v]).sort((p, q) => q[0] - p[0]);
  // diversity: each repeat of a channel higher up the page costs a little, so no single channel owns the feed
  const seen = {}, top = ranked.slice(0, 240).map(([s, v]) => { const k = seen[v.c] = (seen[v.c] || 0) + 1; return [s - 0.09 * (k - 1), v]; });
  return top.sort((p, q) => q[0] - p[0]).concat(ranked.slice(240)).map(p => p[1]);
}

/* ---------- filtering ---------- */
function filtered(extra = {}) {
  const u = { ...S.ui, ...extra };
  const q = (extra.q ?? ($("#q") && $("#q").value) ?? "").trim().toLowerCase();
  const terms = q.split(/\s+/).filter(Boolean);
  const hid = new Set(S.hidden);
  let list = DATA.v.filter(v => {
    if (hid.has(v.id)) return false;
    if (u.tp !== "all" && v.tp !== u.tp) return false;
    if (!u.spark && v.dp < u.dp) return false;
    if (u.len === "short" && v.l > 1200) return false;
    if (u.len === "mid" && (v.l <= 1200 || v.l > 3600)) return false;
    if (u.len === "long" && v.l <= 3600) return false;
    if (terms.length) {
      const hay = (v.t + " " + v.c + " " + TOPIC_BY[v.tp].name + " " + (FORMAT[v.fm] || "")).toLowerCase();
      if (!terms.every(t => hay.includes(t))) return false;
    }
    return true;
  });
  switch (u.sort) {
    case "hn": list.sort((a, b) => b.au - a.au || b.sc - a.sc); break;
    case "new": list.sort((a, b) => b.y - a.y || b.sc - a.sc); break;
    case "timeless": list.sort((a, b) => (b.y1 - b.y0) - (a.y1 - a.y0) || b.au - a.au); break;
    case "short": list.sort((a, b) => a.l - b.l); break;
    case "long": list.sort((a, b) => b.l - a.l); break;
    default: list = foryou(list);
  }
  return list;
}

/* ---------- views ---------- */
function card(v, opts = {}) {
  const p = pct(v.id), saved = S.saved.includes(v.id);
  const hn = v.au >= 2 ? `<span class="hn" title="${v.au} different Hacker News users recommended this, ${hnYears(v)}">&#9650; ${v.au} on HN</span>` : "";
  return `<article class="card" data-id="${v.id}">
    <a class="tile" href="#/v/${v.id}" aria-label="${esc(v.t)}">
      <div class="thumb"><img loading="${opts.eager ? "eager" : "lazy"}" src="${thumb(v.id)}" alt="" data-fb="${thumbFallback(v.id)}">
        <span class="dur">${fmtLen(v.l)}</span>${isDone(v.id) ? `<span class="done-mark">Watched</span>` : ""}
        ${p > .02 && !isDone(v.id) ? `<span class="prog"><i style="width:${Math.round(p * 100)}%"></i></span>` : ""}
      </div>
      <h3>${esc(v.t)}</h3>
    </a>
    <div class="meta"><span>${esc(v.c)}</span><span>${v.y}</span>${hn}</div>
    ${opts.tags === false ? "" : `<div class="tags"><span class="tag">${esc(TOPIC_BY[v.tp].name)}</span><span class="tag d${v.dp}" title="${esc(DEPTH[v.dp][1])}">${DEPTH[v.dp][0]}</span>${v.fm && FORMAT[v.fm] ? `<span class="tag">${FORMAT[v.fm]}</span>` : ""}</div>`}
    <div class="card-act">
      <button class="iconbtn ${saved ? "on" : ""}" data-act="save" title="${saved ? "Remove from saved" : "Save for later"}" aria-label="Save for later">&#9733;</button>
      <button class="iconbtn" data-act="hide" title="Not for me - hide" aria-label="Hide this video">&times;</button>
    </div>
  </article>`;
}

let shown = 48;
function home() {
  const counts = {}; DATA.v.forEach(v => { if (S.ui.spark || v.dp >= S.ui.dp) counts[v.tp] = (counts[v.tp] || 0) + 1; });
  const total = Object.values(counts).reduce((a, b) => a + b, 0);
  app.innerHTML = `
    <section class="hero"><h1>Videos that teach you something, not just make you feel like it.</h1>
    <p>${DATA.v.length.toLocaleString()} science, math and AI videos that people on Hacker News keep recommending year after year, filtered for substance. Pick one, then prove to yourself that it stuck.</p></section>
    <div class="chips" role="group" aria-label="Topics">
      <button class="chip" aria-pressed="${S.ui.tp === "all"}" data-tp="all">All<small>${total}</small></button>
      ${TOPICS.map(t => `<button class="chip" aria-pressed="${S.ui.tp === t.id}" data-tp="${t.id}" title="${esc(t.desc)}">${esc(t.name)}<small>${counts[t.id] || 0}</small></button>`).join("")}
    </div>
    <div class="controls">
      <label>Sort <select id="sort">${[["foryou", "For you"], ["hn", "Most recommended on HN"], ["timeless", "Recommended longest"], ["new", "Newest"], ["short", "Shortest"], ["long", "Longest"]].map(([k, n]) => `<option value="${k}" ${S.ui.sort === k ? "selected" : ""}>${n}</option>`).join("")}</select></label>
      <label>Length <select id="len">${[["any", "Any"], ["short", "Under 20 min"], ["mid", "20-60 min"], ["long", "Over 1 hour"]].map(([k, n]) => `<option value="${k}" ${S.ui.len === k ? "selected" : ""}>${n}</option>`).join("")}</select></label>
      <label>Depth <select id="dp">${[[2, "Explainers and deeper"], [3, "Deep dives and lectures only"]].map(([k, n]) => `<option value="${k}" ${S.ui.dp == k ? "selected" : ""}>${n}</option>`).join("")}</select></label>
      <label class="toggle" title="Pop-science that sparks curiosity but rarely teaches the mechanics"><input type="checkbox" id="spark" ${S.ui.spark ? "checked" : ""}> Include light pop-sci</label>
      <span class="grow"></span><span class="count" id="count"></span>
      <button class="btn" id="surprise" title="Open something good you have not seen">&#10022; Surprise me</button>
    </div>
    <div class="grid" id="grid"></div><div class="more" id="more"></div>`;
  drawGrid();
}

function drawGrid() {
  const list = filtered();
  const g = $("#grid"); if (!g) return;
  $("#count").textContent = `${list.length.toLocaleString()} videos`;
  g.innerHTML = list.length ? list.slice(0, shown).map((v, i) => card(v, { eager: i < 12 })).join("") : `<p class="empty" style="grid-column:1/-1">Nothing matches. Loosen a filter or turn on light pop-sci.</p>`;
  $("#more").innerHTML = list.length > shown ? `<button class="btn" id="moreBtn">Show more (${list.length - shown} left)</button>` : "";
}

function related(v, n = 10) {
  const hid = new Set(S.hidden);
  const pool = DATA.v.filter(x => x.id !== v.id && !hid.has(x.id) && !isDone(x.id) && x.dp >= (S.ui.spark ? 1 : 2));
  const same = foryou(pool.filter(x => x.c === v.c && x.tp === v.tp)).slice(0, 3);
  const used = new Set(same.map(x => x.id));
  const topic = foryou(pool.filter(x => x.tp === v.tp && !used.has(x.id))).slice(0, n - same.length);
  return [...same, ...topic];
}

let player, progTimer;
function watch(id) {
  const v = BY[id]; if (!v) { location.hash = "#/"; return; }
  const n = S.notes[id] || {}, saved = S.saved.includes(id), s = seenOf(id);
  const threads = v.th ? `<ul class="hnlist"><li><a href="https://news.ycombinator.com/item?id=${v.th}" target="_blank" rel="noopener">${esc(v.tt || "HN discussion")}</a></li></ul>` : "";
  app.innerHTML = `<div class="watch"><div>
    <div class="player"><div id="yt"></div></div>
    <h1 class="vtitle">${esc(v.t)}</h1>
    <div class="vmeta"><span>${esc(v.c)}</span><span>${v.y}</span><span>${fmtLen(v.l)}</span>${v.vw ? `<span>${fmtViews(v.vw)}</span>` : ""}
      <span class="tag d${v.dp}" title="${esc(DEPTH[v.dp][1])}">${DEPTH[v.dp][0]}</span><span class="tag">${esc(TOPIC_BY[v.tp].name)}</span></div>
    <div class="vact">
      <button class="btn ${saved ? "on" : ""}" id="saveBtn">&#9733; ${saved ? "Saved" : "Save for later"}</button>
      <a class="btn" href="https://www.youtube.com/watch?v=${id}" target="_blank" rel="noopener">Open on YouTube</a>
      <button class="btn" id="hideBtn">Not for me</button>
    </div>
    ${v.au >= 2 ? `<div class="panel"><h2>Why it is here</h2><p class="sub" style="margin:0">Recommended by <b>${v.au}</b> different people on Hacker News across ${hnYears(v)}${v.rec >= 3 ? `, ${v.rec} of those comments explicitly praising it` : ""}.</p>${threads}</div>` : ""}
    <div class="panel" id="learn"><h2>Did it stick? Prove it to yourself</h2>
      <p class="sub">Watching feels like learning. Explaining from memory is the real test. Write it without scrubbing back through the video. Everything here stays in your browser.</p>
      <label class="f" for="n-core">In your own words, what is the core idea?</label>
      <textarea id="n-core" dir="auto" data-k="core">${esc(n.core || "")}</textarea>
      <label class="f" for="n-use">Where could you use it, at work or in life?</label>
      <textarea id="n-use" dir="auto" data-k="use">${esc(n.use || "")}</textarea>
      <label class="f" for="n-gap">What is still unclear or worth checking?</label>
      <textarea id="n-gap" dir="auto" data-k="gap">${esc(n.gap || "")}</textarea>
      <label class="f">For you, this was</label>
      <div class="rate" role="group">${[["new", "Brand new to me"], ["deep", "Deepened what I knew"], ["knew", "Already knew it"], ["fluff", "Mostly fluff"]].map(([k, l]) => `<button type="button" data-rate="${k}" aria-pressed="${n.rating === k}">${l}</button>`).join("")}<span class="saved-note" id="savedNote">Saved</span></div>
      <p class="sub" style="margin:12px 0 0">${n.core ? `I will bring this back in a few days to check what you remember.` : `Once you write something, I will quiz you on it later (see Review).`}</p>
    </div></div>
    <aside class="up"><h2>Up next</h2>${related(v).map(x => card(x, { tags: false })).join("")}</aside></div>`;
  mountPlayer(v, s && !s.done ? Math.max(0, Math.floor(s.pos - 3)) : 0);
  window.scrollTo(0, 0);
}

function mountPlayer(v, start) {
  const make = () => {
    player = new YT.Player("yt", {
      host: "https://www.youtube-nocookie.com", videoId: v.id, width: "100%", height: "100%",
      playerVars: { rel: 0, modestbranding: 1, start, playsinline: 1 },
      events: {
        onReady: () => { clearInterval(progTimer); progTimer = setInterval(() => track(v.id), 4000); },
        onStateChange: e => { if (e.data === 0) { track(v.id, true); } else if (e.data === 2) track(v.id); },
        onError: () => { const el = $("#yt") || $(".player"); if (el) el.outerHTML = `<div class="empty" style="padding:15% 0"><p>The owner blocked embedding.</p><a class="btn primary" target="_blank" rel="noopener" href="https://www.youtube.com/watch?v=${v.id}">Watch on YouTube</a></div>`; },
      },
    });
  };
  if (window.YT && YT.Player) make();
  else { window.onYouTubeIframeAPIReady = make; if (!$("#ytapi")) { const s = document.createElement("script"); s.id = "ytapi"; s.src = "https://www.youtube.com/iframe_api"; document.head.appendChild(s); } }
}
function track(id, ended) {
  try {
    if (!player || !player.getCurrentTime) return;
    const pos = player.getCurrentTime(), dur = player.getDuration();
    if (!dur) return;
    const s = S.seen[id] || (S.seen[id] = { first: Date.now() });
    s.pos = ended ? 0 : pos; s.dur = dur; s.last = Date.now();
    if (ended || pos / dur > .88) s.done = true;
    persist();
  } catch {}
}
function stopPlayer() { clearInterval(progTimer); try { player && player.destroy && player.destroy(); } catch {} player = null; }

/* ---------- spaced recall ---------- */
const STEPS = [2, 7, 21, 60, 150];
function noteChanged(id) {
  const n = S.notes[id]; if (!n) return;
  if (n.core && n.core.trim() && !n.due) { n.box = 0; n.due = Date.now() + STEPS[0] * DAY; }
  persist(); updateBadge();
}
const dueList = () => Object.entries(S.notes).filter(([id, n]) => n.core && n.core.trim() && n.due && n.due <= Date.now() && BY[id]).sort((a, b) => a[1].due - b[1].due);
function updateBadge() { const b = $("#dueBadge"), n = dueList().length; b.hidden = !n; b.textContent = n; }

function review() {
  const due = dueList();
  const upcoming = Object.entries(S.notes).filter(([id, n]) => n.core && n.due && n.due > Date.now() && BY[id]).length;
  const [id, n] = due[0] || [];
  app.innerHTML = `<section class="review"><h1>Review</h1>
    <p style="color:var(--muted);margin:0">Pulling something out of your head is what makes it permanent. Answer from memory first, then compare with what you wrote right after watching.</p>
    ${id ? `<div class="rev-card" data-id="${id}">
      <div class="thumb"><img src="${thumb(id)}" alt="" data-fb="${thumbFallback(id)}"></div>
      <b>${esc(BY[id].t)}</b><div class="meta">${esc(BY[id].c)} &middot; ${due.length} due</div>
      <label class="f" for="recall" style="display:block;margin:14px 0 4px;color:var(--muted)">Without looking: what was the core idea?</label>
      <textarea id="recall" dir="auto" style="width:100%;min-height:90px;padding:10px 12px;border-radius:10px;border:1px solid var(--line);background:var(--bg)"></textarea>
      <div class="row" style="margin-top:10px"><button class="btn primary" id="reveal">Show what I wrote then</button></div>
      <div id="after" hidden><div class="reveal" dir="auto">${esc(n.core)}</div>
        <p style="margin:6px 0 10px;color:var(--muted)">Honestly, how close were you?</p>
        <div class="row"><button class="btn" data-grade="2">Nailed it</button><button class="btn" data-grade="1">Fuzzy</button><button class="btn" data-grade="0">Forgot</button><a class="btn" href="#/v/${id}">Rewatch</a></div></div>
    </div>` : `<div class="empty">${upcoming ? `Nothing due. ${upcoming} item${upcoming > 1 ? "s" : ""} scheduled for later.` : `Nothing to review yet. Watch a video, write what you took from it, and it will come back here in two days.`}</div>`}
  </section>`;
}

function library(tab = "saved") {
  const ids = {
    saved: S.saved,
    progress: Object.keys(S.seen).filter(id => BY[id] && !isDone(id) && pct(id) > .02).sort((a, b) => S.seen[b].last - S.seen[a].last),
    watched: Object.keys(S.seen).filter(id => BY[id] && isDone(id)).sort((a, b) => S.seen[b].last - S.seen[a].last),
    hidden: S.hidden,
  }[tab].filter(id => BY[id]);
  const names = { saved: "Saved", progress: "In progress", watched: "Watched", hidden: "Hidden" };
  app.innerHTML = `<div class="libhead"><h1>Library</h1></div>
    <div class="tabs" role="tablist">${Object.keys(names).map(k => `<button role="tab" aria-selected="${k === tab}" data-tab="${k}">${names[k]}</button>`).join("")}</div>
    ${ids.length ? `<div class="grid">${ids.map(id => card(BY[id])).join("")}</div>` : `<p class="empty">Nothing here yet.</p>`}`;
}

function about() {
  app.innerHTML = `<section class="about"><h1>About Eureka</h1>
    <p>YouTube optimises for watch time, so it feeds you videos that feel like learning. This is a smaller library with a different rule: show only what people who know the field keep recommending, year after year, and then nudge you to check that you actually understood.</p>
    <h2>Where the videos come from</h2>
    <p>I collected every Hacker News comment that links to a YouTube video (about 260,000 of them, 2007 to ${new Date(DATA.meta.built).getFullYear()}) plus the popular submissions that point at one, and counted how many <i>different people</i> recommended each video and over how many years. A video that keeps being recommended by different people for years survives. Then I filtered for science, mathematics, statistics, AI, computer science and ways of thinking, and removed anything that is mostly entertainment, news or opinion.</p>
    <h2>How depth is labelled</h2>
    <ul class="depth">${Object.values(DEPTH).map(([n, d]) => `<li><b>${n}</b> - ${d}</li>`).join("")}</ul>
    <p>"Spark" videos are hidden by default. They are great for curiosity, but the feeling of understanding they give is not the same as understanding.</p>
    <h2>Privacy</h2>
    <p>No accounts and no analytics. What you watch, save, write and rate is stored only in this browser. Use "Export my data" in the footer to move it elsewhere. Videos play through YouTube's privacy-enhanced player.</p>
    <h2>How the recommendations work</h2>
    <p>"For you" combines the quality signal above with a taste profile computed in your browser from what you finish, save and rate, plus a deliberate push toward topics you have not explored yet.</p>
    <p style="margin-top:30px"><a class="btn" href="#/">Back to the library</a></p></section>`;
}

/* ---------- routing ---------- */
function route() {
  if (!DATA) return;
  stopPlayer();
  const [, page, arg] = (location.hash || "#/").split("/");
  $$(".nav a").forEach(a => a.classList.toggle("on", a.dataset.nav === page));
  updateBadge();
  if (page === "v" && arg) return watch(arg);
  if (page === "library") return library(arg || "saved");
  if (page === "review") return review();
  if (page === "about") return about();
  shown = 48; home(); window.scrollTo(0, 0);
}
window.addEventListener("hashchange", route);

/* ---------- events ---------- */
document.addEventListener("error", e => { const i = e.target; if (i.tagName === "IMG" && i.dataset.fb && i.src !== i.dataset.fb) i.src = i.dataset.fb; }, true);

document.addEventListener("click", e => {
  const t = e.target.closest("button, [data-act]"); if (!t) return;
  const card_ = t.closest(".card"), id = card_ && card_.dataset.id;
  if (t.dataset.act === "save") { e.preventDefault(); const on = toggleIn(S.saved, id); t.classList.toggle("on", on); t.title = on ? "Remove from saved" : "Save for later"; return; }
  if (t.dataset.act === "hide") { e.preventDefault(); S.hidden.push(id); persist(); card_.remove(); return; }
  if (t.dataset.tp) { S.ui.tp = t.dataset.tp; persist(); shown = 48; home(); return; }
  if (t.id === "moreBtn") { shown += 48; drawGrid(); return; }
  if (t.id === "surprise") {
    const pool = filtered().filter(v => !isDone(v.id)); if (!pool.length) return;
    const top = pool.slice(0, Math.max(30, pool.length / 3)); location.hash = "#/v/" + top[Math.floor(Math.random() * top.length)].id; return;
  }
  if (t.dataset.tab) { library(t.dataset.tab); return; }
  const vid = (location.hash.split("/")[2]) || "";
  if (t.id === "saveBtn") { const on = toggleIn(S.saved, vid); t.classList.toggle("on", on); t.innerHTML = `&#9733; ${on ? "Saved" : "Save for later"}`; return; }
  if (t.id === "hideBtn") { S.hidden.push(vid); persist(); location.hash = "#/"; return; }
  if (t.dataset.rate) {
    const n = S.notes[vid] || (S.notes[vid] = {}); n.rating = n.rating === t.dataset.rate ? null : t.dataset.rate;
    $$("[data-rate]").forEach(b => b.setAttribute("aria-pressed", b.dataset.rate === n.rating)); noteChanged(vid); flash(); return;
  }
  if (t.id === "reveal") { $("#after").hidden = false; t.hidden = true; return; }
  if (t.dataset.grade !== undefined) {
    const rid = $(".rev-card").dataset.id, n = S.notes[rid], g = +t.dataset.grade;
    n.box = g === 2 ? Math.min(STEPS.length - 1, (n.box || 0) + 1) : g === 1 ? (n.box || 0) : 0;
    n.due = Date.now() + STEPS[n.box] * DAY * (g === 1 ? .5 : 1); n.reviews = (n.reviews || 0) + 1; persist(); route(); return;
  }
  if (t.id === "exportBtn") { const b = new Blob([JSON.stringify(S, null, 1)], { type: "application/json" }); const a = document.createElement("a"); a.href = URL.createObjectURL(b); a.download = "eureka-data.json"; a.click(); }
});

let flashT;
const flash = () => { const el = $("#savedNote"); if (!el) return; el.classList.add("show"); clearTimeout(flashT); flashT = setTimeout(() => el.classList.remove("show"), 1200); };
document.addEventListener("input", e => {
  const t = e.target;
  if (t.dataset && t.dataset.k) { const vid = location.hash.split("/")[2]; const n = S.notes[vid] || (S.notes[vid] = {}); n[t.dataset.k] = t.value; noteChanged(vid); flash(); }
});
document.addEventListener("change", e => {
  const t = e.target;
  if (t.id === "sort") S.ui.sort = t.value;
  else if (t.id === "len") S.ui.len = t.value;
  else if (t.id === "dp") S.ui.dp = +t.value;
  else if (t.id === "spark") S.ui.spark = t.checked;
  else if (t.id === "importFile") {
    const f = t.files[0]; if (!f) return;
    f.text().then(txt => { try { S = Object.assign(blank(), JSON.parse(txt)); persist(); route(); alert("Imported."); } catch { alert("That file does not look like an Eureka export."); } });
    return;
  } else return;
  persist(); shown = 48; home();
});
$("#searchForm").addEventListener("submit", e => { e.preventDefault(); if (location.hash && location.hash !== "#/") location.hash = "#/"; else drawGrid(); });
$("#q").addEventListener("input", () => { if (!location.hash || location.hash === "#/") { shown = 48; drawGrid(); } else location.hash = "#/"; });
})();
