/* ===== 计算机修行录 - 导航 & 设置面板 v3 =====
 * 统一管理：设置面板、登出、未读消息标记
 * 需要在 api.js + store.js 之后加载
 */

(function() {
  'use strict';

  // 注入设置面板 HTML 到 body
  function injectSettingsPanel() {
    if (document.getElementById('settingsOverlay')) return; // 已注入
    var html =
      '<div class="settings-overlay" id="settingsOverlay">' +
        '<div class="settings-panel" onclick="event.stopPropagation()">' +
          '<div class="settings-header">' +
            '<div class="settings-avatar" id="settingsAvatar"></div>' +
            '<div class="settings-user">' +
              '<div class="settings-username" id="settingsName"></div>' +
              '<div class="settings-level" id="settingsLevel"></div>' +
            '</div>' +
          '</div>' +
          '<ul class="settings-menu">' +
            '<li><a href="profile.html" class="settings-link"><span class="settings-icon">✎</span>编辑资料</a></li>' +
            '<li><a href="messages.html" class="settings-link"><span class="settings-icon">✉</span>消息中心</a></li>' +
            '<li><button onclick="navLogout()" class="settings-danger"><span class="settings-icon">🚪</span>退出登录</button></li>' +
          '</ul>' +
        '</div>' +
      '</div>';
    var div = document.createElement('div');
    div.innerHTML = html;
    document.body.appendChild(div.firstElementChild);

    // 点击遮罩关闭
    document.getElementById('settingsOverlay').addEventListener('click', function(e) {
      if (e.target === this) closeSettings();
    });
  }

  // 打开设置面板
  window.openSettings = function() {
    var overlay = document.getElementById('settingsOverlay');
    if (!overlay) { injectSettingsPanel(); overlay = document.getElementById('settingsOverlay'); }
    // 刷新用户信息
    var avEl = document.getElementById('settingsAvatar');
    if (avEl) {
      var av = (typeof USER !== 'undefined' ? USER.avatar : '') || '?';
      if (av.startsWith && av.startsWith('data:image/')) {
        avEl.innerHTML = '<img src="' + av + '" alt="">';
      } else {
        avEl.textContent = av[0] || '?';
      }
    }
    var nmEl = document.getElementById('settingsName');
    if (nmEl) nmEl.textContent = (typeof USER !== 'undefined' ? USER.name : '') || '修炼者';
    var lvEl = document.getElementById('settingsLevel');
    if (lvEl) {
      if (typeof USER !== 'undefined' && typeof LEVELS !== 'undefined' && USER.level !== undefined) {
        lvEl.textContent = LEVELS[USER.level] ? LEVELS[USER.level].name : '修炼者';
      } else {
        lvEl.textContent = '';
      }
    }
    overlay.classList.add('show');
  };

  // 关闭设置面板
  window.closeSettings = function() {
    var overlay = document.getElementById('settingsOverlay');
    if (overlay) overlay.classList.remove('show');
  };

  // 退出登录
  window.navLogout = function() {
    if (typeof api !== 'undefined' && api.logout) {
      api.logout();
    } else {
      localStorage.removeItem('cultivation_token');
      localStorage.removeItem('cultivation_user');
      window.location.href = 'login.html';
    }
  };

  // ESC 关闭
  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') closeSettings();
  });

  // 更新消息未读标记
  window.updateMsgBadge = function() {
    var badge = document.getElementById('navMsgLink');
    if (!badge) return;
    if (typeof MESSAGES !== 'undefined') {
      var unread = MESSAGES.filter(function(m) { return m.unread; }).length;
      if (unread > 0) {
        badge.classList.add('has-unread');
      } else {
        badge.classList.remove('has-unread');
      }
    }
  };

  // DOM 就绪后注入
  function ready(fn) {
    if (document.readyState !== 'loading') { fn(); return; }
    document.addEventListener('DOMContentLoaded', fn);
  }

  ready(function() {
    injectSettingsPanel();
    updateMsgBadge();
  });
})();
