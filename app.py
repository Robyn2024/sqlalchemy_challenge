# Import the dependencies.
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify
import datetime as dt


#################################################
# Database Setup
#################################################

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
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
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of precipitation (prcp)and date (date) data"""
    
    # Create new variable to store results from query to Measurement table for prcp and date columns
    precipitation_query_results = session.query(Measurement.prcp, Measurement.date).all()

    # Close session
    session.close()

    # Create a dictionary from the row data and append to a list of all_passengers
        # 1. Create an empty list of precipitation query values 
        # 2. Create for loop to iterate through query results (precipitation_query_results) 
        # 3. Create dictionary with key "precipitation" set to prcp from precipitation_query_results and key "date" to date from precipitation_query_results
        # 4. Append values from precipitation_dict to your original empty list precipitation_query_values 
        # 5. Return JSON format of your new list that now contains the dictionary of prcp and date values to your browser
    
    precipitaton_query_values = []
    for prcp, date in precipitation_query_results:
        precipitation_dict = {}
        precipitation_dict["precipitation"] = prcp
        precipitation_dict["date"] = date
        precipitaton_query_values.append(precipitation_dict)

    return jsonify(precipitaton_query_values) 

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all stations"""
    # Query all stations
    results = session.query(Station.id,Station.station,Station.name,Station.latitude,Station.longitude,Station.elevation).all()
    session.close()
    all_station=[]
    for id,station,name,latitude,longitude,elevation in results:
        station_dict={}
        station_dict['Id']=id
        station_dict['station']=station
        station_dict['name']=name
        station_dict['latitude']=latitude
        station_dict['longitude']=longitude
        station_dict['elevation']=elevation
        all_station.append(station_dict)
    return jsonify(all_station)

@app.route("/api/v1.0/tobs")
def tempartureobs():
   

    """Return a list of all temparture observation"""
    # Calculate the date 1 year ago from the last data point in the database
    results_date=session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    str_date=list(np.ravel(results_date))[0]
    latest_date=dt.datetime.strptime(str_date,"%Y-%m-%d")
    year_back=latest_date-dt.timedelta(days=366)
# Perform a query to retrieve the data and precipitation scores
    results=session.query(Measurement.date, Measurement.tobs).order_by(Measurement.date.desc()).\
            filter(Measurement.date>=year_back).all()
    session.close()
    all_temperature=[]
    for tobs,date in results:
        tobs_dict={}
        tobs_dict['date']=date
        tobs_dict['tobs']=tobs
        all_temperature.append(tobs_dict)
    return jsonify(all_temperature)

# This function called `calc_temps` will accept start date and end date in the format '%Y-%m-%d' 
# and return the minimum, average, and maximum temperatures for that range of dates
@app.route("/api/v1.0/<start>/<end>")
def calc_temps(start, end):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    """TMIN, TAVG, and TMAX for a list of dates.
    
    Args:
        start_date (string): A date string in the format %Y-%m-%d
        end_date (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVE, and TMAX
    """
    
    results=session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    session.close()
    temp_obs={}
    temp_obs["Min_Temp"]=results[0][0]
    temp_obs["avg_Temp"]=results[0][1]
    temp_obs["max_Temp"]=results[0][2]
    return jsonify(temp_obs)

@app.route("/api/v1.0/<start>")
def calc_temps_sd(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    """TMIN, TAVG, and TMAX for a list of dates.
    
    Args:
        start_date (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVE, and TMAX
    """
    
    results=session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                filter(Measurement.date >= start).all()
    session.close()
    temp_obs={}
    temp_obs["Min_Temp"]=results[0][0]
    temp_obs["avg_Temp"]=results[0][1]
    temp_obs["max_Temp"]=results[0][2]
    return jsonify(temp_obs)
if __name__ == '__main__':
    app.run(debug=True)