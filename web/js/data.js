/* ===== 计算机修行录 - 数据层 v4 =====
 * v4: 多用户 + 登录鉴权
 * v3: 属性不再手填，从「事件日志」动态计算
 */

// ============================================================
// 登录检查
// ============================================================
var AUTH_TOKEN = localStorage.getItem('cultivation_token');
var AUTH_USER = null;
try { AUTH_USER = JSON.parse(localStorage.getItem('cultivation_user')); } catch(e) {}

if (!AUTH_TOKEN) {
  window.location.href = 'login.html';
  throw new Error('未登录');  // 阻止后续代码执行
}

// ============================================================
// 修炼体系各段位数据
// ============================================================
const LEVELS = [
  {
    id: 0,
    name: "入门",
    poem: "千里之行，始于足下",
    require: "通过入门考核即可进入初段",
    produce: "知道编程是什么，能说出计算机的基本概念",
    color: "#6b6558",
    skills: ["基本计算机操作", "会打字和使用浏览器", "了解编程是什么"],
    tasks: [],
    exam: "通过入门考核即可",
    resources: [
      { name: "计算机科普：编程是什么", url: "https://www.runoob.com/what-is-programming.html" },
      { name: "VS Code 下载与安装", url: "https://code.visualstudio.com/" },
      { name: "键盘指法练习", url: "https://dazi.kukuw.com/" }
    ],
    quiz: []
  },
  {
    id: 1,
    name: "初段",
    poem: "初启灵台见大千",
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
    id: 2,
    name: "二段",
    poem: "执键方知天地宽",
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
    id: 3,
    name: "三段",
    poem: "一砖一瓦起楼台",
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
    id: 4,
    name: "四段",
    poem: "火炼千回始成器",
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
    id: 5,
    name: "五段",
    poem: "独上高楼望尽路",
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
    id: 6,
    name: "六段",
    poem: "运筹帷幄定乾坤",
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
    id: 7,
    name: "七段",
    poem: "破尽虚妄见真章",
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
    id: 8,
    name: "八段",
    poem: "点石成金造化手",
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
    id: 9,
    name: "九段",
    poem: "万法归宗即通神",
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

// ============================================================
// 题库
// ============================================================
const QUESTION_BANK = [
  // --- 入门（level:0）--- 29题，考核抽6题，4题通过
  { level:0, cat:"基础", q:"计算机中 1KB 等于多少字节？", opts:["100","512","1024","2048"], ans:2, tip:"1KB = 1024 字节（Byte）。" },
  { level:0, cat:"基础", q:"以下哪个不是操作系统？", opts:["Windows","Linux","Python","macOS"], ans:2, tip:"Python 是编程语言，不是操作系统。" },
  { level:0, cat:"基础", q:"以下哪个是网址（URL）？", opts:["C:/Users/...","cmd.exe","www.python.org","notepad"], ans:2, tip:"以 www. 开头的一般就是网址。" },
  { level:0, cat:"基础", q:"编程中 `=` 通常表示什么？", opts:["等于判断","赋值","比较大小","删除"], ans:1, tip:"大多数语言里 `=` 是赋值，`==` 才是判断相等。" },
  { level:0, cat:"基础", q:"\"Bug\" 在编程中通常指什么？", opts:["一种虫子","代码中的错误","病毒","操作系统"], ans:1, tip:"Bug 就是代码里的漏洞或错误。" },
  { level:0, cat:"基础", q:"以下哪个是合法的文件名？", opts:["file<>.txt","file?.txt","file.txt","file|.txt"], ans:2, tip:"< > ? | 等符号在文件名中是不允许的。" },
  { level:0, cat:"基础", q:"文件扩展名 .py 通常表示什么？", opts:["图片文件","Python 源代码","压缩文件","可执行程序"], ans:1, tip:".py 是 Python 脚本文件的常见扩展名。" },
  { level:0, cat:"基础", q:"CPU 的主要功能是什么？", opts:["存储文件","执行运算和指令","显示图像","连接网络"], ans:1, tip:"CPU 是计算机的大脑，负责运算和指令执行。" },
  { level:0, cat:"工程", q:"在命令行中 Ctrl+C 通常用于什么？", opts:["复制文字","中断正在运行的程序","关闭窗口","保存文件"], ans:1, tip:"Ctrl+C 在命令行里是发送中断信号。" },
  { level:0, cat:"读码", q:"代码中 `#` 开头的行通常是什么？", opts:["错误提示","注释（不会执行）","重要代码","输出内容"], ans:1, tip:"`#` 在 Python 中表示注释，不会被程序执行。" },
  { level:0, cat:"安全", q:"收到陌生人发的 .exe 文件，最好的做法是？", opts:["直接双击打开","先发给朋友看看","不要打开，可能是病毒","改个名字再开"], ans:2, tip:"不明来源的可执行文件可能包含恶意程序。" },
  { level:0, cat:"安全", q:"设置密码时，以下哪个相对最安全？", opts:["123456","password","生日日期","混合大小写字母数字符号的长密码"], ans:3, tip:"长密码 + 多种字符混合，最难被破解。" },
  { level:0, cat:"基础", q:"计算机内存（RAM）和硬盘的主要区别是什么？", opts:["没有区别","硬盘更快","RAM 断电数据消失，硬盘持久保存","RAM 是用来上网的"], ans:2, tip:"RAM 是临时存储，关机就没了。硬盘文件不会消失。" },
  { level:0, cat:"基础", q:"以下哪个是输入设备？", opts:["显示器","键盘","音箱","打印机"], ans:1, tip:"键盘和鼠标是输入设备；显示器和音箱是输出设备。" },
  { level:0, cat:"基础", q:"\"源代码\" 通常是指什么？", opts:["编译后的文件","程序员写的原始代码","电脑的启动程序","操作系统内核"], ans:1, tip:"源代码就是程序员写的原始程序文本，还没编译。" },
  { level:0, cat:"基础", q:"操作系统的主要功能不包括？", opts:["管理硬件资源","提供用户界面","编写应用程序","管理文件系统"], ans:2, tip:"操作系统不负责帮你写应用，那是程序员干的。" },
  { level:0, cat:"基础", q:"显示器分辨率 1920×1080 表示什么？", opts:["屏幕尺寸大小","横向和纵向的像素点数","刷新频率","色彩范围"], ans:1, tip:"1920×1080 表示横向 1920 个像素，纵向 1080 个像素。" },
  { level:0, cat:"基础", q:"以下哪种文件是压缩文件？", opts:[".txt",".zip",".exe",".html"], ans:1, tip:".zip、.rar、.7z 都是常见的压缩文件格式。" },
  { level:0, cat:"基础", q:"以下哪个存储容量最大？", opts:["1KB","1MB","1GB","1B"], ans:2, tip:"B < KB < MB < GB < TB，1GB = 1024MB。" },
  { level:0, cat:"读码", q:"print('Hello ' + 'World') 输出什么？", opts:["HelloWorld","Hello World","Hello+World","报错"], ans:1, tip:"字符串用 + 拼接，'Hello ' 末尾有空格，所以输出 Hello World。" },
  { level:0, cat:"读码", q:"name = '易' 中 name 是什么？", opts:["函数","变量","文件","命令"], ans:1, tip:"name 是一个变量，存储了字符串 '易'。" },
  { level:0, cat:"读码", q:"print(2 + 3 * 4) 输出什么？", opts:["20","14","9","报错"], ans:1, tip:"先乘除后加减，3×4=12，2+12=14。" },
  { level:0, cat:"读码", q:"print(10 / 3) 输出大概是多少？", opts:["3","3.333...","1","报错"], ans:1, tip:"Python 中 / 是浮点除法，结果带小数。" },
  { level:0, cat:"安全", q:"浏览器提示\"此网站不安全\"通常因为？", opts:["网站没有 HTTPS 加密","网站图片太多","网站内容太长","网站服务器太慢"], ans:0, tip:"HTTPS 加密保护你在网站上输入的信息不会被窃取。" },
  { level:0, cat:"安全", q:"以下哪个做法最容易导致账号被盗？", opts:["使用复杂密码","多个网站用同一个密码","定期换密码","开启两步验证"], ans:1, tip:"一个密码走天下，一处泄露全部遭殃。每个网站用不同密码。" },
  { level:0, cat:"安全", q:"看到弹窗说\"你的电脑中了病毒，打这个电话\"应该？", opts:["立即拨打电话","关闭网页不要理它","点击弹窗里的按钮","下载推荐的软件"], ans:1, tip:"这是常见诈骗手段，正规杀毒软件不会弹窗让你打电话。" },
  { level:0, cat:"工程", q:"写代码时为什么推荐写注释？", opts:["让程序运行更快","帮助自己和别人理解代码","让代码更好看","注释是程序必需的"], ans:1, tip:"注释不运行，但能让代码好懂。一周后你可能也会看不懂自己写的。" },
  { level:0, cat:"工程", q:"以下哪个是代码编辑器？", opts:["VS Code","Chrome","Photoshop","Steam"], ans:0, tip:"VS Code 是目前最流行的代码编辑器。" },
  { level:0, cat:"工程", q:"程序运行报错了，第一件事应该做什么？", opts:["关掉编辑器重写","读报错信息看是哪一行","重装 Python","不管继续运行"], ans:1, tip:"报错信息通常包含出错行号和原因，学会读错误是编程第一步。" },
  { level:0, cat:"工程", q:"把代码保存为 .py 文件后怎么运行？", opts:["双击文件就行","用 Python 解释器执行","拖到浏览器里","不需要运行"], ans:1, tip:"在终端输入 `python 文件名.py` 或者在编辑器里点运行按钮。" },
  // --- 初段（level:1）---
  { level:1, cat:"基础", q:"Python 中 `type(42)` 返回什么？", opts:["<class 'int'>","<class 'str'>","42","<class 'number'>"], ans:0, tip:"42 是整数，类型是 int。" },
  { level:1, cat:"基础", q:"print('Hello' * 3) 输出什么？", opts:["Hello","HelloHelloHello","Hello 3","报错"], ans:1, tip:"字符串乘以数字会重复拼接。" },
  { level:1, cat:"基础", q:"Python 中用哪个函数获取用户键盘输入？", opts:["read()","input()","scan()","get()"], ans:1, tip:"input() 用于读取用户输入，返回字符串。" },
  { level:1, cat:"基础", q:"list = [1,2,3]; print(list[1]) 输出什么？", opts:["1","2","3","报错"], ans:1, tip:"列表索引从 0 开始，list[1] 是第二个元素。" },
  { level:1, cat:"读码", q:"for i in range(3): print(i) 输出什么？", opts:["1 2 3","0 1 2","0 1 2 3","1 2"], ans:1, tip:"range(3) 生成 0,1,2，不包含 3。" },
  { level:1, cat:"读码", q:"x=5; if x>3: print('大') 的执行结果是？", opts:["大","小","报错","没有输出"], ans:0, tip:"5>3 为 True，执行 if 内的语句打印'大'。" },
  { level:1, cat:"读码", q:"print(10 % 3) 输出什么？", opts:["3","1","3.33","0"], ans:1, tip:"% 是取余运算符，10÷3=3 余 1。" },
  { level:1, cat:"工程", q:"Git 暂存区是什么？", opts:["Git 的备份服务器","修改后、提交前的临时区域","代码编译后的文件","分支合并的工具"], ans:1, tip:"暂存区是 git add 后、git commit 前。" },
  { level:1, cat:"工程", q:".gitignore 文件的作用是什么？", opts:["加快 Git 速度","指定哪些文件不加入版本控制","存储 Git 密码","记录提交历史"], ans:1, tip:".gitignore 告诉 Git 忽略某些文件（如临时文件、密钥）。" },
  { level:1, cat:"安全", q:"直接把用户输入拼进 SQL 查询有什么风险？", opts:["更高效","可能被 SQL 注入攻击","代码更短","没有影响"], ans:1, tip:"任何用户输入都不应直接拼进 SQL 查询。" },

  // --- 二段（level:2）---
  { level:2, cat:"基础", q:"Python 中 def 关键字用于什么？", opts:["定义变量","定义函数","导入模块","创建类"], ans:1, tip:"def 是 define 的缩写，用来定义函数。" },
  { level:2, cat:"基础", q:"函数的参数默认值在什么时候被计算？", opts:["每次调用时","函数定义时","程序启动时","永远不会"], ans:1, tip:"默认值在函数定义时计算一次，之后调用共享同一个对象。" },
  { level:2, cat:"基础", q:"import os 中 os 是什么？", opts:["操作系统名称","Python 标准库模块","一个变量名","文件路径"], ans:1, tip:"os 是 Python 内置模块，提供操作系统相关功能。" },
  { level:2, cat:"读码", q:"def add(a,b=10): return a+b; add(5) 返回什么？", opts:["报错","15","5","10"], ans:1, tip:"b 有默认值 10，调用 add(5) 等价于 add(5,10)，返回 15。" },
  { level:2, cat:"读码", q:"open('test.txt','w') 中 'w' 表示什么？", opts:["读取","写入（覆盖）","追加","删除"], ans:1, tip:"'w'=write 写入模式，'r'=read 读取，'a'=append 追加。" },
  { level:2, cat:"工程", q:"pip freeze > requirements.txt 这条命令做了什么？", opts:["安装依赖","导出当前环境的包列表到文件","删除所有包","升级 pip"], ans:1, tip:"pip freeze 列出已安装的包，> 重定向到文件。" },
  { level:2, cat:"工程", q:"git clone 命令的作用是什么？", opts:["创建新分支","复制远程仓库到本地","提交代码","删除仓库"], ans:1, tip:"git clone <url> 把远程仓库完整下载到本地。" },
  { level:2, cat:"安全", q:"把 API 密钥写在代码里直接提交到 GitHub 有什么风险？", opts:["代码运行变慢","密钥泄露，别人可以盗用","GitHub 会封号","没有风险"], ans:1, tip:"密钥应该用环境变量存放，不能硬编码提交。" },

  // --- 三段（level:3）---
  { level:3, cat:"基础", q:"Flask 中 @app.route('/') 装饰器的作用是什么？", opts:["定义函数名","把 URL 路径映射到函数","设置变量类型","导入模块"], ans:1, tip:"@app.route 将 URL 路径绑定到视图函数。" },
  { level:3, cat:"基础", q:"SQL 中 INSERT INTO 语句的作用是什么？", opts:["查询数据","插入新记录","删除数据","修改表结构"], ans:1, tip:"INSERT INTO 用于向表中添加新数据行。" },
  { level:3, cat:"基础", q:"HTML 中 <h1> 标签表示什么？", opts:["段落","一级标题","超链接","图片"], ans:1, tip:"h1-h6 是标题标签，数字越小级别越高。" },
  { level:3, cat:"读码", q:"SELECT * FROM users WHERE age > 18 查询什么？", opts:["所有用户","年龄大于 18 的用户","年龄等于 18 的用户","删除用户"], ans:1, tip:"WHERE 子句过滤符合条件的行。" },
  { level:3, cat:"读码", q:"CSS 中 .box { color: red; } 的 .box 是什么选择器？", opts:["ID 选择器","类选择器","标签选择器","属性选择器"], ans:1, tip:"点号 . 开头是类选择器，# 开头是 ID 选择器。" },
  { level:3, cat:"工程", q:"CRUD 四个字母代表什么操作？", opts:["创建-读取-更新-删除","复制-重命名-上传-下载","编译-运行-测试-部署","连接-请求-响应-断开"], ans:0, tip:"Create, Read, Update, Delete —— 数据操作四大基本动作。" },
  { level:3, cat:"工程", q:"RESTful API 中 GET 请求通常用于什么？", opts:["创建资源","获取/查询资源","更新资源","删除资源"], ans:1, tip:"GET=查询，POST=创建，PUT/PATCH=更新，DELETE=删除。" },
  { level:3, cat:"安全", q:"HTTP 和 HTTPS 的主要区别是什么？", opts:["速度不同","HTTPS 有加密，HTTP 没有","端口不同","没有区别"], ans:1, tip:"HTTPS = HTTP + SSL/TLS 加密，保护数据传输安全。" },

  // --- 四段（level:4）---
  { level:4, cat:"基础", q:"Linux 中 ls 命令的作用是什么？", opts:["创建文件","列出目录内容","删除文件","修改权限"], ans:1, tip:"ls = list，显示当前目录下的文件和文件夹。" },
  { level:4, cat:"基础", q:"Dockerfile 中 FROM 指令的作用是什么？", opts:["指定工作目录","指定基础镜像","复制文件","运行命令"], ans:1, tip:"FROM 指定构建镜像的基础，如 FROM python:3.11。" },
  { level:4, cat:"基础", q:"Nginx 通常用作什么？", opts:["数据库","反向代理 / Web 服务器","编程语言","操作系统"], ans:1, tip:"Nginx 是高性能的 Web 服务器和反向代理。" },
  { level:4, cat:"读码", q:"docker build -t myapp . 中 -t 参数的作用？", opts:["指定超时时间","给镜像打标签（名字）","指定线程数","测试模式"], ans:1, tip:"-t 给构建的镜像命名，如 myapp:latest。" },
  { level:4, cat:"工程", q:"SSH 密钥对包含哪两个文件？", opts:["公钥和私钥","加密和解密","输入和输出","配置和日志"], ans:0, tip:"SSH 密钥对：公钥（放服务器）和私钥（自己保管）。" },
  { level:4, cat:"工程", q:"JWT 令牌通常包含哪三部分？", opts:["用户名-密码-邮箱","Header-Payload-Signature","请求-响应-状态","加密-解密-验证"], ans:1, tip:"JWT 由 Header、Payload、Signature 三部分组成，用点号分隔。" },
  { level:4, cat:"安全", q:"服务器防火墙只开放 80 和 443 端口的好处是什么？", opts:["加速访问","减少攻击面，只允许 Web 流量","省电","方便调试"], ans:1, tip:"最小化开放端口是安全基本原则，减少被攻击的入口。" },
  { level:4, cat:"安全", q:"数据库密码应该怎么存放？", opts:["写在代码注释里","用环境变量 / 密钥管理服务","发到群聊里备份","用 123456"], ans:1, tip:"密码和密钥永远不应硬编码，用环境变量或 Vault 管理。" },

  // --- 五段（level:5）---
  { level:5, cat:"基础", q:"单元测试中 mock 的作用是什么？", opts:["加速测试","模拟外部依赖的行为","美化代码","生成随机数据"], ans:1, tip:"Mock 用于隔离被测代码，模拟数据库、API 等外部依赖。" },
  { level:5, cat:"基础", q:"Redis 默认把数据存在哪里？", opts:["硬盘文件","内存中","远程服务器","数据库表"], ans:1, tip:"Redis 是内存数据库，数据主要在内存中，所以非常快。" },
  { level:5, cat:"读码", q:"CI/CD 流水线中的 'CI' 全称是什么？", opts:["Code Integration","Continuous Integration","Complete Installation","Client Interface"], ans:1, tip:"CI=持续集成，CD=持续交付/部署。" },
  { level:5, cat:"工程", q:"做性能压测时，QPS 指的是什么？", opts:["每秒查询数","代码质量分","量子处理速度","问题数量"], ans:0, tip:"QPS = Queries Per Second，衡量系统吞吐量的关键指标。" },
  { level:5, cat:"工程", q:"Redis 缓存雪崩的主要原因是什么？", opts:["内存太小","大量缓存同时过期，请求直接打到数据库","网络断开","Redis 版本太旧"], ans:1, tip:"缓存雪崩=大量 key 同时过期，流量瞬间压到数据库。设置随机过期时间可缓解。" },
  { level:5, cat:"工程", q:"Code Review 时最应该关注什么？", opts:["代码缩进是否对齐","逻辑正确性、安全漏洞、可维护性","变量命名是否够短","注释是否够多"], ans:1, tip:"CR 核心：逻辑对不对、有没有安全漏洞、以后好不好维护。" },
  { level:5, cat:"安全", q:"生产环境的 DEBUG 模式应该怎么设置？", opts:["永远开启","必须关闭","看情况","无所谓"], ans:1, tip:"DEBUG 模式会泄露代码细节和敏感信息，生产环境必须关闭。" },

  // --- 六段（level:6）---
  { level:6, cat:"基础", q:"CAP 定理中 C、A、P 分别代表什么？", opts:["一致性-可用性-分区容错","计算-分析-处理","创建-追加-清除","缓存-应用-代理"], ans:0, tip:"CAP = Consistency, Availability, Partition Tolerance，分布式系统最多同时满足两个。" },
  { level:6, cat:"基础", q:"消息队列（如 Kafka）的核心作用是什么？", opts:["存储文件","异步解耦、削峰填谷","渲染页面","加密数据"], ans:1, tip:"消息队列让生产者和消费者解耦，平滑流量峰值。" },
  { level:6, cat:"读码", q:"微服务架构相比单体架构的主要优势是？", opts:["代码更少","各服务独立部署、独立扩缩容","不需要数据库","没有 bug"], ans:1, tip:"微服务核心优势：独立部署、技术栈灵活、故障隔离。" },
  { level:6, cat:"工程", q:"数据库读写分离通常怎么实现？", opts:["买更好的服务器","主库写、从库读，通过中间件路由","把所有表拆开","用 Excel"], ans:1, tip:"读写分离：写操作走主库，读操作走从库，减轻主库压力。" },
  { level:6, cat:"工程", q:"画系统架构图时，最应该标注什么？", opts:["每个组件的颜色","组件间数据流向、通信协议、选型理由","代码行数","作者名字"], ans:1, tip:"架构图核心：谁调谁、怎么通信、为什么选这个。" },
  { level:6, cat:"工程", q:"负载均衡的常见算法有哪些？", opts:["冒泡排序","轮询、最少连接、IP 哈希","快速排序","二分查找"], ans:1, tip:"常见负载均衡算法：Round Robin、Least Connections、IP Hash。" },
  { level:6, cat:"安全", q:"SQL 注入攻击的防护措施不包括？", opts:["参数化查询","ORM 框架","直接把用户输入拼 SQL","输入校验"], ans:2, tip:"参数化查询和 ORM 是最有效的 SQL 注入防护手段。" },

  // --- 七段（level:7）---
  { level:7, cat:"基础", q:"操作系统中的虚拟内存是什么？", opts:["不存在的内存","硬盘空间映射为内存地址，扩展可用内存","云端存储","缓存"], ans:1, tip:"虚拟内存让程序以为自己有连续大内存，实际由 OS 映射到物理内存+磁盘。" },
  { level:7, cat:"基础", q:"TCP 三次握手的主要目的是什么？", opts:["加密数据","建立可靠连接，同步序列号","传输文件","关闭连接"], ans:1, tip:"三次握手确保双方收发能力正常，同步初始序列号。" },
  { level:7, cat:"读码", q:"GIL（全局解释器锁）主要影响 Python 的什么场景？", opts:["文件读写","CPU 密集型多线程","网络请求","GUI 界面"], ans:1, tip:"GIL 导致 Python 多线程无法利用多核跑 CPU 密集任务，需用多进程。" },
  { level:7, cat:"工程", q:"高并发系统中，为什么需要限流？", opts:["让用户排队","保护系统不被突发流量打垮","增加收入","减少代码量"], ans:1, tip:"限流（Rate Limiting）防止突发流量耗尽资源导致雪崩。" },
  { level:7, cat:"工程", q:"火焰图（Flame Graph）主要用于什么？", opts:["美化界面","可视化 CPU 耗时分布，定位性能瓶颈","画3D图形","加密"], ans:1, tip:"火焰图横轴表示占用比例，从下往上显示调用栈，宽度越大越值得优化。" },
  { level:7, cat:"工程", q:"DDD（领域驱动设计）的核心思想是什么？", opts:["先写代码再想设计","围绕业务领域建模，代码反映业务语言","用最快的框架","越简单越好"], ans:1, tip:"DDD 强调深入理解业务，用领域模型驱动软件设计。" },
  { level:7, cat:"安全", q:"零信任安全模型的核心原则是什么？", opts:["信任所有人","永不信任，始终验证","只信任内部网络","不需要安全措施"], ans:1, tip:"零信任=不默认信任任何人/设备，每次都验证身份和权限。" },

  // --- 八段（level:8）---
  { level:8, cat:"基础", q:"开源协议 MIT 和 GPL 的主要区别是什么？", opts:["没有区别","GPL 要求衍生作品也开源（传染性），MIT 不要求","MIT 更严格","GPL 不能商用"], ans:1, tip:"MIT=宽松，做啥都行；GPL=强传染，用了就要开源。" },
  { level:8, cat:"基础", q:"技术写作中「代码优先于注释」意味着什么？", opts:["不写注释","好的代码应该自解释，注释解释「为什么」而非「做什么」","注释比代码重要","代码越短越好"], ans:1, tip:"代码写好命名和结构是基础，注释补充为什么要这样设计。" },
  { level:8, cat:"读码", q:"一个开源库有 1000+ GitHub star 说明什么？", opts:["代码完美无 bug","有较多开发者认可和关注","一定适合你的项目","作者很有钱"], ans:1, tip:"Star 是认可指标，不代表质量完美，选库还需看维护频率、文档、社区。" },
  { level:8, cat:"工程", q:"设计一个框架时，API 的「向后兼容」是什么意思？", opts:["兼容旧电脑","新版本不破坏旧版本的使用方式","兼容所有操作系统","兼容其他框架"], ans:1, tip:"向后兼容=升级版本后，老代码无需修改仍能正常运行。" },
  { level:8, cat:"工程", q:"技术布道（Evangelism）的核心是什么？", opts:["推销产品","用技术内容和实践影响开发者，建立信任","写广告","刷存在感"], ans:1, tip:"布道是通过高质量分享让开发者认可你的技术理念。好的布道是教育而非营销。" },
  { level:8, cat:"工程", q:"一个好的技术方案应该包含哪些要素？", opts:["只有代码","背景-目标-方案对比-风险-排期","只写结论","越多越好"], ans:1, tip:"方案要讲清楚：为什么做、怎么做、有什么选择、有什么风险。" },
];

// ============================================================
// 经验事件系统（核心）
// ============================================================

// 每种事件对各属性的贡献（固定值部分）
const EVENT_CONFIG = {
  task_done:     { coding: 0, project: 0, tools: 0 },  // 实际值来自事件的 value 字段
  quiz_pass:     { coding: 10, theory: 8 },       // 通过该段考核
  quiz_correct:  { theory: 2 },                    // 每答对一题
  resource_read: { theory: 3 },                    // 阅读一个推荐资源
  tool_unlock:   { tools: 8 },                     // 解锁新工具/技术栈
  config_file:   { tools: 5 },                     // 编写配置文件（Dockerfile等）
  journal_write: { coding: 3, theory: 5 },         // 写一篇突破感悟
};

// 段位基础属性 = 段位号 × 系数
// 入门(0段)基础为 0，属性全靠行为积累
function getBaseStats(level) {
  return {
    coding:  level * 8,
    project: level * 6,
    theory:  level * 7,
    tools:   level * 6
  };
}

// 关卡任务奖励（随段位递增）
function getTaskReward(levelId) {
  if (levelId <= 1) return { coding: 5, project: 2 };
  if (levelId === 2) return { coding: 8, project: 4 };
  if (levelId === 3) return { coding: 10, project: 5, tools: 3 };
  return { coding: 12, project: 8, tools: 5 };  // 四段及以上
}

// 核心：从段位 + 事件日志计算四维属性
function calcStats(level, events) {
  var stats = getBaseStats(level);
  for (var i = 0; i < events.length; i++) {
    var e = events[i];
    var cfg = EVENT_CONFIG[e.type];
    if (!cfg) continue;
    var keys = Object.keys(cfg);
    for (var k = 0; k < keys.length; k++) {
      var stat = keys[k];
      if (e.value && e.value[stat] !== undefined) {
        stats[stat] = (stats[stat] || 0) + e.value[stat];
      } else {
        stats[stat] = (stats[stat] || 0) + (cfg[stat] || 0);
      }
    }
  }
  // 限制在 0-100 之间
  var statNames = Object.keys(stats);
  for (var s = 0; s < statNames.length; s++) {
    stats[statNames[s]] = Math.max(0, Math.min(100, Math.round(stats[statNames[s]])));
  }
  return stats;
}

// 计算到下一段的进度（当前段任务完成率）
function calcProgress(level, completedTasks) {
  var tasks = LEVELS[level] && LEVELS[level].tasks;
  if (!tasks || tasks.length === 0) return 100;
  var done = 0;
  for (var i = 0; i < tasks.length; i++) {
    var key = level + '-' + i;
    if (completedTasks && completedTasks.indexOf(key) >= 0) done++;
  }
  return Math.round((done / tasks.length) * 100);
}

// ============================================================
// 后端 API 配置
// ============================================================
// 如果前端由后端托管（部署模式），API 和页面在同一地址，直接用空字符串
// 如果是本地 file:// 打开或 Live Server，则指向 localhost
var API_BASE = (function() {
  var origin = window.location.origin;
  if (origin.indexOf('file:') === 0 || origin.indexOf('127.0.0.1') >= 0 || origin.indexOf('localhost') >= 0) {
    return 'http://127.0.0.1:8001';
  }
  return origin;  // 部署模式：API 和前端在同一服务器
})();

// API 密钥已废弃，改用 token 鉴权
function apiFetch(url, options) {
  options = options || {};
  options.headers = options.headers || {};
  options.headers['Authorization'] = 'Bearer ' + (AUTH_TOKEN || '');
  return fetch(url, options).then(function(r) {
    if (r.status === 401) {
      localStorage.removeItem('cultivation_token');
      localStorage.removeItem('cultivation_user');
      window.location.href = 'login.html';
    }
    return r;
  });
}

function logout() {
  apiFetch(API_BASE + '/api/auth/logout', { method: 'POST' }).catch(function() {});
  localStorage.removeItem('cultivation_token');
  localStorage.removeItem('cultivation_user');
  localStorage.removeItem(STORAGE_KEY);
  localStorage.removeItem(STORAGE_KEY + '_mtime');
  window.location.href = 'login.html';
}

function apiSave(payload) {
  try {
    apiFetch(API_BASE + '/api/state', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    }).catch(function() {});
  } catch(e) {}
}

// ============================================================
// 持久化（localStorage，按用户隔离）
// ============================================================
var STORAGE_KEY = 'cultivation_data_v4_' + (AUTH_USER ? AUTH_USER.id : '0');

function loadData() {
  try {
    var raw = localStorage.getItem(STORAGE_KEY);
    if (raw) return JSON.parse(raw);
  } catch(e) {}
  return null;
}

function saveData(data) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
  } catch(e) {}
}

