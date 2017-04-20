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

                if not 'fullname' in user:
                    user.update({'fullname': "%s %s" % (user['firstname'], user['lastname'])})

                lookup = dict({})

                try:
                    lookup = dict({'id': key})
                    r, _, _, status = put_internal(resource='melwin/users', payload=user, concurrency_check=False,
                                                   skip_validation=False, **lookup)

                    if status == 200:
                        result['replaced'] += 1
                    elif status == 201:
                        result['created'] += 1
                    else:
                        app.logger.info("[MELWIN] Status %i for put_internal" % status)

                except KeyError:
                    r, _, _, status, header = post_internal(resource='melwin/users', payl=user, skip_validation=True)

                    if status == 201:
                        result['created'] += 1

                except:
                    result['errors'] += 1
                    result['error_ids'].append(user['id'])
                    app.logger.error("[MELWIN] Error for user %i" % user['id'])


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
    return 10

    # Tomorrows date + time!
    tomorrow = datetime.datetime.combine((datetime.date.today() + datetime.timedelta(days=1)), datetime.time(4, 0))
    # Unix timestamp, just calculate seconds until
    seconds = int(time.mktime(tomorrow.timetuple()) - time.time())

    return seconds


def start(app):
    """Schedule after startup for first run
    @todo: smart schedule "04 tomorrow"
    """

    s = get_timer()
    threading.Timer(get_timer(), do_melwin_update, [app]).start()
