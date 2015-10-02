"""

    Notifications
    =============
    
    Using threading to send email and sms notifications async_chat
    
"""

from ext.app.decorators import async
from flask import current_app as app

from suds.client import Client
import logging

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from ..scf import Scf

class Notification():
    
    def __init__(self):
        
        config = Scf()
        self.c = config.get_email()
        self.prod = config.is_production()
        

    @async
    def send_email_async(self, message, recepient, prefix, subject):
        
        if not self.prod:
            message = '--- ORS TEST ---\r\n\r\n%s\r\n\r\n--- ORS TEST ---' % message
            prefix = '%s TEST' % prefix
            
        msg = MIMEText(message, 'plain')
        msg['From'] = 'FNLF ORS <%s>' % self.c['from']
        msg['Subject'] = '[%s] %s' % (prefix, subject)
        msg['To'] = '%s <%s>' % (recepient['name'], recepient['email'])
        msg.preamble = 'Notification'
        
        s = smtplib.SMTP(self.c['smtp'], self.c['smtp_port'])
        s.ehlo()
        s.starttls()
        s.ehlo()
        s.login(self.c['username'], self.c['password'])
        s.send_message(msg)
        s.quit()
    #http://sendega.com/support/ofte-stilte-spoersmaal-%28faq%29/
    
    #logging.basicConfig(level=logging.INFO)
    #logging.getLogger('suds.client').setLevel(logging.DEBUG)
    #logging.getLogger('suds.transport').setLevel(logging.DEBUG)
    #logging.getLogger('suds.wsdl').setLevel(logging.DEBUG)
    #logging.getLogger('suds.xsd.schema').setLevel(logging.DEBUG)
    
    @async
    def send_sms_async(self,mobile, message, client):
    
        #print client
        result = client.service.Send(username = self.sms_username,
                                        password = self.sms_password,
                                        sender = "FNLF ORS",
                                        destination = mobile,
                                        pricegroup = 0,
                                        contentTypeID = 1,
                                        contentHeader = "",
                                        content = message,
                                        dlrUrl = "https://smsc.sendega.com/Content.asmx?wsdl",
                                        ageLimit = 0,
                                        extID = "",
                                        sendDate = "",
                                        refID = "",
                                        priority = 0,
                                        gwID = 0,
                                        pid = 0,
                                        dcs = 0)
        ##
        #(SendResult){
        #MessageID = "703cd4f8-b2f7-4396-853c-60b98388a8d0"
        #ErrorNumber = 0
        #Success = True
        #}
        return
    
    
    def send_email(self, recepients, subject, message, prefix='ORS'): #, recepients, subject, message, message_html=None, prefix=None
        """ Sends email via async after setting some values
        """
        
        for r in recepients:
            #message, recepient, prefix, subject):
            self.send_email_async( message, r, prefix, subject)
        
        
    def send_sms(self, mobile, message):
        """ Loops through and fixes everything about phone numbers etc
        """
        url = "https://smsc.sendega.com/Content.asmx?WSDL"
        client = Client(url)
        client.set_options(port='ContentSoap')
        
        send_sms_async(mobile, message, client)
        
    def notify(self, msg, to, via):
        """ to should actually be a list of id's
        Then just resolve phone and email
        """
        
        if via == 'sms':
            pass
        elif via == 'email':
            pass
        
        


