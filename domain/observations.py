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
from _base import workflow_schema, comments_schema, watchers_schema, audit_schema, acl_schema
import observation_components

_schema = {'id': {'type': 'integer',
                  'required': False},
           'title': {'type': 'string'},
           'type': {'type': 'string',
                    'allowed': ['unsafe_act', 'near_miss', 'incident', 'accident']},
           'wilfull': {'type': 'boolean',
                       'default': False},
           'owner': {'type': 'integer', 'readonly': True}, # user_id this post/patch
           'reporter': {'type': 'integer', 'readonly': True}, # user_id initial reported by!
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
           'comments': comments_schema,
           'workflow': workflow_schema,
           'watchers': watchers_schema,
           'actions': {'type': 'dict'},
           'audit': audit_schema,
           'acl': acl_schema,
           
           
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
        #makes only user access those...
        #'auth_field': 'owner',
        
        'versioning': True,
        
        'resource_methods': ['GET', 'POST'],
        'item_methods': ['GET', 'PATCH'],
        
        'schema': _schema
        
       }