"""
    Locations vi Kartverket
    =======================
    
    Using kartverket's stedsnavn REST api [GET] to retrieve geographical names in Norway
    
"""

from flask import Blueprint, current_app as app, request, Response, abort, jsonify

from urllib import request as http
import urllib.parse

import xmltodict

from ext.app.decorators import require_token

Locations = Blueprint('Location service via kartverket', __name__,)

@Locations.route("/search", methods=['GET'])
@require_token()
def search(name=None, max=10, epgs=4326):
    """ Search via kartverket's REST service
    - Response is xml, convert to dict with xmltodict
    - Transform each item to our format including geojson for coordinates
    - Transform items into list even if only one result
    
    @todo: need some length don't we? Well we have places like Å so maybe not.
    @todo: verify before http
    """
    
    if name != None:
        q = name
    else:
        q = request.args.get('q', default='', type=str)
    
    query = urllib.parse.urlencode({'navn': q, 'epsgKode': epgs, 'eksakteForst': True, 'maxAnt': max})
    
    r = http.urlopen("https://ws.geonorge.no/SKWS3Index/ssr/sok?%s" % query, timeout=5)
    
    xml = r.read().decode('utf-8')
    
    p = xmltodict.parse(xml)
    
    final = {}
    
    """
    p.get('sokRes').get('sokStatus').get('ok') true|false
    p.get('sokRes').get('sokStatus').get('melding') error message!
    
    """
    
    final.update({'_meta': {"page": 1, "total": 1, "max_results": p.get('sokRes').get('totaltAntallTreff')}})
    final.update({'_links': {"self": {"title": "locations for %s" % q, "href": "locations/search?q=%s" % q},
                             "parent": {"title": "locations", "href": "locations"}
                            }
                  })
    
    places = []
    
    if p.get('sokRes').get('sokStatus').get('ok') == 'false' or p.get('sokRes').get('totaltAntallTreff') == '0':
        final.update({'_items': places})
        return jsonify(**final)
    
    if isinstance(p.get('sokRes').get('stedsnavn'), list):
        for i in p.get('sokRes').get('stedsnavn'):
            places.append(transform(i))
        
    else:
        places = [transform(p.get('sokRes').get('stedsnavn'))]
           
    final.update({'_items': places})
    
    return jsonify(**final)

def transform(item):
    """ Transform item returned from kartverket's xml response
    """
    p = {}
    
    p.update({'geo': {'coordinates': [item.get('nord'), item.get('aust')], 'type': 'Point'}})
    p.update({'geo_type': item.get('navnetype')})
    p.update({'county': item.get('fylkesnavn')})
    p.update({'municipality': item.get('kommunenavn')})
    p.update({'name': item.get('stedsnavn')})
    
    return p
    
    
    
    
    
    
    