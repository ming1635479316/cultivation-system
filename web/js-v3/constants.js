/* ===== 计算机修行录 - 段位常量 v3 =====
 * 纯展示数据，不含计算逻辑。
 * stats、progress、reward 由后端 API 返回。
 */

var LEVELS = [
  {
    id: 0, name: "入门", poem: "千里之行，始于足下",
    require: "通过入门考核即可进入初段",
    produce: "知道编程是什么，能说出计算机的基本概念",
    color: "#6b6558",
    skills: ["基本计算机操作", "会打字和使用浏览器", "了解编程是什么"],
    tasks: [],
    exam: "通过入门考核即可",
    resources: [
      { name: "计算机科普：编程是什么", url: "https://developer.mozilla.org/zh-CN/docs/Learn/Getting_started_with_the_web" },
      { name: "VS Code 下载与安装", url: "https://code.visualstudio.com/" },
      { name: "键盘指法练习", url: "https://dazi.kukuw.com/" }
    ],
    quiz: []
  },
  {
    id: 1, name: "初段", poem: "初启灵台见大千",
    require: "安装好开发环境，跑起第一个程序",
    produce: "能运行代码、理解基本计算逻辑",
    color: "#57534e",
    skills: ["变量与控制流", "基本数据类型与结构", "会用开发工具和命令行"],
    tasks: [
      "关卡一：安装 Python 和 VS Code，跑出 Hello World",
      "关卡二：用变量、if/else 写一个成绩等级判断器",
      "关卡三：用 for/while 循环写出九九乘法表",
      "关卡四：打一个 LeetCode 简单题，理解自己是咋想的"
    ],
    exam: "不看教程，独立写出一个猜数字游戏。程序随机生成 1-100 的数字，玩家猜大小，猜对为止。",
    resources: [
      { name: "菜鸟教程 Python3", url: "https://www.runoob.com/python3/" },
      { name: "Python 官方中文教程", url: "https://docs.python.org/zh-cn/3/tutorial/" },
      { name: "LeetCode 入门题", url: "https://leetcode.cn/problemset/all/?difficulty=EASY" }
    ],
    quiz: []
  },
  {
    id: 2, name: "二段", poem: "执键方知天地宽",
    require: "独立写出一个解决实际问题的程序",
    produce: "能独立写工具解决小问题",
    color: "#78716c",
    skills: ["函数与模块化", "文件操作与数据处理", "版本管理（Git）", "包管理与依赖"],
    tasks: [
      "关卡一：把一段写过的代码用函数重构一遍",
      "关卡二：写一个遍历文件夹统计文件大小的工具",
      "关卡三：学会 Git：init、add、commit、push、clone",
      "关卡四：用 pip 装一个第三方库，用它处理一个实际问题"
    ],
    exam: "写一个批量文件重命名工具。输入文件夹路径和命名规则，遍历所有文件并按要求改名。代码上传到 GitHub。",
    resources: [
      { name: "廖雪峰 Python 教程", url: "https://www.liaoxuefeng.com/wiki/1016959663602400" },
      { name: "猴子都能懂的 Git 入门", url: "https://backlog.com/git-tutorial/cn/" },
      { name: "Python 官方库参考", url: "https://docs.python.org/zh-cn/3/library/" }
    ],
    quiz: []
  },
  {
    id: 3, name: "三段", poem: "一砖一瓦起楼台",
    require: "完成第一个有界面的完整应用",
    produce: "能做出完整可用的应用程序",
    color: "#575e6e",
    skills: ["应用开发框架", "数据持久化与存储", "网络与接口基础", "基本 UI 构建"],
    tasks: [
      "关卡一：学 Flask 或 Django，跑起第一个 Web 服务",
      "关卡二：学 SQL 基础，建表、插数据、查数据",
      "关卡三：学 HTML + CSS，写出一个能看的静态页面",
      "关卡四：把数据和页面连起来，做一个 CRUD 小应用"
    ],
    exam: "做一个带数据库的个人备忘录：能添加、编辑、删除记录，数据不会重启就消失。代码结构清晰，有 README。",
    resources: [
      { name: "Flask 官方教程", url: "https://flask.palletsprojects.com/" },
      { name: "SQL 在线练习（SQLZoo）", url: "https://sqlzoo.net/" },
      { name: "MDN Web 文档", url: "https://developer.mozilla.org/zh-CN/" },
      { name: "HTTP 入门讲解", url: "https://developer.mozilla.org/zh-CN/docs/Web/HTTP" }
    ],
    quiz: []
  },
  {
    id: 4, name: "四段", poem: "火炼千回始成器",
    require: "项目正式上线运行，有真实用户",
    produce: "端到端完成项目，从开发到运维",
    color: "#4e6e5e",
    skills: ["系统部署与运维", "数据库设计与调优", "安全基础（认证/授权/加密）", "性能意识与监控"],
    tasks: [
      "关卡一：学 Linux 基础，能 SSH 上去装东西改配置",
      "关卡二：把三段的项目用 Docker 打包",
      "关卡三：在云服务器上部署，配上域名和 HTTPS",
      "关卡四：加上用户登录，理解 session/JWT 原理"
    ],
    exam: "你的项目在线运行超过 1 个月，有至少 1 个真实用户在正经用。遇到过一次故障并自己修好了。",
    resources: [
      { name: "Linux 命令行教程", url: "https://linuxcommand.org/" },
      { name: "Docker 从入门到实践", url: "https://yeasy.gitbook.io/docker_practice/" },
      { name: "Nginx 入门指南", url: "https://nginx.org/en/docs/beginners_guide.html" },
      { name: "Let's Encrypt 免费 HTTPS", url: "https://letsencrypt.org/zh-cn/" }
    ],
    quiz: []
  },
  {
    id: 5, name: "五段", poem: "独上高楼望尽路",
    require: "深入掌握一个方向，独立维护线上系统",
    produce: "能在某一领域深耕，解决问题有深度",
    color: "#8b7500",
    skills: ["自动化测试与 CI/CD", "性能分析与调优", "中间件使用（缓存/队列）", "工程化与代码质量管理"],
    tasks: [
      "关卡一：为你维护的项目写单元测试，覆盖率 >60%",
      "关卡二：搭建 CI/CD 自动测试 + 部署流水线",
      "关卡三：给你的项目加 Redis 缓存，压测对比优化前后",
      "关卡四：做一次代码评审，让比你强的人挑出毛病"
    ],
    exam: "独立维护一个线上系统超过 3 个月，没有重大事故。能说出自己踩过的坑和怎么修的。",
    resources: [
      { name: "GitHub Actions 文档", url: "https://docs.github.com/zh/actions" },
      { name: "Redis 官方文档", url: "https://redis.io/docs/latest/" },
      { name: "测试驱动开发（TDD）入门", url: "https://martinfowler.com/bliki/TestDrivenDevelopment.html" }
    ],
    quiz: []
  },
  {
    id: 6, name: "六段", poem: "运筹帷幄定乾坤",
    require: "设计并实现中大型系统方案",
    produce: "能设计系统、带团队、做技术决策",
    color: "#b85c12",
    skills: ["系统架构设计", "分布式系统基础", "团队协作与 Code Review", "技术方案与决策"],
    tasks: [
      "关卡一：画出一个中型系统的架构图，标注每层的选型理由",
      "关卡二：给团队做一次技术分享（线上也算）",
      "关卡三：带 1-2 个新手完成一个功能迭代",
      "关卡四：试着把单体项目拆成微服务（练手，别在生产搞）"
    ],
    exam: "设计实现一个中大型系统，带人完成交付。能说清楚为什么这么设计而不是别的方式。",
    resources: [
      { name: "系统设计入门（System Design Primer）", url: "https://github.com/donnemartin/system-design-primer" },
      { name: "设计数据密集型应用（DDIA）", url: "https://book.douban.com/subject/27154352/" },
      { name: "消息队列 Kafka 入门", url: "https://kafka.apache.org/documentation/" }
    ],
    quiz: []
  },
  {
    id: 7, name: "七段", poem: "破尽虚妄见真章",
    require: "攻克核心技术难题，或做出行业级优化",
    produce: "深入底层原理，突破常规限制",
    color: "#c0392b",
    skills: ["底层原理（OS/编译/网络栈）", "高并发与大规模系统", "领域深耕与技术壁垒", "性能极致优化"],
    tasks: [
      "修炼方向一：啃一本经典底层书（CSAPP / 操作系统概念）",
      "修炼方向二：手写一个简单的编译器/解释器",
      "修炼方向三：做一个能扛住 10000 QPS 的系统并验证"
    ],
    exam: "在某一领域达到「别人搞不定的你能搞定」的水平。用文章或分享证明你的理解深度。",
    resources: [
      { name: "深入理解计算机系统（CSAPP）", url: "https://book.douban.com/subject/26912767/" },
      { name: "操作系统导论（OSTEP）", url: "https://pages.cs.wisc.edu/~remzi/OSTEP/" },
      { name: "分布式系统 MIT 6.824", url: "https://pdos.csail.mit.edu/6.824/" }
    ],
    quiz: []
  },
  {
    id: 8, name: "八段", poem: "点石成金造化手",
    require: "原创技术方案被行业广泛使用",
    produce: "创造被认可的轮子，影响行业实践",
    color: "#8b1a1a",
    skills: ["架构与工具创新", "开源贡献与技术布道", "跨越多个子领域", "行业标准参与"],
    tasks: [
      "把你的经验做成工具/库，让更多人能用到",
      "持续写技术文章或做分享，形成自己的方法论"
    ],
    exam: "你写的东西有至少 100 个人在用。别人说「这个问题问他就对了」。",
    resources: [
      { name: "开源指南", url: "https://opensource.guide/zh-hans/" },
      { name: "技术写作指南", url: "https://developers.google.com/tech-writing" }
    ],
    quiz: []
  },
  {
    id: 9, name: "九段", poem: "万法归宗即通神",
    require: "无需条件，此境由后人评说",
    produce: "定义了方向，推动了行业",
    color: "#1c1917",
    skills: ["范式创新", "行业影响力", "传道授业"],
    tasks: [],
    exam: "无需考核。此境由后人评说。",
    resources: [],
    quiz: []
  }
];

