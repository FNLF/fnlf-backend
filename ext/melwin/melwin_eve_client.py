import requests
import json
import random
from .melwin import Melwin
from pprint import pprint

### Eve
from run import app
from eve.methods.post import post_internal #, put_internal, patch_internal, deleteitem_internal

ENTRY_POINT = 'http://localhost:8081/api/v1'


def post_persons():
    
    m = Melwin()

    persons = m.get_all()
    
    i = 0    
    for key, person in persons.items():
        
        """
        Try get on id (alternative lookup)
        
        if 200:
        patch
        
        if 404:
        post
        """
        
        
        print('PERSON')
        pprint(person)
        
        #print(json.dumps(v))
        r = perform_post('melwin/users', json.dumps(person))
        print("'persons' posted", r.status_code)
        #pprint(r.json())
    
        if r.status_code == 201:
            #m.__dbg('POST', 'OK: Posted %s ok' % person['id'])
            print('(Members) Alles in ordnung')

        else:
            #m.__dbg('POST', 'ERR: Posted %s failed' % person['id'])
            pprint(r)
            
        i += 1
        if i > 10:
            break
    
    return None

def post_clubs():
    # Clubs!
    m = Melwin()
    clubs = m.get_all_clubs()
    
    if len(clubs) > 0:
        r = perform_delete('clubs')
        for id, club in clubs.items():
            pprint(json.dumps(club))
            r = perform_post('clubs', json.dumps(club))
            
            if r.status_code == 201:
                #m.__dbg('POST', 'OK: Posted %s ok' % person['id'])
                print('(Clubs) Alles in ordnung')

            else:
                #m.__dbg('POST', 'ERR: Posted %s failed' % person['id'])
                pprint(r)
          
    return None

def post_licenses():
    licenses =  [
        {
            "id": "F-P",
            "name": "Fallskjermpakkerlisens",
            "active": True,
            "url": ""
        },
        {
            "id": "F-MK",
            "name": "Materiellkontrollør",
            "active": True,
            "url": ""
        },
        {
            "id": "F-MR",
            "name": "Materiellreperatør",
            "active": True,
            "url": ""
        },
        {
            "id": "E",
            "name": "Elevbevis line",
            "active": True,
            "url": ""
        },
        {
            "id": "F-EF",
            "name": "Elevbevis fritt fall",
            "active": True,
            "url": ""
        },
        {
            "id": "F-EA",
            "name": "Elevbevis AFF",
            "active": True,
            "url": ""
        },
        {
            "id": "F-A",
            "name": "A-lisens",
            "active": True,
            "url": ""
        },
        {
            "id": "F-B",
            "name": "B-lisens",
            "active": True,
            "url": ""
        },
        {
            "id": "F-C",
            "name": "C-lisens",
            "active": True,
            "url": ""
        },
        {
            "id": "F-D",
            "name": "D-lisens",
            "active": True,
            "url": ""
        },
        {
            "id": "F-TV",
            "name": "Videolisens tandem",
            "active": True,
            "url": ""
        },
        {
            "id": "F-DM2",
            "name": "Demolisens 2",
            "active": True,
            "url": ""
        },
        {
            "id": "F-DM1",
            "name": "Demolisens 1",
            "active": True,
            "url": ""
        },
        {
            "id": "F-TD",
            "name": "Demolisens tandem",
            "active": True,
            "url": ""
        },
        {
            "id": "F-TU-U",
            "name": "Tandemelev",
            "active": True,
            "url": ""
        },
        {
            "id": "F-I3",
            "name": "Instruktør 3",
            "active": True,
            "url": ""
        },
        {
            "id": "F-I2",
            "name": "Instruktør 2",
            "active": True,
            "url": ""
        },
        {
            "id": "F-I1",
            "name": "Instruktør 1",
            "active": True,
            "url": ""
        },
        {
            "id": "F-T",
            "name": "Instruktør tandem",
            "active": True,
            "url": ""
        },
        {
            "id": "F-ITE",
            "name": "Instruktør eksaminator tandem",
            "active": True,
            "url": ""
        },
        {
            "id": "F-I2AFF",
            "name": "Instruktør2 aff",
            "active": True,
            "url": ""
        },
        {
            "id": "F-I3AFF",
            "name": "Instruktør3 aff",
            "active": True,
            "url": ""
        },
        {
            "id": "F-IAE",
            "name": "Instruktør eksaminator aff",
            "active": True,
            "url": ""
        },
        {
            "id": "F-IE",
            "name": "Instruktør eksaminator",
            "active": True,
            "url": ""
        }
    ]
    
    r = perform_post('licenses', json.dumps(licenses))
        
    if r.status_code == 201:
        #m.__dbg('POST', 'OK: Posted %s ok' % person['id'])
        print('(Licenses) Alles in ordnung')

    else:
        #m.__dbg('POST', 'ERR: Posted %s failed' % person['id'])
        pprint(r)

def perform_post(resource, data):
    headers = {'Content-Type': 'application/json'}
    return requests.post(endpoint(resource), data, headers=headers)


def delete(resource):
    r = perform_delete(resource)
    print("'%s' deleted" % resource, r.status_code)


def perform_delete(resource):
    return requests.delete(endpoint(resource))


def endpoint(resource):
    return '%s/%s/' % (ENTRY_POINT, resource)


def get():
    r = requests.get(ENTRY_POINT)
    print(r.json)

if __name__ == '__main__':
    #delete()
    #ids = post_persons()
    #ids = post_clubs()
    #print(ids)
    #delete('persons')
    #ids = post_licenses()
    #ids = post_persons()
    pass 

"""
    Melwin import!
    ==============

"""
"""
from melwin import *

m = Melwin()

r = m.get_all()

for k, v in r:
    
    print('(Eve) Inserting %s' % k)
    app.test_client().post('/persons', json.dumps(v, content_type='application_json'))
"""


