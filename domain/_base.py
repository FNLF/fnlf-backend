"""

    Base schemas
    ============
    
    Reusable schemas for resource definitions
           
"""

workflow_schema = {'type': 'dict', 
                   'readonly': True,
                   'default': {}
                   }

watchers_schema = {'type': 'list',
                   'default': [],
                   'readonly': True}

comments_schema = {'type': 'list',
                   'default': [],
                   'schema': {'date': 'datetime',
                        'user': 'integer',
                        'comment': 'string'
                        }
                   }


audit_schema = {'type': 'list', 
              'readonly': True,
                'default': []
                }

acl_schema = {'type': 'dict', 
              'readonly': True,
              'default': {}
              }

labels_schema = {'type': 'list',
                 'default': []
                 }


geo_schema = {'geo': {'type': 'point'},
              'geo_class': {'type': 'string'},
              'geo_importance': {'type': 'float'},
              'geo_place_id': {'type': 'integer'},
              'geo_type': {'type': 'string'}
              }
                                   
                                   
location_schema = {'type': 'dict',
                        'schema': {
                                   'street': {'type': 'string'},
                                   'zip' : {'type': 'string'},
                                   'city' : {'type': 'string'},
                                   'country' : {'type': 'string'}
                                },
                   }

location_geo_schema = {'type': 'dict',
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
                   }