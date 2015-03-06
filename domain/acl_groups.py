"""

    Acl groups
    ==========
    
    
"""

_schema = {'name': {'type': 'string',
                    'required': 'true',
                    'unique': True}, 
           'description': {'type': 'string'},
           'ref': {'type': 'string',
                   'unique': True
                   },
           
            }

definition = {
        'item_title': 'acl/groups',
        'url': 'acl/groups',
        'datasource': {'source': 'acl_groups',
                       },
        'internal_resource': False,
        'concurrency_check': True,

        'resource_methods': ['GET', 'POST'],
        'item_methods': ['GET','PATCH'],
        
        'versioning': False,
        
        #Make lookup on ref - club id!
        'additional_lookup': {
            'url': 'regex("[\d{3}\-\w{1}]+")',
            'field': 'ref',
        },
        
        'schema': _schema,
}