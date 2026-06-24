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
