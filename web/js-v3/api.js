/* ===== 计算机修行录 - API 层 v3 =====
 * 所有后端通信集中在此
 */

// API 基地址：部署模式下用同源，本地开发用 localhost
var API_BASE = (function() {
  var origin = window.location.origin;
  if (origin.indexOf('file:') === 0 || origin.indexOf('127.0.0.1') >= 0 || origin.indexOf('localhost') >= 0) {
    return 'http://127.0.0.1:8001';
  }
  return origin;
})();

var AUTH_TOKEN = localStorage.getItem('cultivation_token');

function apiFetch(url, options) {
  options = options || {};
  options.headers = options.headers || {};
  options.headers['Authorization'] = 'Bearer ' + (AUTH_TOKEN || '');

  // 10 秒超时（微信 WebView 可能卡住不返回）
  var controller = new AbortController();
  options.signal = controller.signal;
  var timeoutId = setTimeout(function() { controller.abort(); }, 10000);

  return fetch(url, options).then(function(r) {
    clearTimeout(timeoutId);
    if (r.status === 401) {
      localStorage.removeItem('cultivation_token');
      localStorage.removeItem('cultivation_user');
      window.location.href = 'login.html';
    }
    return r;
  });
}

// ---- 认证 ----
var api = {
  register: function(username, password) {
    return apiFetch(API_BASE + '/api/auth/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username: username, password: password })
    }).then(function(r) { return r.json(); });
  },

  login: function(username, password) {
    return apiFetch(API_BASE + '/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username: username, password: password })
    }).then(function(r) { return r.json(); });
  },

  logout: function() {
    apiFetch(API_BASE + '/api/auth/logout', { method: 'POST' }).catch(function() {});
    localStorage.removeItem('cultivation_token');
    localStorage.removeItem('cultivation_user');
    window.location.href = 'login.html';
  },

  // ---- 状态 ----
  getState: function() {
    return apiFetch(API_BASE + '/api/state')
      .then(function(r) { return r.json(); });
  },

  // ---- 任务 ----
  completeTask: function(levelId, taskIdx) {
    return apiFetch(API_BASE + '/api/tasks/complete', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ level_id: levelId, task_idx: taskIdx })
    }).then(function(r) { return r.json(); });
  },

  undoTask: function(levelId, taskIdx) {
    return apiFetch(API_BASE + '/api/tasks/undo', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ level_id: levelId, task_idx: taskIdx })
    }).then(function(r) { return r.json(); });
  },

  // ---- 考核 ----
  getQuizQuestions: function(levelId) {
    return apiFetch(API_BASE + '/api/quiz/questions/' + levelId)
      .then(function(r) { return r.json(); });
  },

  submitQuiz: function(levelId, questionIds, answers) {
    return apiFetch(API_BASE + '/api/quiz/submit', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ level_id: levelId, question_ids: questionIds, answers: answers })
    }).then(function(r) { return r.json(); });
  },

  // ---- 消息 ----
  getMessages: function(page, limit) {
    page = page || 1;
    limit = limit || 50;
    return apiFetch(API_BASE + '/api/messages?page=' + page + '&limit=' + limit)
      .then(function(r) { return r.json(); });
  },

  addMessage: function(msg) {
    return apiFetch(API_BASE + '/api/messages', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(msg)
    }).then(function(r) { return r.json(); });
  },

  updateMessage: function(id, msg) {
    return apiFetch(API_BASE + '/api/messages/' + id, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(msg)
    }).then(function(r) { return r.json(); });
  },

  deleteMessage: function(id) {
    return apiFetch(API_BASE + '/api/messages/' + id, { method: 'DELETE' })
      .then(function(r) { return r.json(); });
  },

  markAllRead: function() {
    return apiFetch(API_BASE + '/api/messages/read-all', { method: 'PUT' })
      .then(function(r) { return r.json(); });
  },

  // ---- 感悟 ----
  getJournals: function(page, limit) {
    page = page || 1;
    limit = limit || 20;
    return apiFetch(API_BASE + '/api/journals?page=' + page + '&limit=' + limit)
      .then(function(r) { return r.json(); });
  },

  // ---- 个人资料 ----
  updateProfile: function(data) {
    return apiFetch(API_BASE + '/api/user/profile', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    }).then(function(r) { return r.json(); });
  },

  addJournal: function(journal) {
    return apiFetch(API_BASE + '/api/journals', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(journal)
    }).then(function(r) { return r.json(); });
  },

  deleteJournal: function(id) {
    return apiFetch(API_BASE + '/api/journals/' + id, { method: 'DELETE' })
      .then(function(r) { return r.json(); });
  },

  // ---- 社区帖子 ----
  getPosts: function(sort, page, limit) {
    var q = 'sort=' + (sort || 'newest') + '&page=' + (page || 1) + '&limit=' + (limit || 20);
    return apiFetch(API_BASE + '/api/posts?' + q).then(function(r) { return r.json(); });
  },
  createPost: function(data) {
    return apiFetch(API_BASE + '/api/posts', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    }).then(function(r) { return r.json(); });
  },
  getPost: function(postId) {
    return apiFetch(API_BASE + '/api/posts/' + postId).then(function(r) { return r.json(); });
  },
  updatePost: function(postId, data) {
    return apiFetch(API_BASE + '/api/posts/' + postId, {
      method: 'PUT', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    }).then(function(r) { return r.json(); });
  },
  deletePost: function(postId) {
    return apiFetch(API_BASE + '/api/posts/' + postId, { method: 'DELETE' })
      .then(function(r) { return r.json(); });
  },

  // ---- 评论 ----
  getComments: function(postId) {
    return apiFetch(API_BASE + '/api/posts/' + postId + '/comments')
      .then(function(r) { return r.json(); });
  },
  addComment: function(postId, content, parentId) {
    return apiFetch(API_BASE + '/api/posts/' + postId + '/comments', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content: content, parent_id: parentId || null })
    }).then(function(r) { return r.json(); });
  },
  deleteComment: function(postId, commentId) {
    return apiFetch(API_BASE + '/api/posts/' + postId + '/comments/' + commentId, { method: 'DELETE' })
      .then(function(r) { return r.json(); });
  },

  // ---- 投票 ----
  vote: function(targetType, targetId, value) {
    return apiFetch(API_BASE + '/api/votes', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ target_type: targetType, target_id: targetId, value: value })
    }).then(function(r) { return r.json(); });
  },

  // ---- 用户搜索 & 公开主页 ----
  searchUsers: function(q) {
    return apiFetch(API_BASE + '/api/users/search?q=' + encodeURIComponent(q))
      .then(function(r) { return r.json(); });
  },
  getPublicProfile: function(userId) {
    return apiFetch(API_BASE + '/api/users/' + userId).then(function(r) { return r.json(); });
  },

  // ---- 私信 ----
  getConversations: function() {
    return apiFetch(API_BASE + '/api/dms/conversations').then(function(r) { return r.json(); });
  },
  getDMs: function(otherUserId, since) {
    var url = API_BASE + '/api/dms/' + otherUserId + '?limit=50';
    if (since) url += '&since=' + encodeURIComponent(since);
    return apiFetch(url).then(function(r) { return r.json(); });
  },
  sendDM: function(otherUserId, content) {
    return apiFetch(API_BASE + '/api/dms/' + otherUserId, {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content: content })
    }).then(function(r) { return r.json(); });
  },

  // ---- 排行榜 ----
  getLeaderboard: function() {
    return apiFetch(API_BASE + '/api/leaderboard').then(function(r) { return r.json(); });
  }
};
