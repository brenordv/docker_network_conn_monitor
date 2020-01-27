# -*- coding: utf-8 -*-
import threading

import flask
from flask import jsonify, make_response

from config import STATISTICS_API_PORT, STATISTICS_API_HOST
from conn_monitor_logger import HistoryLogger
from utils import calc_downtime


def _make_summary_(rows):
    unique_cids = list(set([r["correlation_id"] for r in rows]))
    summary = list()
    for cid in unique_cids:
        row_connected = [r for r in rows if r["correlation_id"] == cid and r["event"] == "connected"][0]
        row_disconnected = [r for r in rows if r["correlation_id"] == cid and r["event"] == "disconnected"][0]
        summary.append({
            "correlation_id": cid,
            "disconnected_at": row_disconnected["event_timestamp"],
            "connected_at": row_connected["event_timestamp"],
            "downtime": calc_downtime(dt_down=row_disconnected["event_timestamp"],
                                      dt_up=row_connected["event_timestamp"])
        })

    return summary


api = flask.Blueprint("statistics_api", "api_blueprint", url_prefix="/api/v1")
web_helper = flask.Flask("statistics_web")


@web_helper.route("/", methods=["GET"])
def route_home():
    return "home", 200


@api.route("/statistics", defaults={"correlation_id": None})
@api.route("/statistics/<correlation_id>")
def route_api_general(correlation_id):
    rows = list()
    with HistoryLogger() as statistics_database:
        rows = statistics_database.get_events(correlation_id=correlation_id)

    if len(rows) == 0:
        return make_response(jsonify(list()), 204)

    if flask.request.args.get("show", "").lower().strip() == "summary":
        return jsonify(_make_summary_(rows=rows))

    return jsonify(rows)


web_helper.register_blueprint(api)


def start_api_in_background():
    global web_helper
    thread = threading.Thread(target=web_helper.run, args=(STATISTICS_API_HOST, STATISTICS_API_PORT))
    thread.daemon = True
    thread.start()


def start_api():
    global web_helper
    web_helper.run(STATISTICS_API_HOST, STATISTICS_API_PORT)
