"""

    Users Auth
    ==========
    
    Internal 
    
    Do NOT contain any personal information
    
"""

_schema = { # Medlemsnummer
            'id': {'type': 'integer',
                   'required': True,
                   },
           
            # Acl list of groups and roles
            'acl': {'type': 'dict',},
            
            'auth': {'type': 'dict',
                     'schema': {'token': {'type': 'string'},
                                'valid': {'type': 'datetime'},
                                }
                     },
           
            'user': {
                 'type': 'objectid',
                 'data_relation': {
                     'resource': 'users',
                     'field': '_id',
                     'embeddable': True,
                    },
                },
            
            }

definition = {
        'item_title': 'users_auth',
        
        'internal_resource': True,
        'concurrency_check': False,

        'datasource': {'source': 'users_auth',
                       'default_sort': [('id', 1)],
                       },
        
        'resource_methods': ['GET', 'POST'],
        'item_methods': ['GET','PATCH'],
        
        'versioning': False,
        
        'additional_lookup': {
            'url': 'regex("[\d{1,6}]+")',
            'field': 'id',
        },
        
        'schema': _schema,
}