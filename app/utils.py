# -*- coding: utf-8 -*-
from datetime import datetime
import requests

from conn_monitor_logger import HistoryLogger


def calc_downtime(dt_down: datetime, dt_up: datetime):
    downtime = (dt_up - dt_down).total_seconds()
    days = int(divmod(downtime, 60 * 60 * 24)[0])
    hours = int(divmod(downtime, 60 * 60)[0])
    minutes, seconds = divmod(downtime, 60)
    return f"{days}d {hours:02d}:{int(minutes):02d}:{int(seconds):02d}"


def import_from_url(url):
    response = requests.get(url)
    if response.status_code != 200:
        return 0
    rows_updated = 0
    with HistoryLogger() as db:
        for i, row in enumerate(response.json()):
            print(f"[{i:03d}] Importing row with id {row.get('íd')} and correlation_id {row.get('correlation_id')} ...")
            try:
                db.log_event(id=row.get("id"),
                             correlation_id=row.get("correlation_id"),
                             event=row.get("event"),
                             event_timestamp=row.get("event_timestamp"),
                             status_code=row.get("status_code"),
                             error_message=row.get("error_message"),
                             url=row.get("url"))
                rows_updated += 1

            except:
                pass
    print("Done importing rows...")
    return rows_updated


if __name__ == '__main__':
    affected_rows = import_from_url(url="http://skyrasp4:10044/api/v1/statistics")
    print(affected_rows)
