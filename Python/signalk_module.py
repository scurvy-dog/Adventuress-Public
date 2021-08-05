import json
import requests


# Define the object class for the module to be called externally
class signalk:
    '''SignalK api object'''
    
    def __init__ (self, user, passwd, ip, port):
        '''initialize values'''
        '''expect coord to be dictionary'''
        self.user = user
        self.passwd =passwd
        self.ip = ip
        self.port = port
        self.token = None

    def Open(self):
        
        error_code = None
        auth_url = "http://" + self.ip + ":" + self.port + "/signalk/v1/auth/login"

        # Creat authentication header and body.
        payload = json.dumps({
            "username": self.user,
            "password": self.passwd
        })

        headers = {
            'Content-Type': 'application/json'
        }

        # Generate token from SignalK server
        response = requests.request("POST", auth_url, headers=headers, data=payload)

        # Fetch authentication token
        ### ADD ERROR HANDLING BEFORE EXECUTING
        a = response.json()

        for k, v in a.items():
            if k == "token":
                self.token = v
        payload={}


        return error_code

    def Get(self,uri):
        # Make a API GET call to SignalK and return value
        error_code =  None
        payload = {}

        # Construct URL
        rest_url = "http://" + self.ip + ":" + self.port + "/signalk/v1/api/vessels/self" + uri
        headers = {
        'Authorization': 'Bearer ' + self.token
        }
        
        try:
            response = requests.request("GET", rest_url, headers=headers, data=payload)
            response.raise_for_status()
            response_dict = response.json()
        except requests.exceptions.ConnectionError as err:
            error_code = err
            return error_code, None
        except requests.exceptions.HTTPError as err:
            error_code = err
            return error_code, None
        
        return error_code, response_dict
