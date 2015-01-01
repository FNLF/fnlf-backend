"""

Avviksrapportering applikasjon

@note: workflow kan feks være readonly, så kan dette rutes via en egen (flask) ressurs for å sette den!

@todo: Observations need an initializing pre_insert/POST to init workflows! 
       Or rather a after with partc_internal since it's a readonly field

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
           'workflow': {'type': 'dict',
                        'readonly': True,
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