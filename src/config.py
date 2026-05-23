import os
import sys
import winreg


def read_config():
    ssid = ""
    pwd = ""
    legacy_auto_start = False
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\UKN\HotspotApp", 0, winreg.KEY_READ)
    except FileNotFoundError:
        return ssid, pwd, False, False

    try:
        ssid = winreg.QueryValueEx(key, "SSID")[0]
    except FileNotFoundError:
        pass

    try:
        pwd = winreg.QueryValueEx(key, "Password")[0]
    except FileNotFoundError:
        pass

    try:
        legacy_auto_start = bool(winreg.QueryValueEx(key, "AutoStart")[0])
    except FileNotFoundError:
        pass

    try:
        launch_at_startup = bool(winreg.QueryValueEx(key, "LaunchAtStartup")[0])
    except FileNotFoundError:
        launch_at_startup = legacy_auto_start

    try:
        auto_enable_hotspot = bool(winreg.QueryValueEx(key, "AutoEnableHotspot")[0])
    except FileNotFoundError:
        auto_enable_hotspot = legacy_auto_start

    winreg.CloseKey(key)
    return ssid, pwd, launch_at_startup, auto_enable_hotspot


def save_config(ssid, pwd, launch_at_startup, auto_enable_hotspot, sync_autostart=False):
    key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\UKN\HotspotApp")
    winreg.SetValueEx(key, "SSID", 0, winreg.REG_SZ, ssid)
    winreg.SetValueEx(key, "Password", 0, winreg.REG_SZ, pwd)
    winreg.SetValueEx(key, "LaunchAtStartup", 0, winreg.REG_DWORD, int(launch_at_startup))
    winreg.SetValueEx(key, "AutoEnableHotspot", 0, winreg.REG_DWORD, int(auto_enable_hotspot))
    winreg.SetValueEx(key, "AutoStart", 0, winreg.REG_DWORD, int(launch_at_startup))
    winreg.CloseKey(key)

    if sync_autostart:
        set_autostart(bool(launch_at_startup))


def set_autostart(bl):
    exe_path = os.path.abspath(sys.argv[0])
    key = winreg.OpenKey(
        winreg.HKEY_CURRENT_USER,
        r"Software\Microsoft\Windows\CurrentVersion\Run",
        0,
        winreg.KEY_SET_VALUE
    )

    if bl:
        winreg.SetValueEx(key, "HotspotApp", 0, winreg.REG_SZ, exe_path)
    else:
        try:
            winreg.DeleteValue(key, "HotspotApp")
        except FileNotFoundError:
            pass
    winreg.CloseKey(key)
