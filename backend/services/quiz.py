"""
计算机修行录 - 题库与考核服务
"""
import random

# 题库（从 data.js QUESTION_BANK 迁移，102题）
QUESTION_BANK: list[dict] = [
    # --- 入门（level:0）--- 29题
    {"level":0, "cat":"基础", "q":"计算机中 1KB 等于多少字节？", "opts":["100","512","1024","2048"], "ans":2, "tip":"1KB = 1024 字节（Byte）。"},
    {"level":0, "cat":"基础", "q":"以下哪个不是操作系统？", "opts":["Windows","Linux","Python","macOS"], "ans":2, "tip":"Python 是编程语言，不是操作系统。"},
    {"level":0, "cat":"基础", "q":"以下哪个是网址（URL）？", "opts":["C:/Users/...","cmd.exe","www.python.org","notepad"], "ans":2, "tip":"以 www. 开头的一般就是网址。"},
    {"level":0, "cat":"基础", "q":"编程中 `=` 通常表示什么？", "opts":["等于判断","赋值","比较大小","删除"], "ans":1, "tip":"大多数语言里 `=` 是赋值，`==` 才是判断相等。"},
    {"level":0, "cat":"基础", "q":"\"Bug\" 在编程中通常指什么？", "opts":["一种虫子","代码中的错误","病毒","操作系统"], "ans":1, "tip":"Bug 就是代码里的漏洞或错误。"},
    {"level":0, "cat":"基础", "q":"以下哪个是合法的文件名？", "opts":["file<>.txt","file?.txt","file.txt","file|.txt"], "ans":2, "tip":"< > ? | 等符号在文件名中是不允许的。"},
    {"level":0, "cat":"基础", "q":"文件扩展名 .py 通常表示什么？", "opts":["图片文件","Python 源代码","压缩文件","可执行程序"], "ans":1, "tip":".py 是 Python 脚本文件的常见扩展名。"},
    {"level":0, "cat":"基础", "q":"CPU 的主要功能是什么？", "opts":["存储文件","执行运算和指令","显示图像","连接网络"], "ans":1, "tip":"CPU 是计算机的大脑，负责运算和指令执行。"},
    {"level":0, "cat":"工程", "q":"在命令行中 Ctrl+C 通常用于什么？", "opts":["复制文字","中断正在运行的程序","关闭窗口","保存文件"], "ans":1, "tip":"Ctrl+C 在命令行里是发送中断信号。"},
    {"level":0, "cat":"读码", "q":"代码中 `#` 开头的行通常是什么？", "opts":["错误提示","注释（不会执行）","重要代码","输出内容"], "ans":1, "tip":"`#` 在 Python 中表示注释，不会被程序执行。"},
    {"level":0, "cat":"安全", "q":"收到陌生人发的 .exe 文件，最好的做法是？", "opts":["直接双击打开","先发给朋友看看","不要打开，可能是病毒","改个名字再开"], "ans":2, "tip":"不明来源的可执行文件可能包含恶意程序。"},
    {"level":0, "cat":"安全", "q":"设置密码时，以下哪个相对最安全？", "opts":["123456","password","生日日期","混合大小写字母数字符号的长密码"], "ans":3, "tip":"长密码 + 多种字符混合，最难被破解。"},
    {"level":0, "cat":"基础", "q":"计算机内存（RAM）和硬盘的主要区别是什么？", "opts":["没有区别","硬盘更快","RAM 断电数据消失，硬盘持久保存","RAM 是用来上网的"], "ans":2, "tip":"RAM 是临时存储，关机就没了。硬盘文件不会消失。"},
    {"level":0, "cat":"基础", "q":"以下哪个是输入设备？", "opts":["显示器","键盘","音箱","打印机"], "ans":1, "tip":"键盘和鼠标是输入设备；显示器和音箱是输出设备。"},
    {"level":0, "cat":"基础", "q":"\"源代码\" 通常是指什么？", "opts":["编译后的文件","程序员写的原始代码","电脑的启动程序","操作系统内核"], "ans":1, "tip":"源代码就是程序员写的原始程序文本，还没编译。"},
    {"level":0, "cat":"基础", "q":"操作系统的主要功能不包括？", "opts":["管理硬件资源","提供用户界面","编写应用程序","管理文件系统"], "ans":2, "tip":"操作系统不负责帮你写应用，那是程序员干的。"},
    {"level":0, "cat":"基础", "q":"显示器分辨率 1920×1080 表示什么？", "opts":["屏幕尺寸大小","横向和纵向的像素点数","刷新频率","色彩范围"], "ans":1, "tip":"1920×1080 表示横向 1920 个像素，纵向 1080 个像素。"},
    {"level":0, "cat":"基础", "q":"以下哪种文件是压缩文件？", "opts":[".txt",".zip",".exe",".html"], "ans":1, "tip":".zip、.rar、.7z 都是常见的压缩文件格式。"},
    {"level":0, "cat":"基础", "q":"以下哪个存储容量最大？", "opts":["1KB","1MB","1GB","1B"], "ans":2, "tip":"B < KB < MB < GB < TB，1GB = 1024MB。"},
    {"level":0, "cat":"读码", "q":"print('Hello ' + 'World') 输出什么？", "opts":["HelloWorld","Hello World","Hello+World","报错"], "ans":1, "tip":"字符串用 + 拼接，'Hello ' 末尾有空格，所以输出 Hello World。"},
    {"level":0, "cat":"读码", "q":"name = '易' 中 name 是什么？", "opts":["函数","变量","文件","命令"], "ans":1, "tip":"name 是一个变量，存储了字符串 '易'。"},
    {"level":0, "cat":"读码", "q":"print(2 + 3 * 4) 输出什么？", "opts":["20","14","9","报错"], "ans":1, "tip":"先乘除后加减，3×4=12，2+12=14。"},
    {"level":0, "cat":"读码", "q":"print(10 / 3) 输出大概是多少？", "opts":["3","3.333...","1","报错"], "ans":1, "tip":"Python 中 / 是浮点除法，结果带小数。"},
    {"level":0, "cat":"安全", "q":"浏览器提示\"此网站不安全\"通常因为？", "opts":["网站没有 HTTPS 加密","网站图片太多","网站内容太长","网站服务器太慢"], "ans":0, "tip":"HTTPS 加密保护你在网站上输入的信息不会被窃取。"},
    {"level":0, "cat":"安全", "q":"以下哪个做法最容易导致账号被盗？", "opts":["使用复杂密码","多个网站用同一个密码","定期换密码","开启两步验证"], "ans":1, "tip":"一个密码走天下，一处泄露全部遭殃。每个网站用不同密码。"},
    {"level":0, "cat":"安全", "q":"看到弹窗说\"你的电脑中了病毒，打这个电话\"应该？", "opts":["立即拨打电话","关闭网页不要理它","点击弹窗里的按钮","下载推荐的软件"], "ans":1, "tip":"这是常见诈骗手段，正规杀毒软件不会弹窗让你打电话。"},
    {"level":0, "cat":"工程", "q":"写代码时为什么推荐写注释？", "opts":["让程序运行更快","帮助自己和别人理解代码","让代码更好看","注释是程序必需的"], "ans":1, "tip":"注释不运行，但能让代码好懂。一周后你可能也会看不懂自己写的。"},
    {"level":0, "cat":"工程", "q":"以下哪个是代码编辑器？", "opts":["VS Code","Chrome","Photoshop","Steam"], "ans":0, "tip":"VS Code 是目前最流行的代码编辑器。"},
    {"level":0, "cat":"工程", "q":"程序运行报错了，第一件事应该做什么？", "opts":["关掉编辑器重写","读报错信息看是哪一行","重装 Python","不管继续运行"], "ans":1, "tip":"报错信息通常包含出错行号和原因，学会读错误是编程第一步。"},
    # --- 初段（level:1）---
    {"level":1, "cat":"基础", "q":"Python 中 `type(42)` 返回什么？", "opts":["<class 'int'>","<class 'str'>","42","<class 'number'>"], "ans":0, "tip":"42 是整数，类型是 int。"},
    {"level":1, "cat":"基础", "q":"print('Hello' * 3) 输出什么？", "opts":["Hello","HelloHelloHello","Hello 3","报错"], "ans":1, "tip":"字符串乘以数字会重复拼接。"},
    {"level":1, "cat":"基础", "q":"Python 中用哪个函数获取用户键盘输入？", "opts":["read()","input()","scan()","get()"], "ans":1, "tip":"input() 用于读取用户输入，返回字符串。"},
    {"level":1, "cat":"基础", "q":"list = [1,2,3]; print(list[1]) 输出什么？", "opts":["1","2","3","报错"], "ans":1, "tip":"列表索引从 0 开始，list[1] 是第二个元素。"},
    {"level":1, "cat":"读码", "q":"for i in range(3): print(i) 输出什么？", "opts":["1 2 3","0 1 2","0 1 2 3","1 2"], "ans":1, "tip":"range(3) 生成 0,1,2，不包含 3。"},
    {"level":1, "cat":"读码", "q":"x=5; if x>3: print('大') 的执行结果是？", "opts":["大","小","报错","没有输出"], "ans":0, "tip":"5>3 为 True，执行 if 内的语句打印'大'。"},
    {"level":1, "cat":"读码", "q":"print(10 % 3) 输出什么？", "opts":["3","1","3.33","0"], "ans":1, "tip":"% 是取余运算符，10÷3=3 余 1。"},
    {"level":1, "cat":"工程", "q":"Git 暂存区是什么？", "opts":["Git 的备份服务器","修改后、提交前的临时区域","代码编译后的文件","分支合并的工具"], "ans":1, "tip":"暂存区是 git add 后、git commit 前。"},
    {"level":1, "cat":"工程", "q":".gitignore 文件的作用是什么？", "opts":["加快 Git 速度","指定哪些文件不加入版本控制","存储 Git 密码","记录提交历史"], "ans":1, "tip":".gitignore 告诉 Git 忽略某些文件（如临时文件、密钥）。"},
    {"level":1, "cat":"安全", "q":"直接把用户输入拼进 SQL 查询有什么风险？", "opts":["更高效","可能被 SQL 注入攻击","代码更短","没有影响"], "ans":1, "tip":"任何用户输入都不应直接拼进 SQL 查询。"},
    # --- 二段（level:2）---
    {"level":2, "cat":"基础", "q":"Python 中 def 关键字用于什么？", "opts":["定义变量","定义函数","导入模块","创建类"], "ans":1, "tip":"def 是 define 的缩写，用来定义函数。"},
    {"level":2, "cat":"基础", "q":"函数的参数默认值在什么时候被计算？", "opts":["每次调用时","函数定义时","程序启动时","永远不会"], "ans":1, "tip":"默认值在函数定义时计算一次，之后调用共享同一个对象。"},
    {"level":2, "cat":"基础", "q":"import os 中 os 是什么？", "opts":["操作系统名称","Python 标准库模块","一个变量名","文件路径"], "ans":1, "tip":"os 是 Python 内置模块，提供操作系统相关功能。"},
    {"level":2, "cat":"读码", "q":"def add(a,b=10): return a+b; add(5) 返回什么？", "opts":["报错","15","5","10"], "ans":1, "tip":"b 有默认值 10，调用 add(5) 等价于 add(5,10)，返回 15。"},
    {"level":2, "cat":"读码", "q":"open('test.txt','w') 中 'w' 表示什么？", "opts":["读取","写入（覆盖）","追加","删除"], "ans":1, "tip":"'w'=write 写入模式，'r'=read 读取，'a'=append 追加。"},
    {"level":2, "cat":"工程", "q":"pip freeze > requirements.txt 这条命令做了什么？", "opts":["安装依赖","导出当前环境的包列表到文件","删除所有包","升级 pip"], "ans":1, "tip":"pip freeze 列出已安装的包，> 重定向到文件。"},
    {"level":2, "cat":"工程", "q":"git clone 命令的作用是什么？", "opts":["创建新分支","复制远程仓库到本地","提交代码","删除仓库"], "ans":1, "tip":"git clone <url> 把远程仓库完整下载到本地。"},
    {"level":2, "cat":"安全", "q":"把 API 密钥写在代码里直接提交到 GitHub 有什么风险？", "opts":["代码运行变慢","密钥泄露，别人可以盗用","GitHub 会封号","没有风险"], "ans":1, "tip":"密钥应该用环境变量存放，不能硬编码提交。"},
    # --- 三段（level:3）---
    {"level":3, "cat":"基础", "q":"Flask 中 @app.route('/') 装饰器的作用是什么？", "opts":["定义函数名","把 URL 路径映射到函数","设置变量类型","导入模块"], "ans":1, "tip":"@app.route 将 URL 路径绑定到视图函数。"},
    {"level":3, "cat":"基础", "q":"SQL 中 INSERT INTO 语句的作用是什么？", "opts":["查询数据","插入新记录","删除数据","修改表结构"], "ans":1, "tip":"INSERT INTO 用于向表中添加新数据行。"},
    {"level":3, "cat":"基础", "q":"HTML 中 <h1> 标签表示什么？", "opts":["段落","一级标题","超链接","图片"], "ans":1, "tip":"h1-h6 是标题标签，数字越小级别越高。"},
    {"level":3, "cat":"读码", "q":"SELECT * FROM users WHERE age > 18 查询什么？", "opts":["所有用户","年龄大于 18 的用户","年龄等于 18 的用户","删除用户"], "ans":1, "tip":"WHERE 子句过滤符合条件的行。"},
    {"level":3, "cat":"读码", "q":"CSS 中 .box { color: red; } 的 .box 是什么选择器？", "opts":["ID 选择器","类选择器","标签选择器","属性选择器"], "ans":1, "tip":"点号 . 开头是类选择器，# 开头是 ID 选择器。"},
    {"level":3, "cat":"工程", "q":"CRUD 四个字母代表什么操作？", "opts":["创建-读取-更新-删除","复制-重命名-上传-下载","编译-运行-测试-部署","连接-请求-响应-断开"], "ans":0, "tip":"Create, Read, Update, Delete —— 数据操作四大基本动作。"},
    {"level":3, "cat":"工程", "q":"RESTful API 中 GET 请求通常用于什么？", "opts":["创建资源","获取/查询资源","更新资源","删除资源"], "ans":1, "tip":"GET=查询，POST=创建，PUT/PATCH=更新，DELETE=删除。"},
    {"level":3, "cat":"安全", "q":"HTTP 和 HTTPS 的主要区别是什么？", "opts":["速度不同","HTTPS 有加密，HTTP 没有","端口不同","没有区别"], "ans":1, "tip":"HTTPS = HTTP + SSL/TLS 加密，保护数据传输安全。"},
    # --- 四段（level:4）---
    {"level":4, "cat":"基础", "q":"Linux 中 ls 命令的作用是什么？", "opts":["创建文件","列出目录内容","删除文件","修改权限"], "ans":1, "tip":"ls = list，显示当前目录下的文件和文件夹。"},
    {"level":4, "cat":"基础", "q":"Dockerfile 中 FROM 指令的作用是什么？", "opts":["指定工作目录","指定基础镜像","复制文件","运行命令"], "ans":1, "tip":"FROM 指定构建镜像的基础，如 FROM python:3.11。"},
    {"level":4, "cat":"基础", "q":"Nginx 通常用作什么？", "opts":["数据库","反向代理 / Web 服务器","编程语言","操作系统"], "ans":1, "tip":"Nginx 是高性能的 Web 服务器和反向代理。"},
    {"level":4, "cat":"读码", "q":"docker build -t myapp . 中 -t 参数的作用？", "opts":["指定超时时间","给镜像打标签（名字）","指定线程数","测试模式"], "ans":1, "tip":"-t 给构建的镜像命名，如 myapp:latest。"},
    {"level":4, "cat":"工程", "q":"SSH 密钥对包含哪两个文件？", "opts":["公钥和私钥","加密和解密","输入和输出","配置和日志"], "ans":0, "tip":"SSH 密钥对：公钥（放服务器）和私钥（自己保管）。"},
    {"level":4, "cat":"工程", "q":"JWT 令牌通常包含哪三部分？", "opts":["用户名-密码-邮箱","Header-Payload-Signature","请求-响应-状态","加密-解密-验证"], "ans":1, "tip":"JWT 由 Header、Payload、Signature 三部分组成，用点号分隔。"},
    {"level":4, "cat":"安全", "q":"服务器防火墙只开放 80 和 443 端口的好处是什么？", "opts":["加速访问","减少攻击面，只允许 Web 流量","省电","方便调试"], "ans":1, "tip":"最小化开放端口是安全基本原则，减少被攻击的入口。"},
    {"level":4, "cat":"安全", "q":"数据库密码应该怎么存放？", "opts":["写在代码注释里","用环境变量 / 密钥管理服务","发到群聊里备份","用 123456"], "ans":1, "tip":"密码和密钥永远不应硬编码，用环境变量或 Vault 管理。"},
    # --- 五段（level:5）---
    {"level":5, "cat":"基础", "q":"单元测试中 mock 的作用是什么？", "opts":["加速测试","模拟外部依赖的行为","美化代码","生成随机数据"], "ans":1, "tip":"Mock 用于隔离被测代码，模拟数据库、API 等外部依赖。"},
    {"level":5, "cat":"基础", "q":"Redis 默认把数据存在哪里？", "opts":["硬盘文件","内存中","远程服务器","数据库表"], "ans":1, "tip":"Redis 是内存数据库，数据主要在内存中，所以非常快。"},
    {"level":5, "cat":"读码", "q":"CI/CD 流水线中的 'CI' 全称是什么？", "opts":["Code Integration","Continuous Integration","Complete Installation","Client Interface"], "ans":1, "tip":"CI=持续集成，CD=持续交付/部署。"},
    {"level":5, "cat":"工程", "q":"做性能压测时，QPS 指的是什么？", "opts":["每秒查询数","代码质量分","量子处理速度","问题数量"], "ans":0, "tip":"QPS = Queries Per Second，衡量系统吞吐量的关键指标。"},
    {"level":5, "cat":"工程", "q":"Redis 缓存雪崩的主要原因是什么？", "opts":["内存太小","大量缓存同时过期，请求直接打到数据库","网络断开","Redis 版本太旧"], "ans":1, "tip":"缓存雪崩=大量 key 同时过期，流量瞬间压到数据库。设置随机过期时间可缓解。"},
    {"level":5, "cat":"工程", "q":"Code Review 时最应该关注什么？", "opts":["代码缩进是否对齐","逻辑正确性、安全漏洞、可维护性","变量命名是否够短","注释是否够多"], "ans":1, "tip":"CR 核心：逻辑对不对、有没有安全漏洞、以后好不好维护。"},
    {"level":5, "cat":"安全", "q":"生产环境的 DEBUG 模式应该怎么设置？", "opts":["永远开启","必须关闭","看情况","无所谓"], "ans":1, "tip":"DEBUG 模式会泄露代码细节和敏感信息，生产环境必须关闭。"},
    # --- 六段（level:6）---
    {"level":6, "cat":"基础", "q":"CAP 定理中 C、A、P 分别代表什么？", "opts":["一致性-可用性-分区容错","计算-分析-处理","创建-追加-清除","缓存-应用-代理"], "ans":0, "tip":"CAP = Consistency, Availability, Partition Tolerance，分布式系统最多同时满足两个。"},
    {"level":6, "cat":"基础", "q":"消息队列（如 Kafka）的核心作用是什么？", "opts":["存储文件","异步解耦、削峰填谷","渲染页面","加密数据"], "ans":1, "tip":"消息队列让生产者和消费者解耦，平滑流量峰值。"},
    {"level":6, "cat":"读码", "q":"微服务架构相比单体架构的主要优势是？", "opts":["代码更少","各服务独立部署、独立扩缩容","不需要数据库","没有 bug"], "ans":1, "tip":"微服务核心优势：独立部署、技术栈灵活、故障隔离。"},
    {"level":6, "cat":"工程", "q":"数据库读写分离通常怎么实现？", "opts":["买更好的服务器","主库写、从库读，通过中间件路由","把所有表拆开","用 Excel"], "ans":1, "tip":"读写分离：写操作走主库，读操作走从库，减轻主库压力。"},
    {"level":6, "cat":"工程", "q":"画系统架构图时，最应该标注什么？", "opts":["每个组件的颜色","组件间数据流向、通信协议、选型理由","代码行数","作者名字"], "ans":1, "tip":"架构图核心：谁调谁、怎么通信、为什么选这个。"},
    {"level":6, "cat":"工程", "q":"负载均衡的常见算法有哪些？", "opts":["冒泡排序","轮询、最少连接、IP 哈希","快速排序","二分查找"], "ans":1, "tip":"常见负载均衡算法：Round Robin、Least Connections、IP Hash。"},
    {"level":6, "cat":"安全", "q":"SQL 注入攻击的防护措施不包括？", "opts":["参数化查询","ORM 框架","直接把用户输入拼 SQL","输入校验"], "ans":2, "tip":"参数化查询和 ORM 是最有效的 SQL 注入防护手段。"},
    # --- 七段（level:7）---
    {"level":7, "cat":"基础", "q":"操作系统中的虚拟内存是什么？", "opts":["不存在的内存","硬盘空间映射为内存地址，扩展可用内存","云端存储","缓存"], "ans":1, "tip":"虚拟内存让程序以为自己有连续大内存，实际由 OS 映射到物理内存+磁盘。"},
    {"level":7, "cat":"基础", "q":"TCP 三次握手的主要目的是什么？", "opts":["加密数据","建立可靠连接，同步序列号","传输文件","关闭连接"], "ans":1, "tip":"三次握手确保双方收发能力正常，同步初始序列号。"},
    {"level":7, "cat":"读码", "q":"GIL（全局解释器锁）主要影响 Python 的什么场景？", "opts":["文件读写","CPU 密集型多线程","网络请求","GUI 界面"], "ans":1, "tip":"GIL 导致 Python 多线程无法利用多核跑 CPU 密集任务，需用多进程。"},
    {"level":7, "cat":"工程", "q":"高并发系统中，为什么需要限流？", "opts":["让用户排队","保护系统不被突发流量打垮","增加收入","减少代码量"], "ans":1, "tip":"限流（Rate Limiting）防止突发流量耗尽资源导致雪崩。"},
    {"level":7, "cat":"工程", "q":"火焰图（Flame Graph）主要用于什么？", "opts":["美化界面","可视化 CPU 耗时分布，定位性能瓶颈","画3D图形","加密"], "ans":1, "tip":"火焰图横轴表示占用比例，从下往上显示调用栈，宽度越大越值得优化。"},
    {"level":7, "cat":"工程", "q":"DDD（领域驱动设计）的核心思想是什么？", "opts":["先写代码再想设计","围绕业务领域建模，代码反映业务语言","用最快的框架","越简单越好"], "ans":1, "tip":"DDD 强调深入理解业务，用领域模型驱动软件设计。"},
    {"level":7, "cat":"安全", "q":"零信任安全模型的核心原则是什么？", "opts":["信任所有人","永不信任，始终验证","只信任内部网络","不需要安全措施"], "ans":1, "tip":"零信任=不默认信任任何人/设备，每次都验证身份和权限。"},
    # --- 八段（level:8）---
    {"level":8, "cat":"基础", "q":"开源协议 MIT 和 GPL 的主要区别是什么？", "opts":["没有区别","GPL 要求衍生作品也开源（传染性），MIT 不要求","MIT 更严格","GPL 不能商用"], "ans":1, "tip":"MIT=宽松，做啥都行；GPL=强传染，用了就要开源。"},
    {"level":8, "cat":"基础", "q":"技术写作中「代码优先于注释」意味着什么？", "opts":["不写注释","好的代码应该自解释，注释解释「为什么」而非「做什么」","注释比代码重要","代码越短越好"], "ans":1, "tip":"代码写好命名和结构是基础，注释补充为什么要这样设计。"},
    {"level":8, "cat":"读码", "q":"一个开源库有 1000+ GitHub star 说明什么？", "opts":["代码完美无 bug","有较多开发者认可和关注","一定适合你的项目","作者很有钱"], "ans":1, "tip":"Star 是认可指标，不代表质量完美，选库还需看维护频率、文档、社区。"},
    {"level":8, "cat":"工程", "q":"设计一个框架时，API 的「向后兼容」是什么意思？", "opts":["兼容旧电脑","新版本不破坏旧版本的使用方式","兼容所有操作系统","兼容其他框架"], "ans":1, "tip":"向后兼容=升级版本后，老代码无需修改仍能正常运行。"},
    {"level":8, "cat":"工程", "q":"技术布道（Evangelism）的核心是什么？", "opts":["推销产品","用技术内容和实践影响开发者，建立信任","写广告","刷存在感"], "ans":1, "tip":"布道是通过高质量分享让开发者认可你的技术理念。好的布道是教育而非营销。"},
    {"level":8, "cat":"工程", "q":"一个好的技术方案应该包含哪些要素？", "opts":["只有代码","背景-目标-方案对比-风险-排期","只写结论","越多越好"], "ans":1, "tip":"方案要讲清楚：为什么做、怎么做、有什么选择、有什么风险。"},
]


