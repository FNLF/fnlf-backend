"""

	Melwin package
	==============
	
	A quick'n dirty (really really dirty) python implementation for the Melwin soap api using suds
	
	NB requires suds-0.7 ('pip install https://bitbucket.org/jurko/suds/get/1871530805fd.zip' - use tip!)
	
	AND changes in suds/sax/date.py line 95, comment out exception just return value!
	#raise ValueError("date data has invalid format '%s'" % (value,))
+	return value 

	Oboj, suds er scattered all over the place
	MEN fungerer med filter slik at man kan reparere fucked up s##t fra Melwin!
	
	@todo: Fix a cache via pickle!!! So 
	>>> import pickle
	>>> favorite_color = { "lion": "yellow", "kitty": "red" }
	>>> pickle.dump( favorite_color, open( "save.p", "wb" ) )
	>>> favorite_color = pickle.load( open( "save.p", "rb" ) )
	So, response is a pickle object!!
	@todo: refacor out the services calls and return whatever you need!
	
	@todo: .replace('Norge', 'Norway') Melwin bruker Norge for vel, men engelsk for utenlandske.... Go figure??
	
	@todo: Remove legacy google api since it only serves 2500 requests pd, use pygeo!
	
	#NB No zip code!
	location = geolocator.geocode("Halfdan Wilhelmsens Alle 16 Tønsberg")
	geolocator = OpenMapQuest() | Nominatim()
	location = geolocator.geocode("Halfdan Willhelmsens Alle 16")
	location == None
	location methods: 'address', 'altitude', 'latitude', 'longitude', 'point', 'raw'
	print(location.latitude, location.longitude)
	location.raw is a dict with keys => osm_id, type, lon, class, lat, place_id, osm_type, importance,display_name,boundingbox,licence

"""

from suds.client import Client
from suds.xsd.doctor  import ImportDoctor, Import
from suds.plugin import MessagePlugin

from pprint import pprint
import json

#import datetime
from datetime import date
from datetime import datetime
from datetime import time


# Use the free one!! Or should we use 
from geopy.geocoders import Nominatim, OpenMapQuest

import itertools,sys

from ..scf import Scf
	
"""
# Monkeypatch will not work since it's not called from here...
def monkeypatch_suds_sax_date(value):

		match_result = _RE_DATE.match(value)
		if match_result is None:
			#raise ValueError("date data has invalid format '%s'" % (value,))
			return value
		return _date_from_match(match_result)
	
Client.sax.Date.__parse = monkeypatch_suds_sax_date
"""

""" 
	Class for suds filter
	=====================
	
	- removes bambus dates from Melwin
	@todo not needed since monkey patching return value?
"""
class Filter(MessagePlugin):
	
	def received(self, context):
		#pprint(context.reply)
		#decoded = context.reply.decode('utf-8', errors='ignore')
		#reencoded = decoded.encode('utf-8')
		#context.reply = reencoded
		reply = context.reply
		context.reply = reply.replace(b'0000-00-00', b'1900-01-01')
		#pprint(context.reply)
		#pass


"""
To save as file!!!

"""
class PayloadInterceptor(MessagePlugin):
        
        def __init__(self, *args, **kwargs):
            self.last_payload = None

        def received(self, context):
            #recieved xml as a string
            
            print("(Suds) %s bytes received (reported by payloadinterceptor)" % len(context.reply))
            
            # Make a copy available
            self.last_payload = context.reply    
            #clean up reply to prevent parsing
            #context.reply = ""
            #return context
"""
	Class Melwin
	============
	
	Methods interfacing Melwin soap api
		
"""

