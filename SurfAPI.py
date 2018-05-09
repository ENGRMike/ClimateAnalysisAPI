import pandas as pd
import datetime as dt
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

engine = create_engine("sqlite:///hawaii.sqlite")

Base = automap_base()
Base.prepare(engine, reflect = True)

weather_station = Base.classes.Hawaii_Weather

session = Session(engine)

app = Flask(__name__)


@app.route("/")
def home_page():
    return(
        f'Here are the available routes: '
        f"api/v1/prcp<br/>"
        f"api/v1/stations<br/>"
        f"api/v1/dailytemp<br/>"
        f"api/v1/temps/start/end"
    )

@app.route("/api/v1/prcp")
def precipitation():
    past_year = dt.date.today() - dt.timedelta(days=365)

    precipitation = session.query(weather_station.date, weather_station.prcp).filter(weather_station.date>=past_year).all()

    precip = {date: prcp for date, prcp in precipitation}
    return jsonify(precip)

@app.route("/api/v1/stations")
def stations():
    station_data=session.query(weather_station.station).all()
    stations = list(np.ravel(station_data))
    return jsonify(stations)

@app.route("/api/v1/dailytemp")
def temp_obs():
    past_year = dt.date.today() - dt.timedelta(days=365)
    dailytemp = session.query(weather_station.tobs).filter(weather_station.station == "USC00519281").filter(weather_station.date >= past_year).all()

    temp = list(np.ravel(dailytemp))
    return jsonify(temp)

@app.route("/api/v1/temp/<start>")
@app.route("/api/v1/temp/<start>/<end>")
def date_range(start = None, end = None):

    weather_stats = [func.min(weather_station.tobs), func.max(weather_station.tobs), func.avg(weather_station.tobs)]

    if not end:
        stats = session.query(*weather_stats).filter(weather_station.date >=  start).all()

        temp = list(np.ravel(stats))
        return jsonify(temp)
    
    data = session.query(*weather_stats).filter(weather_station.date >= start).filter(weather_station.date <= end).all()

    temp = list(np.ravel(data))
    return jsonify(temp)

if __name__ == '__main__':
    app.run()