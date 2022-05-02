import facebook
import json
import requests


class FBPageUtil:
    def __init__(self, access_token):
        self.access_token = access_token
        self.graph = facebook.GraphAPI(access_token)

    def get_pages(self):
        uri = 'https://graph.facebook.com/{}/accounts?fields=name,access_token&access_token={}'.format(self.uid, self.access_token)
        response = requests.get(uri)
        response = response.json()
        return response['data']
    
    def get_user_info(self):
        profile = self.graph.get_object('me', fields='id,name')
        self.uid = profile.get('id')
        self.name = profile.get('name')
        return profile

    def get_page_posts(self, page_id, offset, limit):
        posts = self.graph.request('/{}/posts?offset={}&limit={}&fields=permalink_url,message,created_time'.format(page_id, offset, limit))
        return posts['data']

    def get_page_comments(self, post_id, offset, limit):
        comments = self.graph.request('{}/comments?offset={}&limit={}'.format(post_id, offset, limit))
        return comments['data']

    def get_page_messages(self, page_id, offset, limit):
        total_messages = []
        
        messages = self.graph.request('{}/conversations/?offset={}&limit={}'.format(page_id, offset, limit) +'&fields=id,messages{message},senders')

        for message in messages['data']:
            message['messages'] = self._get_all_message(message)
            total_messages.append(message)

        return total_messages

    def _get_all_message(self, message):
        message_ids = {}
        result = []
        messages = message['messages']
        
        while 'paging' in messages:
            for message in messages['data']:
                if message_ids.get(message['id']):
                    continue
                result.append(message['message'])
                message_ids[message['id']] = True
            if 'next' in messages['paging']:
                messages = requests.get(messages['paging']['next']).json()
            else:
                break
        
        return result
    