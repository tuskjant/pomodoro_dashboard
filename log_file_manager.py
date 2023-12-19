import tkinter as tk
from tkinter import ttk, Label, LEFT
from tkinter.filedialog import asksaveasfile, asksaveasfilename
from tkinter import messagebox
import json

YELLOW = "#f7f5dd"
SUPER_LIGHT_GREEN = "#d9f2de"
RED = "#cc3300"

class ConfigLog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)

        self.geometry('500x400')
        self.title('Pomodoro settings')
        self.iconbitmap("images/tomato.ico")
        self.config(bg=YELLOW)
        self.config(padx=40, pady=50)
        self.show_warning = tk.BooleanVar()
        self.get_settings()

        tom_bask = tk.PhotoImage(file="images/tomate_cesta64.png")
        bt1 = tk.Button(self, text='Save log file', image=tom_bask, compound=LEFT, bg=SUPER_LIGHT_GREEN, fg=RED, width=150, height=80, command=self.download)
        bt1.image = tom_bask # needs to keep a reference to the image or it would not show up
        bt1.grid(column=0, row=0, padx=20, pady=20)

        tom_pa = tk.PhotoImage(file="images/tomate_paint64.png")
        bt2 = tk.Button(self, text='Reset log file', image=tom_pa, compound=LEFT, bg=SUPER_LIGHT_GREEN, fg=RED,  width=150, height=80,  command=self.delete)
        bt2.image = tom_pa
        bt2.grid(column=0, row=1, padx=20, pady=20)

        tom_no = tk.PhotoImage(file="images/tomate_normal64.png")
        bt3 = tk.Button(self, text='Reset task list', image=tom_no, compound=LEFT, bg=SUPER_LIGHT_GREEN, fg=RED, width=150,
                        height=80, command=self.empty_task_list)
        bt3.image = tom_no
        bt3.grid(column=1, row=0, padx=20, pady=20)

        frame_check = tk.Frame(self, background=YELLOW, width=150, height=80)
        frame_check.grid(column=1, row=1, padx=20, pady=20)

        img_um = tk.PhotoImage(file="images/tomate_paraguas.png", width=32, height=32)
        paraguas = Label(frame_check, image=img_um, background=YELLOW)
        paraguas.image = img_um  # needs to keep a reference to the image or it would not show up
        paraguas.pack()

        print(f"before rendering check button show warning is {self.show_warning.get()}")
        want_warnings = tk.Checkbutton(frame_check, text="Show warnings.",
                                       variable=self.show_warning, onvalue=True, offvalue=False, height=2, width=25, font=("Arial bold", 11), background=YELLOW, fg=RED)

        print(f"after rendering check button show warning is {self.show_warning.get()} and type {type(self.show_warning.get())}")



        want_warnings.bind("<Button-1>", self.update_settings)
        want_warnings.pack()



    def delete(self):
        with open("data/pomodoro_log.csv", "w") as file:
            file.write("")
        messagebox.showinfo("Pomodoro log", "Pomodoro log has been reset.")

    def download(self):
        try:
            with open("data/pomodoro_log.csv", "r") as log_f:
                content = log_f.read()
        except:
            pass
        else:
            files = [("Csv file", "*.csv")]
            file_name = asksaveasfile(confirmoverwrite=True, filetypes=files)
            if file_name:
                file_name.write(content)

    def empty_task_list(self):
        file = open("data/tasks.csv", 'w', encoding='utf-8')
        file.close()

    def update_settings(self, event):
        # Receiving before changing variable --> set opposite value to value_selected
        value_selected = not self.show_warning.get()
        if value_selected:
            conf_warning = {"show_warning": True}
        else:
            conf_warning = {"show_warning": False}
        with open("data/config.json", "w") as f:
            json.dump(conf_warning, f, indent=4)

    def get_settings(self):
        try:
            with open("data/config.json", "r") as f:
                data = json.load(f)
                self.show_warning.set(bool(data.get("show_warning")))
        except Exception:
            self.show_warning.set(True)  # if not found or error show messages ...
            self.update_settings(None)  # ... and write data to new file

