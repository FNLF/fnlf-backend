"""

    Melwin Clubs
    ============
    
    Clubs from Melwin
    
"""

_schema = {
            'id': {'type': 'string',
                   'required': True,
                 },
            'name': {'type': 'string',
                   },
            }

definition = {
        'item_title': 'club',
        'url': 'melwin/clubs',
        'description': 'Melwin passthrough',
        
        'datasource': {'source': 'melwin_clubs',
                       'default_sort': [('id', 1)],
                       },
        
        'resource_methods': ['GET'],
        'item_methods': ['GET'],
        
        'versioning': False,
        
        #Make lookup on club id from melwin
        'additional_lookup': {
            'url': 'regex("[\d{3}\-\w{1}]+")',
            'field': 'id',
        },
        
        'schema': _schema,
}




