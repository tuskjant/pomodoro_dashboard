from bokeh.palettes import d3, Light9
from bokeh.models import DatetimeTickFormatter, AnnularWedge, ColumnDataSource, Legend, LegendItem, Plot, Range1d, \
    Segment, TableColumn, DateFormatter, DataTable, HoverTool, Button, Div, WheelZoomTool, PanTool, SaveTool, ResetTool
from bokeh.plotting import figure
from bokeh.transform import cumsum
import datetime as dt
from math import pi



PALETTE1 = ["#A7D2CB", "#F2D388", "#C98474", "#874C62"]
PALETTE2 = ["#FF6D60", "#F7D060", "#F3E99F", "#98D8AA"]
PALETTE3 = ["#8BACAA", "#B04759", "#E76161", "#F99B7D"]
PALETTE4 = ["#e6d600", "#B6E2A1", "#FEBE8C", "#F7A4A4"]
PALETTE5 = ["#FFD966", "#F4B183", "#DFA67B"]
TITLE_COLOR = "#cc3300"
TITLE_FONT = "Arial"

# For very busy people
big_light_palette = Light9*4

# Bar plot showing Total dedicated time by task in minutes
def plot_time_by_task(grouptask_df):
    """
    Bar plot showing Total dedicated time by task in minutes
    :param grouptask_df: Group by task: count occurrences, count days, sum minutes - only work df
    :return:
    """
    # Palette colors
    grouptask_df["color"] = big_light_palette[:len(grouptask_df)]

    #Data and plot
    source = ColumnDataSource(grouptask_df)
    p = figure(x_range=grouptask_df.task,  height=450, title="Total dedicated time by task",
               toolbar_location="right", tools="wheel_zoom, save, reset, hover",
               tooltips=[("Task:", "@task"), ("Minutes:", "@sum_min{0}min")],
               y_axis_label="Time d H:M")
    p.title.text_color = TITLE_COLOR
    p.title.text_font = TITLE_FONT
    p.vbar(x="task", top="total_deltat", width=0.9, color="color", source=source)

    p.xgrid.grid_line_color = None
    p.y_range.start = 0
    p.yaxis[0].formatter = DatetimeTickFormatter(days="%d %H:%M", hours="%H:%M", hourmin="%H:%M", minutes="%H:%M")

    return p

# Line plot by day showing total times (work and breaks)
def line_working_time_by_day(groupdaytasks_df):
    """
    Line plot by day showing total times (work and breaks)
    :param groupdaytasks_df: Group by date, sum minutes, count different tasks, count  periods
    :return: 
    """

    source = ColumnDataSource(groupdaytasks_df)
    p = figure(title="Dedicated time by day",
               width=800, height=250,
               x_axis_type="datetime",
               sizing_mode="stretch_width",
               tools="wheel_zoom,reset,save"
               )
    p.title.text_color = TITLE_COLOR
    p.title.text_font = TITLE_FONT
    p.toolbar_location = "below"
    p.add_tools(HoverTool(
        tooltips=[
            ("Start time:", '@ini_time{%H:%M}'),
            ("End time:", '@end_time{%H:%M}'),
            ("Time:", "@total_deltat{%H:%M}"),
            ("Minutes:", "@total_min{0}min")
        ],
        formatters={
            '@ini_date': 'datetime',  # use 'datetime' formatter for 'date' field
            '@ini_time': 'datetime',
            '@end_time': 'datetime',
            '@total_deltat': 'datetime'
            # use default 'numeral' formatter for other fields
        },
        # display a tooltip whenever the cursor is vertically in line with a glyph
        mode='vline'
    ))

    p.line('ini_date', 'total_min', color='navy', line_width=2, source=source)
    p.circle('ini_date', 'total_min', color="navy", size=8, source=source)

    p.yaxis.axis_label = 'Minutes'
    p.y_range.start = 0
    p.xaxis[0].formatter = DatetimeTickFormatter(days="%Y-%m-%d")

    return p

