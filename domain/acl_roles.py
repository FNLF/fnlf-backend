"""

    Acl roles
    =========
    
    
"""

_schema = {'name': {'type': 'string',
                    'required': 'true',
                    }, 
           'description': {'type': 'string'},
           'ref': {'type': 'string',
                   'unique': True},
           'group': {
                 'type': 'objectid',
                 'required': True,
                 'data_relation': {
                     'resource': 'acl/groups',
                     'field': '_id',
                     'embeddable': True,
                    },
                },
           
            }

definition = {
        'item_title': 'acl/roles',
        'url': 'acl/roles',
        'datasource': {'source': 'acl_roles',
                       },
        'internal_resource': False,
        'concurrency_check': True,

        'resource_methods': ['GET', 'POST'],
        'item_methods': ['GET','PATCH'],
        
        'versioning': False,
        
        'schema': _schema,
}