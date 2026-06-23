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

  api.getState().then(function(data) {
    if (data && data.user) {
      syncFromServer(data);
    } else {
      // 服务端无数据，尝试用缓存
      cacheLoad();
    }
    if (callback) callback();
  }).catch(function() {
    // 网络失败，用缓存兜底
    cacheLoad();
    if (callback) callback();
  });
}
