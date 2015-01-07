from flask import Blueprint, current_app as app, request, Response, abort, jsonify
from bson import json_util
import json

# Need custom decorators
from ext.decorators import *

from yr.libyr import Yr #This should not be here

from ext.aeromet import Aeromet

Weather = Blueprint('Weather', __name__,)


"""

    Custom Flask routes 1:
    =====================
    
    Example using a flask route decorator with an external package
    
    Fetching yr.no data for all practical purposes just proxying via the route...
    
    Depends on libyr:
    >>>pip install git+https://github.com/wckd/python-yr.git
    
    Routes can also be packaged, say we have a 'avvik_custom_routes' package:
    import avvik_custom_routes
    And in the __init__.py the routes are defined, and makes this nice and clean!
    
    This is an example of a 'multiroute', ie the switch is the 'what' variable
    
    Also:
    =====
    
    Can also fetch data (forecast, metar & taf) as a supplement to the anomaly/avvik without user intervention

"""

@Weather.route("/", methods=['GET'])
def index():
    
    return jsonify(**{'message': 'Use yr or aero resources'})

@Weather.route("/yr/<regex('(now|forecast|wind)'):what>", methods=['GET'])
def yr(what):
    """ Downloads data from yr.no
    @todo: Should fix units
    @todo: Should be based on locations and/or clubs default location in clubs '/yr/wind/375-F'
    """
    
    
    weather = Yr(location_name='Norge/Vestfold/Tønsberg/Jarlsberg_flyplass')
    
    if what == 'now':
        return weather.now(as_json=True)
    
    elif what == 'forecast':
        return jsonify(**weather.dictionary['weatherdata']['forecast'])
    
    elif what == 'wind':
        wind_speed = dict()
        wind_speed['wind_forecast'] = [{'from': forecast['@from'], 'to': forecast['@to'],'@unit': 'knots', 'speed': round(float(forecast['windSpeed']['@mps'])*1.943844, 2)} for forecast in weather.forecast()]
        return jsonify(**wind_speed)
        


@Weather.route("/aero/<regex('(metar|taf|shorttaf)'):what>/<icao>", methods=['GET'])
def aero(what, icao):
    """ Aero resource retrieves metar and taf for given icao code
    @todo: support switches for raw and decoded messages
    @todo: support for historical data
    """
    
    w = Aeromet(icao)
    
    if what == 'metar':
        return jsonify(**{'metar': w.metar()})
    elif what == 'taf':
        return jsonify(**{'taf': w.taf()})
    elif what == 'shorttaf':
        return jsonify(**{'shorttaf': w.shorttaf()})
    
    
        
    
    
    