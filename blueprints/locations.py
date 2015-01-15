"""
    Locations vi Kartverket
    =======================
    
    Using kartverket's stedsnavn REST api [GET] to retrieve geographical names in Norway
    
"""

from flask import Blueprint, current_app as app, request, Response, abort, jsonify

from urllib import request as http
import urllib.parse

import xmltodict

import json

Locations = Blueprint('Location service via kartverket', __name__,)

@Locations.route("/search", methods=['GET'])
def search(name='', max=10, epgs=4326):
    
    #Should this be a query string like ?q=<query here>??
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
    
    #if p.get('sokRes').get('sokStatus').get('ok') == 'false' or p.get('sokRes').get('totaltAntallTreff') == '0':
    #    return "Nothing here"
    
    final.update({'_meta': {"page": 1, "total": 1, "max_results": p.get('sokRes').get('totaltAntallTreff')}})
    final.update({'_links': {"self": {"title": "locations for %s" %name, "href": "locations/%s" % name},
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
    """
    "country" : "Norge",
        "geo_type" : "house", navnetype
        "street" : "Majorstuveien 26",
        "geo_class" : "place", 
        "geo_importance" : 0.551,
        "geo" : {
            "coordinates" : [
                59.9262464,
                10.7169424
            ],
            "type" : "Point"
        },
        "city" : "Oslo",
        "zip" : "0367",
        "geo_place_id" : 33268827
        """
    """ for key,val in p.get('sokRes').get('stedsnavn').items():
        
        if key==
        
        print(key)
        print(val)
        print("--")
        #final.get('_items').update(place)
        """
        
                                
                  
    
    return jsonify(**final) #json.dumps(final)
"""
ssrId
92712
--
navnetype
Bruk (gardsbruk)
--
kommunenavn
Bergen
--
fylkesnavn
Hordaland
--
stedsnavn
Stend
--
aust
5.330925000000001
--
nord
60.27261111111111
--
skrivemaatestatus
Vedtatt
--
spraak
NO
--
skrivemaatenavn
Stend
--
epsgKode
4326
"""

def transform(item):
    
    
    p = {}
    
    p.update({'geo': {'coordinates': [item.get('nord'), item.get('aust')], 'type': 'Point'}})
    p.update({'geo_type': item.get('navnetype')})
    p.update({'county': item.get('fylkesnavn')})
    p.update({'municipality': item.get('kommunenavn')})
    p.update({'name': item.get('stedsnavn')})
    
    return p
    
    
    
    
    
    
    