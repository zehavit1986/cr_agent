const $ = (sel) => document.querySelector(sel);
const SEVERITIES = ["critical", "high", "medium", "low", "info"];
const HLJS_LANG = {
  Python: "python", JavaScript: "javascript", TypeScript: "typescript", Java: "java", Kotlin: "kotlin", Go: "go",
  Ruby: "ruby", Rust: "rust", "C#": "csharp", "C++": "cpp", C: "c", PHP: "php", Swift: "swift", Scala: "scala",
  Shell: "bash", SQL: "sql",
};

let inputKind = "github";
let current = null;
let activeTab = "bugs";

function el(tag, props = {}, ...children) {
  const node = document.createElement(tag);
  Object.assign(node, props);
  for (const child of children) node.append(child);
  return node;
}

function highlighted(code, language) {
  const pre = el("pre");
  const codeEl = el("code", { textContent: code });
  const lang = HLJS_LANG[language];
  if (lang) codeEl.className = `language-${lang}`;
  pre.append(codeEl);
  if (window.hljs) window.hljs.highlightElement(codeEl);
  return pre;
}

// ---------- input ----------
document.querySelectorAll("#input-tabs .tab").forEach((tab) =>
  tab.addEventListener("click", () => {
    inputKind = tab.dataset.input;
    document.querySelectorAll("#input-tabs .tab").forEach((t) => t.classList.toggle("active", t === tab));
    document.querySelectorAll(".input-pane").forEach((p) => (p.hidden = p.dataset.pane !== inputKind));
  }),
);

async function buildRequest() {
  if (inputKind === "github") return { kind: "github", url: $("#url").value };
  if (inputKind === "paste") return { kind: "paste", code: $("#paste-code").value, filename: $("#paste-filename").value };
  const file = $("#file").files[0];
  if (!file) throw new Error("Choose a file to upload.");
  return { kind: "upload", code: await file.text(), filename: file.name };
}

$("#review-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const button = $("#submit");
  $("#error").hidden = true;
  button.disabled = true;
  const started = Date.now();
  const timer = setInterval(() => ($("#status").textContent = `Reviewing… ${Math.round((Date.now() - started) / 1000)}s`), 500);
  try {
    const res = await fetch("/api/review", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(await buildRequest()),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || `Request failed (${res.status})`);
    render(data);
    loadHistory();
    $("#status").textContent = `Done in ${Math.round((Date.now() - started) / 1000)}s`;
  } catch (err) {
    $("#error").textContent = err.message;
    $("#error").hidden = false;
    $("#status").textContent = "";
  } finally {
    clearInterval(timer);
    button.disabled = false;
  }
});

// ---------- history ----------
async function loadHistory() {
  const list = $("#history-list");
  const items = await fetch("/api/reviews").then((r) => r.json()).catch(() => []);
  list.replaceChildren();
  if (!items.length) return list.append(el("li", { className: "muted small", textContent: "No reviews yet" }));
  for (const item of items) {
    const btn = el(
      "button",
      { title: new Date(item.createdAt).toLocaleString() },
      el("span", { className: "name", textContent: item.filename }),
      el("span", { className: "muted", textContent: `${item.score} ${item.grade}` }),
    );
    btn.addEventListener("click", async () => render(await fetch(`/api/reviews/${encodeURIComponent(item.id)}`).then((r) => r.json())));
    list.append(el("li", {}, btn));
  }
}

// ---------- results ----------
function render(report) {
  current = report;
  const { review, score } = report;
  $("#results").hidden = false;

  $("#file-title").textContent = report.source.filename;
  $("#meta").textContent = `${review.language} · ${report.source.url ?? report.source.kind} · ${report.model} · ${new Date(report.createdAt).toLocaleString()}`;
  $("#summary").textContent = review.summary;
  $("#score").textContent = score.value;
  $("#grade").textContent = score.grade;
  $("#gauge-fill").style.strokeDashoffset = String(326.7 * (1 - score.value / 100));
  $("#export-md").href = `/api/reviews/${encodeURIComponent(report.id)}?format=md`;
  $("#export-json").href = URL.createObjectURL(new Blob([JSON.stringify(report, null, 2)], { type: "application/json" }));
  $("#export-json").download = `${report.id}.json`;

  $("#counts").replaceChildren(
    ...SEVERITIES.map((s) => el("span", { className: `pill sev-${s}`, textContent: `${score.counts[s]} ${s}` })),
  );
  $("#metrics").replaceChildren(
    ...Object.entries(review.metrics).map(([name, v]) => {
      const bar = el("div", { className: "bar" }, el("span"));
      bar.firstChild.style.width = `${Math.max(0, Math.min(10, v)) * 10}%`;
      return el("div", { className: "metric small" }, el("div", { textContent: `${name} ${v}/10` }), bar);
    }),
  );

  renderCode(report);
  renderTabs();
}

