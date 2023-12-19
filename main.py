import csv
import tkinter
from tkinter import ttk
import math
import datetime
from tkinter import messagebox
import os
from log_file_manager import ConfigLog
import subprocess
import json



# ---------------------------- CONSTANTS ------------------------------- #
PINK = "#e2979c"
RED = "#e7305b"
RED2 = "#b7153b"
GREEN = "#9bdeac"
LIGHT_GREEN = "#b3e6be"
GREEN2 = "#39ac56"
YELLOW = "#f7f5dd"
YELLOW2 = "#a59b27"
GREEN_LETT = "#406020"
FONT_NAME = "Courier"


WORK_MIN = 25 #25
SHORT_BREAK_MIN = 5 #5
LONG_BREAK_MIN = 20 #20
reps = 0
timer = None

ATTRIBUTION1 = "Boton-detener iconos creados por xnimrodx - Flaticon"
ATTRIBUTION2 = "Botón de play iconos creados por xnimrodx - Flaticon"
ATTRIBUTION3 = "Negocios-y-finanzas iconos creados por xnimrodx - Flaticon"
ATTRIBUTION4 = "Función iconos creados por KP Arts - Flaticon"
ATTRIBUTION5 = 'Tomate iconos creados por Adorableninana - Flaticon'


# ---------------------------- TASK LOG ----------------------------------
def update_task_log(period, task=None):
    log_line = []
    today = datetime.datetime.now().strftime("%Y:%m:%d")
    now = datetime.datetime.now().strftime("%H:%M:%S")
    log_line.append(today)
    log_line.append(now)
    if task is None:
        log_line.append(task_var.get().strip())
    else:
        log_line.append(task)
    log_line.append(reps)
    log_line.append(period)
    print(log_line)

    with open("data/pomodoro_log.csv", 'a', newline='', encoding='utf-8') as log_file:
        wr = csv.writer(log_file)
        wr.writerow(log_line)

# ----------------------------- TASK LIST ---------------------------------------

def get_task_list():
    try:
        with open("data/tasks.csv", 'r', encoding='utf-8') as file:
            data = file.readlines()
            data = [x.strip() for x in data]
    except (FileNotFoundError, FileExistsError):
        data = []
    finally:
        return data


def reset_task_list(event):
    input_task.configure(values=get_task_list())


def update_task_list():
    current_task = task_var.get().strip()
    if current_task not in task_list:
        task_list.append(current_task)
    input_task.config(values=task_list)


def save_task_list(data: list):
    try:
        with open("data/tasks.csv", 'w', encoding='utf-8') as file:
            [file.write(f"{x}\n") for x in data]
    except Exception:
        messagebox.showwarning("Logger error", "Task could not be saved to file.")
    else:
        return True


# -------------------------------------------------- Credits and info
def show_credits():
    message = f"This python code is made by Gemma Riu, based on an exercise of '100 Days of Code' by Angela Yu.\n \n" \
              f"Dashboard and charts using bokeh library from bokeh.org" \
              f"\nIcons from https://www.flaticon.es :\n•{ATTRIBUTION5} \n•{ATTRIBUTION2}  \n•{ATTRIBUTION3}\n•{ATTRIBUTION4}\n•{ATTRIBUTION1}"
    messagebox.showinfo(title="Credits and about", message=message, icon="info")

def info():
    message = f"""Timer based on The Pomodoro Technique to manage time while working. 
                    \n1-Decide on the task to be done and select or type itin the bottom
                    \n2-Start the Pomodoro timer 
                    \n3-Work on the task for 25 minutes.
                    \n4-End work when the timer rings and pops and take a short break of 5 minutes. If you're planning to change task update new task at the bottom field.
                    \n5-New Pomodoro period start.
                    \n Repeat the process. After three pomodoros are done, take the fourth pomodoro and then take a long break of 20 minutes. Once the long break is finished, it starts again. You can stop the timer whenever you need. If you start again new block will begin.
                    \n\nThe logger saves all the data in a log file.
                    \nTo see a dashboard of your work click on the graph icon.
                    \nTo save current log file into selected folder go to config.
                    \nTo restart log file or task list go to config.
                    \nFor no more warnings again go to config."""
    messagebox.showinfo(title="The Pomodoro Technique", message=message, icon="info")


