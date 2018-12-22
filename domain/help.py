from _base import acl_item_schema

_schema = {'key': {'type': 'string',
                   'required': True,
                   'readonly': False,
                   'unique': True
                   },
           'title': {'type': 'string',
                     'required': True},
           'body': {'type': 'string'},
           'owner': {'type': 'integer'},
           'acl': acl_item_schema
           }

definition = {
    'item_title': 'help',
    'datasource': {'source': 'help',
                   # 'projection': {'acl': 0} # Not for this?
                   },
    # Make a counter so we can have a lookup for #455
    'additional_lookup': {
        'url': 'regex("[a-z-]+")',
        'field': 'key',
    },
    'extra_response_fields': ['key'],
    'versioning': False,
    'resource_methods': ['GET', 'POST'],
    'item_methods': ['GET', 'PATCH', 'DELETE'],
    'schema': _schema

}
