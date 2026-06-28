/* ===== 计算机修行录 - 社交功能共享工具 v3.5 ===== */

// 时间格式化
// showExact: true = 显示精确到分钟的绝对时间
function formatTime(iso, showExact) {
  if (!iso) return '';
  var now = Date.now();
  var then = new Date(iso + (iso.endsWith('Z') ? '' : 'Z')).getTime();
  var diff = Math.floor((now - then) / 1000);
  var rel;
  if (diff < 60) rel = '刚刚';
  else if (diff < 3600) rel = Math.floor(diff / 60) + '分钟前';
  else if (diff < 86400) rel = Math.floor(diff / 3600) + '小时前';
  else if (diff < 604800) rel = Math.floor(diff / 86400) + '天前';
  else rel = iso.slice(0, 10);

  if (showExact) {
    var exact = iso.slice(0, 16).replace('T', ' '); // "2026-06-28 14:35"
    return '<span title="' + exact + '">' + rel + ' · ' + exact + '</span>';
  }
  return rel;
}

// HTML 转义（防 XSS）
function escapeHtml(str) {
  if (!str) return '';
  return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;').replace(/'/g, '&#x27;');
}

// 用户小头像+名字 HTML 片段
function renderAuthor(user, showLevel) {
  if (!user) return '';
  var av = user.avatar || '';

  // 头像 HTML：支持图片和文字两种模式
  var avatarHtml;
  if (av && av.startsWith('data:image/')) {
    avatarHtml = '<span class="author-avatar avatar-has-img" style="background:transparent;">'
      + '<img src="' + av + '" alt="" class="avatar-img">'
      + '</span>';
  } else {
    var ch = (av || user.name || '?')[0];
    avatarHtml = '<span class="author-avatar">' + escapeHtml(ch) + '</span>';
  }

  var name = escapeHtml(user.name || user.username || '?');
  var levelBadge = '';
  if (showLevel !== false) {
    var title = user.title || '修炼者';
    var level = (user.level !== undefined) ? user.level : 0;
    levelBadge = '<span class="author-level">' + title + ' · ' + levelName(level) + '</span>';
  }
  return '<span class="author-chip" onclick="event.stopPropagation();location.href=\'user.html?id=' + (user.id || user.user_id) + '\'">'
    + avatarHtml
    + '<span class="author-name">' + name + '</span>'
    + levelBadge + '</span>';
}

// 投票按钮 HTML
function renderVoteButtons(targetType, targetId, currentScore, userVote) {
  currentScore = currentScore || 0;
  userVote = userVote || 0;
  var upCls = userVote === 1 ? ' voted' : '';
  var downCls = userVote === -1 ? ' voted' : '';
  return '<span class="vote-group" data-type="' + targetType + '" data-id="' + targetId + '">'
    + '<button class="vote-btn vote-up' + upCls + '">▲</button>'
    + '<span class="vote-score">' + currentScore + '</span>'
    + '<button class="vote-btn vote-down' + downCls + '">▼</button>'
    + '</span>';
}

// 委托投票事件绑定
function bindVoteEvents(container, onVoteDone) {
  if (!container) return;
  container.querySelectorAll('.vote-btn').forEach(function(btn) {
    btn.addEventListener('click', function(e) {
      e.stopPropagation();
      e.preventDefault();
      var group = btn.closest('.vote-group');
      var targetType = group.dataset.type;
      var targetId = parseInt(group.dataset.id);
      var value = btn.classList.contains('vote-up') ? 1 : -1;
      api.vote(targetType, targetId, value).then(function(res) {
        if (res && res.ok !== false) {
          group.querySelector('.vote-score').textContent = res.vote_score;
          var upBtn = group.querySelector('.vote-up');
          var downBtn = group.querySelector('.vote-down');
          upBtn.classList.toggle('voted', res.user_vote === 1);
          downBtn.classList.toggle('voted', res.user_vote === -1);
          if (onVoteDone) onVoteDone(res);
        }
      }).catch(function() {});
    });
  });
}