def pick_questions(level_id: int, n: int) -> list[dict]:
    """Fisher-Yates 洗牌抽题，返回 n 道题（不带答案）。"""
    pool = [q for q in QUESTION_BANK if q["level"] == level_id]
    if len(pool) <= n:
        # 返回全部但洗牌
        result = pool[:]
        _shuffle(result)
        return [_strip_answer(q) for q in result]

    # 先按类别分组，每个类别抽一题（保证覆盖面）
    groups: dict[str, list] = {}
    for q in pool:
        groups.setdefault(q["cat"], []).append(q)

    picks: list[dict] = []
    cats = list(groups.keys())
    _shuffle(cats)
    for cat in cats:
        if len(picks) >= n:
            break
        _shuffle(groups[cat])
        picks.append(groups[cat][0])

    # 不够的随机补
    remaining = [q for q in pool if q not in picks]
    _shuffle(remaining)
    picks.extend(remaining[: n - len(picks)])
    _shuffle(picks)
    return [_strip_answer(q) for q in picks[:n]]


def grade_submission(level_id: int, answers: list[int]) -> dict:
    """判卷，返回详情。需要题目原始数据来比对答案。"""
    # 这里重新拿带答案的题目进行判卷
    pool = [q for q in QUESTION_BANK if q["level"] == level_id]

    # 如果 answers 按顺序对应前端题目列表，需要一个一致的题目列表
    # 这里由调用方传入完整的题目列表（含 ans）进行判卷
    # 实际上 grade 时我们只需要比答案 —— 但需要知道每题对应哪个 level
    # 简化：grade 由 quiz router 调用时传入完整题目列表 + 用户答案
    pass


