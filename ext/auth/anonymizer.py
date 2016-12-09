from flask import current_app as app
from bson.objectid import ObjectId
import ext.auth.acl as acl_helper
import sys
from pprint import pprint

class Anon(object):

    def __init__(self):
        self.persons = []

    def assign(self, person):
        """Keep track of all assigned persons"""
        if person in self.persons:
            return -1 * (self.persons.index(person) + 1)
        else:
            self.persons.append(person)
            #self.persons = list(set(self.persons))
            return -1 * (self.persons.index(person) + 1)

        return 0

    def assign_x(self, x):
        """Take the whole array part, modify id and tempname, return whole array"""

        if not 'id' in x:
            x['id'] = 0

        elif 'id' in x and 'tmpname' not in x:
            print("ID: %s" % x['id'])
            if x['id'] > 0:
                x['id'] = self.assign(x['id'])
            else:
                print("X her: " % x)

        elif 'id' in x and 'tmpname' in x:
            print("ID TMP: %s %s" % (x['id'], x['tmpname']))
            if x['id'] > 0:
                x['id'] = self.assign(x['id'])
            else:
                x['id'] = self.assign(x['id'])


        elif 'id' not in x and 'tmpname' in x:
            print("TMP: %s" % x['tmpname'])
            x['id'] = 0 #self.assign(x['tmpname'])

        else:
            print("ERROR")
            x['id'] = 0

        #Always delete tmpname!
        if 'tmpname' in x:
            del x['tmpname']

        print("NEW: %s" % x['id'])
        return x


    def assign_pair(self,x):
        return self.assign_x(x)


def anonymize_obs(item):
    """ Anonymizes based on a simple scheme
    Only for after_get_observation
    Should see if solution to have association of user id to a fixed (negative) number for that id to be sorted as "jumper 1", "jumper 2" etc in frontend
    @todo: remove anon files from list 
    @todo: add check for nanon's (non-anon) which should return item directly
    @todo: see if you are involved then do not anon that?
    @todo: for workflow see if all involved should be added to nanon or seperate logic to handle that?
    @todo: add "hopper 1" "hopper 2" etc involved[45199] = -3

        try:
                item['involved'][key] = anon.assign_pair(item['involved'][key])

            except KeyError:
                app.logger.info("Keyerr 1")
                pass
            except:
                app.logger.info("Unexpected error 1: %s" % sys.exc_info()[0])
                pass
    """

    anon = Anon()

    if 'audit' not in item['workflow']:
        item['workflow']['audit'] = []

    if 'involved' not in item:
        item['involved'] = []

    if 'components' not in item:
        item['components'] = []

    # Involved
    for key, val in enumerate(item['involved']):
        item['involved'][key] = anon.assign_pair(item['involved'][key])

        # Involved.gear -> rigger
        if 'gear' in item['involved'][key]:
            if 'rigger' in item['involved'][key]['gear']:
                item['involved'][key]['gear']['rigger'] = anon.assign_pair(item['involved'][key]['gear']['rigger'])


    # Involved in components
    for key, val in enumerate(item['components']):

        for k, v in enumerate(item['components'][key]['involved']):
            item['components'][key]['involved'][k] = anon.assign_pair(item['components'][key]['involved'][k])



    # Organization
    for key, val in enumerate(item['organization']):

        if 'hl' in item['organization']:
            for k, hl in enumerate(item['organization']['hl']):
                item['organization']['hl'][k] = anon.assign_pair(item['organization']['hl'][k])

        if 'hfl' in item['organization']:
            for k, hfl in enumerate(item['organization']['hfl']):
                item['organization']['hfl'][k] = anon.assign_pair(item['organization']['hfl'][k])

        if 'hm' in item['organization']:
            for k, hm in enumerate(item['organization']['hm']):
                item['organization']['hm'][k] = anon.assign_pair(item['organization']['hm'][k])

        if 'pilot' in item['organization']:
            for k, pilot in enumerate(item['organization']['pilot']):
                item['organization']['pilot'][k] = anon.assign_pair(item['organization']['pilot'][k])

    # Files
    try:
        item['files'][:] = [d for d in item['files'] if d.get('r') != True]
    except:
        app.logger.info("File error: %s" % sys.exec_info()[0])
        pass

    # Workflow audit trail
    for key, val in enumerate(item['workflow']['audit']):

        try:
            if item['workflow']['audit'][key]['a'] in ['init', 'set_ready', 'send_to_hi', 'withdraw']:
                item['workflow']['audit'][key]['u'] = anon.assign(item['workflow']['audit'][key]['u'])
        except KeyError:
            app.logger.info("Keyerror 4")
            pass
        except:
            app.logger.info("Unexpected error 4: %s" % sys.exc_info()[0])
            pass

    # Reporter AND owner
    item['reporter'] = anon.assign(item['reporter'])
    item['owner'] = anon.assign(item['owner'])

    return item

    return {}

def has_permission_obs(id, type):
    """ Checks if has type (execute, read, write) permissions on an observation or not
    Only for after_get_observation
    @note: checks on list comprehension and returns number of intersects in list => len(list) > 0 == True
    @bug: Possible bug if user comparison is int vs float!
    @todo: Should not be execute rights? Or could it be another type 'noanon' or if in users with read right? 
    """
    
    return acl_helper.has_permission(ObjectId(id), type, 'observations')
    
    return False
