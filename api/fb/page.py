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
        profile = self.graph.get_object('me', fields='id,name,picture')
        self.uid = profile.get('id')
        self.name = profile.get('name')
        return profile

    def get_page_posts(self, page_id, offset, limit):
        posts = self.graph.request(
            '{}/posts?offset={}&limit={}&fields=permalink_url,message,full_picture,created_time,updated_time'.format(
                page_id,
                offset, limit))
        return posts['data']

    def get_page_comments(self, post_id, offset, limit):
        comments = self.graph.request('{}/comments?summary=1&order=reverse_chronological&filter=stream&offset={}&limit={}'.format(post_id, offset, limit))
        return comments['data']

    def dump_comment_hierarchy_to_json(self, comment_id):
        top_level = self._get_top_level(comment_id)
        comments = self.graph.request(
            '{}/comments?fields=parent{{id}},message,from,created_time'.format(top_level['id']))
        comment_map = dict()
        top_level['children'] = []
        comment_map[top_level['id']] = top_level

        for comment in comments['data']:
            comment['children'] = []
            if 'from' not in comment:
                comment['from'] = {
                    "name": "Người dùng facebook",
                    "id": "0"
                }
            comment_map[comment['id']] = comment

        for comment in comments['data']:
            comment_map[comment['parent']['id']]['children'].append(comment)

        return json.dumps(top_level)

    def get_page_messages(self, page_id, offset, limit):
        total_messages = []
        
        messages = self.graph.request('{}/conversations/?offset={}&limit={}'.format(page_id, offset, limit) +'&fields=id,senders,created_time,updated_time,messages{message,from,created_time,attachments}')

        for message in messages['data']:
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

    def _get_top_level(self, comment_id):
        comment = self.graph.request(
            '{}?fields=parent,message,from,created_time'.format(comment_id))
        while 'parent' in comment:
            comment = self.graph.request(
                '{}?fields=parent,message,from,created_time'.format(comment['parent']['id']))

        return comment
    