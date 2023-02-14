import requests
import re, os
from bs4 import BeautifulSoup

class Authentication:
    def OauthAuthorize(self):
        self.LoginIn()
        oauth_url = 'https://www.tistory.com/oauth/authorize?client_id={0}&redirect_uri={1}&response_type=code&state={2}'.format(
            self.app_id, self.callback_url, '')
        res = requests.get(oauth_url)
        return res

    def AccessCodeExtraction(self):
        res = self.OauthAuthorize()
        soup2 = BeautifulSoup(res.text, 'html.parser')
        
        candidates = soup2.findAll("script")
        
        p = re.compile("(?<=\?code=)[a-zA-Z:/0-9?=]*")
        
        m = p.search(str(candidates[0]))
        
        code = m.group()
        return code

    def GetAccessToken(self):
        code = self.AccessCodeExtraction()
        token_url = "https://www.tistory.com/oauth/access_token?client_id={0}&client_secret={1}&redirect_uri={2}&code={3}&grant_type=authorization_code".format(
            self.appid, self.secret_key, self.callback_url, code)

        res = requests.get(token_url)
        access_token = res.text.split("=")[1]
        return access_token
    
    