// ============================================================
// 初始化用户数据
// ============================================================
var saved = loadData();

var DEFAULT_USER = {
  name: (AUTH_USER && AUTH_USER.name) || '易',
  avatar: (AUTH_USER && AUTH_USER.avatar) || '易',
  title: (AUTH_USER && AUTH_USER.title) || '修炼者',
  level: (AUTH_USER && AUTH_USER.level) || 0,
  gender: (AUTH_USER && AUTH_USER.gender) || '',
  age: (AUTH_USER && AUTH_USER.age) || '',
  contact: (AUTH_USER && AUTH_USER.contact) || '',
  joinedDate: (AUTH_USER && AUTH_USER.joinedDate) || '2026-06-13',
  specializations: (AUTH_USER && AUTH_USER.specializations) || [],
  journals: [],
  completedTasks: (AUTH_USER && AUTH_USER.completedTasks) || []
};

// 合并存档（默认值兜底）
var USER = saved ? Object.assign({}, DEFAULT_USER, saved.user) : Object.assign({}, DEFAULT_USER);
var EVENT_LOG = saved ? (saved.events || []) : [];
var _msgCounter = saved ? (saved._msgCounter || 0) : 0;
var MESSAGES = saved ? (saved.messages || []) : [];
// 清理旧版本遗留的碎消息
MESSAGES = MESSAGES.filter(function(m) { return m.text !== '答对一题' && m.text !== '写下了突破感悟'; });
// 迁移旧消息：补充 id 和 pinned 字段
MESSAGES.forEach(function(m) {
  if (m.id === undefined) m.id = ++_msgCounter;
  if (m.pinned === undefined) m.pinned = false;
});

