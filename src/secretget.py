import os
import hvac

class Secret:

    def __init__(self):
        self.vault_url = "http://192.168.2.213:8200"
        self.access_token = "s.x2w1UWjrByrIwpG9qy7jXRO6"


    def get_secret(self,secret_path):
        client = hvac.Client()
        client = hvac.Client(
          url=self.vault_url,
          token=self.access_token
        )       
        return client.read(secret_path)



# list_keys = [ "consumer_key", "consumer_secret" ]
# print(type(list_keys))
# secret_path = 'code/code/stockfi/twitter'
# con_secret = Secret()
# print(con_secret.get_secret(secret_path))