class Melwin():
	
	# Jan got all the permissions!
	
	klubb = '375-F' #311 bodø 375 tøfsk
	do_geo = True
	
	debug = True
	
	geocoder = None
	member = 0
	pin = 0
	
	
	
	
	def __init__(self):
			
		# Make a import filter fixing the broken schemas
		imp = Import('http://schemas.xmlsoap.org/soap/encoding/')
		imp.filter.add('http://www.4d.com/namespace/default')
		Doctor = ImportDoctor(imp)
		
		# To intercept the raw response from the server, ie storing it as cache...
		self.payload_interceptor = PayloadInterceptor()
		
		c = Scf().get_melwin()
		self.member = c['member']
		self.pin = c['pin']
		self.melwin_url = c['url']
		
		# Instantiate the suds soap client NB use doc for it to work!!!!
		self.client = Client(self.melwin_url, plugins=[Filter(),self.payload_interceptor])
		
		if self.do_geo:
			self.geocoder = Nominatim()


	
	"""
		Dump to file
		============
		
		For inspecting large data sets
	"""
	
	def _dump_file(self, data, file="data.txt", json_encoded=True):	
		
		with open(file, 'w') as f:
  			if json_encoded:
  				json.dump(data, f, ensure_ascii=False)
  			else:
  				f.write(data)  		
  		
  	
	"""
		Debug to stdout
	"""
	def __dbg(self, prefix, data):
		
		if self.debug:
			print("(%s)\t %s" % (prefix, data))
		pass
	

	
	
	"""
		Get all members
		===============
		
		Get's all members in a club by the current club (self.club)
		
		@return: dict all members
	
	"""
	
		
	def __get_all_members(self,club):	

		# Do a service call:
		return self.client.service.ws_GetAllClubMemberData(self.member, self.pin, club)
		
	
	def get_all_members(self, club):
		
		# @todo refactor out in a callable method and lambda the args
		self.__dbg('Suds', 'ws_GetAllClubMemberData starting...')
		response = self.__get_all_members(club)
		self.__dbg('Suds', 'ws_GetAllClubMemberData ended')
		
		# Check for empty set!
		if str(response.aClubMembers).strip() == '':
			return None
		
		
		d = {} # the first iteration of members
		rev = {} # reverse lookup
		term = {} # terminated members are not in sync!!
		
		for data in response:
			
			key = data[0]
			i = 0
			
			for v in data[1][0]:
				
				#Make sure to break when no result - only for first iteration?
				#if str(v).strip() == '' or v is None:
				#	continue
				
				v = str(v)
					
				if v == '':
					v = None
						
				if key == 'aClubMembers':
					
					#if v is None:
					#	continue
					
					d[i] = {'id': int(v), 'active': True, 'location': {}, 'membership': {}}
					
					
					rev[v] = i
					
				elif key == 'aDateStamp':
					
					d[i]['updated'] = ("%sT00:00:00CET" % v)
					
				elif key == 'aFornavn':
					d[i]['firstname'] = v
					
				elif key == 'aEtternavn':
					d[i]['lastname'] = v
					
				elif key == 'aDateOfBirth':
					d[i]['birthdate'] = ("%sT00:00:00CET" % v)
					
				elif key == 'aMann':
					if v:
						d[i]['gender'] = 'M'
					else:
				 		d[i]['gender'] = 'F'
					
				elif key == 'aEpost':
					d[i]['email'] = v
					
				elif key == 'aMobil':
					
					if str(v) == '':
						d[i]['phone'] = None
					else:
						data_tmp = str(v)
						d[i]['phone'] = data_tmp.replace(' ','')
						data_tmp = ''
					
				elif key == 'aAdresse':
					d[i]['location'].update({'street': v})
					
				elif key == 'aPostNR':
					d[i]['location'].update({'zip': v})
					
				elif key == 'vPostSted':
					d[i]['location'].update({'city': str(v).lower().title()})
					
				elif key == 'aCountry':
					d[i]['location'].update({'country': v})
					
				elif key == 'aKategori':
					d[i]['membership'].update({'type': v})
					
				elif key == 'aInnmeldt':
					d[i]['membership'].update({'enrolled': "%sT00:00:00CET" % v})
					
				elif key == 'aBetAAr':
					d[i]['membership'].update({'valid': "%s-12-31T23:59:59CET" % v})
					
				elif key == 'aSaldo':
					d[i]['membership'].update({'balance': float(v)})
					
				elif key == 'aArsavgift':
					d[i]['membership'].update({'fee': float(v)})
				
				"""
				Utter rubbish from Melwin two arrays one with membership nr, the next with termination date...
				# Terminations
				elif key == 'aCludDeactiveMembers':
					term[i] = {'id': int(v)} # @todo: what the heck what kind of type is this?
				
				#elif key == 'aUtmeldt':
				#	term[i]['terminated'] = v
				
				elif key == 'aDateDeactive':
					term[i].update({'terminated': "%sT00:00:00CET" % v})
				"""
				
				i += 1
		
		# Pivot into members
		# members key is member number
		members = {}
		
		for key, val in d.items():
			
			members[int(val['id'])] = val
			
		# Now insert terminated items!
		# WTF is terminated a seperate array inside the arry with different non-existing member id's???
		"""
		for k,t in term.items():
			try:
				members[int(t['id'])].update({'active': False})
				members[int(t['id'])]['membership'].update({'terminated': t[int(t['id'])]['terminated']})

			except:
				pass
		"""	
		
		return members
	
				
		
		
		"""
		Termination, unsync with the rest!
		"""
		term = {}
		
		i= 0
		for data in response.aCludDeactiveMembers:
			term[i] = {'id': data}
			i +=1
		
		i= 0
		for data in response.aUtmeldt:
			term[i]['terminated'] = ("%sT00:00:00CET" % data)
			i +=1
		
		i= 0
		for data in response.aDateDeactive:
			term[i]['terminated_date'] = ("%sT00:00:00CET" % data)
			i +=1
		
		"""
		Now pivot and make id key for new dict!
		"""
		members = {}
		
		for k, v in enumerate(d):
			
			members.update({k : v})
			#members[v['id']].update(v)
		
		"""
		Now we join onto main list a key as id
		
		for data in term:
			
			members[data['id']].update({'terminated': data['terminated'],
										'terminated_date': data['terminated_date']}) 
		
		"""
		return members
	
	"""
		Login
		=====
		
		
		
	
		(reply){
   			vSvar = "OK"
   			vRolle = "Ingen"
 		}
	"""
	def login(self, member, pin):
		
		r = self.client.service.ws_APP_User_Autenticate(member, pin)
		
		if r.vSvar == 'OK':
			return True
		
		return False
	
	"""
	Float???
	<ns1:ws_kontingentaarResponse>
	<vKAAr xsi:type="xsd:float">2014</vKAAr>
	</ns1:ws_kontingentaarResponse>
	"""
	
	def __get_kontigentaar(self):
		
		return  self.client.service.ws_kontingentaar()
	
	def get_kontigentaar(self):
		
		r = self.__get_kontigentaar()
		
		return r.vKAAr
	
	"""
	
		Get members from Melwin
		Then pivots around licenses and make a json encoded array
		
		@todo add exceptions try/catch
		@todo check response status before doing anything
		@todo break out pivoting into seperate method?
		
	"""
	
	def __get_all_licenses(self, club):
		
		return self.client.service.ws_Lisenser(self.member, self.pin, club)
	
	def get_all_licenses(self, club):
		
		self.__dbg('Suds', 'ws_Lisenser starting...')
		
		response = self.__get_all_licenses(club)
		#response = client.service.ws_pm_Klubb(klubb)
		#response = client.service.ws_enkeltadresse(medlem, pin, 45199)
		self.__dbg('Suds', 'ws_Lisenser ended')
		
		"""
		pprint('The type of the response is: ')
		pprint(type(response))
		pprint(response.aRettighet)
		print('Methods')
		pprint(dir(response))
		pprint(dir(response))
		"""
		
		key_list = []
		nak_list = []
		license_list = []
		expiry_list = []
		
		
		# Oboj, lets pivot that response and build
		# a dictionary
		for data in response:
			
			key = data[0]
			# Make list of the bloody keys
			key_list.append(key)
			
			# Need to check for item exists and evt break!
			try:			
				for item in data[1].item: #0=> string, #1=> array use .item
					
					if key == 'aNummer':
						nak_list.append(int(item))
					elif key == 'aRettighet':
						license_list.append(str(item))
					elif key == 'aExpires':
						expiry_list.append(item)
					else:
						key = ''
						pass
			except:
				pass
				
			#i++dict(zip([1,2,3,4], [a,b,c,d]))
		
		"""
		# Some debug stuff!
		pprint(nak_list[8])
		pprint(license_list[8])
		pprint(expiry_list[8])
		pprint(key_list)
		"""
		
		"""
		So have the lists, now we need to merge 
		"""
		tmp_license = 0
		d = {}
		tmp_licenses = []
		curr_nak = 0
		
		# Now lets build the final dictionary {key(aNummer): {'licenses': {[]}, 'expiry': isodate}
		# Keys are the melwin id/membership number
		for key, value in enumerate(nak_list):
			#print(key + 'processing ' + value)
			# Build list of licenses!
			
			# If same as before, drop him!
			if(curr_nak == value):
				continue
			
			else: # If not set as new...
				curr_nak = value
			
			for license_key, license in enumerate(license_list):
				
				if(nak_list[license_key] == curr_nak):
					tmp_licenses.append(license)
					if len(nak_list) == key+1:
						break
					if nak_list[key + 1] != value:
						break
			
			# set converts list to unique values but we need it to be list, expiry date is datetime.date object!
			d[int(curr_nak)] = {'rights': list(set(tmp_licenses)), 'expiry': "%sT00:00:00CET" % expiry_list[key]} # expiry_list[key].isoformat()}
			tmp_licenses = []
			mylist = []
			
		return d
		# END get_members


	
	"""
		Get member's clubs
		==================
		
		Returns a list
	"""
	
	
	def __get_member_clubs(self, member):
		
		return self.client.service.ws_pm_TilknyttetKlubber(member)
	
	def get_member_clubs(self, member):
		
		self.__dbg('Suds', ('ws_pm_TilknyttetKlubber(%s) starting...' % member))
		response = self.__get_member_clubs(member)
		self.__dbg('Suds', ('ws_pm_TilknyttetKlubber(%s) ended' % member))
		
		clubs = []
		
		for club in response[1].item:
			clubs.append(str(club))
			
		return clubs
	
	"""
		All clubs
		=========
		
		Using the open ws_pm_Klubb one can get the list of clubs in one section
		
		Hackish and yet another sign that Melwin is a piece of s##t
	"""
	
	def __get_all_clubs(self,club):
		
		return self.client.service.ws_pm_Klubb(club)
	
	def get_all_clubs(self):
		
		clubs = {}
		active = True
		for i in range(299,400):
			club = "%i-F" % i
			response = self.__get_all_clubs(club)
			
			if response == 'Ukjent':
				pass
			else:
				
				if response.find("(SLETTET)") > 0:
					response = response.replace("(SLETTET)", "")
					active = False
				
				else:
					active = True	
					
					
				response.strip()
				clubs.update({club: {'id': '%s' % club,
									'name': '%s' % response.lower().title(),
									'active': active,
									'org': 'nif.nlf.fallskjerm',
									'locations': {}, # {"type":"Point","coordinates":[None, None]}, # Burde vel vært locations? 
									'planes': {}, #default er 0
									'roles': {}, #director, vice director, member, vara etc....
									'ot': 1, 
									#'ci': None,
									#'logo': None,
									'url': '',
									}
							})
			
		
		return clubs
	
	"""
		All membership types
		====================
		
		Using the open ws_pm_MemberTypes one can get the list of types of membership
			
		Hackish and yet another sign that Melwin is a piece of s##t
		
		@return: dict :{id,name}
		
		@todo:	Does not work, server error using doc, and suds fails due to schema s##t n regular wdsl....
	"""
	
	def __get_all_memberships(self):
		
		return self.client.service.ws_GetMemberTypes()
	
	def get_all_memberships(self):
		
		m = {}
		d = {}
		
		response = self.__get_all_memberships()
		
		for data in response:

			key = data[0]
			i = 0
			rev = []
			
			for v in data[1][0]:
				if key == 'aClubID':
					d[i] = {'id': str(v)}
					rev[v] = i
						
				
				if key == 'aClubName':
					d[i]['name'] = "%s" % v
			
				i += 1
		
		
		for v in d.items():
			
			m[v['id']] = v
			
		
		return m
	
	"""
		Set Club
		========
		
		Set the current club
	"""
	def set_club(self, club):
		
		self.klubb = club
	
	"""
		Geolocation
		===========
		
		@attention: Max requests: 2500/day 5/sec 
	"""	
	def get_geo(self, street, city='', zip='', country='Norway'):
		
		try:
			self.__dbg('Geo', "Reverse lookup for %s %s %s %s" % (street, zip, city, country))
			location = self.geocoder.geocode("%s %s %s %s" % (street, zip, city, country))
			
			if location is None:
				location = self.geocoder.geocode("%s %s" % (city, country))
				if location is None:
					return None
				
		except:
			self.__dbg('Geo', "Something went wrong for %s %s %s %s" % (street, zip, city, country))
			location = None
			pass
		
		self.__dbg('Geo', "Got  %s" % location.point)
		return location
	
	"""
		Medlem
		======
		
		Get one member only, seems legit...
		
		vNavn = "Huseby Einar"
		vAdresse_1 = "Halfdan Wllhelmsens Alle 16"
		vAdresse_2 = None
		vPostnr = "3116"
		vEpost = "einar.huseby@gmail.com"
		vPrivat = None
		vArbeid = None
		vTelefaks = None
		vMobil = "40222889"
		vFDato = "28.11.1974"
		vMann = True
		vInfo = "TROMS FALLSKJERMKLUBB (380-F), FALLSKJERMSEKSJONEN, Innmeldt: 08.05.1995, Utmeldt: 17.04.1997, Betalt år: 1996, Kategori: SIDEMEDLEM (samme seksjon)
				TØNSBERG FALLSKJERMKLUBB (375-F), FALLSKJERMSEKSJONEN, Innmeldt: 17.08.1995, Utmeldt: 00.00.00, Betalt år: 2014, Kategori: SENIOR
				NTNU FALLSKJERMKLUBB (351-F), FALLSKJERMSEKSJONEN, Innmeldt: 17.04.1997, Utmeldt: 04.01.2008, Betalt år: 2007, Kategori: SENIOR
				VOSS FALLSKJERMKLUBB (391-F), FALLSKJERMSEKSJONEN, Innmeldt: 30.07.2001, Utmeldt: 09.01.2008, Betalt år: 2007, Kategori: SENIOR
				BERGEN FALLSKJERMKLUBB (310-F), FALLSKJERMSEKSJONEN, Innmeldt: 29.08.2005, Utmeldt: 31.12.2005, Betalt år: 0, Kategori: SIDEMEDLEM (samme seksjon)
				TØNSBERG FALLSKJERMKLUBB (375-F), FALLSKJERMSEKSJONEN, Innmeldt: 24.06.2014, Utmeldt: 00.00.00, Betalt år: 2014, Kategori: TANDEMELEV
				"
		vPostSted = "TØNSBERG"

	"""
	def get_member(self,member):
		
		response = self.client.service.ws_enkeltadresse(self.member, self.pin, member)
		
		d = {}
		
		# Iterate, iterate and pivot!
		for key, data in response:
			
			if key == 'vNavn':
				d['name'] = str(data)
				
				name = d['name'].split(' ')
				d['lastname'] = name[0]
				name.pop(0)
				d['firstname'] = ' '.join(name)
				
			elif key == 'vAdresse_1':
				d['street'] = data
				
			elif key == 'vPostnr':
				d['zip'] = data
				 
			elif key == 'vEpost':
				d['email'] = data
			
			
			elif key == 'vMobil':
				
				#Parsing phone numbers should be done smarter....
				#Should it be string or int?
				#Should one seperate phone number and country code
				#phone = {'cc': 47, 'nr': 40222889} ?
				
				data_tmp = str(data)
				d['phone'] = data_tmp.replace(' ','')
				 
			elif key == 'vMann':
				if data:
					d['gender'] = 'M'
				else:
					d['gender'] = 'F'
					 
			elif key == 'vPostSted':
				d['city'] = data
				
			elif key == 'vFDate':
				
				tmp = data.split('.')
				d['birthdate'] = str(datetime.date(tmp[2], tmp[1], tmp[0])) 
			
			elif key == 'vInfo':
				
				d['info'] = {}
				
				#pprint(len(data.split('\n')))
				
				for k, t in enumerate(data.strip().split('\n')):
					
					l = {}
					
					tmp = t.split(',')
					
					d['info'][k] = {'club': tmp[0].strip(),
									'section': tmp[1].strip(),
									'in': tmp[2].strip(),
									'out': tmp[3].strip(),
									'paid': tmp[4].strip(),
									'category': tmp[5].strip()}
				
			else:
				continue
				
		
		
		return d

	"""
		Get All
		=======
		
		Collects member info, licenses, clubs and makes one dict
		From all clubs!
		
		@todo: Should use twister and get all clubs at once => heavy load on Melwin?
		@return: dict members
		
	
	"""
	def get_all(self):
		
		members = {}
		
		self.__dbg('Clubs', 'Getting a list of all clubs')
		#Get list of all clubs!
		clubs = self.get_all_clubs()
		self.__dbg('Clubs', ('Got %s clubs' % len(clubs)))
		
		#clubs = {}
		#Remove banned clubs! No need to anymore?
		#clubs.pop('300-F', None)
		#clubs = {'330-F': {'id': '330-F', 'name': 'Tøfsk', 'active': True}} #Overriding for testing!!
		
		self.__dbg('Get All', 'Starting member merging')
		
		for key, club in clubs.items():
			
			self.__dbg('Clubs', ("%s (%s), Active: %s" % (club['name'], club['id'], club['active'])))
			
			if club['active'] == False:
				self.__dbg('Clubs', ('%s (%s) is not active, continuing' % (club['name'], club['id'])))
				continue
			
			
			#Iterate over get_all_members
			self.set_club(club['id'])
			tmp_members = self.get_all_members(club['id'])
			
			#@todo: Must validate reply here - items?? All objects can be saved as cPicle or pickle then save/load responses to disk!
			if tmp_members == None:
				self.__dbg('Clubs', ('%s (%s) has no members, continuing' % (club['name'], club['id'])))
				continue
			
			#try:
			# Now do get licenses for new ones!
			#iterate and get all licenses
			
			try:
				all_licenses = self.get_all_licenses(club['id'])
			except:
				self.__dbg('Error', 'Something went wrong')
			
			curr_members = tmp_members.copy()
			for nak, val in tmp_members.items():
				
				#Drop if exists already!
				if int(nak) in members:
					curr_members.pop(int(nak))
					self.__dbg('Merging', ('Removed %s from list already exists' % nak))
					continue
				
				try:
					curr_members[int(nak)].update({'licenses': all_licenses[int(nak)]})
					self.__dbg('Merging', ('%s has licenses, merging' % nak))
				except:
					curr_members[int(nak)].update({'licenses': {}})
					self.__dbg('Merging', ('%s has no licenses, skipping' % nak))
					pass
				
				try:
					member_clubs = self.get_member_clubs(nak)
					curr_members[int(nak)]['membership'].update({'clubs': member_clubs})
					self.__dbg('Merging', ('%s has member clubs, merging' % nak))
				except:
					curr_members[int(nak)]['membership'].update({'clubs': [club['id']]}) #Always member of member club...
					self.__dbg('Merging', ('%s has no member clubs, skipping' % nak))
					pass
				
				"""
				Geojson!
				Using pygeo
				 'address', 'altitude', 'latitude', 'longitude', 'point', 'raw'
				 raw: {
				 'place_id': '2627969483', 
				 'display_name': '16, Halfdan Wilhelmsens Alle, Kaldnes, Tønsberg, Vestfold, 3116, Norge', 
				 'lat': '59.2723302', 
				 'lon': '10.4151179', 
				 'importance': 0.611, 
				 'osm_id': '3130212004', 
				 'osm_type': 'node', 
				 'type': 'house', 
				 'licence': 'Data © OpenStreetMap contributors, ODbL 1.0. http://www.openstreetmap.org/copyright', 
				 'class': 'place', 
				 'boundingbox': ['59.2722802', '59.2723802', '10.4150679', '10.4151679']}
				"""
				if self.do_geo:
					try:
						
						geo = self.get_geo(curr_members[int(nak)]['location']['street'], curr_members[int(nak)]['location']['city'], curr_members[int(nak)]['location']['zip'], curr_members[int(nak)]['location']['country'])
						if geo != None:
							curr_members[int(nak)]['location'].update({'geo': {"type":"Point","coordinates": [geo.latitude, geo.longitude]}})
							curr_members[int(nak)]['location'].update({'geo_type': geo.raw['type']})
							curr_members[int(nak)]['location'].update({'geo_class': geo.raw['class']})
							curr_members[int(nak)]['location'].update({'geo_importance': float(geo.raw['importance'])})
							curr_members[int(nak)]['location'].update({'geo_place_id': int(geo.raw['place_id'])})
							#curr_members[int(nak)]['location']['geo'].update({'altitude': geo.raw['altitude']})
					except:
						#members[val['id']].update({'location': {"type":"Point","coordinates":[0.0,0.0]}})
						#members[val['id']].update({'location': {}})
						pass
			#except:
			#	self.__dbg('Merging', 'Error occured in merging loop with %s' % club['id'])
			#	pass
			
			# First iteration vs next
			# Unfortunately this overwrites the old ones..
			if len(members) > 0:
				members.update(curr_members)
			else:
				members = curr_members
			
				
		
		#Build a humongous obj, replace with newer
		
		#for member in members.items():
		return members

