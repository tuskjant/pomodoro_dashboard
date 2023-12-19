from log_data import LogPomodoro
import log_plots
from bokeh.layouts import gridplot, layout, column, row
from bokeh.plotting import show
from tkinter import messagebox


PALETTE4 = ["#FFFBC1", "#B6E2A1", "#FEBE8C", "#F7A4A4"]


pomodoro_data = LogPomodoro()

if pomodoro_data.data_in_log:

    # Total dedicated time by task
    p1 = log_plots.plot_time_by_task(pomodoro_data.get_grouped_tasks_by_task("work"))

    # Dedicated time by day
    p2 = log_plots.line_working_time_by_day(pomodoro_data.get_grouped_tasks_by_day("all"))

    # Number of different tasks by day
    p3 = log_plots.line_num_tasks_by_day(pomodoro_data.get_grouped_tasks_by_day("work"))

    # Minutes dedicated to tasks by day
    p4 = log_plots.stacked_tasks_by_day(pomodoro_data.wdf)

    # Time dedication
    p5 = log_plots.hz_segment_tasks_datetime(pomodoro_data.df)

    # Time dedicated by type
    p6 = log_plots.donut_task(pomodoro_data.get_grouped_tasks_by_type("all"))

    # Percentage of time dedicated to tasks
    p7 = log_plots.pie_task(pomodoro_data.get_grouped_tasks_by_task("work"))

    # Table
    t_title = log_plots.div_text("Task statistics", 20, "#cc3300")
    p8 = log_plots.data_table(pomodoro_data.get_grouped_tasks_by_task("work"))

    # Bottom line
    t_bottom = log_plots.div_text("All charts from ", 20, "#cc3300")


    #  Heading
    title = log_plots.title_p()
    line = log_plots.thin_line("#B04759")
    dates_line = log_plots.dates_p(pomodoro_data.ini_log_time.strftime("%Y-%m-%d %H:%M"),
                                   pomodoro_data.end_log_time.strftime("%Y-%m-%d %H:%M"))

    # KPI's
    kpi_wdays = log_plots.kpi("Worked days", pomodoro_data.num_working_days, "#FEBE8C", "tomate_normal64.png")
    kpi_diftask = log_plots.kpi("Num. tasks", pomodoro_data.num_tasks, "#FEBE8C", "tomate_compra64.png")
    kpi_wtime = log_plots.kpi("Worked time", pomodoro_data.total_working_deltat, "#FEBE8C", "tomate_pesas64.png")
    kpi_break_min = log_plots.kpi("Break time", pomodoro_data.total_break_deltat, "#B6E2A1", "tomate_gafasSol64.png")


    # First dashboard row
    pom_text = log_plots.div_text("Pomodoro technique times", 20, "#cc3300")
    pom_col = log_plots.kpi_3lines(["Work", "Break", "Long Break"], ["25 min", "5 min", "20 min"], ["#FEBE8C", "#B6E2A1", "#e6d600"], ["tomate_book64.png","tomate_coffee64.png","tomate_sofa64.png"])
    first_col = column(children=[pom_text, pom_col, p6],  width=500, height=700, margin=20, sizing_mode="scale_both")
    second_col = column(children=[p1, p4],  width=500,  sizing_mode="scale_both")

    # Second row
    kpi_row = row(children=[kpi_wdays,  kpi_diftask, kpi_wtime,  kpi_break_min], height=350, sizing_mode="scale_width")

    # Table column
    table_col = column(children=[t_title, p8], height=500, sizing_mode="scale_width", margin=40)

    # Break line
    break_line = log_plots.div_text("\n", 20, "#000000")
    layout = layout(children=[
                        [title],
                        [line],
                        [dates_line],
                        [first_col, second_col],
                        [kpi_row],
                        [p2],
                        [break_line],
                        [p3],
                        [break_line],
                        [p5],
                        [break_line],
                        [p7, table_col]
                    ],
                    sizing_mode="scale_width")
    show(layout)
else:
    messagebox.showwarning("Pomodoro log", "No to enough data in log file.")




