"""
    Observation Components
    ======================
   
   @note: This is imported into onbservations
   
    
"""

_schema = {'what': {'type': 'string',
                    'required': True,
                    'unique': True,},
           'when': {'type': 'datetime'},
           'where': {'type': 'dict',
                     'schema': {'at': {'type': 'string',},
                                'altitude': {'type': 'integer'}
                                }
                     },
           'how': {'type': 'string'},
           'who': {'type': 'list',}, #List of id's
           
           # Flags a component according to the timeline
           'flags': {'type': 'dict',
                    'schema': {'root_cause': {'type': 'boolean'},
                               'cause': {'type': 'boolean'},
                               'consequence': {'type': 'boolean'},
                               'final_consequence': {'type': 'boolean'},
                               'barrier': {'type': 'boolean'},
                               'incident': {'type': 'boolean'},
                                 }
                          }, 
           'tags': {'type': 'list'},
           
           'related': {'type': 'list',
                       'schema': {'type': 'objectid',
                                  'data_relation': {
                                         'resource': 'observations/components',
                                         'field': '_id',
                                         'embeddable': True
                                         }
                                  },
                     },
           # Attributes tell us more about what happened at this component
           'attributes': {'type': 'dict',
                          'schema': {'wilfull': {'type': 'boolean'},
                                     'violation': {'type': 'boolean'},
                                     'injury': {'type': 'boolean'},
                                     'death': {'type': 'boolean'},
                                     'gear_failure': {'type': 'boolean'},
                                     'gear_malfunction': {'type': 'boolean'},
                                     'damage': {'type': 'boolean'}
                                     },
                          },
           
           'help': {'type': 'dict'},
           'sort': {'type': 'integer'},
           'active': {'type': 'boolean'},
           }

definition = {
        'item_title': 'observation_components',
        'url': 'observations/components',
        'datasource': {'source': 'observation_components',
                       },
        'versioning': True,
        
        'resource_methods': ['GET', 'POST'],
        'item_methods': ['GET', 'PATCH', 'PUT'],
        
        'schema': _schema
        
       }