// 初次访问：发一条欢迎消息
if (!saved) {
  MESSAGES.push({
    id: ++_msgCounter,
    icon: '',
    text: '欢迎踏入计算机修行录！从"入门考核"开始你的修炼之路。每完成一个关卡、通过一次考核，你的战力属性都会增长。',
    time: USER.joinedDate,
    unread: false,
    pinned: false
  });
}

// 动态计算属性
USER.stats = calcStats(USER.level, EVENT_LOG);
USER.progress = calcProgress(USER.level, USER.completedTasks);

// ============================================================
// 记录事件（唯一的写入入口）
// ============================================================
function recordEvent(type, details) {
  details = details || {};
  var event = {
    type: type,
    date: new Date().toISOString().slice(0, 10),
    desc: details.desc || '',
    value: details.value || null,
    ref: details.ref || null    // 用于回撤（如取消完成任务时移除事件）
  };
  EVENT_LOG.push(event);

  // 重算属性
  USER.stats = calcStats(USER.level, EVENT_LOG);

  // 自动生成一条消息
  var msgMap = {
    task_done:      { icon: '', text: '完成关卡：' + (event.desc || '未知任务') },
    quiz_pass:      { icon: '', text: '通过【' + LEVELS[USER.level].name + '】考核！' },
    // quiz_correct 太碎，不生成消息，静默加 theory
    resource_read:  { icon: '', text: '阅读了修炼资源：' + (event.desc || '') },
    // journal_write 静默记录，不发消息
    tool_unlock:    { icon: '', text: '解锁新工具：' + (event.desc || '') },
    config_file:    { icon: '', text: '编写了配置文件' }
  };
  if (msgMap[type]) {
    MESSAGES.unshift({
      id: ++_msgCounter,
      icon: msgMap[type].icon,
      text: msgMap[type].text,
      time: event.date,
      unread: true,
      pinned: false
    });
  }

  if (details._localOnly) {
    saveLocalOnly();
  } else {
    persistAll();
  }
  return event;
}

