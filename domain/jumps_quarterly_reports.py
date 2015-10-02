from _base import acl_item_schema

_schema = {'club': {'type': 'string',
                    'required': True},
           'year': {'type': 'integer',
                    'required': True},
           'q': {'type': 'integer',
                    'required': True},
           'ulg': {'type': 'integer',
                    'required': True},
           'ulu': {'type': 'integer',
                    'required': True},
           'ulmg': {'type': 'integer',
                    'required': True},
           'ulmu': {'type': 'integer',
                    'required': True},
           'ultg': {'type': 'integer',
                    'required': True},
           'ultu': {'type': 'integer',
                    'required': True},
           'ffg': {'type': 'integer',
                    'required': True},
           'ffu': {'type': 'integer',
                    'required': True},
           'affg': {'type': 'integer',
                    'required': True},
           'affu': {'type': 'integer',
                    'required': True},
           'demo': {'type': 'integer',
                    'required': True},
           'konk': {'type': 'integer',
                    'required': True},
           'tandem': {'type': 'integer',
                    'required': True},
           'tren': {'type': 'integer',
                    'required': True},
           'acl': acl_item_schema,
            }

definition = {
        'item_title': 'Jump quarterly reports',
        'url': 'jumps/quarterly/reports',
        'description': 'Jump numbers quarterly',
        
        'datasource': {'source': 'jumps_quarterly_reports',
                       'default_sort': [('year', 1)],
                       },
        #'additional_lookup': {
        #    'url': 'regex("[\w{2,5}]+")',
        #    'field': 'year',
        #},
        
        'resource_methods': ['GET', 'POST'],
        'item_methods': ['GET'],
        
        'versioning': False,
        
        
        'schema': _schema,
}