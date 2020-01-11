# -*- coding: utf-8 -*-
"""
Created on Thu Dec 27 01:33:23 2018

@author: foryou
"""
import requests
#from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait

import time
import re
import os
from tqdm import tqdm
import shutil
from io import BytesIO
from PIL import Image
import zipfile
from Module.google_drive_quickstart import GoogleDrive

headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36'
           ,'Referer' : 'https://www.manhuagui.com/'
           ,'cookie' :'country=TW; _ga=GA1.2.1929376959.1545460390; _gid=GA1.2.133063057.1545460390; BB_plg=pm; dom3ic8zudi28v8lr6fgphwffqoz0j6c=68c44a1b-6d71-40da-8db2-576d2ce26b9c%3A1%3A1; 494668b4c0ef4d25bda4e75c27de2817=68c44a1b-6d71-40da-8db2-576d2ce26b9c:1:1'}

class Chrome:
    def __init__(self):
        self.chrome_path = r"Module\chromedriver.exe"#chromedriver.exe執行檔所存在的路徑
        self.options = self.options()
        self.driver = webdriver.Chrome(self.chrome_path, chrome_options=self.options)
#        self.driver.implicitly_wait(10)
#        time.sleep(5)
        self.comic_name = None
        self.comic_stage = None
        self.pages = 0
        self.download_folder = None
        self.googleDrive = GoogleDrive()
        
    def options(self):
        options = webdriver.ChromeOptions()
#        options.add_argument("--headless")   
    #    options.add_argument('lang=zh_CN.UTF-8')
        options.add_argument('--user-agent={}'.format(headers['User-Agent']))
    #    options.add_argument('--cookie={}'.format(headers['cookie']))
        options.add_argument('--referer={}'.format(headers['Referer']))
        options.add_argument('disable-infobars')
        # 配置参数禁止data;的出现
        options.add_argument('user-data-dir=python36\profile')
        return options
                
    def login(self, account, password):
        self.driver.get("https://tw.manhuagui.com/user/login")
        self.driver.find_element_by_xpath("//input[@id='txtUserName']").send_keys(account)
        self.driver.find_element_by_xpath("//input[@id='txtPassword']").send_keys(password)
        self.driver.find_element_by_xpath("//input[@id='chkRemember']").click()
        self.driver.find_element_by_xpath("//input[@id='btnSubmit']").click()
        time.sleep(10)
        
        for index, cookie in enumerate(self.driver.get_cookies()):
            if cookie['name'] == 'my':
                return self.driver.get_cookies(), index
        return False

    def load_cookie(self, cookies): 
        self.driver.get("https://tw.manhuagui.com/")
        for cookie in cookies:
            print(cookie)
            self.driver.add_cookie(cookie)
            
#        self.driver.close()
        self.driver.refresh()
        time.sleep(10)
        for cookie in self.driver.get_cookies():
            if cookie['name'] == 'my':
                return True
        return False
        
    def comic_information(self, url):
        self.driver.get(url)
        title = self.driver.find_element_by_xpath("//div[@class='w980 title']/div[2]").text
        self.comic_name = title.split('/')[0]
        self.comic_stage = '第' + re.search('\d+', title.split('/')[1]).group(0) + '話'
        self.pages = int(title.split('/')[-1].replace(')',''))
        
    def comic_list(self):
        comic_url = list()
        
        self.driver.get("https://tw.manhuagui.com/user/book/shelf")
        for comic_name in self.driver.find_elements_by_xpath("//*[@class='dy_r']/h3/a[1]"):
            comic_url.append(comic_name.get_attribute('href'))
        print(comic_url) 
        return comic_url
        
    def stage_list(self, url):
        comic_stage = list()
        self.driver.get(url)
        stage_group = self.driver.find_elements_by_xpath("//div[@id='chapter-page-1']/ul/li/a[1]")
        
        if len(stage_group) == 0:
            for comic_name in self.driver.find_elements_by_xpath("//a[@class='status0']"):
                comic_stage.append(comic_name.get_attribute('href'))
        else: 
            for stage in stage_group:
                stage.click()                                     
                
                for comic_name in self.driver.find_elements_by_xpath("//a[@class='status0']"):
                    comic_stage.append(comic_name.get_attribute('href'))
    
        return comic_stage
        
        
    def page_process(self, url):
        self.comic_information(url)
        index = 1
        with tqdm(total = self.pages, desc = self.comic_stage, leave = False) as pbar:  
            while(index <= self.pages):
                urls = list()
                for x in range(index, index + 5):
                    if x > self.pages:
                        break
                    urls.append(url + "#p=" + str(x))
                    print(url)
                self.open_page(urls)
                self.close_page()
                self.driver.switch_to.window(self.driver.window_handles[0])
                                    
