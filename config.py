import winreg


def read_config():
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\UKN\HotspotApp", 0, winreg.KEY_READ)
        ssid = winreg.QueryValueEx(key, "SSID")[0]
        pwd = winreg.QueryValueEx(key, "Password")[0]
        winreg.CloseKey(key)
        return ssid, pwd
    except FileNotFoundError:
        return "", ""


def save_config(ssid, pwd):
    key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\UKN\HotspotApp")
    winreg.SetValueEx(key, "SSID", 0, winreg.REG_SZ, ssid)
    winreg.SetValueEx(key, "Password", 0, winreg.REG_SZ, pwd)
    winreg.CloseKey(key)
