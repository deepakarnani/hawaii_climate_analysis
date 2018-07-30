import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"Enter start or end date with format: '%Y-%m-%d'<br/>"
        f"/api/v1.0/start<br/>"

        f"/api/v1.0/start/end<br/>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return a list of all precipitation data from previous year"""
    # Query all passengers
    results = session.execute("""SELECT date, prcp FROM Measurement WHERE date BETWEEN '2016-08-23' and '2017-08-23'""").fetchall()

    # Convert list of tuples into normal list
    all_prcp = []
    for measurement in results:
        prcp_dict = {}
        prcp_dict["date"] = measurement.date
        prcp_dict["precipitation"] = measurement.prcp
        all_prcp.append(prcp_dict)

    return jsonify(all_prcp)

@app.route("/api/v1.0/stations")
def stations():
    """Return a list of all stations"""
    # Query all stations
    results = session.query(Station.name).all()

    # Convert list of tuples into normal list
    station_names = list(np.ravel(results))

    return jsonify(station_names)

@app.route("/api/v1.0/tobs")
def temps():
    """Return a list of all temperatures from previous year"""
    # Query all stations
    results = session.execute("""SELECT date, tobs FROM Measurement WHERE date BETWEEN '2016-08-23' and '2017-08-23'""").fetchall()

    # Convert list of tuples into normal list
    all_temp = []
    for measurement in results:
        temp_dict = {}
        temp_dict["date"] = measurement.date
        temp_dict["temps"] = measurement.tobs
        all_temp.append(temp_dict)

    return jsonify(all_temp)

@app.route("/api/v1.0/<start>")
def start_(start):
    arrival = dt.datetime.strptime(start, '%Y-%m-%d')
    
    departure = dt.timedelta(days=360)

    sel = [
        func.avg(Measurement.tobs),
        func.min(Measurement.tobs),
        func.max(Measurement.tobs)
    ]
    
    start_trip =  session.query(*sel). \
    filter(Measurement.date >= arrival). \
    filter(Measurement.date <= departure).all()

    start_trip = list(np.ravel(start_trip))

    return jsonify(start_trip)

@app.route("/api/v1.0/<start>/<end>")
def start_end(start,end):
    year_final = dt.timedelta(days=365)
    arrival = dt.datetime.strptime(start, '%Y-%m-%d')
    departure = dt.datetime.strptime(end, '%Y-%m-%d')

    start = arrival - year_final
    end = departure - year_final

    sel = [
        func.avg(Measurement.tobs),
        func.min(Measurement.tobs),
        func.max(Measurement.tobs)
    ]
    
    start_trip = session.query(*sel). \
    filter(Measurement.date >= start). \
    filter(Measurement.date <= end).all()

    start_trip = list(np.ravel(start_trip))

    return jsonify(start_trip)

if __name__ == '__main__':
    app.run(debug=True)
