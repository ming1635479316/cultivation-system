/* ===== 计算机修行录 - UI 层 v3 =====
 * 渲染函数 + 事件绑定
 */

// ---- 关卡完成/取消 ----
function toggleTask(levelId, taskIdx) {
  var key = levelId + '-' + taskIdx;
  if (USER.completedTasks.indexOf(key) >= 0) {
    // 取消
    return api.undoTask(levelId, taskIdx).then(function(res) {
      if (applyServerResult(res)) {
        refreshModalTasks(levelId);
        refreshProgress();
      }
    });
  } else {
    // 完成
    return api.completeTask(levelId, taskIdx).then(function(res) {
      if (applyServerResult(res)) {
        refreshModalTasks(levelId);
        refreshProgress();
      }
    });
  }
}

function isTaskDone(levelId, taskIdx) {
  return USER.completedTasks.indexOf(levelId + '-' + taskIdx) >= 0;
}

// ---- 进度条 ----
function refreshProgress() {
  var el = document.getElementById('currentProgress');
  if (!el) return;
  var lv = USER.level;
  var cl = LEVELS[lv];
  el.innerHTML =
    '<div class="cp-title">当前境界</div>' +
    '<div class="cp-level">' + cl.name + '</div>' +
    '<div class="cp-desc">' + cl.poem + '</div>' +
    '<div class="cp-bar"><div class="cp-fill" style="width:' + (USER.progress || 0) + '%"></div></div>';
}

// ---- 段位列表 ----
function renderLevelList() {
  var listEl = document.getElementById('levelList');
  if (!listEl) return;
  listEl.innerHTML = '';
  LEVELS.forEach(function(level, idx) {
    var isCurrent = idx === USER.level;
    var isPast = idx < USER.level;
    var tag = isCurrent
      ? '<span class="level-tag arrived">当前</span>'
      : isPast ? '<span class="level-tag arrived">✓ 已突破</span>'
      : '<span class="level-tag locked">未至</span>';
    listEl.innerHTML +=
      '<div class="level-card' + (isCurrent ? ' current' : '') + '" onclick="openModal(' + idx + ')">' +
        '<div class="level-header">' +
          '<div class="level-badge level-' + level.id + '">' + level.id + '</div>' +
          '<div>' +
            '<div class="level-name">' + level.name + '</div>' +
            '<div class="level-desc">' + level.poem + '</div>' +
          '</div>' +
          tag +
        '</div>' +
        '<div class="level-detail">' +
          '<p><strong>能做什么：</strong>' + level.produce + '</p>' +
          '<p><strong>核心能力：</strong>' + level.skills.join(' · ') + '</p>' +
        '</div>' +
      '</div>';
  });
}

// ---- 弹窗 ----
var overlay, modalBadge, modalTitle, modalPoem, modalTasks, modalExam, modalResources, modalRequire, modalDesc;

function initModalRefs() {
  overlay = document.getElementById('modalOverlay');
  modalBadge = document.getElementById('modalBadge');
  modalTitle = document.getElementById('modalTitle');
  modalPoem = document.getElementById('modalPoem');
  modalTasks = document.getElementById('modalTasks');
  modalExam = document.getElementById('modalExam');
  modalResources = document.getElementById('modalResources');
  modalRequire = document.getElementById('modalRequire');
  modalDesc = document.getElementById('modalDesc');
}

function openModal(idx) {
  if (!overlay) initModalRefs();
  window._currentQuiz = null;

  var level = LEVELS[idx];
  modalBadge.textContent = level.id;
  modalBadge.style.background = level.color;
  modalTitle.textContent = level.name;
  modalPoem.textContent = level.poem;
  refreshModalTasks(level.id);
  modalExam.textContent = level.exam || '暂无考核标准';
  modalResources.innerHTML = level.resources && level.resources.length
    ? level.resources.map(function(r, ri) {
        return '<a href="' + r.url + '" target="_blank" class="res-link" onclick="recordResourceRead(' + level.id + ',' + ri + ')">' + r.name + '</a>';
      }).join('')
    : '<span style="color:var(--text-muted);font-size:13px;">暂无推荐资源</span>';
  modalRequire.textContent = level.require;
  modalDesc.textContent = level.produce;

  document.getElementById('modalInfo').style.display = '';
  document.getElementById('modalQuiz').style.display = 'none';

  // 考核按钮状态
  var btnQuiz = document.getElementById('btnStartQuiz');
  if (idx > USER.level) {
    btnQuiz.style.display = '';
    btnQuiz.textContent = '先突破当前境界再来';
    btnQuiz.disabled = true;
    btnQuiz.style.opacity = '0.5';
  } else if (idx < USER.level) {
    btnQuiz.style.display = '';
    btnQuiz.textContent = '复习考核';
    btnQuiz.disabled = false;
    btnQuiz.style.opacity = '';
  } else {
    btnQuiz.style.display = '';
    btnQuiz.textContent = '开始考核';
    btnQuiz.disabled = false;
    btnQuiz.style.opacity = '';
  }

  overlay.classList.add('open');
}