# Line plot by day showing total times (work and breaks)
def line_num_tasks_by_day(groupdaywork):
    """
    Line plot by day showing total times (work and breaks)
    :param groupdaywork: Group by date, sum minutes, count different tasks, count working periods
    :return:
    """
    source = ColumnDataSource(groupdaywork)
    p = figure(title="Number of different tasks by day",
               width=800, height=250,
               x_axis_type="datetime",
               sizing_mode="stretch_width",
               tools="wheel_zoom,reset,save"
               )
    p.title.text_color = TITLE_COLOR
    p.title.text_font = TITLE_FONT
    p.toolbar_location = "below"
    p.add_tools(HoverTool(
        tooltips=[
            ("Start time:", '@ini_time{%H:%M}'),
            ("End time:", '@end_time{%H:%M}'),
            ("Num tasks:", "@num_tasks"),
            ("Majoritary task :", "@mode_task")
        ],
        formatters={
            '@ini_date': 'datetime',  # use 'datetime' formatter for 'date' field
            '@ini_time': 'datetime',
            '@end_time': 'datetime',
            #'@mode_task': 'printf'
            # use default 'numeral' formatter for other fields
        },
        # display a tooltip whenever the cursor is vertically in line with a glyph
        mode='vline'
    ))

    p.line('ini_date', 'num_tasks', color='brown', line_width=2, source=source)
    p.circle('ini_date', 'num_tasks', color="brown", size=8, source=source)

    p.yaxis.axis_label = 'Number of tasks'
    p.y_range.start = 0
    p.xaxis[0].formatter = DatetimeTickFormatter(days="%Y-%m-%d")

    return p


# Stacked bar plot : stacked time task by day
def stacked_tasks_by_day(tasks_df):
    """
    Stacked bar plot : stacked time task by day
    :param tasks_df: All tasks only filter tasks without stop and finish
    :return:
    """

    # Prepare data as dict
    df = tasks_df.copy()  # since we are modifying sampledata
    df = df[["ini_date", "task", "minutes"]]
    df["ini_date_str"] = df.ini_date.astype(str)
    df_group = df.groupby(["ini_date_str", "task"], as_index=False).agg(min_sum=('minutes', 'sum'))
    df_piv = df_group.pivot(index="task", columns="ini_date_str", values="min_sum").fillna(0).rename_axis(columns=None) #.reset_index()

    dates = df_piv.columns.values.tolist()
    tasks = df_piv.index.values.tolist()

    data = {}
    data["dates"] = dates
    data.update(df_piv.stack().groupby(level=0).apply(list).to_dict())

    # Create colors - categorical data by task
    palette = list(big_light_palette[:len(tasks)])

    # Create plot
    p = figure(x_range=dates, y_range=(0, df_piv.sum().max()+200), height=450, title="Minutes dedicated to tasks by day",
               tools="wheel_zoom, save, reset, hover", tooltips="$name @dates: @$name")
    p.title.text_color = TITLE_COLOR
    p.title.text_font = TITLE_FONT
    p.vbar_stack(tasks, x='dates', width=0.9, color=palette, source=data,
                 legend_label=tasks)



    p.y_range.start = 0
    p.x_range.range_padding = 0.1
    p.xgrid.grid_line_color = None
    p.axis.minor_tick_line_color = None
    p.outline_line_color = None
    p.legend.location = "top"
    p.legend.orientation = "horizontal"

    return p

# Time dedication - segment plot
def hz_segment_tasks_datetime(tasks_df_end):
    """
    Time dedication - segment plot
    :param tasks_df_end: All tasks only filter tasks without stop and finish
    :return:
    """
    # Prepare data
    n_tasks = tasks_df_end['task'].unique()
    n_class = tasks_df_end['class'].unique()
    num_days = tasks_df_end["ini_date"].nunique()
    palette = big_light_palette[:len(n_tasks)]
    for i, t in enumerate(n_tasks):
        tasks_df_end.loc[tasks_df_end["task"] == t, 'color'] = palette[i]

    # Plot
    source = ColumnDataSource(tasks_df_end)
    tools = "wheel_zoom,pan,reset,save"
    p = figure(tools=tools, x_range=(tasks_df_end['ini_date_time'].min(), tasks_df_end['end_date_time'].max()),
               y_range=n_class, width=1200, height=250, title="Time dedication - (wheel zoom to detail)")
    p.title.text_color = TITLE_COLOR
    p.title.text_font = TITLE_FONT

    glyph = Segment(x0='ini_date_time', y0="class", x1='end_date_time', y1="class", line_width=50, line_color="color")
    p.add_glyph(source, glyph)
    p.toolbar.active_scroll = p.select_one(WheelZoomTool)

    # Axes
    p.ygrid.grid_line_color = None
    p.yaxis.major_label_orientation = "vertical"
    p.xaxis[0].ticker.desired_num_ticks = num_days*4
    p.xaxis[0].formatter = DatetimeTickFormatter(days="\n%Y-%M-%d \n%H:%M", hours="%H:%M", minutes="%H:%M")


    # Tools
    p.add_tools(HoverTool(
        tooltips=[
            ("Task:", "@task"),
            ("Start time:", '@ini_date_time{%H:%M}'),
            ("End time:", '@end_date_time{%H:%M}'),
            ("Time :", "@deltat{%H:%M}")
        ],
        formatters={
            '@ini_date_time': 'datetime',
            '@end_date_time': 'datetime',
            '@deltat': 'datetime'
            # use default 'numeral' formatter for other fields
        },
        # display a tooltip whenever the cursor is vertically in line with a glyph
        mode='vline'
    ))

    # Legend
    for i, t in enumerate(n_tasks):
        p.line(0, 0, legend_label=t, color=palette[i], line_width=5)
    p.legend.location = "top_center"
    p.legend.orientation = "horizontal"


    return p

