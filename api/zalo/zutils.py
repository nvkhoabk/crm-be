import requests
from django.conf import settings


class ZaloPage:
    def __init__(self, code='', access_token=''):
        if code:
            self.access_token = self._get_access_token(code)
        if access_token:
            self.access_token = access_token
    
    def _get_access_token(self, code):
        r = requests.post('https://oauth.zaloapp.com/v4/oa/access_token', data={
            'code': code,
            'app_id': settings.ZALO_APP_ID,
            'grant_type': 'authorization_code',
        }, headers={
            'Content-Type': 'application/x-www-form-urlencoded',
            'secret_key': settings.ZALO_APP_SECRET,
        })
        r = r.json()
        if r.get('error', 0) != 0:
            raise

        return r['access_token']

    def get_info(self):
        url = 'https://openapi.zalo.me/v2.0/oa/getoa'
        r = requests.get(url,  headers={'access_token': self.access_token})
        r = r.json()
        if r['error'] != 0:
            raise
        return r['data']

    def get_followers(self):
        offset = 0
        count = 50
        followers = []
        
        while True:
            url = 'https://openapi.zalo.me/v2.0/oa/getfollowers?data={"offset":%d,"count":%d}' % (offset, count)
            
            r = requests.get(url, headers={'access_token': self.access_token})
            r = r.json()
            if r['error'] != 0:
                raise
        
            if r['data']['total'] == 0:
                break
            
            for user in r['data']['followers']:
                followers.append(user['user_id'])

            offset = offset + count
        
        return followers


    def get_follower_message(self, uid):
        offset = 0
        count = 10
        messages = []
        
        while True:
            url = 'https://openapi.zalo.me/v2.0/oa/conversation?data={"offset":%d,"user_id":%s,"count":%d}' % (offset, uid, count)
            
            r = requests.get(url, headers={'access_token': self.access_token})
            r = r.json()
            if r['error'] != 0:
                raise
            
            if len(r['data']) == 0:
                break
            
            for msg in r['data']:
                messages.append(msg['message'])

            offset = offset + count
        
        return messages
