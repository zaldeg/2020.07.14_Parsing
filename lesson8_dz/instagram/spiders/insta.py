import scrapy
import re
import json
from scrapy.http import HtmlResponse
from urllib.parse import urlencode
from copy import deepcopy
from instagram.items import InstagramItem

class InstaSpider(scrapy.Spider):
    def __init__(self, search):
        super().__init__()
        self.users_to_parse = search

    name = 'insta'
    allowed_domains = ['instagram.com']  
    start_urls = ['https://instagram.com/']
    insta_login = 'login'
    insta_pwd = 'pwd'
    inst_login_link = 'https://www.instagram.com/accounts/login/ajax/'

    query_url = 'https://www.instagram.com/graphql/query/?query_hash='
    query_hash_followers = 'c76146de99bb02f6415203be841dd25a'
    query_hash_following = 'd04b0a864b4b54837c0d870b0e77e076'

    def parse(self, response:HtmlResponse):
        csrf_token = self.fetch_csrf_token(response.text)
        yield scrapy.FormRequest(
            self.inst_login_link,
            method='POST',
            callback=self.user_parse,
            formdata={'username': self.insta_login, 'enc_password': self.insta_pwd},
            headers={'X-CSRFToken': csrf_token}
        )
    
    def user_parse(self, response:HtmlResponse):
        j_body = json.loads(response.text)
        for user in self.users_to_parse:
            if j_body['authenticated']:
                yield response.follow(
                    f'/{user}',
                    callback=self.user_info_parse,
                    cb_kwargs={'username':user}
                    )

    def user_info_parse(self, response:HtmlResponse, username):
        user_id = self.fetch_user_id(response.text, username)
        name = self.fetch_name(response.text)
        if name:
            name = name.encode().decode("unicode-escape")
        picture = self.fetch_picture_url(response.text, username)
        if picture:
            picture = picture.encode().decode("unicode-escape")
        item = InstagramItem(
            _id = int(user_id),
            username = username,
            name =  name,
            picture = picture
        )
        yield item

        variables = {
            'id': user_id,
            'first': 50,
            'include_reel': True,
            'fetch_mutual': True
        }
        followers_url = f'{self.query_url}{self.query_hash_followers}&{urlencode(variables)}'
        yield response.follow(
            followers_url,
            callback=self.followers_info_parse,
            cb_kwargs={
                'username':username,
                'user_id':user_id,
                'variables': deepcopy(variables)
            }
        )

        variables = {
            'id': user_id,
            'first': 50,
            'include_reel': True,
            'fetch_mutual': False
        }
        followers_url = f'{self.query_url}{self.query_hash_following}&{urlencode(variables)}'
        yield response.follow(
            followers_url,
            callback=self.following_info_parse,
            cb_kwargs={
                'username':username,
                'user_id':user_id,
                'variables': deepcopy(variables)
            }
        )

    def followers_info_parse(self, response:HtmlResponse, username, user_id, variables):
        j_data = json.loads(response.text)
        
        page_info = j_data.get('data').get('user').get("edge_followed_by").get('page_info')
        if page_info.get('has_next_page'):
            variables['after'] = page_info.get('end_cursor')
        followers_url = f'{self.query_url}{self.query_hash_followers}&{urlencode(variables)}'        
        yield response.follow(
            followers_url,
            callback=self.followers_info_parse,
            cb_kwargs={
                'username':username,
                'user_id':user_id,
                'variables': deepcopy(variables)
            }
        )

        follower_data = j_data.get('data').get('user').get("edge_followed_by").get('edges')
        for follower in follower_data:
            node = follower.get('node')
            item = InstagramItem(
                _id = user_id,
                follower_id = node.get('id'),
                username = node.get('username'),
                name = node.get('full_name'),
                picture = node.get('profile_pic_url')
            )
            yield item
    

    def following_info_parse(self, response:HtmlResponse, username, user_id, variables):
        j_data = json.loads(response.text)
        page_info = j_data.get('data').get('user').get("edge_follow").get('page_info')
        if page_info.get('has_next_page'):
            variables['after'] = page_info.get('end_cursor')
        followers_url = f'{self.query_url}{self.query_hash_following}&{urlencode(variables)}' 
        yield response.follow(
            followers_url,
            callback=self.following_info_parse,
            cb_kwargs={
                'username':username,
                'user_id':user_id,
                'variables': deepcopy(variables)
            }
        )
        following_data = j_data.get('data').get('user').get("edge_follow").get('edges')

        for following in following_data:
            node = following.get('node')
            item = InstagramItem(
                _id = user_id,
                followed_id = node.get('id'),
                username = node.get('username'),
                name = node.get('full_name'),
                picture = node.get('profile_pic_url')
            )
            yield item



    def fetch_csrf_token(self, text):
        matched = re.search('\"csrf_token\":\"\\w+\"', text).group()
        return matched.split(':').pop().replace(r'"', '')

    def fetch_user_id(self, text, username):
        matched = re.search(
            '{\"id\":\"\\d+\",\"username\":\"%s\"}' % username, text
        ).group()
        return json.loads(matched).get('id')
    
    def fetch_name(self, text):
        matched = re.search(r'"Person","name":"(.*?)","alternateName"', text)
        if matched:
            matched = matched.group(1)
        return matched

    def fetch_picture_url(self, text, username):
        matched = re.search(f'(http?[^"]+)","requested_by_viewer":false,"username":"{username}"', text)
        if matched:
            matched = matched.group(1)
        return matched