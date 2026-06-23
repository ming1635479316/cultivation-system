/* ===== 计算机修行录 - 状态管理 v3 =====
 * 后端为唯一可信数据源。
 * 前端只做缓存，stats/progress 由服务端返回。
 */

// ---- 登录检查 ----
var AUTH_TOKEN = localStorage.getItem('cultivation_token');
var AUTH_USER = null;
try { AUTH_USER = JSON.parse(localStorage.getItem('cultivation_user')); } catch(e) {}

if (!AUTH_TOKEN) {
  window.location.href = 'login.html';
}

// ---- 同步加载状态 ----
var STORE_READY = false;
var STORE_ERROR = null;

// 注入加载提示样式（仅在页面有 body 时生效）
(function injectLoadingStyle() {
  if (typeof document === 'undefined') return;
  var style = document.createElement('style');
  style.textContent =
    '.sync-loading {' +
      'position:fixed;top:0;left:0;right:0;z-index:9999;' +
      'padding:6px 12px;text-align:center;font-size:13px;' +
      'background:var(--seal,#c0392b);color:#fff;' +
      'display:flex;align-items:center;justify-content:center;gap:6px;' +
    '}' +
    '.sync-loading.done { background:#16a34a; }' +
    '.sync-loading.error { background:#d97706; }' +
    '.sync-loading .dot { display:inline-block;width:6px;height:6px;border-radius:50%;background:#fff;animation:syncPulse 1s infinite; }' +
    '.sync-loading .dot:nth-child(2){animation-delay:0.2s}' +
    '.sync-loading .dot:nth-child(3){animation-delay:0.4s}' +
    '@keyframes syncPulse{0%,100%{opacity:0.3}50%{opacity:1}}';
  document.head.appendChild(style);
})();

function showSyncBar(msg, type) {
  var el = document.getElementById('syncBar');
  if (!el) {
    el = document.createElement('div');
    el.id = 'syncBar';
    el.className = 'sync-loading';
    document.body.insertBefore(el, document.body.firstChild);
  }
  el.className = 'sync-loading' + (type ? ' ' + type : '');
  el.innerHTML = msg;
}

function hideSyncBar(delay) {
  delay = delay || 1500;
  var el = document.getElementById('syncBar');
  if (!el) return;
  setTimeout(function() {
    if (el.parentNode) el.parentNode.removeChild(el);
  }, delay);
}

// ---- 存储键（按用户隔离）----
var STORAGE_KEY = 'cultivation_v3_' + (AUTH_USER ? AUTH_USER.id : '0');

// ---- 全局状态 ----
var USER = {
  name: AUTH_USER ? AUTH_USER.name : '易',
  avatar: AUTH_USER ? AUTH_USER.avatar : '易',
  title: '修炼者',
  level: 0,
  gender: '',
  age: '',
  contact: '',
  joinedDate: '2026-06-13',
  specializations: [],
  completedTasks: [],
  journals: [],
  stats: null,      // 由后端 GET /api/state 或各 API 返回
  progress: 0
};

var EVENT_LOG = [];
var MESSAGES = [];

// ---- 从 localStorage 加载缓存 ----
function cacheLoad() {
  try {
    var raw = localStorage.getItem(STORAGE_KEY);
    if (raw) {
      var data = JSON.parse(raw);
      if (data.user) {
        USER.name = data.user.name || USER.name;
        USER.avatar = data.user.avatar || USER.avatar;
        USER.title = data.user.title || '修炼者';
        USER.level = data.user.level || 0;
        USER.gender = data.user.gender || '';
        USER.age = data.user.age || '';
        USER.contact = data.user.contact || '';
        USER.joinedDate = data.user.joinedDate || data.user.joined_date || USER.joinedDate;
        USER.specializations = data.user.specializations || [];
        USER.completedTasks = data.user.completedTasks || data.user.completed_tasks || [];
        USER.journals = data.user.journals || [];
      }
      if (data.events) EVENT_LOG = data.events;
      if (data.messages) MESSAGES = data.messages;
    }
  } catch(e) {}
}

function cacheSave() {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify({
      user: {
        name: USER.name, avatar: USER.avatar, title: USER.title,
        level: USER.level, gender: USER.gender, age: USER.age,
        contact: USER.contact, joinedDate: USER.joinedDate,
        specializations: USER.specializations, completedTasks: USER.completedTasks,
        journals: USER.journals
      },
      events: EVENT_LOG,
      messages: MESSAGES
    }));
    localStorage.setItem(STORAGE_KEY + '_mtime', new Date().toISOString());
  } catch(e) {}
}

// ---- 从服务端同步 ----
function syncFromServer(data) {
  if (!data || !data.user) return;

  var u = data.user;
  USER.name = u.name || USER.name;
  USER.avatar = u.avatar || USER.avatar;
  USER.title = u.title || USER.title;
  USER.level = u.level || 0;
  USER.gender = u.gender || '';
  USER.age = u.age || '';
  USER.contact = u.contact || '';
  USER.joinedDate = u.joinedDate || u.joined_date || USER.joinedDate;
  USER.specializations = u.specializations || [];
  USER.completedTasks = u.completedTasks || u.completed_tasks || [];
  USER.journals = data.journals || [];

  // 直接用后端计算的 stats/progress
  USER.stats = data.stats || null;
  USER.progress = data.progress || 0;

  EVENT_LOG = data.events || [];
  MESSAGES = data.messages || [];

  cacheSave();
}

// 更新状态（增量 API 返回后调用）
function applyServerResult(res) {
  if (!res || !res.ok) return false;
  if (res.stats) USER.stats = res.stats;
  if (res.progress !== undefined) USER.progress = res.progress;
  if (res.level !== undefined) USER.level = res.level;
  if (res.completedTasks) USER.completedTasks = res.completedTasks;
  if (res.new_level) {
    USER.level = res.new_level;
  }
  cacheSave();
  return true;
}

// ---- 启动：从服务端拉数据 ----
function initStore(callback) {
  cacheLoad();

  // 如果缓存里有数据，先用缓存渲染（不阻塞 UI）
  var hasCache = MESSAGES.length > 0 || USER.completedTasks.length > 0 || USER.level > 0;

  showSyncBar('<span class="dot"></span><span class="dot"></span><span class="dot"></span> 同步中...');

  api.getState().then(function(data) {
    if (data && data.user) {
      syncFromServer(data);
      STORE_READY = true;
      STORE_ERROR = null;
      showSyncBar('✓ 同步完成', 'done');
      hideSyncBar(1200);
    } else {
      cacheLoad();
      STORE_READY = true;
      hideSyncBar(0);
    }
    if (callback) callback();
  }).catch(function(e) {
    cacheLoad();
    STORE_READY = true;
    STORE_ERROR = '网络连接失败，显示的是本地缓存数据';
    showSyncBar('⚠ ' + STORE_ERROR, 'error');
    hideSyncBar(4000);
    if (callback) callback();
  });
}
