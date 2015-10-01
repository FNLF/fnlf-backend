"""
    Custom methods for Eve
    ~~~~~~~~~~~~~~~~~~~~~~
    
    The custom_eve class is a monkeypatch for our custom needs

"""
from eve import Eve

#Eve.methods.common.oplog_push = oplog_push

class Custom_eve(Eve):
    
    
    def _init_oplog(self):
        """ If enabled, configures the OPLOG endpoint.

        .. versionadded:: 0.5
        """
        name, endpoint, audit = (
            self.config['OPLOG_NAME'],
            self.config['OPLOG_ENDPOINT'],
            self.config['OPLOG_AUDIT']
        )

        if endpoint:
            settings = self.config['DOMAIN'].setdefault(name, {})

            settings.setdefault('url', endpoint)
            settings.setdefault('datasource', {'source': name})

            # this endpoint is always read-only
            settings['resource_methods'] = ['GET']
            settings['item_methods'] = ['GET']

            # schema is also fixed. it is needed because otherwise we
            # would end up exposing the AUTH_FIELD when User-Restricted-
            # Resource-Access is enabled.
            settings['schema'] = {
                'r': {},
                'o': {},
                'i': {},
            }
            
            if self.auth:
                settings['schema'].update(
                    {
                        'u': {},
                    }
                )    
            
            if audit:
                settings['schema'].update(
                    {
                        'ip': {},
                        'c': {}
                    }
                )
                
def oplog_push(resource, updates, op, id=None):
    """ Pushes an edit operation to the oplog if included in OPLOG_METHODS. To
    save on storage space (at least on MongoDB) field names are shortened:

        'r' = resource endpoint,
        'o' = operation performed,
        'i' = unique id of the document involved,
        'pi' = client IP,
        'c' = changes

    config.LAST_UPDATED, config.LAST_CREATED and AUTH_FIELD are not being
    shortened to allow for standard endpoint behavior (so clients can
    query the endpoint with If-Modified-Since queries, and User-Restricted-
    Resource-Access will keep working on the oplog endpoint too).

    :param resource: name of the resource involved.
    :param updates: updates performed with the edit operation.
    :param op: operation performed. Can be 'POST', 'PUT', 'PATCH', 'DELETE'.
    :param id: unique id of the document.

    .. versionadded:: 0.5
    """
    if not config.OPLOG or op not in config.OPLOG_METHODS:
        return

    if updates is None:
        updates = {}

    if not isinstance(updates, list):
        updates = [updates]

    entries = []
    for update in updates:
        entry = {
            'r': config.URLS[resource],
            'o': op,
            'i': update[config.ID_FIELD] if config.ID_FIELD in update else id,
        }
        
        if app.auth:
            entry.update({'u': app.auth.get_user_id()})
                
        if config.LAST_UPDATED in update:
            last_update = update[config.LAST_UPDATED]
        else:
            last_update = datetime.utcnow().replace(microsecond=0)
        entry[config.LAST_UPDATED] = entry[config.DATE_CREATED] = last_update
        if config.OPLOG_AUDIT:

            # TODO this needs further investigation. See:
            # http://esd.io/blog/flask-apps-heroku-real-ip-spoofing.html;
            # https://stackoverflow.com/questions/22868900/how-do-i-safely-get-the-users-real-ip-address-in-flask-using-mod-wsgi
            entry['ip'] = request.remote_addr

            if op in ('PATCH', 'PUT', 'DELETE'):
                # these fields are already contained in 'entry'.
                del(update[config.LAST_UPDATED])
                # legacy documents (v0.4 or less) could be missing the etag
                # field
                if config.ETAG in update:
                    del(update[config.ETAG])
                entry['c'] = update
            else:
                pass

        resolve_user_restricted_access(entry, config.OPLOG_NAME)

        entries.append(entry)

    if entries:
        app.data.insert(config.OPLOG_NAME, entries)
