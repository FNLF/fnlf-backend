"""

    license
    =======
    
    Should return an object with license information
    
    {
        "_id" : ObjectId("5360ad6712afba95dd35a527"),
        "id" : 9,
        "melwinId" : "F-C",
        "licenseName" : "C-lisens",
        "active" : true
    }

"""

_schema = {
            'id': {'type': 'string',
                   'required': True,
                 },
            'name': {'type': 'string',
                   },
            'active': {'type': 'boolean',
                       },
            
            'url': {'type': 'string', 'required': False},
            }

definition = {
        'item_title': 'licenses',
        #'item_url': 'clubs',
        'url': 'licenses',
        'description': 'Licenses with added snacks',
        
        'datasource': {'source': 'licenses',
                       'default_sort': [('id', 1)],
                       },
        
        'resource_methods': ['GET', 'POST'],
        'item_methods': ['GET', 'PATCH'],
        
        'versioning': True,
        
        'additional_lookup': {
            'url': 'regex("[\w{1}\-\w{1,5}]+")',
            'field': 'id',
        },
        
        'schema': _schema,
}