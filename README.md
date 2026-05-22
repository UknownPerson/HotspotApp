# HotspotApp

一个用于 Windows 的开源热点管理小工具，可以快速开启或关闭系统移动热点，并保存热点名称、密码和开机自启动设置。

<img width="322" height="132" alt="HotspotApp screenshot" src="https://github.com/user-attachments/assets/8b0034d0-f1ad-41d3-bc2c-2b2aee37b272" />

## 功能

- 一键开启或关闭 Windows 移动热点
- 保存热点名称和密码
- 支持开机自启动
- 启动后可按配置自动开启热点
- 轻量桌面窗口，无需复杂配置

## 运行环境

- Windows 10/11
- Python 3.12
- 系统需要支持 Windows 移动热点

## 本地运行

安装依赖：

```powershell
pip install -r requirements.txt
```

启动程序：

```powershell
.\.venv\Scripts\python.exe src\main.py
```

当前项目依赖 Windows Runtime 相关包，依赖列表见 [requirements.txt](requirements.txt)。

## 开源协议

本项目基于 Apache License 2.0 开源，详情见 [LICENSE](LICENSE)。