// 移除事件（用于取消完成关卡等回撤操作）
function removeEventByRef(type, ref) {
  for (var i = EVENT_LOG.length - 1; i >= 0; i--) {
    if (EVENT_LOG[i].type === type && EVENT_LOG[i].ref === ref) {
      EVENT_LOG.splice(i, 1);
      USER.stats = calcStats(USER.level, EVENT_LOG);
      persistAll();
      return true;
    }
  }
  return false;
}

// 写全量数据到 localStorage
function persistAll() {
  var payload = {
    user: {
      name: USER.name,
      avatar: USER.avatar,
      title: USER.title,
      level: USER.level,
      gender: USER.gender,
      age: USER.age,
      contact: USER.contact,
      joinedDate: USER.joinedDate,
      specializations: USER.specializations,
      journals: USER.journals,
      completedTasks: USER.completedTasks
    },
    events: EVENT_LOG,
    messages: MESSAGES,
    _msgCounter: _msgCounter
  };
  saveData(payload);
  // 记录本地修改时间（用于 last-write-wins 同步）
  localStorage.setItem(STORAGE_KEY + '_mtime', new Date().toISOString());
  // 同步到后端（fire-and-forget，失败不影响本地）
  apiSave({
    user: payload.user,
    events: payload.events,
    messages: payload.messages,
    journals: payload.user.journals || []
  });
}

