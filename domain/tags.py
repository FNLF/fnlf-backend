"""

    Tags
    ====
    
    Tagservice group->tag
    
    
"""

_schema = {
            'tag': {'type': 'string',
                   'required': True,
                   },
            'group': {'type': 'string',
                      'required': True},
           
            'freq': {'type': 'integer',
                     'required': False,
                     'readonly': True,
                     'default': 0},
            
            # Settings for user
            'related': {'type': 'list',
                        'default': []},
            }

definition = {
        'item_title': 'tags',
        'url': 'tags',
        'datasource': {'source': 'tags',
                       'default_sort': [('tag', 1), ('group', 1)],
                       },
        'extra_response_fields': ['tag'],
        'resource_methods': ['GET', 'POST'], #No post, only internal!!
        'item_methods': ['GET', 'PATCH'],
        'versioning': True,
        
        'additional_lookup': {
            'url': 'regex("[\w{1,20}]+")',
            'field': 'tag',
        },
        
        'schema': _schema,
}