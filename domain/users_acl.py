"""

    User ACL
    ========
    
"""
_schema = {
            # Medlemsnummer
            'id': {'type': 'integer',
                   'readonly': True
                   },
           
            'acl': {'type': 'dict',
                    'readonly': False,
                    'schema': {'groups': {'type': 'list', 'default': [],'schema': {'type': 'objectid'}},
                               'roles': {'type': 'list', 'default': [],'schema': {'type': 'objectid'}},
                               },
                    }
                    
            
            
            }
           
definition = {
        'item_title': 'users/acl',
        'url': 'users/acl',
        'datasource': {'source': 'users',
                       'default_sort': [('id', 1)],
                       },
        'extra_response_fields': ['id'],
        'resource_methods': ['GET'], #No post, only internal!!
        'item_methods': ['GET'],
        #'auth_field': 'id', #This will limit only users who has
    'allowed_write_roles': ['superadmin'],
    'allowed_item_write_roles': ['superadmin'],
        'additional_lookup': {
            'url': 'regex("[\d{1,6}]+")',
            'field': 'id',
        },
        
        'schema': _schema,
}
