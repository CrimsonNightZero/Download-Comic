# -*- coding: utf-8 -*-
"""
Created on Sun Nov 25 16:12:19 2018

@author: foryou
"""

from Module.Chrome import Chrome
from Module.Cookie import Cookie
from Module.google_drive_quickstart import GoogleDrive


class Comic:
    def __init__(self):
        self.comic_cookie = Cookie()
        self.chrome = self.start_chrome()
        self.googleDrive = GoogleDrive()
        
    def start_chrome(self):
        chrome = Chrome()
        cookies = self.comic_cookie.get_cookie()
        if (not cookies) or (not chrome.load_cookie(cookies)):
            self.comic_cookie.get_account()
            cookie, index = chrome.login(self.comic_cookie.account, self.comic_cookie.password)
            self.comic_cookie.save_cookie(cookie, index)
        
        return chrome
        
    def all_comic_process(self):
        for comic_list_url in self.chrome.comic_list():
            for stage_list_url in self.chrome.stage_list(comic_list_url):
                self.chrome.page_process(stage_list_url)
                
    def comic_stage_process(self, stage_url):
        self.chrome.page_process(stage_url)
        
    def comic_process(self, comic_url):
        for stage_list_url in self.chrome.stage_list(comic_url):
            self.chrome.page_process(stage_list_url)
            
    def comic_search_page_process(self):
        print(self.chrome.serach_page())
        
        
if __name__ == "__main__":  
    comic = Comic()
    comic.chrome.download_folder = r'D:\Google 雲端硬碟\Comic\Catalog\ONE PIECE航海王\第928話'
#    comic.chrome.image_merge()
#    aaaa
#    comic.all_comic_process()
    # comic_url = "https://tw.manhuagui.com/comic/1128/"
    # comic.comic_process(comic_url)
    
    # stage_url = "https://tw.manhuagui.com/comic/1128/409057.html"
    # comic.comic_stage_process(stage_url)
    
    # comic.chrome.close_browser()
    comic.comic_search_page_process()
