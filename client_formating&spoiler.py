import base64
import io
import os
import re
import threading
import tkinter as tk
from socket import socket, AF_INET, SOCK_STREAM

from customtkinter import *
from tkinter import filedialog
from PIL import Image, ImageFilter


class MainWindow(CTk):
    def __init__(self):
        super().__init__()

        self.geometry('400x300')
        self.title("Chat Client")

        self.username = "new user"
        self.timer_seconds = 0

        self.label = None
        self.menu_frame = CTkFrame(self, width=30, height=300)
        self.menu_frame.pack_propagate(False)
        self.menu_frame.place(x=0, y=0)
        self.is_show_menu = False
        self.speed_animate_menu = -20
        self.btn = CTkButton(self, text='▶️', command=self.toggle_show_menu, width=30)
        self.btn.place(x=0, y=0)

        self.chat_field = CTkScrollableFrame(self)
        self.chat_field.place(x=0, y=0)

        self.message_entry = CTkEntry(self, placeholder_text='Введіть повідомлення:', height=40)
        self.message_entry.place(x=0, y=0)

        self.timer_button = CTkButton(self, text='⏱️ ∞', width=60, height=40, command=self.select_timer)
        self.timer_button.place(x=0, y=0)

        self.open_img_button = CTkButton(self, text='📂', width=50, height=40, command=self.select_image_type)
        self.open_img_button.place(x=0, y=0)

        self.send_button = CTkButton(self, text='>', width=50, height=40, command=self.send_message)
        self.send_button.place(x=0, y=0)

        self.message_entry.bind("<Button-3>", self.show_context_menu)

        self.adaptive_ui()

        try:
            self.sock = socket(AF_INET, SOCK_STREAM)
            self.sock.connect(('localhost', 8080))
            hello = f"TEXT@{self.username}@[SYSTEM] {self.username} приєднався(лась) до чату!@0\n"
            self.sock.send(hello.encode('utf-8'))
            threading.Thread(target=self.recv_message, daemon=True).start()
        except Exception as e:
            self.add_message(f"Не вдалося підключитися до сервера: {e}")

    def select_timer(self):
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="♾️ Без таймера", command=lambda: self.set_timer(0))
        menu.add_command(label="⏱️ 5 секунд", command=lambda: self.set_timer(5))
        menu.add_command(label="⏱️ 10 секунд", command=lambda: self.set_timer(10))
        menu.add_command(label="⏱️ 30 секунд", command=lambda: self.set_timer(30))
        menu.add_command(label="⏱️ 60 секунд", command=lambda: self.set_timer(60))
        menu.add_command(label="✏️ Задати свій час (1-60с)", command=self.custom_timer_dialog)

        x = self.timer_button.winfo_rootx()
        y = self.timer_button.winfo_rooty() - 140
        menu.tk_popup(x, y)

    def set_timer(self, seconds):
        if seconds > 60:
            seconds = 60
        elif seconds < 0:
            seconds = 0

        self.timer_seconds = seconds
        if seconds == 0:
            self.timer_button.configure(text="⏱️ ∞")
        else:
            self.timer_button.configure(text=f"⏱️ {seconds}s")

    def custom_timer_dialog(self):
        dialog = CTkInputDialog(text="Введіть час автовидалення (1-60 сек):", title="Таймер повідомлення")
        val = dialog.get_input()
        if val and val.isdigit():
            sec = int(val)
            self.set_timer(sec)

    def show_context_menu(self, event):
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="Жирний", command=lambda: self.apply_format("**"))
        menu.add_command(label="Курсив", command=lambda: self.apply_format("*"))
        menu.add_command(label="Закреслений", command=lambda: self.apply_format("~~"))
        menu.add_command(label="Код", command=lambda: self.apply_format("`"))
        menu.add_command(label="Спойлер", command=lambda: self.apply_format("||"))
        menu.tk_popup(event.x_root, event.y_root)

    def select_image_type(self):
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="📁 Ззвичайне зображення", command=lambda: self.open_image(is_spoiler=False))
        menu.add_command(label="🙈 Зображення-спойлер", command=lambda: self.open_image(is_spoiler=True))

        x = self.open_img_button.winfo_rootx()
        y = self.open_img_button.winfo_rooty() - 60
        menu.tk_popup(x, y)

    def apply_format(self, tag):
        try:
            first = self.message_entry.index("sel.first")
            last = self.message_entry.index("sel.last")
            text = self.message_entry.get()[first:last]
            self.message_entry.delete(first, last)
            self.message_entry.insert(first, f"{tag}{text}{tag}")
        except:
            pos = self.message_entry.index("insert")
            self.message_entry.insert(pos, f"{tag}{tag}")
            self.message_entry.icursor(pos + len(tag))

    def toggle_show_menu(self):
        if self.is_show_menu:
            self.is_show_menu = False
            self.speed_animate_menu *= -1
            self.btn.configure(text='▶️')
            self.show_menu()
        else:
            self.is_show_menu = True
            self.speed_animate_menu *= -1
            self.btn.configure(text='◀️')
            self.show_menu()
            self.label = CTkLabel(self.menu_frame, text='Імʼя')
            self.label.pack(pady=30)
            self.entry = CTkEntry(self.menu_frame, placeholder_text="Ваш нік...")
            self.entry.pack()
            self.save_button = CTkButton(self.menu_frame, text="Зберегти", command=self.save_name)
            self.save_button.pack()

    def show_menu(self):
        self.menu_frame.configure(width=self.menu_frame.winfo_width() + self.speed_animate_menu)
        if not self.menu_frame.winfo_width() >= 200 and self.is_show_menu:
            self.after(10, self.show_menu)
        elif self.menu_frame.winfo_width() >= 60 and not self.is_show_menu:
            self.after(10, self.show_menu)
            if self.label:
                self.label.destroy()
            if getattr(self, "entry", None):
                self.entry.destroy()
            if getattr(self, "save_button", None):
                self.save_button.destroy()

    def save_name(self):
        new_name = self.entry.get().strip()
        if new_name:
            self.username = new_name
            self.add_message(f"Ваш новий нік: {self.username}")

    def adaptive_ui(self):
        self.menu_frame.configure(height=self.winfo_height())
        self.chat_field.place(x=self.menu_frame.winfo_width())
        self.chat_field.configure(width=self.winfo_width() - self.menu_frame.winfo_width() - 20,
                                  height=self.winfo_height() - 40)

        self.send_button.place(x=self.winfo_width() - 50, y=self.winfo_height() - 40)
        self.open_img_button.place(x=self.winfo_width() - 105, y=self.winfo_height() - 40)
        self.timer_button.place(x=self.winfo_width() - 170, y=self.winfo_height() - 40)

        self.message_entry.place(x=self.menu_frame.winfo_width(), y=self.send_button.winfo_y())
        self.message_entry.configure(width=self.winfo_width() - self.menu_frame.winfo_width() - 175)

        self.after(50, self.adaptive_ui)

    def add_message(self, message, img=None, raw_pil_img=None, is_spoiler=False, timer_sec=0):
        message_frame = CTkFrame(self.chat_field, fg_color='grey')
        message_frame.pack(pady=3, anchor='w')
        wrapleng_size = self.winfo_width() - self.menu_frame.winfo_width() - 40

        if not img and not raw_pil_img:
            content_frame = CTkFrame(message_frame, fg_color='transparent')
            content_pady = (4, 0) if timer_sec > 0 else 4
            content_frame.pack(padx=6, pady=content_pady, anchor='w')

            parts = re.split(r'(\*\*.*?\*\*|\*.*?\*|~~.*?~~|`.*?`|\|\|.*?\|\|)', message)
            for part in parts:
                if not part:
                    continue
                if part.startswith("**") and part.endswith("**") and len(part) > 4:
                    CTkLabel(content_frame, text=part[2:-2], font=("Arial", 13, "bold"), text_color='white',
                             height=0).pack(side="left")
                elif part.startswith("*") and part.endswith("*") and len(part) > 2:
                    CTkLabel(content_frame, text=part[1:-1], font=("Arial", 13, "italic"), text_color='white',
                             height=0).pack(side="left")
                elif part.startswith("~~") and part.endswith("~~") and len(part) > 4:
                    CTkLabel(content_frame, text=part[2:-2], font=("Arial", 13, "overstrike"), text_color='white',
                             height=0).pack(side="left")
                elif part.startswith("`") and part.endswith("`") and len(part) > 2:
                    CTkLabel(content_frame, text=part[1:-1], font=("Consolas", 12), text_color='#00ff66',
                             fg_color='#2b2b2b', corner_radius=4, height=0).pack(side="left", padx=2)
                elif part.startswith("||") and part.endswith("||") and len(part) > 4:
                    sp_text = part[2:-2]
                    btn = CTkButton(content_frame, text="Спойлер", width=60, height=20, fg_color="#333333",
                                    text_color="white")
                    btn.configure(
                        command=lambda b=btn, t=sp_text: b.configure(text=t, fg_color="transparent", hover=False))
                    btn.pack(side="left", padx=2)
                else:
                    CTkLabel(content_frame, text=part, text_color='white', wraplength=wrapleng_size, justify='left',
                             height=0).pack(side="left")
        else:
            img_container = CTkFrame(message_frame, fg_color='transparent')
            img_container.pack(padx=5, pady=4, anchor='w')

            if message:
                CTkLabel(img_container, text=message, wraplength=wrapleng_size, text_color='white', justify='left',
                         height=0).pack(anchor='w', pady=(0, 3))

            if is_spoiler and raw_pil_img:
                safe_pil = raw_pil_img.convert("RGBA")
                blurred_pil = safe_pil.filter(ImageFilter.GaussianBlur(70))

                blurred_ctk = CTkImage(light_image=blurred_pil, dark_image=blurred_pil, size=(300, 300))
                normal_ctk = CTkImage(light_image=safe_pil, dark_image=safe_pil, size=(300, 300))

                spoiler_lbl = CTkLabel(
                    img_container,
                    text="🙈 Спойлер\n(Натисніть, щоб відкрити)",
                    image=blurred_ctk,
                    compound="center",
                    font=("Arial", 13, "bold"),
                    text_color="white",
                    cursor="hand2"
                )
                spoiler_lbl.pack()

                spoiler_lbl._normal_ctk = normal_ctk
                spoiler_lbl._blurred_ctk = blurred_ctk

                def reveal_image(event=None):
                    spoiler_lbl.configure(image=spoiler_lbl._normal_ctk, text="", cursor="arrow")
                    spoiler_lbl.unbind("<Button-1>")

                spoiler_lbl.bind("<Button-1>", reveal_image)
            else:
                img_label = CTkLabel(img_container, text="", image=img)
                img_label.image = img
                img_label.pack()

        if timer_sec > 0:
            timer_lbl = CTkLabel(message_frame, text=f"⏱️ {timer_sec}s", font=("Arial", 10, "bold"),
                                 text_color="#ff5555", height=0)
            timer_lbl.pack(anchor='e', padx=6, pady=(0, 3))

            def countdown(rem_sec):
                if not message_frame.winfo_exists():
                    return
                if rem_sec <= 0:
                    message_frame.destroy()
                else:
                    timer_lbl.configure(text=f"⏱️ {rem_sec}s")
                    self.after(1000, countdown, rem_sec - 1)

            self.after(1000, countdown, timer_sec - 1)

    def send_message(self):
        message = self.message_entry.get()
        if message:
            self.add_message(f"{self.username}: {message}", timer_sec=self.timer_seconds)
            data = f"TEXT@{self.username}@{message}@{self.timer_seconds}\n"
            try:
                self.sock.sendall(data.encode())
            except:
                pass
        self.message_entry.delete(0, END)

    def recv_message(self):
        buffer = ""
        while True:
            try:
                chunk = self.sock.recv(4096)
                if not chunk:
                    break
                buffer += chunk.decode('utf-8', errors='ignore')

                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    self.handle_line(line.strip())

            except:
                break
        self.sock.close()

    def handle_line(self, line):
        if not line:
            return
        parts = line.split("@")
        msg_type = parts[0]

        if msg_type == "TEXT":
            if len(parts) >= 3:
                author = parts[1]
                message = parts[2]
                timer_sec = int(parts[3]) if len(parts) >= 4 and parts[3].isdigit() else 0
                self.add_message(f"{author}: {message}", timer_sec=timer_sec)
        elif msg_type == "IMAGE":
            if len(parts) >= 4:
                author = parts[1]
                filename = parts[2]
                b64_img = parts[3]
                is_spoiler = (parts[4] == "1") if len(parts) >= 5 else False
                timer_sec = int(parts[5]) if len(parts) >= 6 and parts[5].isdigit() else 0
                try:
                    img_data = base64.b64decode(b64_img)
                    pil_img = Image.open(io.BytesIO(img_data)).convert("RGBA")
                    ctk_img = CTkImage(light_image=pil_img, dark_image=pil_img, size=(300, 300))
                    self.add_message(f"{author} надіслав(ла) зображення: {filename}", img=ctk_img, raw_pil_img=pil_img,
                                     is_spoiler=is_spoiler, timer_sec=timer_sec)
                except Exception as e:
                    self.add_message(f"Помилка відображення зображення: {e}")
        else:
            self.add_message(line)

    def open_image(self, is_spoiler=False):
        file_name = filedialog.askopenfilename()
        if not file_name:
            return
        try:
            with open(file_name, "rb") as f:
                raw = f.read()
            b64_data = base64.b64encode(raw).decode()
            short_name = os.path.basename(file_name)

            spoiler_flag = "1" if is_spoiler else "0"
            data = f"IMAGE@{self.username}@{short_name}@{b64_data}@{spoiler_flag}@{self.timer_seconds}\n"
            self.sock.sendall(data.encode())

            pil_img = Image.open(file_name).convert("RGBA")
            ctk_img = CTkImage(light_image=pil_img, dark_image=pil_img, size=(300, 300))
            self.add_message('', img=ctk_img, raw_pil_img=pil_img, is_spoiler=is_spoiler, timer_sec=self.timer_seconds)
        except Exception as e:
            self.add_message(f"Не вдалося надіслати зображення: {e}")


if __name__ == "__main__":
    win = MainWindow()
    win.mainloop()