# -*- coding: utf-8 -*-
from datetime import datetime


def calc_downtime(dt_down: datetime, dt_up: datetime):
    downtime = (dt_up - dt_down).total_seconds()
    days = int(divmod(downtime, 60 * 60 * 24)[0])
    hours = int(divmod(downtime, 60 * 60)[0])
    minutes, seconds = divmod(downtime, 60)
    return f"{days}d {hours:02d}:{int(minutes):02d}:{int(seconds):02d}"
