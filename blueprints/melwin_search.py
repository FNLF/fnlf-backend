"""
    The melwin search blueprint!
    ============================
"""


from flask import Blueprint, current_app as app, request, Response, abort, jsonify

#from ext.melwin import Melwin
# Debug
from pprint import pprint
# TIME & DATE - better with arrow only?
import arrow
# Auth, not needed since token based
from time import sleep

#Need those badly!
from ext.decorators import *
import json
import re



MelwinSearch = Blueprint('Melwin Search', __name__,)

@MelwinSearch.route("/", methods=['GET'])
@require_token()
def search_user():
    
    err = True
    result = []
    num_results = 0
    data = {}
    message = 'No results'
    
    col = app.data.driver.db['melwin_users']
    
    q = request.args.get('q', default='', type=str)
    max_results = request.args.get('max_results', default=25, type=int)
    
    if len(q) > 2:
    
        if q.isnumeric():
            query = "/^%s.*/.test(this.id)" % q
            r = col.find({ "$where": query }, {"id": 1, "fullname": 1}).limit(max_results)
            pprint(r.count())
            pprint(query)
        else:
            regex = re.compile('[^a-zæøåA-ZÆØÅ\s]')
            query = regex.sub('', q)
            
            #re.sub('[^A-Zæøåa-zæøå]+', '', q)
            pprint(query)
            r = col.find({"fullname": {"$regex": ".*%s.*" % query, "$options": "i"}}, {"id": 1, "fullname": 1}).limit(max_results)
        
        num_results = r.count()    
        # We have a result set!    
        if r and num_results > 0:
            
            message = "Found %s results" % num_results
            err = False
            
            for u in r:
                if 'id' not in u:
                    pprint(u)
                    continue
                else:
                    result.append({'id': u['id'], 'fullname': u['fullname']})
            
    else:
        message = "You need at least 3 characters for searching"
    # Build the result
            
    data.update({'_meta': {'err': err, 'total': num_results, 'max_results': max_results, 'message': message}, '_items': result})
    
    
    #return jsonify(**{data})
    return Response(json.dumps(data),  mimetype='application/json')
    
    
