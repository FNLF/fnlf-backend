from _base import acl_item_schema

_schema = {'title': {'type': 'string',
                     'required': True,
                     'readonly': False
                     },
           'slug': {'type': 'string',
                    'required': True},
           'body': {'type': 'string',
                    'required': True},
           'space_key': {'type': 'string',
                       'required': True},
           'parent': {'type': 'objectid',
                      'default': None},
           'order': {'type': 'integer'},
           'ref': {'type': 'string'},
           'owner': {'type': 'integer',
                     'required': False,
                     'readonly': True}
           # 'acl': acl_item_schema
           }

definition = {
    'item_title': 'content',
    'datasource': {'source': 'content',
                   # 'projection': {'acl': 0} # Not for this?
                   },
    'additional_lookup': {
        'url': 'regex("[a-z0-9-]+")',
        'field': 'slug',
    },
    'extra_response_fields': ['key'],
    'versioning': True,
    'resource_methods': ['GET', 'POST'],
    'item_methods': ['GET', 'PATCH', 'DELETE'],
    'schema': _schema

}
