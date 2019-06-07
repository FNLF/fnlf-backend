"""

        Melwin package
        ==============
        
        A quick'n dirty (really really dirty) python implementation for the Melwin soap api using suds
        
        AND changes in suds/sax/date.py line 95, comment out exception just return value!
        #raise ValueError("date data has invalid format '%s'" % (value,))
+       return value 

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
from suds.xsd.doctor import ImportDoctor, Import
from suds.plugin import MessagePlugin
from suds.cache import NoCache
from retry import retry
import socket

import json, re, unicodedata

# import datetime
import datetime

# Use the free one!! Or should we use
from geopy.geocoders import Nominatim, OpenMapQuest


import ssl
"""Need to allow the SSL certificate at melwin"""
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    # Legacy Python that doesn't verify HTTPS certificates by default
    pass
else:
    # Handle target environment that doesn't support HTTPS verification
    ssl._create_default_https_context = _create_unverified_https_context


import itertools, sys

from ..scf import Scf

"""Control characters for remove_control_chars(s)"""
all_chars = (chr(i) for i in range(0x110000))
control_chars = ''.join(c for c in all_chars if unicodedata.category(c) == 'Cc')
control_char_re = re.compile('[%s]' % re.escape(control_chars))


def remove_control_chars(s):
    """Remove all control chars in string"""

    return control_char_re.sub('', s)


class Filter(MessagePlugin):
    """Replace bambus dates from response"""

    def received(self, context):
        reply = context.reply
        context.reply = reply.replace(b'0000-00-00', b'1900-01-01')


class UnicodeFilter(MessagePlugin):
    """Decode and recode in utf-8 to remove gremlins"""

    def received(self, context):
        dirty = context.reply.decode('utf-8', errors='ignore')
        clean = remove_control_chars(dirty)
        context.reply = clean.encode('utf-8')


class PayloadInterceptor(MessagePlugin):
    """Suds payload interceptor
    Intercept requests and responses on httplib level.
    Keeps last request and response"""

    def __init__(self, *args, **kwargs):
        self.last_response = None
        self.last_request = None

    def sending(self, context):
        self.last_request = context.envelope

    def received(self, context):
        # print("(Suds) %s bytes received (reported by payloadinterceptor)" % len(context.reply))
        # Make a copy available
        self.last_response = context.reply


class Melwin():
    """Melwin class
    Interfaces the Melwin Soap API
    Suds used for xml http 
    Parses reponses to members"""

    do_geo = False

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

        self.ors_id = c['orsid']
        self.ors_pwd = c['orspwd']

        self.melwin_url = c['url']

        """SUDS-jurko instantiating
        Needs cache=NoCache() because suds do not check in a predicable manner...
        With cache it complains of open files cache=NoCache()"""
        try:
            self.client = Client(self.melwin_url, plugins=[Filter(), UnicodeFilter(), self.payload_interceptor], timeout=600)
        except:
            self.__dbg('SUDS', 'Could not create suds client instanse')
            return None

        self.geocoder = Nominatim(user_agent='ors-app')

    def _dump_file(self, data, file="data.txt", json_encoded=True):
        """Dump data to file"""

        with open(file, 'w') as f:
            if json_encoded:
                json.dump(data, f, ensure_ascii=False)
            else:
                f.write(data)

    def __dbg(self, prefix, data):
        """Debug to std.out"""
        if self.debug:
            # print("(%s)\t %s" % (prefix, data))
            pass
        pass

    """MELWIN SERVICES
    @TODO: Exceptions for retry, include urllib.error.URLError caused by socket.gaierror"""

    def __status(self):

        try:
            return self.client.service.ws_sjekkOK()
        except:
            pass

        return False

    @retry(exceptions=(ResourceWarning, Exception, socket.timeout, socket.gaierror), tries=3, delay=2)
    def __login(self, member, pin):
        """Authenticates via Melwin"""
        return self.client.service.ws_APP_User_Autenticate(member, pin)

    @retry(exceptions=(ResourceWarning, Exception, socket.timeout, socket.gaierror), tries=3, delay=2)
    def __get_all_memberships(self):
        """Returns all membership types"""
        return self.client.service.ws_GetMemberTypes()

    @retry(exceptions=(ResourceWarning, Exception, socket.timeout, socket.gaierror), tries=3, delay=2)
    def __get_all_members(self, club):
        """Returns all members in given club"""
        return self.client.service.ws_GetAllClubMemberData(self.member, self.pin, club)

    @retry(exceptions=(ResourceWarning, Exception, socket.timeout, socket.gaierror), tries=3, delay=2)
    def __get_member_clubs(self, member):
        """Returns all clubs for member"""
        return self.client.service.ws_pm_TilknyttetKlubber(member)

    @retry(exceptions=(ResourceWarning, Exception, socket.timeout, socket.gaierror), tries=3, delay=2)
    def __get_member_licenses(self, member):
        """Get licenses for given member"""
        return self.client.service.ws_GetORSLisenser(self.ors_id, self.ors_pwd, member)

    @retry(exceptions=(ResourceWarning, Exception, socket.timeout, socket.gaierror), tries=3, delay=2)
    def __get_all_club_licenses(self, club):
        "Returns all members and licenses for given club"
        return self.client.service.ws_Lisenser(self.member, self.pin, club)

    @retry(exceptions=(ResourceWarning, Exception, socket.timeout, socket.gaierror), tries=3, delay=2)
    def __get_club(self, club):
        """Returns info on given club"""
        return self.client.service.ws_pm_Klubb(club)

    @retry(exceptions=(ResourceWarning, Exception, socket.timeout, socket.gaierror), tries=3, delay=2)
    def __get_kontigentaar(self):
        """Returns year"""
        return self.client.service.ws_kontingentaar()

    """ORS SPECIFIC SERVICES"""
    @retry(exceptions=(ResourceWarning, Exception, socket.timeout, socket.gaierror), tries=3, delay=2)
    def __ors_get_all_club_members(self, club):
        """Returns list of membership numbers for club members in given club"""
        return self.client.service.ws_GetORSClubMembers(self.ors_id, self.ors_pwd, club)

    @retry(exceptions=(ResourceWarning, Exception, socket.timeout, socket.gaierror), tries=3, delay=2)
    def __ors_get_member_data(self, member):
        """Returns member data for given member"""
        return self.client.service.ws_GetORSMemberData(self.ors_id, self.ors_pwd, member)

    @retry(exceptions=(ResourceWarning, Exception, socket.timeout, socket.gaierror), tries=3, delay=2)
    def __ors_get_member_licenses(self, member):
        """Returns licenses for given member
        @NOTE vKode vKlubbnr not in use"""
        return self.client.service.ws_GetORSLisenser(self.ors_id, self.ors_pwd, member)

    """LOGICAL METHODS"""

    def status(self):

        return self.__status()

    def login(self, member, pin):
        """Authenticate via Melwin"""

        r = self.__login(member, pin)

        if r.vSvar == 'OK':
            return True

        return False

    def get_kontigentaar(self):
        """Return current license year"""

        r = self.__get_kontigentaar()

        return r.vKAAr

    def get_all_members(self, club):

        # @todo refactor out in a callable method and lambda the args
        self.__dbg('Suds', 'ws_GetAllClubMemberData starting...')
        response = self.__get_all_members(club)
        self.__dbg('Suds', 'ws_GetAllClubMemberData ended')
        if response is None:
            return response

        #return response
        # Check for empty set!
        if 'aClubMembers' in response and str(response['aClubMembers']).strip() == '':
            return None

        d = {}  # the first iteration of members
        rev = {}  # reverse lookup
        term = {}  # terminated members are not in sync!!

        for data in response:

            key = data[0]

            if key in ['vSvar', 'aCludDeactiveMembers', 'aUtmeldt', 'aCludDeactiveMembers']:
                """These keys/columns are not same length as the rest and not processable"""
                continue

            i = 0
            try:
                for v in data[1][0]:
                    print(v)
                    v = str(v)

                    if i not in d:
                        d[i] = {}
                        d[i]['location'] = {}
                        d[i]['membership'] = {}
                        d[i]['active'] = False

                    if v == '':
                        v = None

                    if key == 'aClubMembers':

                        d[i].update({'id': int(v)})
                        d[i]['active'] = True

                        rev[v] = i

                    elif key == 'aDateStamp':
                        d[i]['updated'] = datetime.datetime.strptime(v, '%Y-%m-%d')
                    elif key == 'aFornavn':
                        d[i].update({'firstname': v})
                    elif key == 'aEtternavn':
                        d[i]['lastname'] = v
                    elif key == 'aDateOfBirth':
                        d[i]['birthdate'] = datetime.datetime.strptime(v, '%Y-%m-%d')
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
                            d[i]['phone'] = data_tmp.replace(' ', '')
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
                        d[i]['membership'].update({'enrolled': datetime.datetime.strptime(v, '%Y-%m-%d')})
                    elif key == 'aBetAAr':
                        if v == '0':
                            v = datetime.datetime.now().year - 1
                        n = "%s-12-31" % v
                        d[i]['membership'].update({'valid': datetime.datetime.combine(
                            datetime.datetime.strptime(n, '%Y-%m-%d'), datetime.datetime.max.time())})
                    elif key == 'aSaldo':
                        d[i]['membership'].update({'balance': float(v)})
                    elif key == 'aArsavgift':
                        d[i]['membership'].update({'fee': float(v)})

                    i += 1
            except Exception as e:
                print('Error', e)
                print('Data')
                print(data)

        members = {}

        for key, val in d.items():
            if 'id' in val:
                members[int(val['id'])] = val

        return members

    def get_member_licenses(self, member):
        """Get and parse licenses for given member"""

        licenses = {'rights': []}
        response = self.__get_member_licenses(member)

        try:
            if len(response[1][0]) > 0:

                licenses = {'rights': response[1][0]}
                if isinstance(response[5][0][0], datetime.date):
                    licenses.update(
                        {'expiry': datetime.datetime.combine(response[5][0][0], datetime.datetime.max.time())})
            else:
                pass


        except:
            pass

        if 'expiry' not in licenses:
            licenses.update(
                {'expiry': datetime.datetime.combine(datetime.date((datetime.datetime.now().year - 1), 12, 31),
                                                     datetime.datetime.max.time())})

        return licenses

    def get_all_licenses(self, club):
        """Get all members and licenses for given club"""

        self.__dbg('Suds', 'ws_Lisenser starting...')
        response = self.__get_all_club_licenses(club)
        self.__dbg('Suds', 'ws_Lisenser ended')

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
                for item in data[1].item:  # 0=> string, #1=> array use .item

                    if key == 'aNummer':
                        nak_list.append(int(item))
                    elif key == 'aRettighet':
                        license_list.append(str(item))
                    elif key == 'aExpires':
                        expiry_list.append(datetime.datetime.strptime(item, '%Y-%m-%d'))
                    else:
                        key = ''
                        pass
            except:
                pass

        tmp_license = 0
        d = {}
        tmp_licenses = []
        curr_nak = 0

        # Now lets build the final dictionary {key(aNummer): {'licenses': {[]}, 'expiry': isodate}
        # Keys are the melwin id/membership number
        for key, value in enumerate(nak_list):
            # print(key + 'processing ' + value)
            # Build list of licenses!

            # If same as before, drop him!
            if (curr_nak == value):
                continue

            else:  # If not set as new...
                curr_nak = value

            for license_key, license in enumerate(license_list):

                if (nak_list[license_key] == curr_nak):
                    tmp_licenses.append(license)
                    if len(nak_list) == key + 1:
                        break
                    if nak_list[key + 1] != value:
                        break

            # set converts list to unique values but we need it to be list, expiry date is datetime.datetime.date object!
            d[int(curr_nak)] = {'rights': list(set(tmp_licenses)),
                                'expiry': datetime.datetime.strptime(expiry_list[key], '%Y-%m-%d')}
            # "%sT00:00:00CET" % expiry_list[key]}  #  expiry_list[key].isoformat()}
            tmp_licenses = []
            mylist = []

        return d

    def get_member_clubs(self, member):
        """Get and parse clubs for given member"""
        self.__dbg('Suds', ('ws_pm_TilknyttetKlubber(%s) starting...' % member))
        response = self.__get_member_clubs(member)
        self.__dbg('Suds', ('ws_pm_TilknyttetKlubber(%s) ended' % member))

        clubs = []

        for club in response[1].item:
            clubs.append(str(club))

        return clubs

    def get_all_clubs(self):
        """Get and parse all clubs in melwin for -F
        @NOTE: Assumes club numbers between 300 and 399"""

        clubs = {}
        active = True
        for i in range(299, 400):
            club = "%i-F" % i
            response = self.__get_club(club)

            if response == 'Ukjent':
                pass
            else:

                if response.find("(SLETTET)") > 0:
                    response = response.replace("(SLETTET)", "")
                    active = False
                elif response.find("(Slettet)") > 0:
                    response = response.replace("(Slettet)", "")
                    active = False

                else:
                    active = True

                response.strip()
                clubs.update({club: {'id': '%s' % club,
                                     'name': '%s' % response.lower().title(),
                                     'active': active,
                                     'org': 'nif.nlf.fallskjerm',
                                     'locations': {},
                                     # {"type":"Point","coordinates":[None, None]}, # Burde vel vært locations?
                                     'planes': {},  # default er 0
                                     'roles': {},  # director, vice director, member, vara etc....
                                     'ot': 1,
                                     # 'ci': None,
                                     # 'logo': None,
                                     'url': '',
                                     }
                              })

        return clubs

    """
        All membership types
        ====================

        Using the open ws_pm_MemberTypes one can get the list of types of membership

        Hackish and yet another sign that Melwin is a piece of s##t

        
    """

    def get_all_memberships(self):
        """Get list of all types of memberships, parse and return
        @return: dict :{id,name}
        @todo:  Does not work, server error using doc, and suds fails due to schema s##t n regular wdsl...."""

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

    def get_geo(self, street, city='', zip='', country='Norway'):
        """Geolocation wrapper
        @NOTE: Max requests: 2500/day 5/sec"""

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

    def get_member(self, member):
        """Get one member via ws_enkeltadresse
        @NOTE: Do not work anymore"""

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

                data_tmp = str(data)
                d['phone'] = data_tmp.replace(' ', '')

            elif key == 'vMann':
                if data:
                    d['gender'] = 'M'
                else:
                    d['gender'] = 'F'

            elif key == 'vPostSted':
                d['city'] = data

            elif key == 'vFDate':

                tmp = data.split('.')
                d['birthdate'] = str(datetime.datetime.datetime(tmp[2], tmp[1], tmp[0]))

            elif key == 'vInfo':

                d['info'] = {}

                # pprint(len(data.split('\n')))

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

    def get_all(self):
        """Get all members from all clubs:
        Collects member info, licenses, clubs and returns one dict using member no as key
        @todo: Should use twister and get all clubs at once => heavy load on Melwin?
        @return: dict members
        @USES: 
            get_all_clubs()
            get_all_members(club)
            get_member_licenses(member)
            get_member_clubs(member)
            get_geo(..)
        """

        members = {}

        self.__dbg('Clubs', 'Getting a list of all clubs')
        clubs = self.get_all_clubs()
        self.__dbg('Clubs', ('Got %s clubs' % len(clubs)))

        self.__dbg('Get All', 'Starting member merging')

        for key, club in clubs.items():

            self.__dbg('Clubs', ("%s (%s), Active: %s" % (club['name'], club['id'], club['active'])))

            if club['active'] == False:
                self.__dbg('Clubs', ('%s (%s) is not active, continuing' % (club['name'], club['id'])))
                continue

            # Iterate over get_all_members
            tmp_members = self.get_all_members(club['id'])

            # @todo: Must validate reply here - items?? All objects can be saved as cPicle or pickle then save/load responses to disk!
            if tmp_members == None:
                self.__dbg('Clubs', ('%s (%s) has no members, continuing' % (club['name'], club['id'])))
                continue

            curr_members = tmp_members.copy()
            for member, val in tmp_members.items():

                # Drop if exists already and continue!
                if int(member) in members:
                    members[int(member)]['membership']['fee'] += curr_members[int(member)]['membership']['fee']
                    curr_members.pop(int(member))
                    self.__dbg('Merging', ('Removed %s from list - exists' % member))
                    continue

                # Get liceneses
                try:
                    curr_members[int(member)].update({'licenses': self.get_member_licenses([int(member)])})
                    self.__dbg('Merging', ('%s has licenses, merging' % member))
                except:
                    curr_members[int(member)].update({'licenses': {}})
                    self.__dbg('Merging', ('%s has no licenses, skipping' % member))
                    pass

                # Get current member clubs
                try:
                    member_clubs = self.get_member_clubs(member)
                    curr_members[int(member)]['membership'].update({'clubs': member_clubs})
                    self.__dbg('Merging', ('%s has member clubs, merging' % member))
                except:
                    curr_members[int(member)]['membership'].update(
                        {'clubs': [club['id']]})  # Always member of member club...
                    self.__dbg('Merging', ('%s has no member clubs, skipping' % member))
                    pass

                # Get geolocaiton for location
                if self.do_geo:
                    try:

                        geo = self.get_geo(curr_members[int(member)]['location']['street'],
                                           curr_members[int(member)]['location']['city'],
                                           curr_members[int(member)]['location']['zip'],
                                           curr_members[int(member)]['location']['country'])
                        if geo != None:
                            curr_members[int(member)]['location'].update(
                                {'geo': {"type": "Point", "coordinates": [geo.latitude, geo.longitude]}})
                            curr_members[int(member)]['location'].update({'geo_type': geo.raw['type']})
                            curr_members[int(member)]['location'].update({'geo_class': geo.raw['class']})
                            curr_members[int(member)]['location'].update(
                                {'geo_importance': float(geo.raw['importance'])})
                            curr_members[int(member)]['location'].update({'geo_place_id': int(geo.raw['place_id'])})
                        # curr_members[int(nak)]['location']['geo'].update({'altitude': geo.raw['altitude']})
                    except:
                        # members[val['id']].update({'location': {"type":"Point","coordinates":[0.0,0.0]}})
                        # members[val['id']].update({'location': {}})
                        self.__dbg('Geo', ('Could not geocode %s' % member))
                        pass

            # First iteration vs next
            # Unfortunately this overwrites the old ones..
            if len(members) > 0:
                members.update(curr_members)
            else:
                members = curr_members

        return members
