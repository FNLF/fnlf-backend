"""

    Melwin licenses
    ===============
    
    Should return an object with license information
    

"""

_schema = {
            'id': {'type': 'string',
                   'required': True,
                 },
            'name': {'type': 'string',
                   },
            }

definition = {
        'item_title': 'licenses',
        #'item_url': 'clubs',
        'url': 'melwin/licenses',
        'description': 'Melwin passthrough',
        
        'datasource': {'source': 'licenses',
                       'default_sort': [('id', 1)],
                       },
        
        'resource_methods': ['GET'],
        'item_methods': ['GET'],
        
        'versioning': False,
        
        'additional_lookup': {
            'url': 'regex("[\w{1}\-\w{1,5}]+")',
            'field': 'id',
        },
        
        'schema': _schema,
}