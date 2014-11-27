"""

    Clubs
    =====
    
    Clubs from Melwin with added information
    
"""

_schema = {
            'id': {'type': 'string',
                   'required': True,
                 },
            'name': {'type': 'string',
                   },
            'active': {'type': 'boolean',
                       },
            'org': {'type': 'string',
                    },
            'locations': {'type': 'dict'}, #Should be refs or embedded locations??
            'planes': {'type': 'dict'}, #Should be refs or embedded planes??
            'roles' : {'type': 'dict'}, #Should be refs or embedded roles
            'ot': {'type': 'integer',
                   'required': True,
                   'allowed': [1,2]},
            'ci': {'type': 'integer', 'required': False}, #Embedded or??
            'logo': {'type': 'media', 'required': False},
            'url': {'type': 'string', 'required': False},
            }

definition = {
        'item_title': 'club',
        #'item_url': 'clubs',
        
        'datasource': {'source': 'clubs',
                       'default_sort': [('id', 1)],
                       },
        
        'resource_methods': ['GET', 'POST', 'DELETE'],
        'item_methods': ['GET', 'PATCH', 'PUT'],
        
        'versioning': True,
        
        #Make lookup on club id from melwin
        'additional_lookup': {
            'url': 'regex("[\d{3}\-\w{1}]+")',
            'field': 'id',
        },
        
        'schema': _schema,
}




