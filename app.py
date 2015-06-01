"""
Running in dev:
python app.py

If you want to create a new db when you run:
DROP_CREATE=true python app.py
"""
from flask import Flask, render_template, jsonify, request
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.schema import Index
from datetime import datetime
from os import environ
from json import loads, dumps


app = Flask(__name__)
env_db = environ.get('DATABASE_URL')
drop_and_create_db = environ.get('DROP_CREATE')

if env_db:
    app.config['SQLALCHEMY_DATABASE_URI'] = env_db
    drop_and_create_db = False
else:
    # just assume dev, who cares
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
db = SQLAlchemy(app)

TIME_FORMAT = "%a, %d %b %Y %H:%M:%S %Z"


# API

def render(content):
    '''Render inner template into base'''
    return render_template("base.html", content=content)


@app.route("/")
def add_form():
    '''Render the map view to add a report'''
    key = "AIzaSyAF_o9iMtsGlET7yYVhAWoLFsRGBU9ge4o"
    content = render_template("form.html", key=key)
    return render(content)


@app.route("/save", methods=['POST'])
def post_save():
    '''Save a report'''
    success = False
    message = None
    try:
        data = loads(request.data)
        success = save(data)
    except Exception as e:
        app.logger.error(e)
        message = str(e)
    return jsonify({"success": success, "message": message})


@app.route("/view")
def view():
    view_html = render_template("view.html")
    return render(view_html)


@app.route("/view-json")
def view_json():
    event_types = request.args.get('event_types', '').split(',')
    start_date = request.args.get('start', None)
    end_date = request.args.get('end', None)
    page = int(request.args.get('page', 1)) - 1
    limit = int(request.args.get('limit', 50))

    start_date = datetime.strptime(start_date, TIME_FORMAT) if start_date else None
    end_date = datetime.strptime(end_date, TIME_FORMAT) if end_date else None

    report_resp, total = load_reports(page=page, limit=limit, event_types=event_types,
                                      start_date=start_date, end_date=end_date)
    reports = []
    events = []
    if report_resp:
        reports = [r for r in report_resp]
        report_map = {r.id: r for r in reports} if reports else {}
        events = load_events_for_reports(reports) if reports else []

    for e in events:
        report = report_map.get(e.report_id)
        if not report.events:
            report_map = []

        report.events.append(e)

    return jsonify({
        "events": [e.to_dict() for e in events],
        "reports": [r.to_dict() for r in reports],
        "total": total
    })


# Service

def save(form):
    email = form.get('email')
    conditions = form.get('conditions')
    starting = form.get('starting')
    ending = form.get('ending')
    input_date = form.get('date')
    association = form.get('association')
    events = form.get('events')

    if not events:
        raise Exception("Please include events")

    date = datetime.strptime(input_date, TIME_FORMAT)

    report = Report(email, conditions, starting, ending, date, association)
    if not report.is_valid():
        raise Exception('Report not valid. {}'.format(report))

    db.session.add(report)

    for f_event in events:
        event_type = f_event.get('type')
        latitude = f_event.get('k')
        longitude = f_event.get('d')
        comment = f_event.get('comment')
        people_involved = f_event.get('people_involved')
        event = Event(event_type, latitude, longitude, people_involved, comment, report)
        if event.is_valid():
            db.session.add(event)
        else:
            raise Exception('Event {} is not valid'.format(event))

    db.session.commit()

    return True


def load_reports(page=0, limit=50, event_types=None, reporter=None,
                 start_date=None, end_date=None):
    offset = page * limit
    query = Report.query

    if start_date:
        query = query.filter(Report.date >= start_date)

    if end_date:
        query = query.filter(Report.date <= end_date)

    if event_types:
        # TODO - will actually require rewriting how these queries are performed
        pass
        # query = query.filter(.type.in_((123,456))

    total = query.count()

    query = query.order_by("ID DESC")
    query = query.limit(limit)
    query = query.offset(offset)

    return query.all(), total


def load_events_for_reports(reports):
    report_ids = [r.id for r in reports]
    query = Event.query.filter(Event.id.in_(report_ids))
    return query.all()


# DB Models

class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reporter = db.Column(db.String(120))
    conditions = db.Column(db.String(2000))
    starting = db.Column(db.String(120))
    ending = db.Column(db.String(120))
    date = db.Column(db.DateTime(), index=True)
    association = db.Column(db.String(255))

    def __init__(self, email, conditions, starting, ending, date, association):
        self.reporter = self.munge_email(email)
        self.conditions = conditions
        self.starting = starting
        self.ending = ending
        self.date = date
        self.association = association

    def __repr__(self):
        return '<Report {} {}>'.format(self.id, self.date)

    def munge_email(self, email):
        try:
            at_pos = email.index("@")
            return email[:2] + "..." + email[at_pos:]
        except Exception:
            return "no email"

    def to_dict(self):
        return {
            'id': self.id,
            'reporter': self.reporter,
            'conditions': self.conditions,
            'starting': self.starting,
            'ending': self.ending,
            'date': self.date.strftime("%B %-d, %Y"),
            'association': self.association,
            'events': [e.to_dict() for e in self.events] if self.events else []
        }

    def is_valid(self):
        if self.date:
            return True


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_type = db.Column(db.String(3))
    latitude = db.Column(db.Float())
    longitude = db.Column(db.Float())
    comment = db.Column(db.String(500))
    people_involved = db.Column(db.Integer)

    report_id = db.Column(db.Integer, db.ForeignKey('report.id'))
    report = db.relationship('Report',
                             backref=db.backref('events', lazy='dynamic'))

    report_id = db.Column(db.Integer, db.ForeignKey('report.id'))

    def __init__(self, event_type, latitude, longitude, people_involved, comment, report):
        self.event_type = event_type
        self.latitude = latitude
        self.longitude = longitude
        self.people_involved = people_involved
        self.comment = comment
        self.report = report

    def __repr__(self):
        return '<Event {}: {} ({}, {}) report: {}>'.format(self.id,
                                                           self.event_type,
                                                           self.latitude,
                                                           self.longitude,
                                                           self.report_id)

    def to_dict(self):
        return {
            'id': self.id,
            'event_type': self.event_type,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'report_id': self.report_id,
            'comment': self.comment,
            'people_involved': self.people_involved
        }

    def is_valid(self):
        required = [self.event_type, self.latitude, self.longitude, self.report]
        for prop in required:
            if not prop:
                return False
        return True

Index('event_type_index', Event.report_id, Event.event_type)

if __name__ == "__main__":
    if drop_and_create_db:
        print db.drop_all()
        print db.create_all()

    app.run(debug=True)
