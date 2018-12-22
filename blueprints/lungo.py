"""
    Custom lungo passthrough route
    ==============================

    Basically a clean passthrough to Lungo

"""

from flask import Blueprint
from ext.scf import LUNGO_HEADERS, LUNGO_URL
from ext.app.eve_helper import eve_response
from ext.app.decorators import require_token
import requests

Lungo = Blueprint('Lungo passthrough', __name__, )


@Lungo.route("/", defaults={"path": ""}, methods=['GET'])
@Lungo.route("/<string:path>", methods=['GET'])
@Lungo.route("/<path:path>", methods=['GET'])
# @require_token()
def lungo(path):
    resp = requests.get('{}/{}'.format(LUNGO_URL, path),
                        headers=LUNGO_HEADERS)

    return eve_response(resp.json(), resp.status_code)