// 仅保存到 localStorage，不调用后端全量同步
function saveLocalOnly() {
  var payload = {
    user: {
      name: USER.name,
      avatar: USER.avatar,
      title: USER.title,
      level: USER.level,
      gender: USER.gender,
      age: USER.age,
      contact: USER.contact,
      joinedDate: USER.joinedDate,
      specializations: USER.specializations,
      journals: USER.journals,
      completedTasks: USER.completedTasks
    },
    events: EVENT_LOG,
    messages: MESSAGES,
    _msgCounter: _msgCounter
  };
  saveData(payload);
  localStorage.setItem(STORAGE_KEY + '_mtime', new Date().toISOString());
}

// 后端任务完成接口
function apiCompleteTask(levelId, taskIdx) {
  return apiFetch(API_BASE + '/api/tasks/complete', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ level_id: levelId, task_idx: taskIdx })
  }).then(function(r) {
    if (!r.ok) return r.json().then(function(err) { return { ok: false, error: err }; });
    return r.json();
  }).catch(function() { return { ok: false }; });
}

// 后端任务取消接口
function apiUndoTask(levelId, taskIdx) {
  return apiFetch(API_BASE + '/api/tasks/undo', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ level_id: levelId, task_idx: taskIdx })
  }).then(function(r) {
    if (!r.ok) return r.json().then(function(err) { return { ok: false, error: err }; });
    return r.json();
  }).catch(function() { return { ok: false }; });
}