# Donut by task
def donut_task(grouptype_df):
    xdr = Range1d(start=-2, end=2)
    ydr = Range1d(start=-2, end=2)


    plot = Plot(x_range=xdr, y_range=ydr, height=550, height_policy='fit')
    plot.title.text = "Time dedicated by type"
    plot.toolbar_location = "right"
    plot.title.text_color = TITLE_COLOR
    plot.title.text_font = TITLE_FONT

    # Palette colors
    grouptype_df["color"] = PALETTE4[:len(grouptype_df)]

    colors = dict(zip(grouptype_df["type"], grouptype_df["color"]))


    angles = grouptype_df.sum_type_perc.map(lambda x: 2 * pi * (x / 100)).cumsum().tolist()

    tasks_source = ColumnDataSource(dict(
        start=[0] + angles[:-1],
        end=angles,
        colors=grouptype_df["color"].tolist(),
    ))

    glyph = AnnularWedge(x=0, y=0, inner_radius=0.6, outer_radius=1.3,
                         start_angle="start", end_angle="end",
                         line_color="white", line_width=3, fill_color="colors")
    r = plot.add_glyph(tasks_source, glyph)

    legend = Legend(location="center")
    for i, name in enumerate(colors):
        legend.items.append(LegendItem(label=name, renderers=[r], index=i))
    plot.add_layout(legend, "center")

    wzt = WheelZoomTool()
    p = PanTool()
    s = SaveTool()
    r = ResetTool()
    plot.add_tools(wzt, p, r, s)

    return plot


# Pie by task
def pie_task(grouptask_df):

    data = grouptask_df
    data['angle'] = data['sum_min_perc'] / data['sum_min_perc'].sum() * 2 * pi
    data['color'] = big_light_palette[:len(grouptask_df)]

    p = figure(height=250, title="Percentage of time dedicated to tasks", toolbar_location=None,
               tools="hover,wheel_zoom,pan,reset,save", tooltips="@task: @sum_min_perc %", x_range=(-0.5, 1.0))
    p.title.text_color = TITLE_COLOR
    p.title.text_font = TITLE_FONT
    p.toolbar_location = "right"

    p.wedge(x=0, y=1, radius=0.4,
            start_angle=cumsum('angle', include_zero=True), end_angle=cumsum('angle'),
            line_color="white", fill_color='color', legend_field='task', source=data)

    p.axis.axis_label = None
    p.axis.visible = False
    p.grid.grid_line_color = None

    return p

# DataTable
def data_table(grouped_tasks_by_task_df):

    # Prepare data
    cn = grouped_tasks_by_task_df.columns.tolist()
    g_task_dict = {}
    for c in cn:
        g_task_dict[c] = grouped_tasks_by_task_df[c].tolist()

    source = ColumnDataSource(g_task_dict)

    columns = [
        TableColumn(field="task", title="Task"),
        TableColumn(field="total_deltat", title="Time", formatter=DateFormatter(format="%H:%M")),
        TableColumn(field="sum_min", title="Minutes"),
        TableColumn(field="sum_min_perc", title="% Time"),
        TableColumn(field="days", title="# Days"),
        TableColumn(field="order_count", title="# Blocks"),
    ]
    data_table = DataTable(source=source, columns=columns, width=400, height=280)

    return data_table

# Button
def button_data(data, mode):
    button = Button(label=data, button_type=mode, disabled=False, height=50, width=150)
    return button

