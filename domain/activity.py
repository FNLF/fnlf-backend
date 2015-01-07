"""

    Activity
    ========
    
    Simple activity logger
    
"""

_schema = {
           'resource': {'type': 'string',
                        'required': True,
                        },
           'user': {'type': 'integer',
                  'required': False
                  },
           'action': {'type': 'string',
                 #'allowed': 
                 #['created', 'deleted', 'edited', 'replaced', # Rest verbs
                 #'commented', # Comments
                 #'approved', 'rejected', 'withdrew', 'closed', 'reopened', # Workflows
                 #'logged_in', 'logged_out'] # user actions
                    },
           'ref': {'type': 'string',
                   },
           'date': {'type': 'datetime',
                    'required': True
                    }
            }

definition = {
        'item_title': 'activity',
        'url': 'activity',
        'description': 'Activity logger',
        
        'datasource': {'source': 'activity',
                       'default_sort': [('d', 1)],
                       },
        
        'resource_methods': ['GET', 'POST'],
        'item_methods': ['GET'],
        
        'versioning': False,
        
        'schema': _schema,
}