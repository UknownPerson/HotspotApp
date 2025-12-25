import webbrowser
from ToolTip import ToolTip
from tkinter import *
from tkinter import messagebox

from main import *
from config import *

import asyncio
import threading


def run():
    loop = asyncio.new_event_loop()
    threading.Thread(target=loop.run_forever, daemon=True).start()

    window = Tk()
    window.withdraw()

    saved_ssid, saved_pwd, auto_start = read_config()

    window.ssid_var = StringVar(value=saved_ssid)
    window.pwd_var = StringVar(value=saved_pwd)
    window.autosave_var = IntVar(value=int(auto_start))

    def on_change(*args):
        save_config(window.ssid_var.get(), window.pwd_var.get(), window.autosave_var.get())

    on_change()

    window.ssid_var.trace_add("write", on_change)
    window.pwd_var.trace_add("write", on_change)
    window.autosave_var.trace_add("write", on_change)

    window.title_ = '热点'
    window.suffix = ''

    window.title(f"{window.title_} {window.suffix}")

    if hasattr(sys, "_MEIPASS"):
        icon_path = os.path.join(sys._MEIPASS, "icon64.ico")
    else:
        icon_path = os.path.join(os.path.dirname(__file__), "icon64.ico")

    window.iconbitmap(icon_path)

    window.geometry('340x100')
    window.resizable(False, False)

    lab1 = Label(window, text="热点名称：")
    lab2 = Label(window, text="热点密码：")
    #lab3 = Label(window, text="作者：ukn")
    lab1.place(x=10, y=20)
    lab2.place(x=10, y=60)
    #lab3.place(x=240, y=60)

    frame1_1 = Frame(window, bg="gray", padx=1, pady=1)
    frame1_1.place(x=76, y=16)
    frame1_2 = Frame(frame1_1, bg="white", padx=8, pady=4)
    frame1_2.pack()
    ent1 = Entry(frame1_2, width=20, bd=0, insertwidth=1, insertontime=600, insertofftime=600,
                 textvariable=window.ssid_var)
    ent1.pack()

    frame2_1 = Frame(window, bg="gray", padx=1, pady=1)
    frame2_1.place(x=76, y=56)
    frame2_2 = Frame(frame2_1, bg="white", padx=8, pady=4)
    frame2_2.pack()
    ent2 = Entry(frame2_2, width=20, bd=0, insertwidth=1, insertontime=600, insertofftime=600,
                 textvariable=window.pwd_var)
    ent2.pack()

    but1 = Button(window, text="开启热点", bd=3)
    but1.place(x=260, y=14)

    cbt1 = Checkbutton(window, text="开机自启动\n并打开热点", bd=1, variable=window.autosave_var)
    cbt1.place(x=246, y=50)

    tooltip_text = "勾选后程序会随系统开机自动启动，并且在每次程序打开时自动开启热点。"
    ToolTip(cbt1, tooltip_text)

    def open_link(url):
        webbrowser.open(url)

    men1 = Menu(window, tearoff=0)
    men1.add_command(label="作者：ukn",state="disabled")
    men1.add_command(label="开源免费工具，请勿倒卖",state="disabled")
    men1.add_command(label="打开 Github 项目地址", command=lambda: open_link("github.com/UknownPerson/HotspotApp/"))

    def show_menu(event):
        men1.post(event.x_root, event.y_root)

    window.bind("<Button-3>", show_menu)

    window.deiconify()

    def refresh_button(delay):
        window.after(0, lambda: window.title(f"{window.title_} {window.suffix}"))

        def update_button_state():
            if window.suffix != "":
                but1.config(state="disabled")
            else:
                but1.config(state="normal")

        window.after(0, update_button_state)

        future = asyncio.run_coroutine_threadsafe(getStates(), loop)

        def done(f):
            try:
                state = f.result()
                but1.config(text="关闭热点" if state else "开启热点")
            except Exception as e:
                print(e)

        future.add_done_callback(done)
        if delay > 0:
            window.after(delay, refresh_button, delay)

    def on_button_click():

        future = asyncio.run_coroutine_threadsafe(getStates(), loop)

        def done_turnoff(f):
            window.suffix = ''
            code = f.result().status
            if code != 0:
                messagebox.showerror("错误", "关闭失败，错误码{}。".format(code))

        def done_turnon(f):
            window.suffix = ''
            code = f.result().status
            if code != 0:
                messagebox.showerror("错误", "开启失败，错误码{}。".format(code))

        def decide(f):
            internet_connection_profile = NetworkInformation.get_internet_connection_profile()
            if internet_connection_profile is None:
                messagebox.showerror("错误", "当前无网络连接，无法开启。")
                return
            tethering_manager = NetworkOperatorTetheringManager.create_from_connection_profile(
                internet_connection_profile)

            state = f.result()
            if state:
                window.suffix = '关闭中...'
                refresh_button(0)
                code_turnoff = asyncio.run_coroutine_threadsafe(disable(tethering_manager), loop)
                code_turnoff.add_done_callback(done_turnoff)
            else:
                ssid = ent1.get()
                pwd = ent2.get()
                if not ssid:
                    messagebox.showwarning("提示", "热点名称不能为空。")
                    return
                if len(pwd) < 8:
                    messagebox.showwarning("提示", "热点密码至少八个字符。")
                    return

                window.suffix = '开启中...'
                refresh_button(0)
                code_turnon = asyncio.run_coroutine_threadsafe(enable(tethering_manager, ssid, pwd), loop)
                code_turnon.add_done_callback(done_turnon)

        future.add_done_callback(decide)

    but1.config(command=on_button_click)
    window.after(0, refresh_button, 1000)

    if window.autosave_var.get() == 1 and not asyncio.run_coroutine_threadsafe(getStates(), loop).result():
        but1.invoke()

    window.mainloop()
