"""

    Observations
    ============
    
    @note: workflow kan feks være readonly, så kan dette rutes via en egen (flask) ressurs for å sette den!

    @todo: Observations need an initializing pre_insert/POST to init workflows! 
           Or rather a after with partc_internal since it's a readonly field
    @todo: Add autogenerating id for observation in pre hook
    @todo: Add workflow by default in pre hook
    @todo: add schema for organisation or club + location
"""

import observation_components

_schema = {'id': {'type': 'integer',
                  'required': True},
           'title': {'type': 'string'},
           'type': {'type': 'dict'},
           'owner': {'type': 'integer'}, # user_id this post/patch
           'when': {'type': 'datetime'},
           'involved': {'type': 'list'},
           'organisation': {'type': 'dict'},
           'rating': {'type': 'dict',
                      'schema': {'actual': {'type': 'integer'},
                                 'potential': {'type': 'integer'},
                                 'user': {'type': 'float', 
                                          'readonly': True},
                                 }
                      },
           'weather': {'type': 'dict',
                       'schema': {'auto': {'type': 'dict'},
                                  'manual': {'type': 'dict'},
                                  }
                       },
           
           'components': {'type': 'list',
                          'schema': observation_components._schema,
                          #'schema': {''} # Possibly the same as components
                          },
           
           'files': {'type': 'list', 
                     'schema': {'type': 'media'}
                     },
           'freetext': {'type': 'dict',
                        'schema': {'jumper': {'type': 'string'},
                                   'hl': {'type': 'string'},
                                   'hi': {'type': 'string'},
                                   'fs': {'type': 'string'},
                                   'su': {'type': 'string'},
                                   }
                        },
           
           'related': {'type': 'list'},
           'labels': {'type': 'list'},
           'comments': {'type': 'list',
                        'schema': {'date': 'datetime',
                                   'user': 'integer',
                                   'comment': 'string'
                                   }
                        },
           'workflow': {'type': 'dict', 'readonly': True},
           'watchers': {'type': 'list', 'readonly': True},
           'actions': {'type': 'dict'},
           'audit': {'type': 'list'},
           'acl': {'type': 'dict'},
           
           
           }

definition = {
        'item_title': 'observations',
        'datasource': {'source': 'observations',
                       'projection': {'files': 0, 'acl': 0} },
        
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