// ============================================================
// 关卡完成/取消
// ============================================================
function toggleTask(levelId, taskIdx) {
  var key = levelId + '-' + taskIdx;
  var idx = USER.completedTasks.indexOf(key);
  if (idx >= 0) {
    // 取消完成：先调后端，成功再更新本地
    return apiUndoTask(levelId, taskIdx).then(function(res) {
      if (!res || !res.ok) return false;
      USER.completedTasks.splice(idx, 1);
      // 删除对应的本地事件
      for (var i = EVENT_LOG.length - 1; i >= 0; i--) {
        if (EVENT_LOG[i].type === 'task_done' && EVENT_LOG[i].ref === key) {
          EVENT_LOG.splice(i, 1);
          break;
        }
      }
      USER.stats = calcStats(USER.level, EVENT_LOG);
      USER.progress = calcProgress(USER.level, USER.completedTasks);
      saveLocalOnly();
      return true;
    });
  } else {
    // 标记完成：先调后端，成功再更新本地
    return apiCompleteTask(levelId, taskIdx).then(function(res) {
      if (!res || !res.ok) return false;
      USER.completedTasks.push(key);
      var taskDesc = (LEVELS[levelId].tasks[taskIdx] || '').substring(0, 40);
      recordEvent('task_done', {
        value: res.reward,
        ref: key,
        desc: taskDesc,
        _localOnly: true
      });
      USER.progress = calcProgress(USER.level, USER.completedTasks);
      USER.stats = res.stats || calcStats(USER.level, EVENT_LOG);
      saveLocalOnly();
      return true;
    });
  }
}

