"""
    Observation Components
    ======================
   
   @note: This is imported into onbservations
   
    
"""

_schema = {'what': {'type': 'string',
                    'required': True},
           'when': {'type': 'datetime'},
           'where': {'type': 'dict',
                     'schema': {'at': {'type': 'string'},
                                'altitude': {'type': 'integer'}
                                }},
           'how': {'type': 'string'},
           'who': {'type': 'list',}, #List of id's
           'definition': {'type': 'dict'},
           'labels': {'type': 'list'},
           'freetext': {'type': 'string'},
           'files': {'type': 'list', 
                     'schema': {'type': 'media'}
                     },
           'related': {'type': 'list'},
           }


definition = {
        'item_title': 'observation_components',
        'datasource': {'source': 'observation_components',
                       },
        'versioning': True,
        
        'resource_methods': ['GET', 'POST'],
        'item_methods': ['GET', 'PATCH', 'PUT'],
        
        'schema': _schema
        
       }