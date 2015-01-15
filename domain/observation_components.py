"""
    Observation Components
    ======================
   
   @note: This is imported into onbservations
   
    
"""

_schema = {'what': {'type': 'string',
                    'required': True},
           'when': {'type': 'datetime'},
           'where': {'type': 'dict',
                     'schema': {'at': {'type': 'string', 
                                       'allowed': ['pakkeområde', 'pakking', 'innlastingsområde', 'publikumsområde', 'innlastning', 'flyet', 'flyet (ned)', \
                                                   'utstabling', 'exit', 'frittfall', 'seperasjon', 'wave-off', 'skjermåpning', 'innflyging', 'finale', \
                                                   'landing', 'landingsområdet', 'fjellet', 'vannet (ute)', 'treet (ute)', 'skogen (ute)', \
                                                   'jordet (ute)', 'tettbebyggelse (ute)','annet'],
                                       },
                                #retur fra landingsområdet
                                'altitude': {'type': 'integer'}
                                }
                     },
           'how': {'type': 'string'},
           'who': {'type': 'list',}, #List of id's
           
           'freetext': {'type': 'string'},
           
           'flags': {'type': 'dict',
                    'schema': {'root_cause': {'type': 'boolean'},
                               'final_consequence': {'type': 'boolean'},
                               'barrier': {'type': 'boolean'},
                               'incident': {'type': 'boolean'},
                               'wilfull': {'type': 'boolean'},
                               'violation': {'type': 'boolean'}
                                 }
                          }, 
           'tags': {'type': 'list'},
           
           'files': {'type': 'list', 
                     'schema': {'type': 'media'}
                     },
           
           'related': {'type': 'list',
                       'schema': {'type': 'objectid',
                                  'data_relation': {
                                         'resource': 'observations/components',
                                         'field': '_id',
                                         'embeddable': True
                                         }
                                  },
                     },
           'attributes': {'type': 'dict',
                          'schema': {'injury': {'type': 'boolean'},
                                     'death': {'type': 'boolean'},
                                     'gear_failure': {'type': 'boolean'},
                                     'gear_malfunction': {'type': 'boolean'},
                                     'damage': {'type': 'boolean'}
                                     },
                          }
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