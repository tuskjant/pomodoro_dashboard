import pandas as pd

LOG_FILE = "data/pomodoro_log.csv"


class LogPomodoro:

    def __init__(self):
        self.df = self.log_to_df()
        if len(self.df) > 10 and len(self.df.loc[self.df["type"] == "WORK"]) > 5:
            self.data_in_log = True
            self.wdf = self.get_only_work_df()
            # Task with minimum time
            self.min_time_task = self.df[self.df["minutes"] == self.df["minutes"].min()]
            self.min_time_wtask = self.wdf[self.wdf["minutes"] == self.wdf["minutes"].min()]
            # Totals
            self.total_working_minutes = self.wdf["minutes"].sum()
            self.total_working_deltat = self.wdf["deltat"].sum()
            self.total_break_deltat = self.get_only_break_df()["deltat"].sum()
            self.num_working_periods = self.wdf["task"].count()
            self.num_working_days = self.wdf["ini_date"].nunique()
            self.num_tasks = self.wdf["task"].nunique()
            self.total_break_minutes = self.df.loc[self.df["task"] == "break"]["minutes"].sum()
            self.num_break_periods = self.df.loc[self.df["task"] == "break"]["task"].count()
            self.ini_log_time = self.df["ini_date_time"].min()
            self.end_log_time = self.df["ini_date_time"].max()
        else:
            self.data_in_log = False

    # Load data from csv file to dataframe
    def log_to_df(self):
        """
        DATAFRAME: df
        Dataframe from csv file excluding FINISH and STOP lines

         #   Column         Non-Null Count  Dtype
        ---  ------         --------------  -----
         0   ini_date_time  83 non-null     datetime64[ns]
         1   task           83 non-null     object
         2   order          83 non-null     int64
         3   type           83 non-null     object
         4   ini_date       83 non-null     object
         5   deltat         82 non-null     timedelta64[ns]
         6   minutes        82 non-null     float64
         7   end_date_time  82 non-null     datetime64[ns]
         8   class          83 non-null     object

                 ini_date_time    task  order   type    ini_date          deltat  minutes       end_date_time  class
        0 2023-06-06 08:15:00  python      1   WORK  2023-06-06 0 days 00:25:00     25.0 2023-06-06 08:40:00  Tasks
        1 2023-06-06 08:40:00   break      2  BREAK  2023-06-06 0 days 00:05:00      5.0 2023-06-06 08:45:00  Tasks
        2 2023-06-06 08:45:00     C++      3   WORK  2023-06-06 0 days 00:25:00     25.0 2023-06-06 09:10:00  Tasks
        """

        headers = ["date", "time", "task", "order", "type"]
        with open(LOG_FILE, 'r') as file:
            df = pd.read_csv(file, header=None,
                                names=headers,
                                parse_dates={'ini_date_time': ['date', 'time']},
                                date_parser=lambda x: pd.to_datetime(x, format='%Y:%m:%d %H:%M:%S'))

        df["ini_date"] = df["ini_date_time"].dt.date
        df["deltat"] = df["ini_date_time"].shift(-1) - df["ini_date_time"]
        df["minutes"] = df["deltat"].dt.total_seconds().div(60)
        df['end_date_time'] = df['ini_date_time'] + df['deltat']
        df["class"] = "Tasks"
        df["task"].fillna("Generic", inplace=True)

        # Filter tasks without stop and finish
        tasks_df = df[df["type"].isin(["WORK", "BREAK", "LONG_BREAK"])]

        return tasks_df

    # Filter data to get only work registers
    def get_only_work_df(self):
        tasks_df = self.df

        # Filter taks only work lines
        work_df = tasks_df.loc[tasks_df["type"] == "WORK"]

        return work_df

    # Filter data to get only break registers
    def get_only_break_df(self):
        break_df = self.df

        # Filter taks only work lines
        break_df = break_df.loc[break_df["task"] == "break"]

        return break_df

    # Group data
    def get_grouped_tasks_by_type(self, which_df: str):
        """
        Group by type: count occurrences, count days, sum minutes, task mode
        :param which_df: [all, work]
        :return: grouptype_df
                         type  order_count  days  sum_min    total_deltat task_mode
            0       BREAK           27     4    135.0 0 days 02:15:00     break
            1  LONG_BREAK            7     4    140.0 0 days 02:20:00     break
            2        WORK           39     4    927.0 0 days 15:27:00      ruby
        """
        if which_df not in["all", "work"]:
            return 0
        elif which_df == "all":
            tasks_df = self.df
        elif which_df == "work":
            tasks_df = self.wdf

        grouptype_df = tasks_df.groupby('type', as_index=False).agg(order_count=('order', 'count'),
                                                    days=('ini_date', 'nunique'),
                                                    sum_min=('minutes', 'sum'),
                                                    total_deltat=('deltat', 'sum'),
                                                    task_mode=('task', pd.Series.mode))
        grouptype_df["sum_type_perc"] = round((grouptype_df["sum_min"]/sum(grouptype_df["sum_min"]))*100,2)
        return grouptype_df

    def get_grouped_tasks_by_date_task(self, which_df: str):
        """
        Group by date and task count occurrences and sum minutes
        :param which_df: [all, work]
        :return: groupdaytask_df
                    ini_date    task  order_count  sum_min    total_deltat
            0   2023-06-06     C++            1     25.0 0 days 00:25:00
            1   2023-06-06   break            8     70.0 0 days 01:10:00
            2   2023-06-06    java            2     50.0 0 days 00:50:00
            3   2023-06-06  python            1     25.0 0 days 00:25:00
            4   2023-06-06    ruby            5    125.0 0 days 02:05:00
            5   2023-06-07     C++            2     50.0 0 days 00:50:00
            6   2023-06-07   break            9     75.0 0 days 01:15:00
            7   2023-06-07    java            2     50.0 0 days 00:50:00
            8   2023-06-07  python            1     25.0 0 days 00:25:00
            9   2023-06-07    ruby            5    108.0 0 days 01:48:00
        """
        if which_df not in["all", "work"]:
            return 0
        elif which_df == "all":
            tasks_df = self.df
        elif which_df == "work":
            tasks_df = self.wdf
        groupdaytask_df = tasks_df.groupby(['ini_date', 'task'], as_index=False).agg(order_count=('order', 'count'),
                                                                                    sum_min=('minutes', 'sum'),
                                                                                    total_deltat=('deltat', 'sum'))
        return groupdaytask_df

    def get_grouped_tasks_by_day(self, which_df: str):
        """
        Group by date, sum minutes, count different tasks, count periods
        :param which_df: [all, work]
        :return: groupday_df
                  ini_date  total_min    total_deltat  num_tasks mode_task  num_work_per            ini_time            end_time mode_task_str
            0  2023-06-06      295.0 0 days 04:55:00          5     break            17 2023-06-06 08:15:00 2023-06-06 13:10:00         break
            1  2023-06-07      308.0 0 days 05:08:00          5     break            19 2023-06-07 09:05:00 2023-06-07 14:13:00         break
            2  2023-06-08      321.0 0 days 05:21:00          5     break            20 2023-06-08 11:08:00 2023-06-08 18:43:00         break
            3  2023-06-09      278.0 0 days 04:38:00          4     break            17 2023-06-09 10:11:00 2023-06-09 14:49:00         break
        """
        if which_df not in["all", "work"]:
            return 0
        elif which_df == "all":
            tasks_df = self.df
        elif which_df == "work":
            tasks_df = self.wdf
        groupday_df = tasks_df.groupby("ini_date", as_index=False).agg(total_min=('minutes', 'sum'),
                                                                         total_deltat=('deltat', 'sum'),
                                                                         num_tasks=('task', 'nunique'),
                                                                         mode_task=('task', pd.Series.mode),
                                                                         num_work_per=('task', 'count'),
                                                                         ini_time=('ini_date_time', 'min'),
                                                                         end_time=('end_date_time', 'max'))
        groupday_df["mode_task_str"] = groupday_df["mode_task"].astype('string')
        return groupday_df

    def get_grouped_tasks_by_task(self, which_df: str):
        """
        Group by task including breaks: count occurrences, count days, sum minutes
        :param which_df: ["all", "work"]
        :return: grouptask_df
                 task  order_count  days  sum_min    total_deltat  sum_min_perc
            0     C++            9     4    225.0 0 days 03:45:00     18.72
            1   break           34     4    275.0 0 days 04:35:00     22.88
            2    java           10     3    236.0 0 days 03:56:00     19.63
            3  python            8     4    183.0 0 days 03:03:00     15.22
            4    ruby           12     4    283.0 0 days 04:43:00     23.54
        """
        if which_df not in ["all", "work"]:
            return 0
        elif which_df == "all":
            tasks_df = self.df
        elif which_df == "work":
            tasks_df = self.wdf
        grouptask_df = tasks_df.groupby('task', as_index=False).agg(order_count=('order', 'count'),
                                                                    days=('ini_date', 'nunique'),
                                                                    sum_min=('minutes', 'sum'),
                                                                    total_deltat=('deltat', 'sum'))
        grouptask_df["sum_min_perc"] = round((grouptask_df["sum_min"]/sum(grouptask_df["sum_min"]))*100,2)
        return grouptask_df



