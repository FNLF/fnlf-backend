"""

    Dev
    ~~~
    
    This is just a container for misc testing
    
    Example:
        During development of a frontend application before you know what you want in the database
        Since you do not know the schema, you have a fully custom dictionary in payload
        The only required field is the app field to keep it a bit tidy ;)

"""

_schema = {
            'app': {
                   'type': 'string',
                   'required': True,
                   },
            'payload': {
                      'type': 'dict',
                      'required': True,
                      },

                
            }

definition = {
        'item_title': 'dev',
        'versioning': False,
        
        # Full on!
        'resource_methods': ['GET', 'POST', 'DELETE'],
        'item_methods': ['GET', 'PATCH', 'PUT', 'DELETE'],
        # Add schema
        'schema': _schema,
}