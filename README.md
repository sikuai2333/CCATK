# CCATK

> ⚠️ 安全声明：本仓库新增的 GUI 工具仅用于**合法授权**的可达性巡检与代理连通性检测，不提供攻击能力。

## 新增：Geek 风格 GUI 监控台

为改善原有单线命令行流程，新增 `gui_monitor.py`：

- 黑色背景、终端日志窗口风格（geek theme）
- 参数面板 + 控制按钮 + 实时日志 + 统计信息
- 交互式流程：配置参数 → 启动巡检 → 实时观测 → 导出日志
- 代理文件加载与批量可用性检测（结果输出 `available_proxies.txt`）

### 运行方式

```bash
pip3 install requests
python3 gui_monitor.py
```

### GUI 功能说明

1. **目标 URL**：输入待巡检服务地址（`http://` 或 `https://`）。
2. **HTTP 方法**：可选择 `GET` / `HEAD`。
3. **巡检间隔**：每次请求之间的时间（秒）。
4. **请求超时**：单次请求超时（秒）。
5. **代理文件**：加载 `ip:port` 的 txt 文件后可执行代理可用性检测。
6. **日志导出**：将窗口日志导出为 `.log/.txt` 文件。

---

## 旧脚本

使用socks4 / 5代理攻击http（s）服务器的脚本。

新闻：

 增加了输出指示器
 添加了网址解析器
信息：

 使用Python3
 添加了更多类似人的选项
 Http Get / Head / Post / Slow Flood
 随机Http标头/数据
 Socks4/5代理下载器
 Socks4/5代理检查器
 自定义Cookie
 自定义帖子数据
 支持HTTPS
 支持Socks4/5

## 安装

    pip3 install requests pysocks
    git clone https://github.com/BlueSkyXN/CCATK.git
    cd CCATK

## 使用

    python3 atk2.py
## GUI 控制台（Geek 风格）

新增 `gui_console.py`，提供黑色背景日志窗主题的可视化界面，并将原本线性的命令交互整理为单线流程：

1. 配置目标 URL、超时、间隔、轮次
2. （可选）载入代理文件并做可用性校验
3. 一键启动并在日志窗口实时查看状态

### 运行方式

```bash
python3 gui_console.py
```

> 注意：GUI 仅实现**授权范围内**的连通性/健康检查，不包含破坏性攻击逻辑。