// 标签徽章 HTML
function renderTags(tags) {
  if (!tags || !tags.length) return '';
  return tags.map(function(t) {
    return '<span class="tag-pill">' + escapeHtml(t) + '</span>';
  }).join('');
}

// 段位中文名
var LEVEL_NAMES = ['入门','初段','二段','三段','四段','五段','六段','七段','八段','九段'];
function levelName(level) {
  if (typeof LEVELS !== 'undefined' && LEVELS[level]) return LEVELS[level].name;
  return LEVEL_NAMES[level] || (level + '段');
}

// 战力数字格式化
function formatPower(n) {
  if (n === undefined || n === null) return '0';
  if (n >= 100000000) return (n / 100000000).toFixed(1).replace(/\.0$/, '') + '亿';
  if (n >= 10000) return (n / 10000).toFixed(1).replace(/\.0$/, '') + '万';
  return n.toLocaleString();
}

// 删除按钮（仅自己的帖子/评论显示）
function renderDeleteBtn(type, id, authorId) {
  var curId = (AUTH_USER && AUTH_USER.id);
  if (curId && curId === authorId) {
    return '<button class="btn-del-mini" data-del-type="' + type + '" data-del-id="' + id + '" title="删除" onclick="event.stopPropagation();">✕</button>';
  }
  return '';
}

// IP 属地徽章
function renderIpProvince(province) {
  if (!province) return '';
  return '<span class="ip-province">' + escapeHtml(province) + '</span>';
}

// 隐藏按钮（仅自己的帖子显示）
function renderHideBtn(postId, authorId, isHidden) {
  var curId = (AUTH_USER && AUTH_USER.id);
  if (curId && curId === authorId) {
    var label = isHidden ? '取消隐藏' : '隐藏';
    return '<button class="btn-hide-mini" data-hide-id="' + postId + '" data-hidden="' + (isHidden ? '1' : '0') + '" title="' + label + '" onclick="event.stopPropagation();">' + (isHidden ? '👁' : '🙈') + '</button>';
  }
  return '';
}

// 委托隐藏事件
function bindHideEvents(container, onHidden) {
  if (!container) return;
  container.querySelectorAll('.btn-hide-mini').forEach(function(btn) {
    btn.addEventListener('click', function(e) {
      e.stopPropagation();
      e.preventDefault();
      var postId = parseInt(btn.dataset.hideId);
      var isHidden = btn.dataset.hidden === '1';
      if (isHidden) {
        api.unhidePost(postId).then(function(res) {
          if (res && res.ok !== false) {
            if (onHidden) onHidden();
          }
        }).catch(function() {});
      } else {
        if (!confirm('确定要隐藏这篇帖子吗？隐藏后其他用户将看不到，你可以随时取消隐藏。')) return;
        api.hidePost(postId).then(function(res) {
          if (res && res.ok !== false) {
            if (onHidden) onHidden();
          }
        }).catch(function() {});
      }
    });
  });
}

// 委托删除事件
function bindDeleteEvents(container, onDeleted) {
  if (!container) return;
  container.querySelectorAll('.btn-del-mini').forEach(function(btn) {
    btn.addEventListener('click', function(e) {
      e.stopPropagation();
      e.preventDefault();
      var type = btn.dataset.delType;
      var id = parseInt(btn.dataset.delId);
      if (!confirm('确定要删除吗？')) return;
      if (type === 'post') {
        api.deletePost(id).then(function() {
          if (onDeleted) onDeleted();
        }).catch(function() {});
      } else if (type === 'comment') {
        // 需要从父级找到 postId
        var postIdEl = document.getElementById('postId');
        var postId = postIdEl ? parseInt(postIdEl.value) : (window.postId || 0);
        api.deleteComment(postId, id).then(function() {
          if (onDeleted) onDeleted();
        }).catch(function() {});
      }
    });
  });
}
