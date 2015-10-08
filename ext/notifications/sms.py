""""

    Send SMS via sendega.com
    ~~~~~~~~~~~~~~~~~~~~~~~~
    
    Using suds
        
"""

from ext.app.decorators import async
from flask import current_app as app

from suds.client import Client
import logging

from ..scf import Scf


class Sms():
    
    def __init__(self):
        
        self.c = Scf()
        self.config = self.c.get_sms()
        self.prod = self.c.is_production()
        
        print(self.config)
    
    @async
    def send_async(self,mobile, message, client):
    
        #print client
        result = client.service.Send(username = self.get_username(),
                                        password = self.get_password(),
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
        
        
    def send(self, mobile, message):
        """ Loops through and fixes everything about phone numbers etc
        @todo: verify mobile number - norwegian ONLY
        @todo: verify message length, we do not allow...
        """
        url = "https://smsc.sendega.com/Content.asmx?WSDL"
        client = Client(url)
        client.set_options(port='ContentSoap')
        
        send_sms_async(mobile, message, client)
        
        
    def get_username(self):
        
        return self.config.get('username')
    
    def get_password(self):
        
        return self.config.get('password')
    