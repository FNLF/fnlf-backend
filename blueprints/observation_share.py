
from flask import Blueprint, current_app as app, request, Response, abort, jsonify
from bson import json_util
import json

from eve.methods.patch import patch_internal

# Need custom decorators
from ext.app.decorators import *

from ext.auth.helpers import Helpers
from ext.notifications.email import Email  # , Sms

ObsShare = Blueprint('Observation Share', __name__,)

@ObsShare.route("/<int:observation_id>", methods=['POST'])
@require_token()
def share_observation(observation_id):

    try:
        args = request.get_json() #use force=True to do anyway!
        users = args.get('recepients')

        mail = Email()
        helper = Helpers()

        recepients = helper.get_melwin_users_email(users)
        action_by = helper.get_user_name(app.globals.get('user_id'))

        subject = '%s har delt observasjon #%i' % (action_by, observation_id)

        message = {}
        message.update({'observation_id': observation_id})
        message.update({'action_by': action_by})
        message.update({'action': 'delt'})
        message.update({'title': args.get('title')})
        #message.update({'club': self.helper.get_melwin_club_name(self.db_wf.get('club'))})
        message.update({'date': datetime.today().strftime('%Y-%m-%d %H:%M')})
        message.update({'url': 'app/obs/#!/observation/report/%i\n' % observation_id})
        message.update({'url_root': request.url_root})
        message.update({'comment': args.get('comment')})
        message.update({'context': 'shared'})

        mail.add_message_html(message, 'ors')
        mail.add_message_plain(message, 'ors')

        mail.send(recepients, subject, 'ORS')

        return Response(json.dumps({'status': 'ok', 'code': 200}),  mimetype='application/json')
    except Exception as e:
        app.logger.error("Error sending share observation")

    return Response(json.dumps({'status': 'error', 'code': 500}), mimetype='application/json')