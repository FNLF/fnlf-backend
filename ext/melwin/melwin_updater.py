# noinspection PyPackageRequirements
from flask import current_app as app
from eve.methods.post import post_internal
from eve.methods.patch import patch_internal
from eve.methods.put import put_internal
from eve.methods.get import get_internal, getitem_internal
from ext.app.responseless_decorators import async
import datetime, time
import pickle
from .melwin import Melwin
import threading
import os

def remove_none(obj):
  if isinstance(obj, (list, tuple, set)):
    return type(obj)(remove_none(x) for x in obj if x is not None)
  elif isinstance(obj, dict):
    return type(obj)((remove_none(k), remove_none(v))
      for k, v in obj.items() if k is not None and v is not None)
  else:
    return obj

# @track_time_spent('Melwin Update')
@async
def do_melwin_update(app):

    app.logger.info("[MELWIN] Updater started")
    use_pickle = False

    result = {'replaced': 0, 'created': 0, 'errors': 0, 'error_ids': []}

    try:

        with app.test_request_context('api/v1/melwin/users'):

            try:
                if not use_pickle:
                    raise FileNotFoundError

                with open("persons.p", "rb") as f:
                    persons = pickle.load(f)
                    app.logger.info("[MELWIN] Using local person pickle file")

            except FileNotFoundError:
                app.logger.info("[MELWIN] requesting data from Melwin")
                m = Melwin()
                persons = m.get_all()
                with open("persons.p", "wb") as f:
                    pickle.dump(persons, f)
            except:
                pass

            for key, user in persons.items():
                """"Iterate every person from Melwin"""

                try:
                    existing_user, _, _, status = getitem_internal(resource='melwin/users', **{'id': user['id']})
                    if not existing_user or status != 200:
                        existing_user = None
                except:
                    app.logger.info("[MELWIN] No existing user %i" % user['id'])
                    existing_user = None


                if existing_user is None \
                        or user['location'].get('street', 'a') != existing_user['location'].get('street', 'b') \
                        or user['location'].get('zip', 'a') != existing_user['location'].get('zip', 'b') \
                        or user['location'].get('country', 'a') != existing_user['location'].get('country', 'b') \
                        or user['location'].get('city', 'a') != existing_user['location'].get('city', 'b'):

                    app.logger.info("[MELWIN] Geocoding %i" % user['id'])
                    try:
                        if user['location'].get('city', None) is not None:
                            geo = m.get_geo(user['location'].get('street', ''),
                                            user['location'].get('city', ''),
                                            user['location'].get('zip', ''),
                                            user['location'].get('country', ''))
                            if geo != None:
                                user['location'].update(
                                    {'geo': {"type": "Point", "coordinates": [geo.latitude, geo.longitude]}})
                                user['location'].update({'geo_type': geo.raw['type']})
                                user['location'].update({'geo_class': geo.raw['class']})
                                user['location'].update({'geo_importance': float(geo.raw['importance'])})
                                user['location'].update({'geo_place_id': int(geo.raw['place_id'])})
                        else:
                            app.logger.error("[MELWIN] Geocoding for user %i failed NO CITY" % user['id'])
                    except:
                        app.logger.error("[MELWIN] Geocoding for user %i failed" % user['id'])


                if not 'fullname' in user:
                    try:
                        user.update({'fullname': "%s %s" % (user['firstname'], user['lastname'])})
                    except Exception as e:
                        app.logger.info("[MELWIN] error", e)
                        app.logger.error("[MELWIN] User: ", user)
                        user.update({'fullname': "%s %s" % (user.get('firstname', ''), user.get('lastname', ''))})


                lookup = dict({})


                try:
                    lookup = dict({'id': key})
                    r, _, _, status = put_internal(resource='melwin/users', payload=remove_none(user), concurrency_check=False,
                                                   skip_validation=False, **lookup)

                    if status == 200:
                        result['replaced'] += 1
                    elif status == 201:
                        result['created'] += 1
                    else:
                        app.logger.info("[MELWIN] Status %i for put_internal user %i" % (status, user['id']))
                        app.logger.info("[MELWIN] {}".format(r))

                except KeyError:
                    r, _, _, status, header = post_internal(resource='melwin/users', payl=remove_none(user), skip_validation=True)

                    if status == 201:
                        result['created'] += 1
                    else:
                        app.logger.error("[MELWIN] Error for user %i" % user['id'])
                        app.logger.error("[MELWIN] {}".format(r))

                except:
                    result['errors'] += 1
                    result['error_ids'].append(user['id'])
                    app.logger.error("[MELWIN] Error for user %i" % user['id'])
                    app.logger.error("[MELWIN] {}".format(r))


    except:
        """Major error, warn"""
        from ext.notifications.sms import Sms
        app.logger.exception("[MELWIN] Error updating users from Melwin")
        sms = Sms()
        sms.send(mobile=sms.get_warn_sms(), message="[%s] %s" % (500, "Error updating users from Melwin"))
        result['errors'] += 1

    app.logger.info("[MELWIN] Updater finished (created: %i updated: %i errors: %i)" %
                    (result['created'], result['replaced'], result['errors']))
    # Restart in one day!
    threading.Timer(get_timer(), do_melwin_update, [app]).start()


def get_timer():
    """Return seconds until we run
    """
    # For testing
    #return 3600*3

    # Tomorrows date + time!
    tomorrow = datetime.datetime.combine((datetime.date.today() + datetime.timedelta(days=1)), datetime.time(4, 0))
    # Unix timestamp, just calculate seconds until
    seconds = int(time.mktime(tomorrow.timetuple()) - time.time())

    return seconds

def touch(path):
    with open(path, 'a'):
        os.utime(path, None)

def check(path):
    return os.path.isfile(path)

def start(app):
    """Schedule after startup for first run
    @todo: smart schedule "04 tomorrow"
    """
    pid = 'melwin_updater.pid'
    if check(pid):
        return
    else:
        touch(pid)
        s = get_timer()
        threading.Timer(get_timer(), do_melwin_update, [app]).start()
