"""
    1 => 'EL-UL Underkjent',
    2 => 'EL-UL/M',
    4 => 'EL-UL/T',
    6 => 'EF-FF',
    8 => 'AFF L1-7',
    10 => 'AFF-L8',
    11 => 'AFF-L8 Underkjent',
    12 => 'Treningshopp',
    13 => 'Demohopp',
    14 => 'Konkurransehopp',
    15 => 'AFF Instruktør',
    16 => 'Tandem Instruktør');
                                    
                                    
"""

from _base import workflow_schema, comments_schema, watchers_schema, audit_schema, acl_schema

_schema = {
           'id': {'type': 'string',
                    'required': True},
           'name': {'type': 'string',
                    'required': True},
           'description': {'type': 'string'},
           'verdicts': {'type': 'list',
                       'allowed': ['undekjent','godkjent']
                       },
           
           'licenses': {'type': 'list'}, 
           
           'tags': {'type': 'list'},
           
           'url': {'type': 'string', 
                   'required': False},
           
           'active': {'type': 'boolean',
                      },
                      
           'files': {'type': 'list', 'schema': {'type': 'media'}},
            
           'comments': comments_schema,
           'workflow': workflow_schema,
           'watchers': watchers_schema,
           'audit': audit_schema,
           'acl': acl_schema,
            }

definition = {
        'item_title': 'Jump types',
        'url': 'jumps/categories',
        'description': 'Jump types and variants',
        
        'datasource': {'source': 'jump_categories',
                       'default_sort': [('name', 1)],
                       },
        'additional_lookup': {
            'url': 'regex("[\w{2,5}]+")',
            'field': 'id',
        },
        
        'resource_methods': ['GET', 'POST'],
        'item_methods': ['GET', 'PATCH'],
        
        'versioning': True,
        
        
        'schema': _schema,
}