// 检查某个关卡是否已完成
function isTaskDone(levelId, taskIdx) {
  return USER.completedTasks.indexOf(levelId + '-' + taskIdx) >= 0;
}

// ============================================================
// 题库抽取（保持不变）
// ============================================================
function pickQuestions(levelId, n) {
  var pool = QUESTION_BANK.filter(function(q) { return q.level === levelId; });
  if (pool.length <= n) return pool.slice();
  var groups = {}, picks = [];
  pool.forEach(function(q) {
    if (!groups[q.cat]) groups[q.cat] = [];
    groups[q.cat].push(q);
  });
  var cats = Object.keys(groups);
  cats.sort(function() { return Math.random() - 0.5; });
  cats.forEach(function(cat) {
    if (picks.length >= n) return;
    var arr = groups[cat];
    arr.sort(function() { return Math.random() - 0.5; });
    picks.push(arr[0]);
  });
  var remaining = [];
  pool.forEach(function(q) {
    if (!picks.some(function(p) { return p === q; })) remaining.push(q);
  });
  remaining.sort(function() { return Math.random() - 0.5; });
  while (picks.length < n && remaining.length > 0) picks.push(remaining.shift());
  picks.sort(function() { return Math.random() - 0.5; });
  return picks.slice(0, n);
}

