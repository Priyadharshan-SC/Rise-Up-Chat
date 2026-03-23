/* ══════════════════════════════════════
   CONFIG
══════════════════════════════════════ */
const API_BASE   = 'http://127.0.0.1:8000';
const CHAT_URL   = API_BASE + '/chat/';
const CHATS_URL  = API_BASE + '/chats/';
const SOS_URL    = API_BASE + '/chats/sos';
const MAX_CHARS  = 500;
const FETCH_TIMEOUT_MS = 60000;

/* ══════════════════════════════════════
   STATE
══════════════════════════════════════ */
let currentChatId   = null;
let isWaiting       = false;
let voiceActive     = false;
let recognition     = null;
let currentCrisisChatId = null;

/* ══════════════════════════════════════
   INIT
══════════════════════════════════════ */
document.addEventListener('DOMContentLoaded', () => {
  applyTheme();
  bindInput();
  checkConnection();
  loadChatList();
});

/* ══════════════════════════════════════
   CONNECTION CHECK
══════════════════════════════════════ */
async function checkConnection() {
  const el   = document.getElementById('connStatus');
  const text = document.getElementById('connText');
  const sub  = document.getElementById('hdrStatus');
  el.className = 'conn-status checking';
  text.textContent = 'Checking server…';
  try {
    const r = await Promise.race([
      fetch(API_BASE + '/api/health'),
      new Promise((_, rej) => setTimeout(() => rej(new Error('timeout')), 5000)),
    ]);
    if (r.ok) {
      el.className = 'conn-status online';
      text.textContent = 'Server online';
      sub.textContent = '● Online';
    } else {
      throw new Error('not ok');
    }
  } catch {
    el.className = 'conn-status offline';
    text.textContent = 'Server unreachable';
    sub.textContent = '● Disconnected';
  }
}

/* ══════════════════════════════════════
   CHAT SESSION MANAGEMENT
══════════════════════════════════════ */
async function loadChatList() {
  try {
    const r = await fetch(CHATS_URL);
    if (!r.ok) return;
    const chats = await r.json();
    renderChatList(chats);
  } catch { /* server may be off */ }
}

function renderChatList(chats) {
  const list = document.getElementById('chatList');
  list.innerHTML = '';
  if (!chats.length) {
    list.innerHTML = '<div class="chat-empty">No chats yet</div>';
    return;
  }
  chats.forEach(c => {
    const item = document.createElement('div');
    item.className = 'chat-item' + (c.chat_id === currentChatId ? ' active' : '');
    item.dataset.id = c.chat_id;
    item.innerHTML = `
      <span class="chat-item-title" onclick="switchChat('${c.chat_id}', this.closest('.chat-item'))">${escHtml(c.title)}</span>
      <button class="chat-item-del" onclick="deleteChat('${c.chat_id}')" title="Delete">🗑</button>
    `;
    list.appendChild(item);
  });
}

async function createNewChat() {
  try {
    const r = await fetch(CHATS_URL, { method: 'POST' });
    if (!r.ok) return showToast('Could not create chat', 'error');
    const chat = await r.json();
    currentChatId = chat.chat_id;
    clearMsgs();
    await loadChatList();
    document.getElementById('hdrTitle').textContent = 'New Chat';
    closeSidebar();
  } catch { showToast('Server unavailable', 'error'); }
}

function newChatFromHeader() { createNewChat(); }

async function switchChat(chatId, el) {
  currentChatId = chatId;
  document.querySelectorAll('.chat-item').forEach(i => i.classList.remove('active'));
  el.classList.add('active');
  clearMsgs();
  try {
    const r = await fetch(CHATS_URL + chatId);
    if (!r.ok) return;
    const history = await r.json();
    document.getElementById('hdrTitle').textContent =
      el.querySelector('.chat-item-title').textContent;
    history.forEach(row => {
      appendUserMsg(row.user_message);
      appendBotMsg(row.reply, row.emotion, row.risk_level, row.response_source, row.safe);
    });
  } catch { showToast('Could not load history', 'error'); }
  closeSidebar();
}

async function deleteChat(chatId) {
  if (!confirm('Delete this chat?')) return;
  try {
    await fetch(CHATS_URL + chatId, { method: 'DELETE' });
    if (currentChatId === chatId) {
      currentChatId = null;
      clearMsgs();
      document.getElementById('hdrTitle').textContent = 'Solace AI';
    }
    await loadChatList();
  } catch { showToast('Could not delete chat', 'error'); }
}

