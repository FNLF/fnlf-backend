
Eve config
==========

See also [_template.py](_template.py)

Globals
-------


Locals
--------


**`url`** The endpoint URL.
If omitted the resource key of the DOMAIN dict will be used to build the URL. As an example, contacts would make the people resource available at /contacts (instead of /people). URL can be as complex as needed and can be nested relative to another API endpoint (you can have a /contacts endpoint and then a /contacts/overseas endpoint. Both are independent of each other and freely configurable). You can also use regexes to setup subresource-like endpoints. See Sub Resources.

**`allowed_filters`**             List of fields on which filtering is allowed. Can be set to [] (no filters allowed), or ['*'] (fields allowed on every field). Defaults to ['*']. Please note: If API scraping or DB DoS attacks are a concern, then globally disabling filters (see ALLOWED_FILTERS above) and then whitelisting valid ones at the local level is the way to go.

**`sorting`**                     True if sorting is enabled, False otherwise. Locally overrides SORTING.

**`pagination`**                  True if pagination is enabled, False otherwise. Locally overrides PAGINATION.

**`resource_methods`**            A list of HTTP methods supported at resource endpoint. Allowed values: GET, POST, DELETE. Locally overrides RESOURCE_METHODS. Please note: if you’re running version 0.0.5 or earlier use the now unsupported methods keyword instead.

**`public_methods`**              A list of HTTP methods supported at resource endpoint, open to public access even when Authentication and Authorization is enabled. Locally overrides PUBLIC_METHODS.

**`item_methods`**                A list of HTTP methods supported at item endpoint. Allowed values: GET, PATCH and DELETE. PATCH or, for clients not supporting PATCH, POST with the X-HTTP-Method-Override header tag. Locally overrides ITEM_METHODS.

**`public_item_methods`**         A list of HTTP methods supported at item endpoint, left open to public access when Authentication and Authorization is enabled. Locally overrides PUBLIC_ITEM_METHODS.

**`allowed_roles`**               A list of allowed roles for resource endpoint. See Authentication and Authorization for more information. Locally overrides ALLOWED_ROLES.

**`allowed_read_roles`**          A list of allowed roles for resource endpoint with GET and OPTIONS methods. See Authentication and Authorization for more information. Locally overrides ALLOWED_READ_ROLES.

**`allowed_write_roles`**         A list of allowed roles for resource endpoint with POST, PUT and DELETE. See Authentication and Authorization for more information. Locally overrides ALLOWED_WRITE_ROLES.

**`allowed_item_read_roles`**     A list of allowed roles for item endpoint with GET and OPTIONS methods. See Authentication and Authorization for more information. Locally overrides ALLOWED_ITEM_READ_ROLES.

**`allowed_item_write_roles`**    A list of allowed roles for item endpoint with PUT, PATH and DELETE methods. See Authentication and Authorization for more information. Locally overrides ALLOWED_ITEM_WRITE_ROLES.

**`allowed_item_roles`**          A list of allowed roles for item endpoint. See Authentication and Authorization for more information. Locally overrides ALLOWED_ITEM_ROLES.

**`cache_control`**               Value of the Cache-Control header field used when serving GET requests. Leave empty if you don’t want to include cache directives with API responses. Locally overrides CACHE_CONTROL.

**`cache_expires`**               Value (in seconds) of the Expires header field used when serving GET requests. If set to a non-zero value, the header will always be included, regardless of the setting of CACHE_CONTROL. Locally overrides CACHE_EXPIRES.

**`item_lookup`**                 True if item endpoint should be available, False otherwise. Locally overrides ITEM_LOOKUP.

**`item_lookup_field`**           Field used when looking up a resource item. Locally overrides ITEM_LOOKUP_FIELD.

**`item_url`**                    Rule used to construct item endpoint URL. Locally overrides ITEM_URL.

**`resource_title`**              Title used when building resource links (HATEOAS). Defaults to resource’s url.

**`item_title`**                  Title to be used when building item references, both in XML and JSON responses. Overrides ITEM_TITLE.

**`additional_lookup`**           Besides the standard item endpoint which defaults to /<resource>/<ID_FIELD_value>, you can optionally define a secondary, read-only, endpoint like /<resource>/<person_name>. You do so by defining a dictionary comprised of two items field and url. The former is the name of the field used for the lookup. If the field type (as defined in the resource schema) is a string, then you put a URL rule in url. If it is an integer, then you just omit url, as it is automatically handled. See the code snippet below for an usage example of this feature.

**`datasource {source,filter,projection,default_sort}`**                 Explicitly links API resources to database collections. See Advanced Datasource Patterns.

**`auth_field`**                  Enables User-Restricted Resource Access. When the feature is enabled, users can only read/update/delete resource items created by themselves. The keyword contains the actual name of the field used to store the id of the user who created the resource item. Locally overrides AUTH_FIELD.

**`allow_unknown`**               When True, this option will allow insertion of arbitrary, unknown fields to the endpoint. Use with caution. Locally overrides ALLOW_UNKNOWN. See Allowing the Unknown for more information. Defaults to False.

**`projection`**                  When True, this option enables the Projections feature. Locally overrides PROJECTION. Defaults to True.

**`embedding`**                   When True this option enables the Embedded Resource Serialization feature. Defaults to True.

**`extra_response_fields`**       Allows to configure a list of additional document fields that should be provided with every POST response. Normally only automatically handled fields (ID_FIELD, LAST_UPDATED, DATE_CREATED, ETAG) are included in response payloads. Overrides EXTRA_RESPONSE_FIELDS.

**`hateoas`**                     When False, this option disables HATEOAS for the resource. Defaults to True.

**`mongo_write_concern`**         A dictionary defining MongoDB write concern settings for the endpoint datasource. All standard write concern settings (w, wtimeout, j, fsync) are supported. Defaults to {'w': 1} which means ‘do regular acknowledged writes’ (this is also the Mongo default.) Please be aware that setting ‘w’ to a value of 2 or greater requires replication to be active or you will be getting 500 errors (the write will still happen; Mongo will just be unable to check that it’s being written to multiple servers.)

**`authentication`**              A class with the authorization logic for the endpoint. If not provided the eventual general purpose auth class (passed as application constructor argument) will be used. For details on authentication and authorization see Authentication and Authorization. Defaults to None,

**`embedded_fields`**             A list of fields for which Embedded Resource Serialization is enabled by default. For this feature to work properly fields in the list must be embeddable, and embedding must be active for the resource.

**`query_objectid_as_string`**    When enabled the Mongo parser will avoid automatically casting electable strings to ObjectIds. This can be useful in those rare occurrences where you have string fields in the database whose values can actually be casted to ObjectId values, but shouldn’t. Only effects queries (?where=). Defaults to False.

**`internal_resource`**           When True, this option makes the resource internal. No HTTP action can be performed on the endpoint, which is still accessible from the Eve data layer. See Internal Resources for more informations. Defaults to False.

**`schema`**                      A dict defining the actual data structure being handled by the resource. Enables data validation. See Schema Definition.

