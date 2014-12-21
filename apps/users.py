"""

    User
    ====
    
    A simple user collection as a cache before requests goes to Melwin.
    
    Do NOT contain any personal information
    
"""

_schema = {
            # Medlemsnummer
            'id': {'type': 'integer',
                   'required': True,
                   },
           
            'avatar': {'type': 'media',},
            
            # Settings for user
            'config': {'type': 'dict',},
            
            # 
            'custom': {'type': 'dict',},
            
            # Extra info, worktype, material status, interests...
            'info': {'type': 'dict',},
            
            # Generated information, better as an internal one?
            'statistics': {'type': 'dict',},
            
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
        
        'resource_methods': ['GET'], #No post, only internal!!
        'item_methods': ['GET', 'PATCH'],
        
        'versioning': False,
        
        'additional_lookup': {
            'url': 'regex("[\d{1,6}]+")',
            'field': 'id',
        },
        
        'schema': _schema,
}
