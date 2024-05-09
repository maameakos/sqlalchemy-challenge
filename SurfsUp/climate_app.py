from flask import Flask, jsonify
from sqlalchemy import func
from sqlalchemy.ext.automap import automap_base
import datetime as dt
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, desc



# Create a Flask app
app = Flask(__name__)
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)
Measurement = Base.classes.measurement
Station = Base.classes.station

session = Session(engine)

most_recent_date = session.query(func.max(Measurement.date)).scalar()
one_year_ago = dt.datetime.strptime(most_recent_date, '%Y-%m-%d') - dt.timedelta(days=365)

# Define the routes
@app.route("/")
def home():
    """List all available routes."""
    return (
        f"Available Routes:<br/>"
        f"<a href='/api/v1.0/precipitation'>/api/v1.0/precipitation</a><br/>"
        f"<a href='/api/v1.0/stations'>/api/v1.0/stations</a><br/>"
        f"<a href='/api/v1.0/tobs'>/api/v1.0/tobs</a><br/>"
        f"<a href='/api/v1.0/&lt;start&gt;'>/api/v1.0/&lt;start&gt;</a><br/>"
        f"<a href='/api/v1.0/&lt;start&gt;/&lt;end&gt;'>/api/v1.0/&lt;start&gt;/&lt;end&gt;</a>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return JSON with date as key and precipitation as value for the last year."""
    # Query the most recent date in the database
    
    # Calculate the date one year ago from the most recent date
    
    # Query precipitation data for the last year
    precipitation_data = session.query(Measurement.date, Measurement.prcp).\
                         filter(Measurement.date >= one_year_ago).order_by(Measurement.date).all()
    
    # Convert query results to a dictionary with date as key and precipitation as value
    precipitation_dict = {date: prcp for date, prcp in precipitation_data}
    
    return jsonify(precipitation_dict)

@app.route("/api/v1.0/stations")
def stations():
    """Return a JSON list of stations."""
    # Query the list of stations
    stations = session.query(Station.station).all()
    
    # Convert the query results to a list
    station_list = [station for station, in stations]
    
    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
    """Return a JSON list of temperature observations for the most-active station for the previous year."""
    # Calculate the date one year ago from the most recent date
    most_active_stations = session.query(Measurement.station, func.count(Measurement.station)).\
                        group_by(Measurement.station).\
                        order_by(desc(func.count(Measurement.station))).all()
    most_active_station_id = most_active_stations[0][0]

    # Query the temperature observations for the most-active station for the previous year
    most_active_station_tobs = session.query(Measurement.tobs).\
                                filter(Measurement.station == most_active_station_id).\
                                filter(Measurement.date >= one_year_ago).all()
    
    # Convert the query results to a list
    tobs_list = [tobs for tobs, in most_active_station_tobs]
    
    return jsonify(tobs_list)

@app.route("/api/v1.0/<start>")
def start_date_stats(start):
    """Accepts the start date as a parameter from the URL.
    Returns the min, max, and average temperatures calculated from the given start date to the end of the dataset."""
    # Query temperature statistics for dates greater than or equal to the start date
    temperature_stats = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                        filter(Measurement.date >= start).all()
    
    # Convert query results to a list of dictionaries
    temperature_stats_list = [{"TMIN": tmin, "TAVG": tavg, "TMAX": tmax} for tmin, tavg, tmax in temperature_stats]
    
    return jsonify(temperature_stats_list)

@app.route("/api/v1.0/<start>/<end>")
def start_end_date_stats(start, end):
    """Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature 
    for dates between the start and end dates (inclusive)."""
    # Query temperature statistics for dates between the start and end dates
    temperature_stats = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                        filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    
    # Convert query results to a dictionary
    temperature_stats_dict = {"TMIN": temperature_stats[0][0], "TAVG": temperature_stats[0][1], "TMAX": temperature_stats[0][2]}
    
    return jsonify(temperature_stats_dict)

# Run the app
if __name__ == "__main__":
    app.run()
