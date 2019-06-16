import google.auth.transport.requests as transport
import googleapiclient.discovery as discovery
import google_auth_oauthlib.flow as oauthflow
import six.moves.urllib.parse as urllib
import googleapiclient.http as HTTP
import pickle
import os.path
import asyncio
import collections
import csv
import json
import copy
import functools
import operator


class GoogleAPI:

    def __init__(self, token:str, credentials:str):
        self.token_path = token
        self.credentials_path = credentials
        self.scopes = ["https://www.googleapis.com/auth/drive.metadata.readonly", 
                "https://www.googleapis.com/auth/drive"]
        self._credentials = None
        

    def service(self, api, version):        
        return discovery.build(api, version, credentials=self.credentials)
    
    @property    
    def credentials(self) -> dict:
        if self._credentials is None:
            if not os.path.exists(self.credentials_path):
                raise ValueError(f"{self.credentials_path}: no such file or directory")
        
            if os.path.exists(self.token_path):
                with open(self.token_path, "rb") as fp:
                    self._credentials = pickle.load(fp)

            if not self._credentials or not self._credentials.valid:
                if self._credentials and self._credentials.expired and self._credentials.refresh_token:
                    self._credentials.refresh(transport.Request())
                else:
                    flow = oauthflow.InstalledAppFlow.from_client_secrets_file(self.credentials_path, self.scopes)
                    self._credentials = flow.run_local_server()
                
                with open(self.token_path, "wb") as fp:
                    pickle.dump(self._credentials, fp)
        return self._credentials
    
    async def _async_execute(self, http, num_retries=0):
        _http = http.http

        if http.resumable:
            body = None
            while body is None:
                _, body = http.next_chunk(http=http, num_retries=num_retries)
                await asyncio.sleep(1/30)
            return body

        if 'content-length' not in http.headers:
            http.headers['content-length'] = str(http.body_size)
        if len(http.uri) > 2048 and http.method == 'GET':
            http.method = 'POST'
            http.headers['x-http-method-override'] = 'GET'
            http.headers['content-type'] = 'application/x-www-form-urlencoded'
            parsed = urllib.urlparse(http.uri)
            http.uri = urllib.urlunparse(
                (parsed.scheme, parsed.netloc, parsed.path, parsed.params, None,
                None))

            http.body = parsed.query
            http.headers['content-length'] = str(len(http.body))

        # Handle retries for server-side errors.
        resp, content = HTTP._retry_request(
            http.http, num_retries, 'request', http._sleep, http._rand, str(http.uri),
            method=str(http.method), body=http.body, headers=http.headers)

        for callback in http.response_callbacks:
            callback(resp)
        if resp.status >= 300:
            raise HTTP.HttpError(resp, content, uri=http.uri)
        return http.postproc(resp, content)


class DriveAPI(GoogleAPI):

    def __init__(self, token:str, credentials:str, readonly=True):
        super().__init__(token, credentials)
        self._drive_service = None

    @property
    def drive_service(self):
        if self._drive_service is None:
            self._drive_service = self.service("drive", "v3")
        return self._drive_service
    
    async def files(self, pagesize=10):
        result = self.drive_service.files().list( #pylint: disable=E1101
            pageSize=pagesize, fields="nextPageToken, files(id, name)")
        result = await self._async_execute(result)
        return tuple(
            (dct["id"], dct["name"]) for dct in result["files"])

    
    async def delete(self, file_id):
        result = self.drive_service.files().delete(fileId=file_id)
        return await self._async_execute(result)
            
        

    

    