/* ══════════════════════════════════════
   SENDING MESSAGES
══════════════════════════════════════ */
async function sendMessage() {
  const inp = document.getElementById('inp');
  const msg = inp.value.trim();
  if (!msg || isWaiting) return;
  if (msg.length > MAX_CHARS) return showToast(`Max ${MAX_CHARS} characters`, 'warn');

  inp.value = '';
  inp.style.height = 'auto';
  updateCharHint('');
  hideWelcome();
  appendUserMsg(msg);
  showTyping();
  setWaiting(true);

  try {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), FETCH_TIMEOUT_MS);

    const r = await fetch(CHAT_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: msg, chat_id: currentChatId }),
      signal: controller.signal,
    });
    clearTimeout(timer);

    if (!r.ok) {
      const err = await r.json().catch(() => ({}));
      throw new Error(err.detail || `HTTP ${r.status}`);
    }

    const data = await r.json();

    // Remember the current chat session
    if (!currentChatId) {
      currentChatId = data.chat_id;
      await loadChatList();
    }

    removeTyping();
    appendBotMsg(data.reply, data.emotion, data.risk_level, data.response_source, data.safe);

    // Show crisis panel if triggered
    if (!data.safe || data.risk_level === 'crisis') {
      currentCrisisChatId = data.chat_id;
      showCrisisPanel();
    }

  } catch (e) {
    removeTyping();
    const errMsg = e.name === 'AbortError'
      ? 'Request timed out (60s). Make sure Ollama is running: `ollama serve`'
      : e.message || 'Unexpected error';
    appendErrorCard(errMsg);
  } finally {
    setWaiting(false);
  }
}

/* ══════════════════════════════════════
   RENDER MESSAGES
══════════════════════════════════════ */
function appendUserMsg(text) {
  const msgs = document.getElementById('msgs');
  const div  = document.createElement('div');
  div.className = 'msg user';
  div.innerHTML = `<div class="bubble">${escHtml(text)}</div><div class="avatar user-av">yo</div>`;
  const time = document.createElement('div');
  time.className = 'msg-time';
  time.textContent = nowTime();
  div.appendChild(time);
  msgs.appendChild(div);
  scrollBottom();
}

function appendBotMsg(reply, emotion, riskLevel, source, safe) {
  const msgs = document.getElementById('msgs');
  const div  = document.createElement('div');
  div.className = 'msg bot';

  const emoteMeta = EMOTE_META[emotion] || EMOTE_META['neutral'];
  const riskBadge = buildRiskBadge(riskLevel || 'low');
  const srcBadge  = source === 'llm'
    ? '<span class="src-badge llm">🧠 LLM</span>'
    : '<span class="src-badge fast">⚡ Fast</span>';

  div.innerHTML = `
    <div class="avatar bot-av">${emoteMeta.icon}</div>
    <div class="bubble-wrap">
      <div class="bubble">${escHtml(reply)}</div>
      <div class="meta-row">
        <span class="emo-badge">${emoteMeta.icon} ${capitalize(emotion)}</span>
        ${riskBadge}
        ${srcBadge}
        <span class="msg-time">${nowTime()}</span>
      </div>
    </div>`;
  msgs.appendChild(div);
  scrollBottom();
}

function buildRiskBadge(level) {
  const map = {
    crisis: { label: '🚨 Crisis',   cls: 'risk-crisis'  },
    high:   { label: '🔴 High',     cls: 'risk-high'    },
    medium: { label: '🟡 Medium',   cls: 'risk-medium'  },
    low:    { label: '🟢 Low',      cls: 'risk-low'     },
  };
  const m = map[level] || map.low;
  return `<span class="risk-badge ${m.cls}">${m.label}</span>`;
}

function appendErrorCard(msg) {
  const msgs = document.getElementById('msgs');
  const div  = document.createElement('div');
  div.className = 'error-card';
  div.innerHTML = `
    <div class="error-title">⚠️ Error</div>
    <div class="error-msg">${escHtml(msg)}</div>`;
  msgs.appendChild(div);
  scrollBottom();
}

function showTyping() {
  const msgs = document.getElementById('msgs');
  const div  = document.createElement('div');
  div.id = 'typing';
  div.className = 'msg bot';
  div.innerHTML = `<div class="avatar bot-av">🧘</div>
    <div class="bubble typing-bubble"><span></span><span></span><span></span></div>`;
  msgs.appendChild(div);
  scrollBottom();
}

function removeTyping() {
  const t = document.getElementById('typing');
  if (t) t.remove();
}

/* ══════════════════════════════════════
   CRISIS PANEL
══════════════════════════════════════ */
function showCrisisPanel() {
  document.getElementById('crisisPanel').style.display = 'flex';
}

function closeCrisisPanel() {
  document.getElementById('crisisPanel').style.display = 'none';
}

async function triggerSOS() {
  if (!currentCrisisChatId) return;
  try {
    await fetch(`${SOS_URL}?chat_id=${currentCrisisChatId}`, { method: 'POST' });
    const btn = document.getElementById('sosBtn');
    btn.textContent = '✅ SOS Logged';
    btn.disabled = true;
    showToast('SOS logged. Stay safe. 💙', 'info');
  } catch { showToast('Could not log SOS', 'error'); }
}

