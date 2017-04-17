import sys
from eve.methods.post import post_internal
from eve.methods.patch import patch_internal
from eve.methods.put import put_internal
from ext.app.decorators import async, track_time_spent
import datetime, time
import pickle
from .melwin import Melwin
import threading

#@track_time_spent('Melwin Update')
@async
def do_melwin_update(app):

	use_pickle = False

	result = {'replaced': 0, 'created': 0, 'errors': 0, 'error_ids': []}

	try:

		# Need correct context or fails miserable!
		with app.test_request_context('api/v1/melwin/users'):

			try:
				if not use_pickle:
					raise FileNotFoundError

				with open("persons.p", "rb") as f:
					persons = pickle.load(f)
					print("Using local person pickle file")

			except FileNotFoundError:
				print("Doing the Melwin limbo")
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
					r, _, _, status = put_internal(resource='melwin/users', payload=user, concurrency_check=False, skip_validation=False, **lookup)

					if status == 200:
						result['replaced'] += 1
					if status != 200:
						print("NOT 200")

				except KeyError:
					r, _, _, status, header = post_internal(resource='melwin/users', payl=user, skip_validation=True)

					if status == 201:
						result['created'] += 1

				except:
					result['errors'] += 1
					result['error_ids'].append(user['id'])
					msg = "Melwin update for %i failed" % int(user['id'])
					print(msg)
					#eve_abort(status=503, message=msg, sysinfo=None)


	except:
		"""Major error, warn"""
		from ext.notifications.sms import Sms
		sms = Sms()
		sms.send(mobile=sms.get_warn_sms(), message="[%s] %s" % (500, "Error updating users from Melwin"))
		result['errors'] += 1

	#Restart in one day!
	threading.Timer(get_timer(), do_melwin_update, [app]).start()

def get_timer():
	"""Return seconds until we run
	"""
	# For testing
	#return 10

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
