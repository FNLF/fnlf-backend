"""

    User
    ====
    
    User collection to hold information not in Melwin
    
    
"""

_schema = {
            # Medlemsnummer
            'id': {'type': 'integer',
                   'required': True,
                   'readonly': True
                   },
           
            'avatar': {'type': 'media',},
            
            # Settings for user
            'config': {'type': 'dict',},
            
            # 
            'custom': {'type': 'dict',},
            
            # Extra info, worktype, material status, interests...
            'info': {'type': 'dict',},
            
            # Generated information, better as an internal one?
            'statistics': {'type': 'dict',
                           'readonly': True},
            
            # Should these be here or seperate?
            #'notes': {'type': 'dict',},
            #'flags': {'type': 'dict',},
            #'verdicts': {'type': 'dict',},
            
            }

definition = {
        'item_title': 'users',
        'url': 'users',
        'datasource': {'source': 'users',
                       'default_sort': [('id', 1)],
                       },
        'extra_response_fields': ['id'],
        'resource_methods': ['GET', 'POST'], #No post, only internal!!
        'item_methods': ['GET', 'PATCH', 'PUT'],
        'auth_field': 'id', #This will limit only users who has
        
        'versioning': True,
        
        'additional_lookup': {
            'url': 'regex("[\d{1,6}]+")',
            'field': 'id',
        },
        
        'schema': _schema,
}