// 关卡验证题（后续迁移到后端）
var TASK_CHECKS = {
  "1-0": { q: "Python 源文件的正确扩展名是？", opts: [".js", ".py", ".java", ".html"], ans: 1 },
  "1-1": { q: "Python 中，if 后面跟的条件表达式最终被当作什么类型判断？", opts: ["数字", "布尔值（True/False）", "字符串", "列表"], ans: 1 },
  "1-2": { q: "range(3) 生成的数字序列是什么？", opts: ["1, 2, 3", "0, 1, 2", "0, 1, 2, 3", "1, 2"], ans: 1 },
  "1-3": { q: "LeetCode 上标记为 Easy 的题目通常意味着？", opts: ["不需要写代码", "难度较低，适合初学者练习", "只有一行代码", "不需要调试"], ans: 1 },
  "2-0": { q: "将一段代码封装成函数，最主要的好处是什么？", opts: ["代码运行更快", "提高复用性，便于维护和测试", "减少文件大小", "不需要写注释"], ans: 1 },
  "2-1": { q: "Python 中用来遍历文件夹、处理文件路径的标准库是？", opts: ["json", "os / os.path", "sys", "math"], ans: 1 },
  "2-2": { q: "git commit 命令的实际作用是什么？", opts: ["下载远程代码", "将暂存区修改保存到版本历史", "创建新分支", "删除文件"], ans: 1 },
  "2-3": { q: "pip install requests 这条命令做了什么？", opts: ["运行一个 Python 脚本", "从 PyPI 下载并安装 requests 库", "创建虚拟环境", "卸载 Python"], ans: 1 },
  "3-0": { q: "Flask 是一个什么样的框架？", opts: ["前端 UI 框架", "Python 的轻量级 Web 框架", "数据库管理工具", "操作系统"], ans: 1 },
  "3-1": { q: "SQL 中用来查询数据的关键字是？", opts: ["INSERT", "DELETE", "SELECT", "UPDATE"], ans: 2 },
  "3-2": { q: "CSS 中控制文字颜色的属性是？", opts: ["font-size", "background", "color", "margin"], ans: 2 },
  "3-3": { q: "CRUD 四个字母中的 R 代表什么操作？", opts: ["Remove（删除）", "Read（读取）", "Rename（重命名）", "Restart（重启）"], ans: 1 },
  "4-0": { q: "SSH 的全称是什么？", opts: ["Super Safe Host", "Secure Shell", "Simple Server Hub", "System Service Handler"], ans: 1 },
  "4-1": { q: "Dockerfile 中指定基础镜像的指令是？", opts: ["RUN", "COPY", "FROM", "CMD"], ans: 2 },
  "4-2": { q: "HTTPS 协议默认使用的端口号是？", opts: ["80", "8080", "443", "3000"], ans: 2 },
  "4-3": { q: "JWT 的全称是什么？", opts: ["Java Web Token", "JSON Web Token", "Just Web Test", "JavaScript Window Type"], ans: 1 },
  "5-0": { q: "单元测试一般测试的是什么粒度？", opts: ["整个系统端到端", "单个函数或方法的逻辑", "用户界面", "网络连接"], ans: 1 },
  "5-1": { q: "CI/CD 中的 CI 指什么？", opts: ["Code Input", "Continuous Integration（持续集成）", "Complete Installation", "Client Interface"], ans: 1 },
  "5-2": { q: "Redis 在项目中通常用来做什么？", opts: ["替代数据库", "缓存热点数据，提升读取速度", "发送邮件", "渲染 HTML"], ans: 1 },
  "5-3": { q: "Code Review 最核心的价值是什么？", opts: ["找出所有 bug", "知识共享、提升团队代码质量", "批评别人的代码风格", "只是走个流程"], ans: 1 }
};
