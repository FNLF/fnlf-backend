"""
    Weather
    ~~~~~~~

    Blueprint for accessing weather resources,


"""
from flask import Blueprint, current_app as app, request, Response, abort, jsonify
from bson import json_util
import json

# Need custom decorators
from ext.app.decorators import *

from yr.libyr import Yr  # This should not be here
from ext.weather.aeromet import Aeromet

Weather = Blueprint('Weather', __name__, )


@require_token()
@Weather.route("/", methods=['GET'])
def index():
    return jsonify(**{'message': 'Use yr or aero resources'})


@require_token()
@Weather.route("/yr/<string:county>/<string:municipality>/<string:name>/<regex('(now|forecast|wind)'):what>", methods=['GET'])
def yr(what, county, municipality, name):
    """ Downloads data from yr.no
    @todo: Should fix units
    @todo: Should be based on locations and/or clubs default location in clubs '/yr/wind/375-F'
    """

    yrpath = ("Norge/%s/%s/%s" % (county, municipality, name))
    weather = Yr(location_name=yrpath)

    if what == 'now':

        return weather.now(as_json=True)

    elif what == 'forecast':
        return jsonify(**weather.dictionary['weatherdata']['forecast'])

    elif what == 'wind':
        wind_speed = dict()
        wind_speed['wind_forecast'] = [{'from': forecast['@from'], 'to': forecast['@to'], '@unit': 'knots', 'speed': round(float(forecast['windSpeed']['@mps']) * 1.943844, 2)} for forecast in
                                       weather.forecast()]
        return jsonify(**wind_speed)


@require_token()
@Weather.route("/aero/<regex('[aA-zZ]{4}'):icao>/<regex('(metar|taf|shorttaf)'):what>", methods=['GET'])
def aero(what, icao):
    """ Aero resource retrieves metar and taf for given icao code
    @todo: support switches for raw and decoded messages
    @todo: support for historical data
    """

    w = Aeromet(icao.upper())

    if what == 'metar':
        return jsonify(**{'metar': w.metar()})
    elif what == 'taf':
        return jsonify(**{'taf': w.taf()})
    elif what == 'shorttaf':
        return jsonify(**{'shorttaf': w.shorttaf()})