# ------------------------------------- LOGGER ------------------------------
def config():
   w = ConfigLog(window)
   w.grab_set()

def show_me_my_work():
    # graphs and statistics with work
    #os.system('dashboard.py')
    subprocess.call(["venv/Scripts/python.exe", "dashboard.py"])


# ------------------------------------ WARNING - SETTINGS -------------------------

def show_warning():
    try:
        with open("data/config.json", "r") as f:
            data = json.load(f)
            show_warnings = bool(data.get("show_warning"))
    except FileNotFoundError:
        show_warnings = True  # in case can't found the file show messages
    return show_warnings



# ---------------------------- TIMER RESET ------------------------------- # 
def reset_timer():
    update_task_log(period="STOP", task="stop")
    button_start.config(state="normal") #you can start again
    input_task.config(state="normal")  #you can select a task again
    window.after_cancel(timer)
    label_timer.config(text="Timer", foreground=GREEN2)
    canvas.itemconfig(timer_text, text=f"00:00")
    label_check.config(text="")
    global reps
    reps = 0


# ---------------------------- TIMER MECHANISM ------------------------------- # 
def start_timer():
    button_start.config(state="disabled") #no more starts
    button_reset.config(state="normal") #you can now stop
    # Check logger entry status
    if len(input_task.get()) < 1 and show_warning():
        response = messagebox.askokcancel("Task logger", "No task selected. The log will save 'Generic' for task period", icon="warning")
        if not response:
            button_start.config(state="normal")  # can start again
            button_reset.config(state="disabled")  # can not stop something not started
            return
    # Start timer
    global reps
    reps += 1
    work_sec = WORK_MIN * 60
    short_break_sec = SHORT_BREAK_MIN * 60
    long_break_sec = LONG_BREAK_MIN * 60
    window.attributes('-topmost', 1)
    window.attributes('-topmost', 0)
    window.bell()
    # Case long break after four short breaks :)!!!
    if reps % 8 == 0:
        label_timer.config(text="Break", foreground=RED2)
        input_task.config(state="normal")
        label_task.config(text="Next task: ")
        update_task_log(period="LONG_BREAK", task="break")
        count_down(long_break_sec)
    # Case short break :)
    elif reps % 2 == 0:
        label_timer.config(text="Break", foreground=PINK)
        input_task.config(state="normal")
        label_task.config(text="Next task: ")
        # Remind to change task
        global SHOW_ME_WARNING
        if show_warning() and SHOW_ME_WARNING == 1:
            answer = messagebox.askquestion("Logger alert", "If you're going to change task, during break time you should "
                                                            "update NEXT TASK.\n\nDou you want me to remind you of this next break?")
            if answer == "no":
                SHOW_ME_WARNING = 0
        # update data and start counter
        update_task_log(period="BREAK", task="break")
        count_down(short_break_sec)
    # Case working :(
    else:
        label_timer.config(text="Work", foreground=GREEN2)
        input_task.config(state="disabled")
        label_task.config(text="Current task: ")
        # When work start update task list
        update_task_list()
        save_task_list(task_list)
        # and update logg file
        update_task_log(period="WORK")
        # then start timer
        count_down(work_sec)


# ---------------------------- COUNTDOWN MECHANISM ------------------------------- # 
def count_down(count):
    global reps
    count_min = math.floor(count / 60)
    count_sec = count % 60
    if count_sec < 10:
        count_sec = f"0{count_sec}"

    canvas.itemconfig(timer_text, text=f"{count_min }:{count_sec}")
    if count > 0:
        global timer
        timer = window.after(1000, count_down, count-1)
    else:
        start_timer()
        mark = ""
        work_sessions = math.floor(reps/2)
        for _ in range(work_sessions):
            mark += "✓"
        label_check.config(text=mark)