function refreshModalTasks(levelId) {
  var level = LEVELS[levelId];
  var el = document.getElementById('modalTasks');
  if (!el) return;
  el.innerHTML = level.tasks.length
    ? level.tasks.map(function(t, ti) {
        var done = isTaskDone(levelId, ti);
        return '<li class="task-item' + (done ? ' task-done' : '') +
          '" onclick="handleTaskClick(' + levelId + ',' + ti + ')" title="点击切换完成状态">' +
          (done ? '✅' : '☐') + ' ' + t + '</li>';
      }).join('')
    : '<li style="color:var(--text-muted)">此境界的修炼关卡待补充</li>';
}

function closeModal() {
  if (overlay) overlay.classList.remove('open');
}

// ---- 关卡验证 ----
function handleTaskClick(levelId, taskIdx) {
  if (isTaskDone(levelId, taskIdx)) {
    toggleTask(levelId, taskIdx).then(function() {
      refreshModalTasks(levelId);
      refreshProgress();
    });
    return;
  }
  var taskText = LEVELS[levelId].tasks[taskIdx];
  var checkKey = levelId + '-' + taskIdx;
  var check = TASK_CHECKS[checkKey];

  document.getElementById('taskCheckTask').textContent = taskText;
  document.getElementById('taskCheckFeedback').style.display = 'none';
  document.getElementById('btnSubmitCheck').style.display = '';

  if (check) {
    document.getElementById('taskCheckQuestion').textContent = check.q;
    document.getElementById('taskCheckQuestion').style.display = '';
    var optsHtml = check.opts.map(function(o, i) {
      return '<label class="task-check-opt"><input type="radio" name="taskCheck" value="' + i + '"><span>' + 'ABCD'[i] + '. ' + o + '</span></label>';
    }).join('');
    document.getElementById('taskCheckOpts').innerHTML = optsHtml;
    document.getElementById('taskCheckOpts').style.display = '';
  } else {
    document.getElementById('taskCheckQuestion').style.display = 'none';
    document.getElementById('taskCheckOpts').style.display = 'none';
    document.getElementById('btnSubmitCheck').textContent = '我确实完成了';
  }

  window._pendingTask = { levelId: levelId, taskIdx: taskIdx, hasCheck: !!check };
  document.getElementById('taskCheckOverlay').classList.add('open');
}

function submitTaskCheck() {
  var t = window._pendingTask;
  if (!t) return;

  if (t.hasCheck) {
    var sel = document.querySelector('input[name="taskCheck"]:checked');
    if (!sel) return;
    var answer = parseInt(sel.value);
    var checkKey = t.levelId + '-' + t.taskIdx;
    var check = TASK_CHECKS[checkKey];
    if (answer === check.ans) {
      toggleTask(t.levelId, t.taskIdx).then(function() {
        refreshModalTasks(t.levelId);
        refreshProgress();
        closeTaskCheck();
      });
    } else {
      var fb = document.getElementById('taskCheckFeedback');
      fb.textContent = '✕ 答错了，回顾一下这个知识点再试';
      fb.style.display = 'block';
      fb.style.color = 'var(--seal)';
    }
  } else {
    toggleTask(t.levelId, t.taskIdx).then(function() {
      refreshModalTasks(t.levelId);
      refreshProgress();
      closeTaskCheck();
    });
  }
}

function closeTaskCheck() {
  document.getElementById('taskCheckOverlay').classList.remove('open');
  document.getElementById('btnSubmitCheck').textContent = '提交';
  window._pendingTask = null;
}

// ---- 弹窗事件 ----
function bindModalEvents() {
  initModalRefs();
  if (overlay) {
    overlay.addEventListener('click', function(e) {
      if (e.target === overlay) closeModal();
    });
  }
  var closeBtn = document.getElementById('modalClose');
  if (closeBtn) closeBtn.addEventListener('click', closeModal);
  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') closeModal();
  });

  // 考核开始按钮
  var btnQuiz = document.getElementById('btnStartQuiz');
  if (btnQuiz) {
    btnQuiz.addEventListener('click', startQuiz);
  }

  // 考核返回按钮
  var btnBack = document.getElementById('btnBackQuiz');
  if (btnBack) {
    btnBack.addEventListener('click', function() {
      document.getElementById('modalInfo').style.display = '';
      document.getElementById('modalQuiz').style.display = 'none';
    });
  }

  // 考核提交按钮
  var btnSubmit = document.getElementById('btnSubmitQuiz');
  if (btnSubmit) {
    btnSubmit.addEventListener('click', submitQuiz);
  }
}

