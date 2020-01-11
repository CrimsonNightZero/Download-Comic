# -*- coding: utf-8 -*-
"""
Created on Sat Jun  3 13:30:45 2017

@author: foryou
"""
import httplib2
import os
import io

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

from apiclient import errors
from apiclient.http import MediaFileUpload
from apiclient.http import MediaIoBaseDownload
from apiclient.http import MediaIoBaseUpload

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/drive-python-quickstart.json
SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly',
          'https://www.googleapis.com/auth/drive.readonly',
          'https://www.googleapis.com/auth/drive',
          'https://www.googleapis.com/auth/drive.file']

CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Drive API Python Quickstart'
"""
refer https://github.com/googledrive
MIME Type https://developers.google.com/drive/v3/web/mime-types?hl=zh-TW
"""
class GoogleDrive:
    def __init__(self):
        credentials = self.get_credentials()
        http = credentials.authorize(httplib2.Http())
        service = discovery.build('drive', 'v3', http=http)
        self.service = service;
        
    def get_credentials(self):
        """Gets valid user credentials from storage.
    
        If nothing has been stored, or if the stored credentials are invalid,
        the OAuth2 flow is completed to obtain the new credentials.
    
        Returns:
            Credentials, the obtained credential.
        """
        home_dir = os.path.expanduser('~')
        credential_dir = os.path.join(home_dir, '.credentials')
        if not os.path.exists(credential_dir):
            os.makedirs(credential_dir)
        credential_path = os.path.join(credential_dir,
                                       'drive-python-quickstart.json')
    
        store = Storage(credential_path)
        credentials = store.get()
        if not credentials or credentials.invalid:
            flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
            flow.user_agent = APPLICATION_NAME
            if flags:
                credentials = tools.run_flow(flow, store, flags)
            else: # Needed only for compatibility with Python 2.6
                credentials = tools.run(flow, store)
            print('Storing credentials to ' + credential_path)
        return credentials
    
    def main(self):
        """Shows basic usage of the Google Drive API.
    
        Creates a Google Drive API service object and outputs the names and IDs
        for up to 10 files.
        """
    
        results = self.service.files().list(
            pageSize=1000, fields="nextPageToken, files(id, name)").execute()
        items = results.get('files', [])
        if not items:
            print('No files found.')
        else:
            print('Files:')
            for item in items:
                print('{0} ({1})'.format(item['name'], item['id']))
                
    def search_folder(self, q):
        page_token = None
        while True:
            response = self.service.files().list(q = q, spaces = 'drive',
                                                 pageToken = page_token).execute()
            
            
            for file in response.get('files', []):
                # Process change
                print ('Found file: %s (%s)(%s)' % (file.get('parents'), file.get('id'), file.get('name')))
                return file.get('id')
            page_token = response.get('nextPageToken', None)
            
            if page_token is None:
                break;
                
    def search_file(self, fileId):
        response = self.service.files().get(fileId = fileId).execute()
        #response = self.service.files().watch(fileId = fileId, body = body).execute()
        print(response)
        print ('Found file: %s (%s)(%s)' % (response.get('parents'), response, response.get('name')))
            
    def search_file_from_folder(self, q, parents_id):
        page_token = None
        structure = {'folder':{}, 'file':{}}
        while True:
            response = self.service.files().list(q = q, spaces = 'drive',
                                                 fields = 'nextPageToken, files(id, parents, name, mimeType)',
                                                 pageToken = page_token).execute()
            for file in response.get('files', []):
                # Process change
                if (file.get('parents')[0] == parents_id):
                    if(file.get('mimeType') == "application/vnd.google-apps.document"):
                        structure['file'][file.get('name')] = file.get('id');
                    else:
                        structure['folder'][file.get('name')] = file.get('id');
                print(file.get('parents') == parents_id)
                print ('Found file: %s (%s)(%s)' % (file, file.get('id'), file.get('name')))
            page_token = response.get('nextPageToken', None)
            print(page_token)
            if page_token is None:
                break;
        return structure;
    
    def create(self, body):
        response = self.service.files().create(body = body).execute()
        print(response)
        print ('Found file: %s (%s)(%s)' % (response.get('parents'), response.get('id'), response.get('name')))
        return response
    
    def update(self, fileId, content, mimetype = None):
        #file_metadata = {
        #  'name' : 'My Report',
        #  'mimeType' : 'application/vnd.google-apps.document'
        #}
        if mimetype == 'image':
            media = MediaFileUpload(content,
                    mimetype='image/jpeg',chunksize=1024*1024, resumable=True)
        else:
            content = io.BytesIO(content.encode("utf-8"))
            media = MediaIoBaseUpload(content, mimetype = 'application/octet-stream')
        
        file = self.service.files().update(fileId = fileId,
                                      media_body = media).execute()
        
        print ('File ID: %s' % file.get('id'))  
   
    def export(self, fileId, mimeType):
        response = self.service.files().export(fileId = fileId, mimeType = mimeType).execute()
        print ('Found file: %s ' % (response.decode("utf-8")))
            
if __name__ == "__main__":
    googleDrive = GoogleDrive()
    #search file or folder
    
    q = "name = 'xml' and mimeType = 'application/vnd.google-apps.folder'"
    #fields = 'nextPageToken, files(id, parents, name)'
    parents_id = googleDrive.search_folder(q)
    print(parents_id)
    q = "'0B_zC2JhWq_REQUt6X0dxaU1YOWM' in parents"
    structure = googleDrive.search_file_from_folder(q, parents_id)
    
    
    """
    fileId = '0B_zC2JhWq_REQUt6X0dxaU1YOWM'
    body = {
            'id': '0B_zC2JhWq_REQUt6X0dxaU1YOWM',
            'type': 'web_hook',
          }
    googleDrive.search_file(fileId)
    """
    
    #update file
    '''
    fileId = "1VWb6ZDBx6fG83xlIVWR9PrC98C9t22mOj0DoTTK0KNs"
    content = "aaaa"
    googleDrive.update(fileId, content)
    '''
    
    #output file content
    """
    fileId = "1D17LLubJ2Ie2SWDvvcGSXdfhiuPKklKYSsb53pVkiiM"
    mimeType = 'text/plain'
    googleDrive.export(fileId, mimeType)
    """
    
    #create file
    '''
    body = {"name": "00",
            "kind": "drive#file",
            "mimeType": "application/vnd.google-apps.folder"}
    print(googleDrive.create(body)['id'])
    '''