import os
import sys
import threading
import webbrowser
import logging

import customtkinter as ctk
from ToolTip import ToolTip
from tkinter import messagebox
import tkinter as tk
from tkinter import ttk

from config import read_config, save_config
from hotspot import NetworkInformation, NetworkOperatorTetheringManager, TetheringOperationalState, disable, enable, getStates

import asyncio

logger = logging.getLogger("HotspotApp")


def run():
    loop = asyncio.new_event_loop()
    threading.Thread(target=loop.run_forever, daemon=True).start()

    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")

    window = ctk.CTk(fg_color="#f3f3f3")

    saved_ssid, saved_pwd, launch_at_startup, auto_enable_hotspot = read_config()

    window.ssid_var = tk.StringVar(value=saved_ssid)
    window.pwd_var = tk.StringVar(value=saved_pwd)
    window.launch_at_startup_var = tk.IntVar(value=int(launch_at_startup))
    window.auto_enable_hotspot_var = tk.IntVar(value=int(auto_enable_hotspot))
    window._save_config_after_id = None

    def save_current_config(sync_autostart=False):
        try:
            save_config(
                window.ssid_var.get(),
                window.pwd_var.get(),
                window.launch_at_startup_var.get(),
                window.auto_enable_hotspot_var.get(),
                sync_autostart=sync_autostart,
            )
        except Exception:
            logger.exception("Failed to save config")

    def flush_debounced_config():
        if window._save_config_after_id is not None:
            try:
                window.after_cancel(window._save_config_after_id)
            except Exception:
                pass
            window._save_config_after_id = None
        save_current_config()

    def schedule_config_save(*args):
        if window._save_config_after_id is not None:
            try:
                window.after_cancel(window._save_config_after_id)
            except Exception:
                pass
        window._save_config_after_id = window.after(350, flush_debounced_config)

    def on_launch_at_startup_change(*args):
        save_current_config(sync_autostart=True)

    def on_auto_enable_hotspot_change(*args):
        save_current_config()

    save_current_config(sync_autostart=True)

    window.ssid_var.trace_add("write", schedule_config_save)
    window.pwd_var.trace_add("write", schedule_config_save)
    window.launch_at_startup_var.trace_add("write", on_launch_at_startup_change)
    window.auto_enable_hotspot_var.trace_add("write", on_auto_enable_hotspot_change)

    window.title_ = '热点'
    window.suffix = ''
    window.hotspot_state = TetheringOperationalState.UNKNOWN

    window.title(f"{window.title_} {window.suffix}")

    if hasattr(sys, "_MEIPASS"):
        icon_path = os.path.join(sys._MEIPASS, "assets", "icon64.ico")
    else:
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        icon_path = os.path.join(project_root, "assets", "icon64.ico")

    window.iconbitmap(icon_path)

    window.geometry('340x100')
    window.resizable(False, False)

    def on_window_close():
        flush_debounced_config()
        window.destroy()

    window.protocol("WM_DELETE_WINDOW", on_window_close)

    style = ttk.Style(window)
    for theme_name in ("vista", "xpnative", "winnative"):
        if theme_name in style.theme_names():
            style.theme_use(theme_name)
            break

    label_font = ("Microsoft YaHei UI", 9)
    native_control_font = ("Microsoft YaHei UI", 9)
    input_font = ("Microsoft YaHei UI", 12)
    text_color = "#111111"
    control_border = "#d0d0d0"
    entry_border = control_border
    entry_focus_border = "#0078d4"

    style.configure("Hotspot.TLabel", font=label_font, background="#f3f3f3")
    style.configure("Hotspot.TButton", font=native_control_font, padding=(6, 3))
    style.layout(
        "Hotspot.TButton",
        [
            (
                "Button.button",
                {
                    "sticky": "nswe",
                    "children": [
                        (
                            "Button.padding",
                            {
                                "sticky": "nswe",
                                "children": [
                                    ("Button.label", {"sticky": "nswe"}),
                                ],
                            },
                        ),
                    ],
                },
            )
        ],
    )
    style.configure("Hotspot.TCheckbutton", font=native_control_font, background="#f3f3f3")
    style.layout(
        "Hotspot.TCheckbutton",
        [
            (
                "Checkbutton.padding",
                {
                    "sticky": "nswe",
                    "children": [
                        ("Checkbutton.indicator", {"side": "left", "sticky": ""}),
                        ("Checkbutton.label", {"side": "left", "sticky": "nswe"}),
                    ],
                },
            )
        ],
    )

    lab1 = ttk.Label(
        window,
        text="热点名称：",
        style="Hotspot.TLabel",
    )
    lab2 = ttk.Label(
        window,
        text="热点密码：",
        style="Hotspot.TLabel",
    )
    lab1.place(x=10, y=18)
    lab2.place(x=10, y=58)

    ent1 = ctk.CTkEntry(
        window,
        width=165,
        height=30,
        corner_radius=4,
        border_width=1,
        border_color=entry_border,
        fg_color="#ffffff",
        text_color=text_color,
        font=input_font,
        textvariable=window.ssid_var,
        insertwidth=1,
        insertontime=600,
        insertofftime=600,
    )
    ent1.place(x=76, y=14)

    ent2 = ctk.CTkEntry(
        window,
        width=165,
        height=30,
        corner_radius=4,
        border_width=1,
        border_color=entry_border,
        fg_color="#ffffff",
        text_color=text_color,
        font=input_font,
        textvariable=window.pwd_var,
        insertwidth=1,
        insertontime=600,
        insertofftime=600,
    )
    ent2.place(x=76, y=54)

    def parse_hex_color(color):
        color = color.lstrip("#")
        return tuple(int(color[index:index + 2], 16) for index in (0, 2, 4))

    def format_hex_color(rgb):
        return "#{:02x}{:02x}{:02x}".format(*rgb)

    def interpolate_color(start_color, end_color, progress):
        start = parse_hex_color(start_color)
        end = parse_hex_color(end_color)
        return format_hex_color(
            tuple(round(start[index] + (end[index] - start[index]) * progress) for index in range(3))
        )

    def animate_entry_border(entry, target_color, steps=8, delay=15):
        after_id = getattr(entry, "_border_animation_after", None)
        if after_id is not None:
            try:
                window.after_cancel(after_id)
            except Exception:
                pass

        start_color = getattr(entry, "_current_border_color", entry_border)

        def step(index):
            progress = index / steps
            color = interpolate_color(start_color, target_color, progress)
            entry.configure(border_color=color)
            entry._current_border_color = color

            if index < steps:
                entry._border_animation_after = window.after(delay, step, index + 1)
            else:
                entry._border_animation_after = None

        step(1)

    for entry in (ent1, ent2):
        entry._current_border_color = entry_border
        entry._border_animation_after = None
        entry.bind("<FocusIn>", lambda event, current=entry: animate_entry_border(current, entry_focus_border), add="+")
        entry.bind("<FocusOut>", lambda event, current=entry: animate_entry_border(current, entry_border), add="+")

    but1 = ttk.Button(
        window,
        text="开启热点",
        style="Hotspot.TButton",
        takefocus=False,
    )
    but1.place(x=255, y=13, width=72, height=32)
    but1.pointer_inside = False

    def is_pointer_inside_button():
        pointer_x = but1.winfo_pointerx()
        pointer_y = but1.winfo_pointery()
        left = but1.winfo_rootx()
        top = but1.winfo_rooty()
        right = left + but1.winfo_width()
        bottom = top + but1.winfo_height()
        return left <= pointer_x < right and top <= pointer_y < bottom

    def sync_button_hover_state():
        if not but1.instate(["disabled"]) and (but1.pointer_inside or is_pointer_inside_button()):
            but1.state(["active"])
        else:
            but1.state(["!active"])

    def set_button_disabled(disabled):
        if disabled:
            but1.state(["disabled", "!active"])
        else:
            but1.state(["!disabled"])
            window.after_idle(sync_button_hover_state)

    def on_button_enter(event=None):
        but1.pointer_inside = True
        sync_button_hover_state()

    def on_button_leave(event=None):
        but1.pointer_inside = False
        sync_button_hover_state()

    but1.bind("<Enter>", on_button_enter, add="+")
    but1.bind("<Leave>", on_button_leave, add="+")

    cbt1 = ttk.Checkbutton(
        window,
        text="",
        variable=window.launch_at_startup_var,
        style="Hotspot.TCheckbutton",
        takefocus=False,
    )
    cbt1.place(x=256, y=53, width=72, height=18)

    cbt1_text = ttk.Label(
        window,
        text="开机自启",
        style="Hotspot.TLabel",
    )
    cbt1_text.place(x=275, y=51)

    cbt2 = ttk.Checkbutton(
        window,
        text="",
        variable=window.auto_enable_hotspot_var,
        style="Hotspot.TCheckbutton",
        takefocus=False,
    )
    cbt2.place(x=256, y=71, width=72, height=18)

    cbt2_text = ttk.Label(
        window,
        text="启动即开",
        style="Hotspot.TLabel",
    )
    cbt2_text.place(x=275, y=69)

    ToolTip(cbt1, "勾选后程序会随系统开机自动启动，但不开启热点。")
    ToolTip(cbt2, "勾选后每次打开程序都会自动开启热点。")
    ToolTip(cbt1_text, "勾选后程序会随系统开机自动启动，但不开启热点。")
    ToolTip(cbt2_text, "勾选后每次打开程序都会自动开启热点。")

    def toggle_checkbutton(var):
        var.set(0 if var.get() else 1)

    cbt1_text.bind("<Button-1>", lambda event: toggle_checkbutton(window.launch_at_startup_var), add="+")
    cbt2_text.bind("<Button-1>", lambda event: toggle_checkbutton(window.auto_enable_hotspot_var), add="+")

    def open_link(url):
        webbrowser.open(url)

    def show_error(title, message):
        window.after(0, lambda: messagebox.showerror(title, message))

    def show_warning(title, message):
        window.after(0, lambda: messagebox.showwarning(title, message))

    def set_suffix(suffix):
        window.suffix = suffix
        if suffix:
            but1.configure(text=suffix)
        refresh_button(0)

    men1 = tk.Menu(window, tearoff=0)
    men1.add_command(label="作者：ukn",state="disabled")
    men1.add_command(label="开源免费工具，请勿倒卖",state="disabled")
    men1.add_command(label="打开 Github 项目地址", command=lambda: open_link("github.com/UknownPerson/HotspotApp/"))

    def show_menu(event):
        men1.post(event.x_root, event.y_root)

    def is_descendant(widget, parent):
        while widget is not None:
            if widget == parent:
                return True
            widget = getattr(widget, "master", None)
        return False

    def clear_entry_focus(event):
        widgets_to_keep_focus = (ent1, ent2, cbt1, cbt2, cbt1_text, cbt2_text)
        if any(is_descendant(event.widget, widget) for widget in widgets_to_keep_focus):
            return
        window.focus_set()

    window.bind("<Button-1>", clear_entry_focus, add="+")
    window.bind("<Button-3>", show_menu)

    def is_transition_state(state):
        return state == TetheringOperationalState.IN_TRANSITION

    def refresh_button(delay):
        window.after(0, lambda: window.title(f"{window.title_} {window.suffix}"))

        def update_button_state():
            should_disable = (
                window.suffix != ""
                or is_transition_state(window.hotspot_state)
                or window.hotspot_state == TetheringOperationalState.UNKNOWN
            )
            is_disabled = but1.instate(["disabled"])
            if should_disable != is_disabled:
                set_button_disabled(should_disable)

        window.after(0, update_button_state)

        future = asyncio.run_coroutine_threadsafe(getStates(), loop)

        def done(f):
            try:
                state = f.result()
                window.hotspot_state = state

                if window.suffix:
                    button_text = window.suffix
                    should_disable = True
                elif state == TetheringOperationalState.ON:
                    button_text = "关闭热点"
                    should_disable = window.suffix != ""
                elif state == TetheringOperationalState.OFF:
                    button_text = "开启热点"
                    should_disable = window.suffix != ""
                elif is_transition_state(state):
                    button_text = "处理中"
                    should_disable = True
                else:
                    button_text = "状态未知"
                    should_disable = True

                def apply_button_state():
                    if but1.cget("text") != button_text:
                        but1.configure(text=button_text)

                    is_disabled = but1.instate(["disabled"])
                    if should_disable != is_disabled:
                        set_button_disabled(should_disable)
                    elif not should_disable:
                        sync_button_hover_state()

                window.after(0, apply_button_state)
            except Exception:
                logger.exception("Failed to refresh hotspot state")

        future.add_done_callback(done)
        if delay > 0:
            window.after(delay, refresh_button, delay)

    def on_button_click():
        ssid = ent1.get()
        pwd = ent2.get()

        future = asyncio.run_coroutine_threadsafe(getStates(), loop)

        def done_turnoff(f):
            window.after(0, lambda: set_suffix(''))
            try:
                code = f.result().status
            except Exception:
                logger.exception("Failed to turn off hotspot")
                show_error("错误", "关闭失败，请查看日志。")
                return
            if code != 0:
                logger.error("Failed to turn off hotspot, status code: %s", code)
                show_error("错误", "关闭失败，错误码{}。".format(code))

        def done_turnon(f):
            window.after(0, lambda: set_suffix(''))
            try:
                code = f.result().status
            except Exception:
                logger.exception("Failed to turn on hotspot")
                show_error("错误", "开启失败，请查看日志。")
                return
            if code != 0:
                logger.error("Failed to turn on hotspot, status code: %s", code)
                show_error("错误", "开启失败，错误码{}。".format(code))

        def decide(f):
            try:
                state = f.result()
            except Exception:
                logger.exception("Failed to read hotspot state before toggling")
                show_error("错误", "读取热点状态失败，请查看日志。")
                return

            if is_transition_state(state):
                show_warning("提示", "热点状态正在切换，请稍后再试。")
                return
            if state == TetheringOperationalState.UNKNOWN:
                show_error("错误", "当前热点状态未知，请稍后再试。")
                return

            try:
                internet_connection_profile = NetworkInformation.get_internet_connection_profile()
                if internet_connection_profile is None:
                    show_error("错误", "当前无网络连接，无法开启。")
                    return
                tethering_manager = NetworkOperatorTetheringManager.create_from_connection_profile(
                    internet_connection_profile)
            except Exception:
                logger.exception("Failed to create tethering manager")
                show_error("错误", "获取热点管理器失败，请查看日志。")
                return

            if state == TetheringOperationalState.ON:
                window.after(0, lambda: set_suffix('关闭中...'))
                code_turnoff = asyncio.run_coroutine_threadsafe(disable(tethering_manager), loop)
                code_turnoff.add_done_callback(done_turnoff)
            elif state == TetheringOperationalState.OFF:
                if not ssid:
                    show_warning("提示", "热点名称不能为空。")
                    return
                if len(pwd) < 8:
                    show_warning("提示", "热点密码至少八个字符。")
                    return

                window.after(0, lambda: set_suffix('开启中...'))
                code_turnon = asyncio.run_coroutine_threadsafe(enable(tethering_manager, ssid, pwd), loop)
                code_turnon.add_done_callback(done_turnon)

        future.add_done_callback(decide)

    but1.configure(command=on_button_click)
    window.after(0, refresh_button, 1000)

    try:
        should_auto_enable = (
            window.auto_enable_hotspot_var.get() == 1
            and asyncio.run_coroutine_threadsafe(getStates(), loop).result() == TetheringOperationalState.OFF
        )
    except Exception:
        logger.exception("Failed to run startup auto-enable check")
        should_auto_enable = False

    if should_auto_enable:
        but1.invoke()

    window.mainloop()