// ---- 考核：从后端取题 ----
function startQuiz() {
  var ctx = window._currentQuiz;
  if (!ctx) return;

  api.getQuizQuestions(ctx.level.id).then(function(data) {
    if (!data || !data.questions || data.questions.length === 0) {
      alert('此境界暂未设置考核题目。');
      return;
    }
    var picked = data.questions;
    window._pickedQuiz = picked;

    document.getElementById('modalInfo').style.display = 'none';
    document.getElementById('modalQuiz').style.display = '';

    var badge = document.getElementById('quizBadge');
    badge.textContent = ctx.level.id;
    badge.style.background = ctx.level.color;
    document.getElementById('quizTitle').textContent = ctx.level.name + ' · 考核';

    var html = '';
    picked.forEach(function(qq, qi) {
      html += '<div class="quiz-item" data-idx="' + qi + '">';
      html += '<div class="quiz-question"><strong>' + (qi + 1) + '.</strong> ' + qq.question + '</div>';
      html += '<div class="quiz-opts">';
      qq.options.forEach(function(o, oi) {
        html += '<label class="quiz-opt"><input type="radio" name="q' + qi + '" value="' + oi + '"><span>' + 'ABCD'[oi] + '. ' + o + '</span></label>';
      });
      html += '</div>';
      html += '</div>';
    });
    document.getElementById('quizQuestions').innerHTML = html;
  }).catch(function() {
    alert('加载考核题目失败，请检查网络后重试。');
  });
}

// ---- 考核：提交到后端判卷 ----
function submitQuiz() {
  var picked = window._pickedQuiz;
  var ctx = window._currentQuiz;
  if (!picked || !ctx) return;

  // 收集答案
  var answers = [];
  picked.forEach(function(qq, qi) {
    var sel = document.querySelector('input[name="q' + qi + '"]:checked');
    answers.push(sel ? parseInt(sel.value) : -1);
  });

  api.submitQuiz(ctx.level.id, answers).then(function(data) {
    if (!data) return;

    // 显示每题对错
    picked.forEach(function(qq, qi) {
      var itemEl = document.querySelector('.quiz-item[data-idx="' + qi + '"]');
      if (!itemEl) return;
      var r = data.results[qi];
      if (r && r.is_correct) {
        itemEl.classList.add('correct');
      } else {
        itemEl.classList.add('wrong');
      }
    });

    // 显示结果
    var container = document.getElementById('quizQuestions');
    var existing = container.querySelector('.quiz-result');
    if (existing) existing.remove();

    var msg = data.passed
      ? (ctx.idx === 0 ? '✅ 通过。可以去修炼初段了。' : '通过。')
      : (ctx.idx === 0 ? '未通过，再复习一下错题解析。' : '再看看错题，弄懂了再来。');

    var resultHtml = '<div class="quiz-result">' +
      '<div class="qr-score">' + data.score + ' / ' + data.total + '</div>' +
      '<div class="qr-pct" style="color:' + (data.passed ? 'var(--green)' : 'var(--seal)') + '">需 ' + data.pass_score + '/' + data.total + ' 通过</div>' +
      '<div class="qr-msg">' + msg + '</div>' +
      '</div>';
    container.insertAdjacentHTML('afterbegin', resultHtml);

    // 更新状态
    if (data.stats) USER.stats = data.stats;
    if (data.progress !== undefined) USER.progress = data.progress;
    cacheSave();

    // 突破
    if (data.level_up && data.new_level) {
      USER.level = data.new_level;
      cacheSave();
      showBreakthroughEffect(LEVELS[data.new_level]);
      refreshProgress();
      renderLevelList();
    }
  }).catch(function() {
    alert('提交考核失败，请重试。');
  });
}

// ---- 突破动效 ----
function showBreakthroughEffect(level) {
  var overlayEl = document.getElementById('breakthroughOverlay');
  document.getElementById('breakthroughLevel').textContent = level.name;
  document.getElementById('breakthroughPoem').textContent = '— ' + level.poem;
  overlayEl.classList.add('show');
  setTimeout(function() {
    overlayEl.classList.remove('show');
  }, 2600);
}

// ---- 资源点击 ----
function recordResourceRead(levelId, resIdx) {
  var level = LEVELS[levelId];
  if (!level || !level.resources || !level.resources[resIdx]) return;
  // 通过后端记录
  api.addMessage({
    icon: '📖',
    text: '阅读了修炼资源：' + level.resources[resIdx].name,
    time: new Date().toISOString().slice(0, 10),
    unread: true
  }).catch(function() {});
}

// ---- 登出 ----
function logout() {
  api.logout();
}
