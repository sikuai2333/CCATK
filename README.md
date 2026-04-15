# CCATK-V1

使用socks4 / 5代理攻击http服务器的脚本。

删除了混合代理洪水

 新特性:
-  快速套接字重用
-  改进的CC模式
-  随机客户端IP

 具体信息:
-  使用Python3
-  添加了更多智能选项
-  Http洪水
-  Http端口洪水
-  Http慢速攻击
-  支持HTTPS
-  Socks4代理下载器
-  Socks4代理检查器
-  Socks5代理下载器
-  Socks5代理检查器
-  随机Http发布数据
-  随机Http标头
-  随机Http Useragent
-  移除了混合代理洪水
-  添加了代理模式选择
-  仍在改进的项目

## 安装

    pip3 install requests pysocks
    git clone https://github.com/BlueSkyXN/CCATK.git
    cd CCATK

## 使用

    python3 atk.py


#CCATK-V2

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
