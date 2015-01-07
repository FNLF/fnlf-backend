"""

    Gear
    =====
    
    A generic gear schema, can basically hold anything
    
"""

from _base import workflow_schema, comments_schema, watchers_schema, audit_schema, acl_schema

_schema = {
           'name': {'type': 'string',
                    'required': True},
           'manufacturer': {
                            'type': 'objectid',
                            'data_relation': {
                                              'resource': 'gear/manufacturers',
                                              'field': '_id',
                                              'embeddable': True
                                              }
                     },
           'category': {'type': 'string',
                     #'allowed': ['aad', 'main', 'reserve', 'harness', 'altimeter', 'audible']
                     },
           
           'models': {'type': 'dict',
                      'schema': {'attr': {'type': 'dict'}, #key=>value list, you define what you want!
                                 'variants': {'type': 'list'}},
                     },
           'url': {'type': 'string', 'required': False},
           
           'tags': {'type': 'list'},
                      
           'files': {'type': 'list', 'schema': {'type': 'media'}},
           
           # More specialized stuff to come, as service orders, 
           'active': {'type': 'boolean',
                      'default': True,
                      'required': True},
           'airworthy': {'type': 'boolean',
                         'default': True,
                         #'required': True
                         },
            
           'comments': comments_schema,
           'workflow': workflow_schema,
           'watchers': watchers_schema,
           'audit': audit_schema,
           'acl': acl_schema,
            }

definition = {
        'item_title': 'Generic gear',
        'url': 'gear',
        'description': 'Generic gear collection',
        
        'datasource': {'source': 'gear',
                       'default_sort': [('name', 1)],
                       },
        
        'resource_methods': ['GET', 'POST'],
        'item_methods': ['GET', 'PATCH'],
        
        'versioning': True,
        
        
        'schema': _schema,
}
