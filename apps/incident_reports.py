"""

Avviksrapportering applikasjon

"""

_schema = {'anomalyType': {'type': 'dict',
                           'required': True},
           
           'id': {'type': 'integer',
                  'required': True},
           
           'involvedPersons': {'type': 'dict',
                               'required': True},
           'incidents': {'type': 'dict',
                         'required': True},
           'location': {'type': 'dict',
                        'required': True},
           'club': {'type': 'dict',
                    'required': True},
           'jumpleaderComment': {'type': 'string',
                                 'required': False
                                 },
           }

definition = {
        'item_title': 'avvik',
        'datasource': {'source': 'anomalies', },
        
        # Make a counter so we can have a lookup for #455
        'additional_lookup': {
            'url': 'regex("[\d{1,9}]+")',
            'field': 'id',
        },
        
        'versioning': True,
        
        'resource_methods': ['GET', 'POST'],
        'item_methods': ['GET', 'PATCH', 'PUT'],
        
        'schema': _schema
        
       }