def kpi(kpi_text, kpi_value, color, img=None):
    if img is not None:
        div_square = Div(text=f"""<div style="
            display: inline-block; 
            padding: 20px 20px; 
            margin: 50px 10px; 
            background-color: {color};
            color: #FFFFFF; 
            font-family: Arial,sans-serif; 
            font-size: 20px; 
            font-weight: bold; 
            border-radius: 5px; 
            border: none; 
            justify-content: center; 
            text-align: center">
            <p ><img style="vertical-align:middle" src="images/{img}" alt="pomodoro" width="40" height="40"> {kpi_text}</p>
            <p style="font-weight: normal">{kpi_value}</p></div>""", width=300, height=200, sizing_mode="fixed")
    else:
        div_square = Div(text=f"""<div style="
            display: inline-block; 
            padding: 20px 5px; 
            margin: 25px 5px; 
            background-color: {color};
            color: #FFFFFF; 
            font-family: Arial,sans-serif; 
            font-size: 20px; 
            font-weight: bold; 
            border-radius: 5px; 
            border: none; 
            justify-content: center; 
            text-align: center">
            <p >{kpi_text}</p>
            <p style="font-weight: normal">{kpi_value}</p></div>""",
            width=200, height=60,  sizing_mode="fixed")
    return div_square


def kpi_3lines(kpi_text, kpi_value, color, img):
    div_square = Div(text=f"""<div>
        <div style="display: inline-block; padding: 0px 20px; margin: 25px 10px; background-color: {color[0]};
        color: #FFFFFF; font-family: Arial, sans-serif; font-size: 20px; font-weight: bold; border-radius: 5px; 
        border: none; justify-content: center; text-align: center">
        <p ><img style="vertical-align:middle" src="images/{img[0]}" 
        alt="pomodoro" width="40" height="40"> {kpi_text[0]}</p>
        <p style="text-align:center; font-weight: normal">{kpi_value[0]}</p>
        </div>
        <div style="display: inline-block; padding: 0px 20px; margin: 25px 10px; background-color: {color[1]};
        color: #FFFFFF; font-family: Arial, sans-serif; font-size: 20px; font-weight: bold; border-radius: 5px; 
        border: none; justify-content: center; text-align: center">
        <p ><img style="vertical-align:middle" src="images/{img[1]}" 
        alt="pomodoro" width="40" height="40"> {kpi_text[1]}</p>
        <p style="text-align:center; font-weight: normal">{kpi_value[1]}</p>
        </div>
        <div style="display: inline-block; padding: 0px 20px; margin: 25px 10px; background-color: {color[2]};
        color: #FFFFFF; font-family: Arial, sans-serif; font-size: 20px; font-weight: bold; border-radius: 5px; 
        border: none; justify-content: center; text-align: center">
         <p ><img style="vertical-align:middle" src="images/{img[2]}" 
        alt="pomodoro" width="40" height="40"> {kpi_text[2]}</p>
        <p style="text-align:center; font-weight: normal">{kpi_value[2]}</p>
        </div>
        </div>""", width=200, height=150, sizing_mode="stretch_width")

    return div_square


def thin_line(color):
    line = Div(text=f"""<div style="margin=5px">
    <hr size="5px" color={color} width=1200"/></div>""", width=1200)
    return line


def block_line(color):
    line = Div(text=f"""<div style="
    border-top: 10px solid {color}; ">
    </div>""",  width=1200)
    return line


def title_p():
    title = Div(text=f"""
        <div style="display: block;
        color: #cc3300;
        font-family: Arial, sans-serif;
        font-size: 40px;
        font-weight: bold;
        text-align: center">
        <img style="vertical-align:bottom"
        src="images/tomate_gafas.png" alt="pomodoro" width="64" height="64">
         <span> &ensp; Pomodoro log dashboard</span></div>
    """)
    return title


def dates_p(data_ini, data_end):
    dates_line = Div(text=f"""<div style="
    display: block; 
    color: #666666; 
    font-family: Arial, sans-serif; 
    font-size: 20px; 
    font-weight: bold; 
    margin=20px">
       Data from {data_ini} to {data_end}</div>""", width=500)
    return dates_line


def div_text(text, size, color):
    text_in_div = Div(text=f"""<div style="
    display: block; 
    color: {color}; 
    font-family: Arial, sans-serif; 
    font-size: {size}px; 
    font-weight: bold; 
    margin=20px">
      {text}</div>""", width=500)
    return text_in_div
