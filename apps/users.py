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
           
            # Burde ikke, men vi trenger en bedre løsning enn pin kode
            'password': {'type': 'string',
                         'required': False
                         },
           
            'avatar': {'type': 'media',},
            
            # Settings for user
            'config': {'type': 'dict',},
            
            # 
            'custom': {'type': 'dict',},
            
            # Extra info, worktype, material status, interests...
            'info': {'type': 'dict',},
            
            # Generated information, better as a internal one?
            'statistics': {'type': 'dict',},
            
            # Acl list of groups and roles
            'acl': {'type': 'dict',},
            
            # Should these be here or seperate?
            'notes': {'type': 'dict',},
            'flags': {'type': 'dict',},
            'verdicts': {'type': 'dict',},
            
            }

definition = {
        'item_title': 'users',
        #'item_url': 'clubs',
        
        'datasource': {'source': 'users',
                       'default_sort': [('id', 1)],
                       },
        
        'resource_methods': ['GET', 'POST', 'DELETE'],
        'item_methods': ['GET', 'PATCH', 'PUT'],
        
        'versioning': True,
        
        'additional_lookup': {
            'url': 'regex("[\d{1,6}]+")',
            'field': 'id',
        },
        
        'schema': _schema,
}
