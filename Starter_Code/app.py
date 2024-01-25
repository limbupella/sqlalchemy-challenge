# Import the dependencies
import numpy as np
import datetime as dt

import sqlalchemy 
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite",echo=True)

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# View all of the classes that automap found
Base.classes.keys()

# Save references to each table
measurement= Base.classes.measurement
station= Base.classes.station

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
def Welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start_date<br/>"
        f"/api/v1.0/start_date/end_date"
    )
#app routing for precip for the past 12 months
@app.route("/api/v1.0/precipitation")
def precipitation():
  
    #The last 12 months of preciptipation data
    # Find the most recent date in the data set.
    recent_date = session.query(measurement.date).order_by(measurement.date.desc()).first()[0]

    # Calculate the date one year from the last date in data set.
    year_ago = dt.date(2017,8,23) - dt.timedelta(days=365)


# Perform a query to retrieve the data and precipitation scores
    perc_data = session.query(measurement.date, measurement.prcp)\
            .filter(measurement.date >= year_ago)\
            .order_by(measurement.date).all()
    
    # Convert the query results to a dictionary
    precip_dict = {date: prcp for date, prcp in precip_dict}

    return jsonify(precip_dict)

@app.route("/api/v1.0/stations")
def stations():
    # Design a query to calculate the total number of stations in the dataset
    station_data = session.query(func.count(station.station)).first()[0]

    # Convert the query results to a list of dictionaries
    stations_list = [{"Station": station, "Name": name} for station, name in station_data]

    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def tobs():
    # Using the most active station id from the previous query, calculate the lowest, highest, and average temperature.
    station_id = session.query(func.min(measurement.tobs),
                                func.max(measurement.tobs),
                                func.avg(measurement.tobs))\
    .filter(measurement.station == 'USC00519281')\
    .all()

    # Calculate the date one year from the last date in data set.
    year_ago = dt.date(2017,8,23) - dt.timedelta(days=365)

    # Using the most active station id
    active_id = session.query(measurement.tobs, measurement.station)\
            .filter(measurement.station == "USC00519281")\
            .filter(measurement.date >= year_ago)\
            .all()
    
    active_id = [{"Date": date, "Temperature": tobs} for date, tobs in active_id]

    return jsonify(active_id)

@app.route("/api/v1.0/<start>")
def temperature_start(start):
    station_id = session.query(func.min(measurement.tobs),
                                  func.max(measurement.tobs),
                                  func.avg(measurement.tobs))\
    .filter(measurement.station == 'USC00519281')\
    .all()

    temp_list = [{"TMIN": tmin, "TAVG": tavg, "TMAX": tmax} for tmin, tavg, tmax in station_id]

    return jsonify(temp_list)

@app.route("/api/v1.0/<start>/<end>")
def temperature_range(start, end):
    station_id = session.query(func.min(measurement.tobs),
                                  func.max(measurement.tobs),
                                  func.avg(measurement.tobs))\
        .filter(measurement.station == 'USC00519281')\
    .all()
    temp_list = [{"TMIN": tmin, "TAVG": tavg, "TMAX": tmax} for tmin, tavg, tmax in station_id]

    return jsonify(temp_list)

if __name__ == '__main__':
    app.run(debug=True)
