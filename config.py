import os
import sys
import winreg


def read_config():
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\UKN\HotspotApp", 0, winreg.KEY_READ)
        ssid = winreg.QueryValueEx(key, "SSID")[0]
        pwd = winreg.QueryValueEx(key, "Password")[0]
        auto_start = winreg.QueryValueEx(key, "AutoStart")[0]
        winreg.CloseKey(key)
        return ssid, pwd, bool(auto_start)
    except FileNotFoundError:
        return "", "", False


def save_config(ssid, pwd, auto_start):
    key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\UKN\HotspotApp")
    winreg.SetValueEx(key, "SSID", 0, winreg.REG_SZ, ssid)
    winreg.SetValueEx(key, "Password", 0, winreg.REG_SZ, pwd)
    winreg.SetValueEx(key, "AutoStart", 0, winreg.REG_DWORD, int(auto_start))
    set_autostart(bool(auto_start))
    winreg.CloseKey(key)


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
