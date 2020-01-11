# -*- coding: utf-8 -*-
"""
Created on Thu Dec 27 13:45:05 2018

@author: foryou
"""

from Module.aes_crypto import Cryption
import os
import json
import pickle

class Cookie:
    def __init__(self):
        self.cryption = Cryption()
        self.key = self.cryption.sha256(os.path.dirname(os.path.abspath(__file__)))
        self.cookie_path = r"Module\cookies.pkl"
        self.cookie_json_path = r'C:\Users\foryou\comic_cookie.json'
        self.cookie = None
        self.account_json_path = r'C:\Users\foryou\account.json'
        self.account = None
        self.password = None
        
    def save_cookie(self, cookies, index):
        self.cookie = cookies[index]['value']
        self.encryption()
        cookies[index]['value'] = self.cookie
        pickle.dump(cookies , open(self.cookie_path, "wb"))
        
    def get_cookie(self):
        if (not os.path.isfile(self.cookie_path)) or (not os.path.isfile(self.cookie_json_path)):
            return False
        self.decryption()
        cookies = pickle.load(open(self.cookie_path, "rb"))
        for index, cookie in enumerate(cookies):
            if cookie['name'] == 'my':
                cookies[index]['value'] = self.cookie
                
        return cookies
        
    def encryption(self):
        cookie_encypt = self.cryption.encryption(self.key, self.cookie)
        default = {"Cookie" : cookie_encypt, "Iv" : self.cryption.iv}
        self.cookie = cookie_encypt
        with open(self.cookie_json_path, 'w') as f:
            json.dump(default, f)
            
    def decryption(self):
        with open(self.cookie_json_path, 'r') as r:
            user_json = json.load(r)
            self.cookie = self.cryption.decryption(self.key, user_json['Iv'], user_json['Cookie'])
          
    def save_account(self):
        account = ""
        password = ""
        account_encypt = self.cryption.encryption(self.key, account)
        password_encypt = self.cryption.encryption(self.key, password)
        default = {"Account" : account_encypt, "Password" : password_encypt, "Iv" : self.cryption.iv}
        with open(self.account_json_path, 'w') as f:
            json.dump(default, f)
        
    def get_account(self):
        with open(self.account_json_path, 'r') as r:
            user_json = json.load(r)
            self.account = self.cryption.decryption(self.key, user_json['Iv'], user_json['Account'])
            self.password = self.cryption.decryption(self.key, user_json['Iv'], user_json['Password'])
        
#if __name__ == '__main__':
#    cookie = Cookie()
#    cookie.save_account()
#    get_account()
    
    