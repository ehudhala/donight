import json
import os

import datetime
from flask import Flask, Response
from flask.helpers import send_from_directory
from sqlalchemy import func

from donight.config.consts import ROOT_DIR, DEBUG
from donight.events import Session, Event

STATIC_FOLDER = os.path.join(ROOT_DIR, 'web', 'client', 'static')

app = Flask(__name__, static_folder=STATIC_FOLDER)


class JsonResponse(Response):
    """
    A response used to return a json object.
    Needed because flask doesn't handle well utf-8,
    so flask.jsonify doesn't work.
    """
    default_mimetype = 'application/json'

    def __init__(self, response=None, *args, **kwargs):
        response = json.dumps(response, ensure_ascii=False).encode('utf8')
        super(JsonResponse, self).__init__(response, *args, **kwargs)


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def index(path):
    return send_from_directory(os.path.join(STATIC_FOLDER, 'build'), 'index.html')


@app.route('/api/events/all')
def get_all_events():
    """
    Returns a flask response, containing all the events in the db.
    """
    session = Session()
    all_events = (session.query(Event)
        .filter(func.date(Event.start_time) >= datetime.datetime.now().date())
        .order_by(Event.start_time).all())
    return JsonResponse([event.to_dict() for event in all_events])


# if __name__ == '__main__':
#     app.run('0.0.0.0', debug=DEBUG)

