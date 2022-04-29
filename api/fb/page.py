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

    def get_page_posts(self, page_id):
        post_ids = {}
        total_posts = []

        posts = self.graph.request('/me/posts?fields=permalink_url,message,created_time')
        while 'paging' in posts:
            for post in posts['data']:
                if post_ids.get(post['id']):
                    return total_posts
                total_posts.append(post)
                post_ids[post['id']] = True
            if 'next' in posts['paging']:
                posts = requests.get(posts['paging']['next']).json()
            else:
                break

        return total_posts

    def get_page_comments(self, post_id):
        comment_ids = {}
        total_comments = []

        comments = self.graph.request(post_id + '/comments')
        while 'paging' in comments:
            for comment in comments['data']:
                if comment_ids.get(comment['id']):
                    continue
                total_comments.append(comment)
                comment_ids[comment['id']] = True
            if 'next' in comments['paging']:
                comments = requests.get(comments['paging']['next']).json()
            else:
                break

        return total_comments

    def get_page_messages(self):
        message_ids = {}
        total_messages = []
        
        messages = self.graph.request('me?fields=conversations{id,messages{message},senders}')
        if not messages.get('conversations'):
            return total_messages
        messages = messages['conversations']
        while 'paging' in messages:
            for message in messages['data']:
                message['messages'] = self._get_all_message(message)
                if message_ids.get(message['id']):
                    continue 
                total_messages.append(message)
                message_ids[message['id']] = True
            if 'next' in messages['paging']:
                messages = requests.get(messages['paging']['next']).json()
            else:
                break

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
    