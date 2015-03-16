
from flask import Blueprint, current_app as app, request, Response, abort, jsonify
from bson import json_util
import json

from eve.methods.patch import patch_internal

# Need custom decorators
from ext.decorators import *

from ext.helpers import helpers
from ext.notification import notification

ObsShare = Blueprint('Observation Share', __name__,)

@ObsShare.route("/<int:observation_id>", methods=['POST'])
@require_token()
def share_observation(observation_id):
    
    args = request.get_json() #use force=True to do anyway!
    users = args.get('recepients')
    # Notify!
    notify = notification()
    helper = helpers()
    
    recepients = helper.get_melwin_users_email(users)
    
    action_by = helper.get_user_name(app.globals['user_id'])
    
    subject = '%s har delt observasjon #%i' % (action_by, observation_id)
    
    message = '%s\n' % subject
    message += '\n'
    message += 'Tittel:\t %s\n' % args.get('title')
    message += 'Av:\t %s\n' % action_by
    message += 'Dato:\t %s\n' % datetime.today().strftime('%Y-%m-%d %H:%M')
    message += 'Url:\t %sapp/obs/#!/observation/report/%i\n' % (request.url_root, observation_id)
    message += '\nMelding:\n'
    message += args.get('comment')
    print(recepients)
    notify.send_email(recepients, subject, message)
    
    return Response(json.dumps({'status': 'ok', 'code': 200}),  mimetype='application/json')