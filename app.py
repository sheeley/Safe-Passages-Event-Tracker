from flask import Flask, render_template, jsonify, request
from flask.ext.sqlalchemy import SQLAlchemy
import geoalchemy
from geoalchemy.postgis import PGComparator
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
db = SQLAlchemy(app)

TIME_FORMAT = "%a %b %d %Y %H:%M:%S"


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
    form = request.form
    success = False
    message = None
    try:
        success = save(form)
    except Exception as e:
        app.logger.error(e)
        message = str(e)
    return jsonify({"success": success, "message": message})


@app.route("/list")
def list_existing():
    reports, total = view()
    list_html = render_template("list.html", reports=reports, total=total)
    return render(list_html)


# Service

def save(form):
    email = form.get('email')
    conditions = form.get('conditions')
    starting = form.get('starting')
    ending = form.get('ending')
    input_date = form.get('date')
    date = datetime.strptime(input_date[:len(TIME_FORMAT)+3], TIME_FORMAT)
    report = Report(email, conditions, starting, ending, date)

    db.session.add(report)
    for f_event in form.getlist('events[]'):
        event_type = f_event.get('type')
        latitude = f_event.get('k')
        longitude = f_event.get('d')
        comment = f_event.get('comment')
        # events.append
        db.session.add(Event(event_type, latitude, longitude, comment, report))

    db.session.commit()
    return True


def view(page=0, event_type=None, limit=50, reporter=None,
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
    results = query.order_by("ID DESC").limit(limit).offset(offset).all()
    total = query.count()
    return results, total


# DB Models

class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reporter = db.Column(db.String(120))
    conditions = db.Column(db.String(120))
    starting = db.Column(db.String(120))
    ending = db.Column(db.String(120))
    date = db.Column(db.DateTime())
    events = db.relationship('Event',
                             backref=db.backref('report'))

    def __init__(self, email, conditions, starting, ending, date):
        self.reporter = self.munge_email(email)
        self.conditions = conditions
        self.starting = starting
        self.ending = ending
        self.date = date

    def __repr__(self):
        return '<Report %r>' % self.id

    def munge_email(self, email):
        at_pos = email.index("@")
        return email[:2] + "..." + email[at_pos:]


class Geography(geoalchemy.Geometry):
    """Subclass of `Geometry` that stores a `Geography Type`_.

      Defaults to storing a point.  Call with `specific=False` if you don't
      want to define the geography type it stores, or specify using
      `geography_type='POLYGON'`, etc.

      _`Geography Type`: http://postgis.refractions.net/docs/ch04.html#PostGIS_Geography
    """

    @property
    def name(self):
        if not self.kwargs.get('specific', True):
            return 'GEOGRAPHY'
        geography_type = self.kwargs.get('geography_type', 'POINT')
        srid = self.kwargs.get('srid', 4326)
        return 'GEOGRAPHY(%s,%d)' % (geography_type, srid)


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_type = db.Column(db.String(1))
    # location = geoalchemy.GeometryColumn(Geography(2), comparator=PGComparator)
    comment = db.Column(db.String(500))
    report_id = db.Column(db.Integer, db.ForeignKey('report.id'))

    def __init__(self, event_type, latitude, longitude, comment, report):
        self.event_type = event_type
        # self.location = "POINT(%0.8f %0.8f)" % (longitude, latitude)
        self.comment = comment
        self.report_id = report.id

    def __repr__(self):
        return '<Report %r>' % self.id

if __name__ == "__main__":
    # print db.drop_all()
    # print db.create_all()

    app.run(debug=True)