# example:

# import time
# @spinner(10)
# def process_chunk():
#     time.sleep(.1)

# sys.stdout.write("running... ")
# while True:
#     process_chunk()	

"""

Working loop!
	
m = Melwin()

r = m.get_all()

pprint(r[45199])
		
pprint(json.dumps(r[45199]))		

"""

########################################################################
#
#	LEGACY S##T
#	
#######################################################################







"""
Test bygge user object
NB denne bygger fra lisenser!!!
"""

"""
all = m.ggg()

all_licenses = m.get_all_licenses()

for key, val in all.items():
	
	try:
		all[key].update({'licenses': all_licenses[int(key)]})
	except:
		all[key].update({'licenses': {}})
		print('EEE Could not get licenses for %s' % str(key))
		pass
	
	try:
		clubs = m.get_member_clubs(key)
		all[key].update({'clubs': clubs})
	except:
		all[key].update({'clubs': {}})
		print('EEE Could not get clubs for %s' % str(key))
		pass

pprint(dir(all))
for k,v in all.items():
	print(type(k))
	print("%s: %s" % (k, v['id']))
	
pprint(json.dumps(all))
"""




"""
import json
print('>>> 45199')
pprint(json.dumps(d[45199]))
print('>>> 38168')
pprint(json.dumps(d[38168]))
"""





"""
This works!
for k, v in response:
	pprint(type(v))
	for key, val in v:
		pprint(type(val))
		for vin in val:
			print('Now key:')
			pprint(vin)
			break #just one iteration
"""
#fml = {}
#for r in response:
#	for n in r:
#		for s in n:
#			fml = s
#

		

"""
Pure xml play?
#response = client.service.ws_Instruktorer(klubb)
#response = client.service.ws_GetMemberTypes()
import xml.etree.ElementTree as ET
tree = ET.ElementTree(ET.fromstring(response))

root = tree.getroot()

for child in root:
	#print(child.tag, child.attrib)
	pprint(child.ns1)

END
"""
"""
for data in response:
	
	for i in data:
		for t in i:
			for r in t:
				print('>>>>>>>>\n')
				pprint(r)
				for endelig in r:
					print(endelig)
	#pprint(data[2])
	# 1 is aNummer (key), then 3 is aRettighet	
	# fmt[item[1]].append(str(item[3]))
	#for i in data:
	#	pprint(i)

#client.service.ws_sjekkOK()
"""

