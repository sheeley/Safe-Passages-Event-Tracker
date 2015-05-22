from flask import Flask, render_template, jsonify, request
from flask.ext.sqlalchemy import SQLAlchemy
from datetime import datetime
from os import environ
from json import loads, dumps


class Config(object):
    DB_PATH = ""


app = Flask(__name__)
env_db = environ.get('DATABASE_URL')
drop_and_create_db = False

if env_db:
    app.config['SQLALCHEMY_DATABASE_URI'] = env_db
else:
    # just assume dev, who cares
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
    drop_and_create_db = True
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
    content = render_template("map.html", key=key)
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
    reports, total = load_reports()
    events_json = dumps([e.to_dict() for e in load_events_for_reports(reports)])
    reports_json = dumps([r.to_dict() for r in reports])

    view_html = render_template("view.html", reports_json=reports_json, total=total, events_json=events_json)
    return render(view_html)


# Service

def save(form):
    email = form.get('email')
    conditions = form.get('conditions')
    starting = form.get('starting')
    ending = form.get('ending')
    input_date = form.get('date')
    date = datetime.strptime(input_date, TIME_FORMAT)

    report = Report(email, conditions, starting, ending, date)
    db.session.add(report)

    for f_event in form.get('events'):
        event_type = f_event.get('type')
        latitude = f_event.get('k')
        longitude = f_event.get('d')
        comment = f_event.get('comment')
        people_involved = f_event.get('people_involved')

        db.session.add(Event(event_type, latitude, longitude, people_involved, comment, report))
    db.session.commit()

    return True


def load_reports(page=0, limit=50, event_type=None, reporter=None,
                 start_date=None, end_date=None):
    offset = page * limit
    query = Report.query
    filters = {
        "type": event_type,
        "reporter": reporter,
        "start_date": start_date,
        "end_date": end_date
    }
    filters = {k: v for k, v in filters.iteritems() if v}
    if filters:
        query = query.filter_by(**filters)
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
    conditions = db.Column(db.String(120))
    starting = db.Column(db.String(120))
    ending = db.Column(db.String(120))
    date = db.Column(db.DateTime())

    def __init__(self, email, conditions, starting, ending, date):
        self.reporter = self.munge_email(email)
        self.conditions = conditions
        self.starting = starting
        self.ending = ending
        self.date = date

    def __repr__(self):
        return '<Report %r>' % self.id

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
            'date': self.date.isoformat()
        }


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_type = db.Column(db.String(1))
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
        return '<Event %r>' % self.id

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

if __name__ == "__main__":
    if drop_and_create_db:
        print db.drop_all()
        print db.create_all()

    app.run(debug=True)
