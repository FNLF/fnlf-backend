"""

    Melwin memberships
    ==================
    
    Connects the melwin code for membership with human readable description
    
    "_id" : ObjectId("54970947a01ed2381196c9f5"),
    "name" : "Familie Medlemsskap",
    "id" : "FAM"
    
"""

_schema = {
            'id': {'type': 'string',
                   'required': True,
                 },
            'name': {'type': 'string',
                   },
            }

definition = {
        'item_title': 'membership',
        #'item_url': 'clubs',
        'url': 'melwin/memberships',
        'description': 'Melwin passthrough',
        
        'datasource': {'source': 'melwin_membership',
                       'default_sort': [('id', 1)],
                       },
        
        'resource_methods': ['GET'],
        'item_methods': ['GET'],
        
        'versioning': False,
        
        'additional_lookup': {
            'url': 'regex("[\w{3}]+")',
            'field': 'id',
        },
        
        'schema': _schema,
}