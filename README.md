# HotspotApp

一个用于 Windows 的开源热点管理小工具，可以快速开启或关闭系统移动热点，并保存热点名称、密码和开机自启动设置。

<img width="342" height="132" alt="aa3744b8-2278-4ed9-b0b9-3af735e09348" src="https://github.com/user-attachments/assets/f7281df9-5827-4734-83f3-b011e4535184" />


## 功能

- 一键开启或关闭 Windows 移动热点
- 保存热点名称和密码
- 支持开机自启动
- 启动后可按配置自动开启热点
- 记录运行日志，方便排查启动失败或热点切换异常
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

## 日志

程序会将运行日志写入：

```text
%LOCALAPPDATA%\HotspotApp\logs\HotspotApp.log
```

如果程序无法启动、窗口闪退，或热点开启/关闭失败，可以查看该日志获取错误信息。

## 开源协议

本项目基于 Apache License 2.0 开源，详情见 [LICENSE](LICENSE)。
