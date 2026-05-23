import tkinter as tk

import customtkinter as ctk


class ToolTip:
    def __init__(self, widget, text, delay=400, wraplength=300):
        self.widget = widget
        self.text = text
        self.delay = delay
        self.wraplength = wraplength
        self.tipwindow = None
        self._after_id = None

        widget.bind("<Enter>", self._on_enter, add="+")
        widget.bind("<Leave>", self._on_leave, add="+")
        widget.bind("<Destroy>", lambda e: self._hide_tip(), add="+")

    def _on_enter(self, event=None):
        self._schedule()

    def _on_leave(self, event=None):
        self._unschedule()
        self._hide_tip()

    def _schedule(self):
        self._unschedule()
        self._after_id = self.widget.after(self.delay, self._show_tip)

    def _unschedule(self):
        if self._after_id:
            try:
                self.widget.after_cancel(self._after_id)
            except Exception:
                pass
            self._after_id = None

    def _show_tip(self):
        if self.tipwindow or not self.text:
            return
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5

        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.overrideredirect(True)
        tw.geometry(f"+{x}+{y}")
        tw.configure(bg="#ff00ff")
        tw.wm_attributes("-transparentcolor", "#ff00ff")
        tw.wm_attributes("-topmost", True)
        tw.wm_attributes("-alpha", 0.97)

        shadow = tk.Frame(tw, bg="#a8a8a8")
        shadow.place(x=3, y=3)

        frame = ctk.CTkFrame(
            tw,
            fg_color="#ffffff",
            border_color="#c8c8c8",
            border_width=1,
            corner_radius=6,
        )
        frame.pack()

        label = ctk.CTkLabel(
            frame,
            text=self.text,
            justify="left",
            fg_color="transparent",
            text_color="#1f1f1f",
            font=("Microsoft YaHei UI", 11),
            wraplength=self.wraplength,
        )
        label.pack(padx=10, pady=6)

        tw.update_idletasks()
        shadow.configure(width=frame.winfo_width(), height=frame.winfo_height())
        shadow.lower(frame)

    def _hide_tip(self):
        if self.tipwindow:
            try:
                self.tipwindow.destroy()
            except Exception:
                pass
            self.tipwindow = None
