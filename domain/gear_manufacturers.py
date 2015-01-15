"""

    Gear Manufeacturers
    ===================
    
"""

from _base import workflow_schema, comments_schema, watchers_schema, audit_schema, acl_schema

_schema = {
           'name': {'type': 'string',
                    'required': True},
           
           'url': {'type': 'string', 
                   'required': False},
           
            'contact': {'type': 'dict', #Or list
                        'schema': {'phone' : {'type': 'string'},
                                   'email' : {'type': 'string'},
                                   'fax' : {'type': 'string'},
                                   }
                        },
            'contacts': {'type': 'list',
                         'default': [],
                         'schema': {'name': 'string',
                                    'phone': 'string',
                                    'email': 'string',
                                    'description': 'string',
                                    'position': 'string'}
                         },
           
            'location' : {'type': 'dict',
                          'schema': {
                                    'street': {'type': 'string'},
                                    'zip' : {'type': 'string'},
                                    'city' : {'type': 'string'},
                                    'state' : {'type': 'string'},
                                    'country' : {'type': 'string'},
                                    'geo': {'type': 'point'},
                                    'geo_class': {'type': 'string'},
                                    'geo_importance': {'type': 'float'},
                                    'geo_place_id': {'type': 'integer'},
                                    'geo_type': {'type': 'string'},
                                    },
                          },
           
           'tags': {'type': 'list'},
 
           'active': {'type': 'boolean',
                      },
                      
           'files': {'type': 'list', 'schema': {'type': 'media'}},
            
           'comments': comments_schema,
           'workflow': workflow_schema,
           'watchers': watchers_schema,
           'audit': audit_schema,
           'acl': acl_schema,
            }

definition = {
        'item_title': 'Gear Manufacturers',
        'url': 'gear/manufacturers',
        'description': 'Gear Manufacturers',
        
        'datasource': {'source': 'gear_manufacturers',
                       'default_sort': [('name', 1)],
                       },
        
        'resource_methods': ['GET', 'POST'],
        'item_methods': ['GET', 'PATCH', 'PUT'],
        
        'versioning': True,
        
        
        'schema': _schema,
}
