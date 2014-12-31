
from transitions import Machine

from flask import current_app as app
from bson.objectid import ObjectId

from pprint import pprint

from eve.methods.patch import patch_internal

class ObservationWorkflow(Machine):
    
    
    
    def __init__(self,object_id=None,initial_state=None, user_id=None):
        
        self.user_id = user_id
        # The states
        # states 'name', 'on_enter', 'on_exit'
        self._states=['draft', 'ready', 'pending_review_hi', 'pending_review_fs', 'pending_review_su', 'closed', 'withdrawn']
        
        self._state_attrs = {'draft': {'title': 'Draft', 'description': 'Draft'},
                     'ready': {'title': 'Ready', 'description': 'Ready to send for review'},
                     'pending_review_hi': {'title': 'Pending review', 'description': 'Pending review by HI'},
                     'pending_review_fs': {'title': 'Pending review', 'description': 'Pending review by Fagsjef'},
                     'pending_review_su': {'title': 'Pending review', 'description': 'Pending review by SU'},
                     'closed': {'title': 'Closed', 'description': 'Observation is closed'},
                     'withdrawn': {'title': 'Withdrawn', 'description': 'Observation is withdrawn'},
                     }
                     
        """ And some transitions between states. We're lazy, so we'll leave out 
        the inverse phase transitions (freezing, condensation, etc.).
        name, source, dest
        
        This is event chaining methods/functions
        Callbacks: after, before
        conditions: is_flammable, is_something
        
        Apply to all states
        machine.add_transition('to_liquid', '*', 'liquid')
        
        Linear states:
        machine.add_ordered_transitions()
        
        machine.next_state()
        
        WISHLIST:
        states: should also have an extended version, say {'name':'state_name', 'attr': {whatever you like}
        trigger: dict name, title='approve' or a attributes = {} just to hold some shait!
        conditions: takes arguments (event) like after & before!!
        permissions: should be a condition maybe? Conditions will always be first (now we send event_data on conditions)
        All: Set callbacks on _all_ transitions (say has_permission etc)
        
        
        """
        
        """
        Workflows has also wathcers, so call them when something happens!
        And all involved ARE watchers, aren't they=
        
        """
        
        # def __init__(self, source, dest, conditions=None, before=None, after=None)
        
        """ The transition definition
        """
        self._transitions = [
            { 'trigger': 'set_ready', 'source': 'draft', 'dest': 'ready', 'after': 'save_workflow', 'conditions':['has_permission']},
            { 'trigger': 'send_to_hi', 'source': 'ready', 'dest': 'pending_review_hi', 'after': 'save_workflow', 'conditions':['has_permission']},
            { 'trigger': 'withdraw', 'source': ['draft', 'ready'], 'dest': 'withdrawn', 'after': 'save_workflow', 'conditions':['has_permission']},
            { 'trigger': 'reopen', 'source': 'withdrawn', 'dest': 'draft', 'after': 'save_workflow', 'conditions':['has_permission']},
            
            { 'trigger': 'reject_hi', 'source': 'pending_review_hi', 'dest': 'draft', 'after': 'save_workflow', 'conditions':['has_permission']},
            { 'trigger': 'approve_hi', 'source': 'pending_review_hi', 'dest': 'pending_review_fs', 'after': 'save_workflow', 'conditions':['has_permission']},
            
            { 'trigger': 'reject_fs', 'source': 'pending_review_fs', 'dest': 'pending_review_hi', 'after': 'save_workflow', 'conditions':['has_permission']},
            { 'trigger': 'approve_fs', 'source': 'pending_review_fs', 'dest': 'pending_review_su', 'after': 'save_workflow', 'conditions':['has_permission']},
            
            { 'trigger': 'reject_su', 'source': 'pending_review_su', 'dest': 'pending_review_fs', 'after': 'save_workflow', 'conditions':['has_permission']},
            { 'trigger': 'approve_su', 'source': 'pending_review_su', 'dest': 'closed', 'after': 'save_workflow' , 'conditions':['has_permission']},
            { 'trigger': 'reopen_su', 'source': 'closed', 'dest': 'pending_review_fs', 'after': 'save_workflow', 'conditions':['has_permission']},
            
            #{'trigger': '*', 'source': '*', 'dest': '*', 'after': 'save_workflow'},
            ]
        
        # Users - Groups
        su = [5766, 4455, 3322, 32233, 45199]
        fs = [5766, 45199]
        hi = [45199]
        owner = [45199]
        #self.user_id 
        
        """ Extra attributes needed for sensible feedback from API to client
        """
        self._trigger_attrs = {'set_ready': {'title': 'Set Ready', 'action': 'Set Ready', 'resource': 'approve', 'comment': False, 'permission': list(set(owner))},
                              'send_to_hi': {'title': 'Send to HI', 'action': 'Send to HI', 'resource': 'approve','comment': True, 'permission': list(set(owner))},
                              'withdraw': {'title': 'Withdraw Observation', 'action': 'Withdraw', 'resource': 'withdraw','comment': True, 'permission': list(set(owner))},
                              'reopen': {'title': 'Reopen Observation', 'action': 'Reopen', 'resource': 'reopen','comment': True, 'permission': list(set(owner))},
                              'reject_hi': {'title': 'Reject Observation', 'action': 'Reject', 'resource': 'reject','comment': True, 'permission': list(set(hi + fs))},
                              'approve_hi': {'title': 'Approve Observation', 'action': 'Approve', 'resource': 'approve','comment': True, 'permission': list(set(hi))},
                              'reject_fs': {'title': 'Reject Observation', 'action': 'Reject', 'resource': 'reject','comment': True, 'permission': list(set(fs))},
                              'approve_fs': {'title': 'Approve Observation', 'action': 'Approve', 'resource': 'approve','comment': True, 'permission': list(set(fs))},
                              'reject_su': {'title': 'Reject Observation', 'action': 'Reject', 'resource': 'reject','comment': True, 'permission': list(set(su))},
                              'approve_su': {'title': 'Approve Observation', 'action': 'Approve', 'resource': 'approve','comment': True, 'permission': list(set(su))},
                              'reopen_su': {'title': 'Reopen Observation', 'action': 'Reopen', 'resource': 'reopen','comment': True, 'permission': list(set(su + fs))},
                              }
        
        """ Make sure to start with a defined state!
        """
        
        col = app.data.driver.db['anomalies']
        
        self.db_wf = col.find_one({'_id': ObjectId(object_id)}, {'workflow': 1}) #, '_etag': 1
        
        pprint(self.db_wf)
        
        print(self.db_wf.get('workflow').get('state'))
        
        initial_state = self.db_wf.get('workflow').get('state')
        
        if initial_state == None or initial_state not in self._states:
            self.initial_state = 'draft'
        else:
             self.initial_state = initial_state
             
        Machine.__init__(self, states=self._states, send_event=True, transitions=self._transitions, initial=self.initial_state)

        
    def get_actions(self):
        
        events = []
        for transition in self._transitions:
            if self.state in transition['source']:
                events.append(transition['trigger'])
                
        return events
    
    def get_resource_mapping(self):
        """ This will return a dict containing a mapping of resource => trigger
        Example: {'approve': 'approval_from_someone'}
        resource should be utilised in the endpoint/resource and trigger is the callee trigger method in the workflow
        """
        events = {}
        for transition in self._transitions:
            if self.state in transition.get('source', None):
                events.update({self._trigger_attrs.get(transition['trigger']).get('resource'): transition['trigger']})
                
        return events 
    
    def get_resources(self):
        
        resources = []
        
        for event in self.get_actions():
            
            resources.append(self._trigger_attrs.get(event))
            
        return resources
    
    def get_current_state(self):
        
        d = {'state': self.state}
        d.update(self._state_attrs[self.state])
        d.update({'actions': self.get_resources()})
        
        return d
    
    
    def get_allowed_users_for_transitions(self):
        
        # Should return users allowed for this transition!
        return NotImplemented
    
    def has_permission(self, event): 
        """ No events sendt by conditions...
        if event.kwargs.get('user_id', 0) in self.trigger_permissions:
            return True
        return False"""
        
        print("%s is the current transition " % event.event.name)
        if self.user_id in self._trigger_attrs.get(event.event.name).get('permission'):
            print("%s has permission" % self.user_id)
            return True
        
        print("%s has not permission" % self.user_id)
        return False
    
    def condition_completed_tasks(self):
        
        #Check if has completed all tasks,
        # Have "current tasks" and then
        print("AUDIT")
        pprint(self.db_wf['workflow']['audit'])
        return self.db_wf['workflow']['audit']
        
    
    def get_audit(self):
        
        # Get which trigger where done, and by who?
        # This is called before the save_state
        
        print("AUDIT")
        trail = {'trail': self.db_wf['workflow']['audit']}
        pprint(trail)
        return trail
    
    def save_state(self):
        
        # app.data... update OR patch_internal
        # Save *.workflow dictionary
        
        return NotImplemented
        
    def save_workflow(self,event):
        """ Will only trigger when it actually IS changed, so save every time this is called!
        patch_internal(self.known_resource, data, concurrency_check=False,**{'_id': self.item_id})
        patch_internal(resource, payload=None, concurrency_check=False,skip_validation=False, **lookup):
        
        Hmmm, need audit trail since version control will not cut this. Workflow should also increase the number
        """
        _id = self.db_wf.get('_id')
        _etag = self.db_wf.get('_etag')
        self.db_wf.get('workflow').update({'state': self.state})
        
        # Make a new without _id etc
        new = {'workflow': self.db_wf.get('workflow')}

        # Should really supply the e-tag here, will work! , '_etag': _etag
        result = patch_internal("observations", payload=new, concurrency_check=False, **{'_id': "%s" % _id})
        
        pprint(result)
        
        if self.state != self.initial_state:
            print("SAVING WORKFLOW NOW!!!")
        else:
            print("No changes, should not change it should I?")    
    