function renderCode(report) {
  const flags = new Map();
  const all = [...report.review.bugs, ...report.review.security, ...report.review.style];
  for (const f of all) {
    // Whole-file findings would tint every line; mark only where they start.
    const end = f.line_end - f.line_start > 15 ? f.line_start : Math.max(f.line_start, f.line_end);
    for (let n = f.line_start; n <= end; n++) {
      const prev = flags.get(n);
      if (!prev || SEVERITIES.indexOf(f.severity) < SEVERITIES.indexOf(prev)) flags.set(n, f.severity);
    }
  }
  const lang = HLJS_LANG[report.review.language];
  $("#code-filename").textContent = report.source.filename;
  $("#code").replaceChildren(
    ...report.code.split("\n").map((text, i) => {
      const n = i + 1;
      const src = el("span", { className: "src" });
      if (lang && window.hljs) src.innerHTML = window.hljs.highlight(text, { language: lang, ignoreIllegals: true }).value;
      else src.textContent = text;
      const line = el("div", { className: `line${flags.has(n) ? ` flag-${flags.get(n)}` : ""}`, id: `L${n}` },
        el("span", { className: "ln", textContent: n }), src);
      return line;
    }),
  );
}

const TABS = [
  ["bugs", "Bugs"],
  ["security", "Security"],
  ["style", "Style"],
  ["refactors", "Refactors"],
  ["tests", "Tests"],
];

function renderTabs() {
  const { review } = current;
  $("#result-tabs").replaceChildren(
    ...TABS.map(([key, label]) => {
      const count = key === "tests" ? null : review[key].length;
      const btn = el("button", { className: `tab${key === activeTab ? " active" : ""}`, role: "tab" }, label);
      if (count !== null) btn.append(el("span", { className: "badge", textContent: count }));
      btn.addEventListener("click", () => {
        activeTab = key;
        renderTabs();
      });
      return btn;
    }),
  );

  const body = $("#tab-body");
  body.replaceChildren();
  if (activeTab === "refactors") return renderRefactors(body, review);
  if (activeTab === "tests") return renderTests(body, review);

  const items = [...review[activeTab]].sort((a, b) => SEVERITIES.indexOf(a.severity) - SEVERITIES.indexOf(b.severity));
  if (!items.length) return body.append(el("div", { className: "empty", textContent: "No issues found." }));
  for (const f of items) {
    const card = el(
      "div",
      { className: `finding ${f.severity}` },
      el("div", { className: "finding-head" },
        el("span", { className: `pill sev-${f.severity}`, textContent: f.severity }),
        el("h3", { textContent: f.title }),
        el("span", { className: "lines", textContent: f.line_start === f.line_end ? `L${f.line_start}` : `L${f.line_start}–${f.line_end}` })),
      el("p", { textContent: f.description }),
      el("p", { className: "suggestion small", textContent: `→ ${f.suggestion}` }),
    );
    card.addEventListener("click", () => jumpTo(f.line_start, f.line_end));
    body.append(card);
  }
}

function renderRefactors(body, review) {
  if (!review.refactors.length) return body.append(el("div", { className: "empty", textContent: "No refactors suggested." }));
  for (const r of review.refactors) {
    body.append(
      el("div", { className: "refactor" },
        el("h3", { textContent: r.title }),
        el("p", { className: "small", textContent: r.rationale }),
        el("span", { className: "label", textContent: "Before" }), highlighted(r.before, review.language),
        el("span", { className: "label", textContent: "After" }), highlighted(r.after, review.language)),
    );
  }
}

function renderTests(body, review) {
  const t = review.tests;
  const copy = el("button", { className: "button", type: "button", textContent: "Copy" });
  copy.addEventListener("click", async () => {
    await navigator.clipboard.writeText(t.code);
    copy.textContent = "Copied";
    setTimeout(() => (copy.textContent = "Copy"), 1500);
  });
  const download = el("a", {
    className: "button",
    textContent: `Download ${t.filename}`,
    href: URL.createObjectURL(new Blob([t.code], { type: "text/plain" })),
    download: t.filename,
  });
  body.append(
    el("div", { className: "tests-head" },
      el("span", { className: "small muted", textContent: `Framework: ${t.framework} · Result: ${t.result ?? "not run"}` }),
      el("div", { className: "export" }, copy, download)),
    el("p", { className: "small", textContent: t.notes }),
    highlighted(t.code, review.language),
  );
}

function jumpTo(start, end) {
  const first = document.getElementById(`L${start}`);
  if (!first) return;
  first.scrollIntoView({ behavior: "smooth", block: "center" });
  for (let n = start; n <= Math.max(start, end); n++) {
    const line = document.getElementById(`L${n}`);
    if (!line) continue;
    line.classList.add("pulse");
    setTimeout(() => line.classList.remove("pulse"), 1600);
  }
}

loadHistory();
