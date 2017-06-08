"""

    User
    ====
    
    User collection to hold information not in Melwin
    
    
"""

_schema = {
    # Medlemsnummer
    'id': {'type': 'integer',
           'required': True,
           'readonly': True
           },

    'avatar': {'type': 'media', },

    # Settings for user
    'settings': {'type': 'dict',
                 'default': {}},

    #
    'custom': {'type': 'dict', },

    # Extra info, worktype, material status, interests...
    'info': {'type': 'dict', },

    # Generated information, better as an internal one?
    'statistics': {'type': 'dict',
                   'readonly': True},

    # Should these be here or seperate?
    # 'notes': {'type': 'dict',},
    # 'flags': {'type': 'dict',},
    # 'verdicts': {'type': 'dict',},

    'acl': {'type': 'dict',
            'readonly': True,
            'schema': {'groups': {'type': 'list', 'default': [], 'schema': {'type': 'objectid'}},
                       'roles': {'type': 'list', 'default': [], 'schema': {'type': 'objectid'}},
                       },
            'default': {'groups': [], 'roles': []}
            },

}

definition = {
    'item_title': 'users',
    #'internal_resource': True,
    'datasource': {'source': 'users',
                   'default_sort': [('id', 1)],
                   },
    'extra_response_fields': ['id'],
    'resource_methods': ['POST', 'GET'],  # No post, only internal!!
    'item_methods': ['GET', 'PATCH'],
    'auth_field': 'id',  # This will limit only users who has
    'versioning': True,

    'additional_lookup': {
        'url': 'regex("[\d{1,6}]+")',
        'field': 'id',
    },

    'schema': _schema,
}
