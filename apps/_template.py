"""

    Template for definitions
    ========================
    
    @summary: A simple template for definitions, copy paste 
    
    @see:     Confluence Eve help url
    @todo:    Add all config options
    
"""

_schema = {
            '': {'type': 'string',
                 'required': True,
                 },
           
            '': {'type': 'dict',
                 'required': True,
                 },
                
            }

definition = {
        
        'item_title': 'Your Title',
        'versioning': False,
        
        # Full on!
        'resource_methods': ['GET', 'POST', 'DELETE'],
        'item_methods': ['GET', 'PATCH', 'PUT', 'DELETE'],
        
        # Add schema
        'schema': _schema,
}