def get_questions_with_answers(level_id: int, n: int) -> list[dict]:
    """抽题（带答案），供判卷用。"""
    pool = [q for q in QUESTION_BANK if q["level"] == level_id]
    if len(pool) <= n:
        result = pool[:]
        _shuffle(result)
        return result

    groups: dict[str, list] = {}
    for q in pool:
        groups.setdefault(q["cat"], []).append(q)

    picks: list[dict] = []
    cats = list(groups.keys())
    _shuffle(cats)
    for cat in cats:
        if len(picks) >= n:
            break
        _shuffle(groups[cat])
        picks.append(groups[cat][0])

    remaining = [q for q in pool if q not in picks]
    _shuffle(remaining)
    picks.extend(remaining[: n - len(picks)])
    _shuffle(picks)
    return picks[:n]


def grade_answers(questions: list[dict], answers: list[int], level_id: int) -> dict:
    """判卷并返回结果。
    questions: 带答案的题目列表
    answers: 用户答案（按题目顺序）
    level_id: 段位
    """
    total = len(questions)
    correct = 0
    results = []
    for i, q in enumerate(questions):
        user_ans = answers[i] if i < len(answers) else -1
        is_correct = user_ans == q["ans"]
        if is_correct:
            correct += 1
        results.append({
            "question": q["q"],
            "user_answer": user_ans,
            "correct_answer": q["ans"],
            "is_correct": is_correct,
            "tip": q.get("tip", ""),
        })

    pass_score = 4 if level_id == 0 else max(1, int(total * 0.75))
    passed = correct >= pass_score

    return {
        "passed": passed,
        "score": correct,
        "total": total,
        "pass_score": pass_score,
        "results": results,
    }


def _shuffle(arr: list):
    """Fisher-Yates 洗牌（原地）。"""
    for i in range(len(arr) - 1, 0, -1):
        j = random.randint(0, i)
        arr[i], arr[j] = arr[j], arr[i]


def _strip_answer(q: dict) -> dict:
    """返回不带答案的题目。"""
    return {
        "id": q.get("id", hash(q["q"]) % 100000),
        "level": q["level"],
        "category": q["cat"],
        "question": q["q"],
        "options": q["opts"],
    }