// ============================================================
// 关卡验证题库（每关一道客观题，答对方可勾选完成）
// key = "段位号-关卡序号"
// ============================================================
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

// 段位突破（通过当前段考核后调用）
function levelUp() {
  if (USER.level >= 9) return false;
  USER.level++;
  USER.stats = calcStats(USER.level, EVENT_LOG);
  USER.progress = calcProgress(USER.level, USER.completedTasks);
  MESSAGES.unshift({
    id: ++_msgCounter,
    icon: '',
    text: '突破至【' + LEVELS[USER.level].name + '】— ' + LEVELS[USER.level].poem,
    time: new Date().toISOString().slice(0, 10),
    unread: true,
    pinned: false
  });
  persistAll();
  return true;
}

// 消息操作
function deleteMessage(id) {
  for (var i = 0; i < MESSAGES.length; i++) {
    if (MESSAGES[i].id === id) {
      MESSAGES.splice(i, 1);
      persistAll();
      return true;
    }
  }
  return false;
}

function togglePinMessage(id) {
  for (var i = 0; i < MESSAGES.length; i++) {
    if (MESSAGES[i].id === id) {
      MESSAGES[i].pinned = !MESSAGES[i].pinned;
      persistAll();
      return true;
    }
  }
  return false;
}

// 点击资源链接时记录
function recordResourceRead(levelId, resIdx) {
  var level = LEVELS[levelId];
  if (!level || !level.resources || !level.resources[resIdx]) return;
  recordEvent('resource_read', { desc: level.resources[resIdx].name });
}

// ============================================================
// 全部已读
// ============================================================
function markAllRead() {
  for (var i = 0; i < MESSAGES.length; i++) {
    MESSAGES[i].unread = false;
  }
  persistAll();
  // 同步到后端
  apiFetch(API_BASE + '/api/messages/read-all', { method: 'PUT' }).catch(function() {});
}

// ============================================================
// 启动时从后端同步数据（last-write-wins）
// ============================================================
function pullAndReload() {
  // 用页面加载次数防止同一次加载里反复 reload
  var loadCount = parseInt(sessionStorage.getItem('_cultivation_load') || '0');
  sessionStorage.setItem('_cultivation_load', String(loadCount + 1));
  if (loadCount > 2) return;  // 防止死循环

  apiFetch(API_BASE + '/api/state')
    .then(function(r) { return r.json(); })
    .then(function(data) {
      if (!data || !data.user) return;

      var remoteModified = data.lastModified || '';
      var localModified = localStorage.getItem(STORAGE_KEY + '_mtime') || '';

      var hasRemoteData = (data.events && data.events.length > 0) ||
        (data.messages && data.messages.length > 1) ||
        (data.user.level > 0);

      var localRaw = localStorage.getItem(STORAGE_KEY);
      var hasLocalData = localRaw && localRaw.length > 10;

      if (!hasRemoteData && !hasLocalData) return;

      if (!hasRemoteData) {
        if (hasLocalData) {
          var local = JSON.parse(localRaw);
          apiSave({
            user: local.user || {},
            events: local.events || [],
            messages: local.messages || [],
            journals: (local.user && local.user.journals) || []
          });
        }
        return;
      }

      if (!hasLocalData) {
        var remotePayload = {
          user: Object.assign({}, data.user, { journals: data.journals || [] }),
          events: data.events || [],
          messages: data.messages || [],
          _msgCounter: (data.messages || []).length
            ? Math.max.apply(null, data.messages.map(function(m) { return m.id; }))
            : 0
        };
        saveData(remotePayload);
        localStorage.setItem(STORAGE_KEY + '_mtime', remoteModified);
        window.location.reload();
        return;
      }

      // 两边都有 → last-write-wins
      if (remoteModified && localModified && remoteModified <= localModified) {
        var loc = JSON.parse(localRaw);
        apiSave({
          user: loc.user || {},
          events: loc.events || [],
          messages: loc.messages || [],
          journals: (loc.user && loc.user.journals) || []
        });
        return;
      }

      if (remoteModified && (!localModified || remoteModified > localModified)) {
        var rp = {
          user: Object.assign({}, data.user, { journals: data.journals || [] }),
          events: data.events || [],
          messages: data.messages || [],
          _msgCounter: (data.messages || []).length
            ? Math.max.apply(null, data.messages.map(function(m) { return m.id; }))
            : 0
        };
        saveData(rp);
        localStorage.setItem(STORAGE_KEY + '_mtime', remoteModified);
        window.location.reload();
        return;
      }
    })
    .catch(function() {});
}

pullAndReload();
