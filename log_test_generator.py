import random
import datetime as dt

task = ["C++", "java", "python"]

date_ini = dt.datetime(year=2023, month=6, day=13, hour=15, minute=11)
date_end = dt.datetime(year=2023, month=6, day=13, hour=20, minute=29)

work_t = dt.timedelta(minutes=25)
break_t = dt.timedelta(minutes=5)
long_break_t = dt.timedelta(minutes=20)


current_time = date_ini
iter_num = 1
while current_time < date_end:
    if iter_num % 8 == 0:
        if current_time < date_end:
            print(current_time.strftime("%Y:%m:%d") + "," + current_time.strftime("%H:%M:%S") + ',' + "break," + str(iter_num) + ',' + "LONG_BREAK")
        current_time += long_break_t
    elif iter_num % 2 == 0:
        if current_time < date_end:
            print(current_time.strftime("%Y:%m:%d") + "," + current_time.strftime("%H:%M:%S") + ',' + "break," + str(iter_num) + ',' + "BREAK")
        current_time += break_t
    else:
        if current_time < date_end:
            print(current_time.strftime("%Y:%m:%d") + "," + current_time.strftime("%H:%M:%S") + ',' + random.choice(task) + ',' + str(iter_num) + ',' + "WORK")
        current_time += work_t
    iter_num += 1

print(date_end.strftime("%Y:%m:%d") + "," + date_end.strftime("%H:%M:%S") + ',' + "stop," + str(iter_num - 1) + ',' + "STOP")
print(date_end.strftime("%Y:%m:%d") + "," + date_end.strftime("%H:%M:%S") + ',' + "FINISH," + '0' + ',' + "FINISH")