#                self.driver.find_element_by_link_text(u"自動").click()
#                element =  self.driver.find_element_by_id("mangaFile").get_attribute("src")
        #        print(element)
                index += 5
                pbar.update(5)
            self.image_merge()
            self.update()
#        return True
        
    def exist_folder(self, folder_path):
        path = os.path.join(folder_path, self.comic_stage)
        if not os.path.isdir(path):
            os.makedirs(r'%s/%s' % (folder_path, self.comic_stage))
            
        return path
    
    comic_url_dict = dict()
    
    def serach_page(self):
        self.driver.get('https://tw.manhuagui.com/comic/1128/')
        comic_url_dict = dict()
        for comic_name in self.driver.find_elements_by_xpath("//a[@class='status0']"):
            title = comic_name.get_attribute('title')
            href = comic_name.get_attribute('href')
            comic_url_dict[title] = href
            if re.search('第.*?(話|回)',title):
                # string = re.search('第\d*(話|回)',title).group(0)
                for key, values in comic_url_dict.items():
                    if str(900) in key:
                        return self.page_process_mangaFile(values)
    
    def page_process_mangaFile(self, url):
        self.comic_information(url)
        index = 1
        manga_urls = list()
        with tqdm(total = self.pages, desc = self.comic_stage, leave = False) as pbar:  
            while(index <= self.pages):
                urls = list()
                for x in range(index, index + 5):
                    if x > self.pages:
                        break
                    urls.append(url + "#p=" + str(x))
                    print(url)
                manga_urls.extend(self.get_mangaFile(urls))
                self.close_page()
                self.driver.switch_to.window(self.driver.window_handles[0])
                                    
#                self.driver.find_element_by_link_text(u"自動").click()
#                element =  self.driver.find_element_by_id("mangaFile").get_attribute("src")
        #        print(element)
                index += 5
                pbar.update(5)
        return manga_urls
    
    def get_mangaFile(self, urls):
        for url in urls: 
            self.driver.execute_script("window.open('%s');" % (url))
#                self.driver.get(url)
        manga_urls = list()
        for tab in range(1, len(urls) + 1):
#            print(tab)
            self.driver.switch_to.window(self.driver.window_handles[tab])
            element =  self.driver.find_element_by_id("mangaFile").get_attribute("src")
            manga_urls.append(element)
        return manga_urls
    
    def open_page(self, urls):
        for url in urls: 
            self.driver.execute_script("window.open('%s');" % (url))
#                self.driver.get(url)
        for tab in range(1, len(urls) + 1):
#            print(tab)
            self.driver.switch_to.window(self.driver.window_handles[tab])
            element =  self.driver.find_element_by_id("mangaFile").get_attribute("src")
            self.driver.execute_script("window.open('%s');" % (element))
            print(element)
            file_name = None