/* ══════════════════════════════════════
   INPUT HELPERS
══════════════════════════════════════ */
function bindInput() {
  const inp = document.getElementById('inp');

  inp.addEventListener('keydown', e => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  });

  inp.addEventListener('input', () => {
    inp.style.height = 'auto';
    inp.style.height = Math.min(inp.scrollHeight, 140) + 'px';
    const left = MAX_CHARS - inp.value.length;
    updateCharHint(left < 80 ? `${left} characters left` : '');
  });
}

function updateCharHint(msg) {
  document.getElementById('charHint').textContent = msg;
}

function useSuggestion(text) {
  const inp = document.getElementById('inp');
  inp.value = text;
  inp.dispatchEvent(new Event('input'));
  inp.focus();
}

function setWaiting(v) {
  isWaiting = v;
  document.getElementById('sendBtn').disabled = v;
  document.getElementById('inp').disabled = v;
}

function hideWelcome() {
  const w = document.getElementById('welcome');
  if (w) w.style.display = 'none';
}

function clearMsgs() {
  const msgs = document.getElementById('msgs');
  msgs.innerHTML = '';
  // Re-add welcome screen
  const welcome = document.createElement('div');
  welcome.id = 'welcome';
  welcome.className = 'welcome';
  welcome.innerHTML = `
    <div class="welcome-orb">🫶</div>
    <h2>How are you feeling today?</h2>
    <p>I'm here to listen without judgment.<br/>Share anything — I'll support you through it.</p>
    <div class="chips">
      <button class="chip" onclick="useSuggestion(\`I've been feeling really stressed lately\`)">😣 I'm stressed</button>
      <button class="chip" onclick="useSuggestion(\`I feel sad and can't figure out why\`)">😔 I feel sad</button>
      <button class="chip" onclick="useSuggestion(\`I'm actually feeling great today!\`)">😊 I'm happy</button>
      <button class="chip" onclick="useSuggestion(\`I just need someone to talk to\`)">💬 Just talk</button>
    </div>`;
  msgs.appendChild(welcome);
}

function scrollBottom() {
  const msgs = document.getElementById('msgs');
  msgs.scrollTo({ top: msgs.scrollHeight, behavior: 'smooth' });
}

/* ══════════════════════════════════════
   VOICE
══════════════════════════════════════ */
function toggleVoice() {
  if (!('webkitSpeechRecognition' in window || 'SpeechRecognition' in window)) {
    return showToast('Voice not supported in this browser', 'warn');
  }
  if (voiceActive) {
    recognition?.stop();
    return;
  }
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  recognition = new SR();
  recognition.lang = 'en-US';
  recognition.interimResults = false;
  recognition.onstart = () => {
    voiceActive = true;
    document.getElementById('voiceBtn').classList.add('recording');
  };
  recognition.onresult = e => {
    document.getElementById('inp').value = e.results[0][0].transcript;
    document.getElementById('inp').dispatchEvent(new Event('input'));
  };
  recognition.onend = () => {
    voiceActive = false;
    document.getElementById('voiceBtn').classList.remove('recording');
  };
  recognition.start();
}

/* ══════════════════════════════════════
   SIDEBAR & THEME
══════════════════════════════════════ */
function toggleSidebar() {
  const sb = document.getElementById('sidebar');
  const ov = document.getElementById('overlay');
  sb.classList.toggle('open');
  ov.classList.toggle('visible');
}

function closeSidebar() {
  document.getElementById('sidebar').classList.remove('open');
  document.getElementById('overlay').classList.remove('visible');
}

function applyTheme() {
  const saved = localStorage.getItem('solace-theme') || 'dark';
  document.documentElement.setAttribute('data-theme', saved);
  updateThemeBtn(saved);
}

function toggleTheme() {
  const current = document.documentElement.getAttribute('data-theme');
  const next    = current === 'dark' ? 'light' : 'dark';
  document.documentElement.setAttribute('data-theme', next);
  localStorage.setItem('solace-theme', next);
  updateThemeBtn(next);
}

function updateThemeBtn(theme) {
  const isDark = theme === 'dark';
  ['themeIco', 'hdrThemeBtn'].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.textContent = isDark ? '☀️' : '🌙';
  });
  const lbl = document.getElementById('themeLabel');
  if (lbl) lbl.textContent = isDark ? 'Light Mode' : 'Dark Mode';
}

/* ══════════════════════════════════════
   TOAST
══════════════════════════════════════ */
function showToast(msg, type = 'info') {
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.className = `toast ${type} show`;
  setTimeout(() => t.className = 'toast', 3000);
}

/* ══════════════════════════════════════
   UTILS
══════════════════════════════════════ */
const EMOTE_META = {
  sad:     { icon: '😔' },
  anxious: { icon: '😣' },
  angry:   { icon: '😡' },
  happy:   { icon: '😊' },
  neutral: { icon: '💬' },
  crisis:  { icon: '🚨' },
};

function escHtml(t) {
  return String(t).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

function capitalize(s) {
  return s ? s.charAt(0).toUpperCase() + s.slice(1) : '';
}

function nowTime() {
  return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}