# ---------------------------- UI SETUP ------------------------------- #

window = tkinter.Tk()
window.title("The Pomodoro Technique")
window.iconbitmap("images/tomato.ico")


# ------------------------------------ top frame

top_frame = tkinter.Frame(window, bg=YELLOW)
top_frame.pack(fill=tkinter.X)

button_help = tkinter.Button(top_frame, text="Help", font=(FONT_NAME,10, "bold"), foreground=GREEN_LETT, background=YELLOW, borderwidth=0, command=info)
button_help.grid(row=0, column=0, sticky="w", pady=10, padx=20)

button_credits = tkinter.Button(top_frame, text="Credits & About", font=(FONT_NAME,10, "bold"), foreground=GREEN_LETT, background=YELLOW, borderwidth=0, command=show_credits)
button_credits.grid(row=0, column=4, sticky="e", pady=10, padx=(240,20))

# ---------------------------- middle frame

upper_frame = tkinter.Frame(window, bg=YELLOW, padx=100, pady=25)
upper_frame.pack()

canvas = tkinter.Canvas(upper_frame, width=206, height=224, bg=YELLOW, highlightthickness=0)
tomato_img = tkinter.PhotoImage(file="images/tomato.png")
canvas.create_image(100, 112, image=tomato_img)
timer_text = canvas.create_text(100, 130, text="00:00", fill="white", font=(FONT_NAME, 25, "bold"))
canvas.grid(row=1, column=1)

label_timer = tkinter.Label(upper_frame, text="Timer", justify="center", foreground=GREEN2, background=YELLOW, font=(FONT_NAME, 35, "bold"))
label_timer.grid(row=0, column=1)

img_start = tkinter.PhotoImage(file="images/boton-de-play_32.png")
button_start = tkinter.Button(upper_frame, image=img_start, font=("Arial", 12, "bold"), borderwidth=0, command=start_timer)
button_start.grid(row=2, column=0)

img_stop = tkinter.PhotoImage(file="images/boton-detener_32.png")
button_reset = tkinter.Button(upper_frame, image=img_stop, font=("Arial", 12, "bold"), borderwidth=0, state="disabled", command=reset_timer)
button_reset.grid(row=2, column=2)

label_check = tkinter.Label(upper_frame, justify="center", foreground=GREEN, background=YELLOW, font=("Arial", 20, "bold"))
label_check.grid(row=3, column=1)


# ----------------------- bottom frame

bottom_frame = tkinter.Frame(window,  bg=LIGHT_GREEN)
bottom_frame.pack(fill=tkinter.X)

img_set = tkinter.PhotoImage(file="images/fabricacion.png")
button_set = tkinter.Button(bottom_frame, image=img_set, background=LIGHT_GREEN, borderwidth=0, command=config)
button_set.grid(row=0, column=0, padx=(20, 20), sticky='w')

label_task = tkinter.Label(bottom_frame, text="Next task: ", foreground=GREEN_LETT, background=LIGHT_GREEN, font=(FONT_NAME, 10, "bold"))
label_task.grid(row=0, column=1)

task_var = tkinter.StringVar()
task_list = get_task_list()
input_task = ttk.Combobox(bottom_frame, textvariable=task_var, values=task_list, width=25, foreground=GREEN_LETT,
                          background=LIGHT_GREEN, font=("Arial", 10, "normal"))
input_task.bind("<Button-1>", reset_task_list)
input_task.grid(row=0, column=2, pady=25)



img_graph = tkinter.PhotoImage(file="images/grafico-de-barras.png")
button_task = tkinter.Button(bottom_frame, image=img_graph, background=LIGHT_GREEN, borderwidth=0, command=show_me_my_work)
button_task.grid(row=0, column=3, padx=(35, 20), sticky='e')



window.mainloop()
update_task_log(period="FINISH", task="FINISH")