#            print(element)
#            print(element.split('/'))
            for text in reversed(element.split('/')):
                if "png" in text:
                    file_name = re.search('(.*?)\.png',text)
                elif "jpg" in text:
                    file_name = re.search('(.*?)\.jpg',text)
                if file_name:
                    break
            self.download(element, file_name.group(0))
            
    def close_page(self):
        handles = self.driver.window_handles
        for hand in handles[1:]:
            self.driver.switch_to.window(hand)
            self.driver.close()
        
    def download(self, url, page):
        print(url)
        response = requests.get(url, headers=headers, stream=True)
        file_raw2 = BytesIO(response.content)
        buffer_size = 16000
        folder_path = r'Catalog'
#        comic_name_path = os.path.join(folder_path, self.comic_name)
        folder_path = self.exist_folder(os.path.join(folder_path, self.comic_name))
        self.download_folder = folder_path
        
        file_path = os.path.join(folder_path, page)
        file_path = file_path.replace("png", "jpg")
        
        with open(file_path ,"wb") as f:
            shutil.copyfileobj(file_raw2, f, buffer_size)
        
        im = Image.open(file_path).convert("RGB")
        im.save(file_path,"jpeg")
        
    def get_zip(self):
        zip_file = os.path.basename(self.download_folder) + '.zip'
        with zipfile.ZipFile(os.path.join(self.download_folder, zip_file), 'w') as zf:
            for file in os.listdir(self.download_folder):
                if 'jpg' in file:
                    zf.write(os.path.join(self.download_folder, file), file)
                    
    def image_merge(self):
        hight = 0
        width = 0
        images = dict()
        index = 0
        image_folder = os.path.dirname(self.download_folder)
        image_file = os.path.basename(self.download_folder) + '.jpg'
        result = os.path.join(image_folder, image_file)
        
        files = dict()
        for file in os.listdir(self.download_folder):
            print(re.match('\d+.jpg', file))
            if 'jpg' in file and (not 'result' in file) and re.match('\d+.jpg', file):
                files[int(file.replace('.jpg', ''))] = file
            
        for key in sorted(files.keys()):
            image = Image.open(os.path.join(self.download_folder, files[key]))
#            
            if hight < image.height:
                hight = image.height
            if width < image.width:
                width = image.width
            images[index] = [image, image.height, image.width]
            
            index += 1
        print(width, hight * len(images))
        target = Image.new('RGB', (width, hight * len(images)))
        top = 0
        bottom = 0
        for key, item in images.items():
            image = item[0]
            hight = item[1]
            width = item[2]
            if key == 0:
                bottom = hight
            else:
                bottom += hight
            print(0, top, width, bottom)
            target.paste(image, (0, top, width, bottom))
            top += hight 
            quality_value = 100
            target.save(result, quality = quality_value)
            
    def update(self):
        image_folder = os.path.dirname(self.download_folder)
        image_file = os.path.basename(self.download_folder) + '.jpg'
        result = os.path.join(image_folder, image_file)
        
        q = "name = 'Comic' and mimeType = 'application/vnd.google-apps.folder'"
        parents_id = self.googleDrive.search_folder(q)
        
        q = "name = '" + image_file + "' and mimeType = 'image/jpeg'"
        file_id = self.googleDrive.search_folder(q)
        
        if not file_id:
            body = {"name": image_file,
                    "parents": [parents_id],
                    "mimeType": "image/jpeg"}
            file_id = self.googleDrive.create(body)['id']
        
        print("!!!", file_id, result)
        self.googleDrive.update(file_id, result, 'image')
        
    def close_browser(self):
        self.driver.close()
        
#def search_data():
#    url_comic = "https://tw.manhuagui.com/comic/13885/408884.html"
#    payload = {'page': '1'}
#    
#    res_comic = requests.get(url_comic, headers = headers, params = payload)
#    images_download_soup = bs(res_comic.text, "html.parser")
#    
#    for a in images_download_soup.select('#imgPreLoad'):
#        print(a)
        
if __name__ == "__main__":
    chrome = Chrome()
    chrome.login()
    ##    
###    WebDriverWait(driver, 5)
##    

##    driver.find_element_by_tag_name("body").send_keys(Keys.F5)
##    html = driver.page_source 
##    print(html)
##    driver.close()
##    search_data()