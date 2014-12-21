"""
    Person
    ======
    
    This schema resembles the complete person object generated with melwin.py
    
    Note that it uses "strong typing" for membership and licenses!
    
    Also:
    - getting object for snapshot in avvik: projection: {id: 1, membership: 1, licenses: 1, clubs: 1} 
        
    NB: Non conforming melwinId type string in mongo, should be integer!
    
    Indexes:
    db.users.ensureIndex({"id": 1},{ unique: true } );
    db.users.ensureIndex({ "location" :"2dsphere"}); 
    @todo: Look at taking location apart as loacation { location {type, coordinates()}, -and the rest of openstreetmap-}
    @todo: This should be routed as melwin? People??

"""


_schema = {
            'id' : {'type': 'integer',
                    'unique': True,
                    'required': True
                    },
           
            'active': {'type': 'boolean'},
            
            'updated': {'type': 'datetime'},
            
            'firstname' : {'type': 'string',
                           'required': True,
                           },
            
            'lastname' : {'type': 'string',
                          'required': True,},
            
            'birthdate' : {'type': 'datetime'},
            
            'gender': {'type': 'string',
                       'maxlength': 1,
                       'allowed': ['M', 'F']},       
           
            'email' : {'type': 'string'},
           
            'phone' : {'type': 'string'},
           
            'location' : {'type': 'dict',
                          'schema': {
                                    'street': {'type': 'string'},
                                    'zip' : {'type': 'string'},
                                    'city' : {'type': 'string'},
                                    'country' : {'type': 'string'},
                                    'geo': {'type': 'point'},
                                    'geo_class': {'type': 'string'},
                                    'geo_importance': {'type': 'float'},
                                    'geo_place_id': {'type': 'integer'},
                                    'geo_type': {'type': 'string'},
                                    },
                          },
            'membership' : {'type': 'dict',
                            'schema': {
                                       'type': {'type': 'string'},
                                       'clubs' : {'type': 'list'},
                                       'valid': {'type': 'datetime'},
                                       'enrolled': {'type': 'datetime'},
                                       'balance': {'type': 'number'},
                                       'fee': {'type': 'number'},
                                       #'terminated': {'type': 'datetime', 'required': False} # Just rubbish from Melwin...
                                       },
                          },
            
            'licenses': {'type': 'dict',
                         'schema': {'rights': {'type': 'list'},
                                    'expiry': {'type': 'datetime'},
                                    },
                         },
            }
        
definition = {
        'item_title': 'Melwin Users',
        'url': 'melwin/users',
        'description': 'Melwin passthrough',
        
        #'item_url': 'users',
        
        'datasource': {'source': 'melwin_users',
                       #'projection' : {'firstname': 1, 'lastname': 1, 'id': 1},
                       'default_sort': [('id', 1)],
                       },
        
        'resource_methods': ['GET', 'POST', 'DELETE'], #NB delete only for testing!!
        'item_methods': ['GET', 'PATCH', 'PUT'],
        
        'additional_lookup': {
            'url': 'regex("[\d{1,6}]+")',
            'field': 'id',
        },
        
        'versioning': True,
        
        'schema': _schema
        
        }