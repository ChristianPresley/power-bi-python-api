#!/usr/bin/env python

import os
import datetime
import logging
import requests

from typing import Dict, List, NoReturn, Union

class RestClient:
    tenant_id = os.getenv('AZURE_TENANT_ID')
    client_id = os.getenv('AZURE_CLIENT_ID')
    client_secret = os.getenv('AZURE_CLIENT_SECRET')

    base_url = "https://api.powerbi.com/v1.0/myorg/"
    token_url = "https://login.microsoftonline.com/" + tenant_id + "/oauth2/v2.0/token"
    scope_url = "https://analysis.windows.net/powerbi/api/.default"

    json_headers = {"Content-Type": "application/json"}
    urlencoded_headers = {"Content-Type": "application/x-www-form-urlencoded"}

    http_accepted_code = 202
    http_created_code = 201
    http_ok_code = 200
    
    def __init__(self, authz_header = None, token = None, token_expiration = None):
            self.tenant_id = RestClient.tenant_id
            self.client_id = RestClient.client_id
            self.client_secret = RestClient.client_secret
            self.base_url = RestClient.base_url
            self.token_url = RestClient.token_url
            self.scope_url = RestClient.scope_url
            self.http_accepted_code = RestClient.http_accepted_code
            self.http_created_code = RestClient.http_created_code
            self.http_ok_code = RestClient.http_ok_code
            self.authz_header = authz_header
            self.token = token
            self.token_expiration = token_expiration
            self.request_bearer_token()
            self.json_headers = RestClient.json_headers
            self.json_headers.update(self.authz_header)
            self.urlencoded_headers = RestClient.urlencoded_headers
            self.urlencoded_headers.update(self.authz_header)
            self._workspaces = None
            self._pipelines = None

    def get_authz_header(self) -> Dict[str, str]:
        return {"Authorization": "Bearer " + self.token}
    
    def request_bearer_token(self) -> None:
        renew_token = True

        if self.token is None:
            logging.info(f"Access token does not exist. Attempting to generate access token.")    
        elif self.token_expiration < datetime.datetime.utcnow():
            logging.info(f"Access token has expired. Attempting to renew access token.")
        else:
            logging.info("Access token exists and is not expired. Proceeding to use existing token.")
            renew_token = False

        if renew_token:
            headers = {
                "Content-Type": "application/x-www-form-urlencoded",
            }
            payload = {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "grant_type": "client_credentials",
                "scope": self.scope_url,
            }
        
            response = requests.post(self.token_url, data = payload, headers = headers)

            if response.status_code == self.http_ok_code:
                logging.info(f"Successfully retrieved access token for client id {self.client_id}.")
                # self.token = response.json()["access_token"]
                self.token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsIng1dCI6ImpTMVhvMU9XRGpfNTJ2YndHTmd2UU8yVnpNYyIsImtpZCI6ImpTMVhvMU9XRGpfNTJ2YndHTmd2UU8yVnpNYyJ9.eyJhdWQiOiJodHRwczovL2FuYWx5c2lzLndpbmRvd3MubmV0L3Bvd2VyYmkvYXBpIiwiaXNzIjoiaHR0cHM6Ly9zdHMud2luZG93cy5uZXQvYTIwOGZhMzUtNDRlZS00ZDYxLTk1ODktOTQ3ZjExZmY3ZWQ2LyIsImlhdCI6MTY0OTM0MzE1NywibmJmIjoxNjQ5MzQzMTU3LCJleHAiOjE2NDkzNDc2OTMsImFjY3QiOjAsImFjciI6IjEiLCJhaW8iOiJBVFFBeS84VEFBQUF1QW5zK21HL1NTUlZlUUZ0Z3VhWTJ6VG9nd1NRcFY5cElvek5pYzZOSDZ4SHZ6STBMYnArNzZCNnBYSkNSaXdBIiwiYW1yIjpbInB3ZCJdLCJhcHBpZCI6IjQxMDZmNzYxLTNiNmMtNDA5OS04NDllLTMxZmJkNjM4ZmZiMCIsImFwcGlkYWNyIjoiMCIsImZhbWlseV9uYW1lIjoiQWRtaW5pc3RyYXRvciIsImdpdmVuX25hbWUiOiJNT0QiLCJpcGFkZHIiOiIyNC4xOC4xOTkuMTM4IiwibmFtZSI6Ik1PRCBBZG1pbmlzdHJhdG9yIiwib2lkIjoiNGFhNTU2YjMtNWEwZi00MGZhLWE5MzAtODRkNDc1NTU1MjIwIiwicHVpZCI6IjEwMDMyMDAxQ0YxN0Y3REQiLCJyaCI6IjAuQVVZQU5mb0lvdTVFWVUyVmlaUl9FZjktMWdrQUFBQUFBQUFBd0FBQUFBQUFBQUNBQUtVLiIsInNjcCI6IkFwcC5SZWFkLkFsbCBDYXBhY2l0eS5SZWFkLkFsbCBDYXBhY2l0eS5SZWFkV3JpdGUuQWxsIENvbnRlbnQuQ3JlYXRlIERhc2hib2FyZC5SZWFkLkFsbCBEYXNoYm9hcmQuUmVhZFdyaXRlLkFsbCBEYXRhZmxvdy5SZWFkLkFsbCBEYXRhZmxvdy5SZWFkV3JpdGUuQWxsIERhdGFzZXQuUmVhZC5BbGwgRGF0YXNldC5SZWFkV3JpdGUuQWxsIEdhdGV3YXkuUmVhZC5BbGwgR2F0ZXdheS5SZWFkV3JpdGUuQWxsIFBpcGVsaW5lLkRlcGxveSBQaXBlbGluZS5SZWFkLkFsbCBQaXBlbGluZS5SZWFkV3JpdGUuQWxsIFJlcG9ydC5SZWFkLkFsbCBSZXBvcnQuUmVhZFdyaXRlLkFsbCBTdG9yYWdlQWNjb3VudC5SZWFkLkFsbCBTdG9yYWdlQWNjb3VudC5SZWFkV3JpdGUuQWxsIFRlbmFudC5SZWFkLkFsbCBUZW5hbnQuUmVhZFdyaXRlLkFsbCBVc2VyU3RhdGUuUmVhZFdyaXRlLkFsbCBXb3Jrc3BhY2UuUmVhZC5BbGwgV29ya3NwYWNlLlJlYWRXcml0ZS5BbGwiLCJzdWIiOiJjUUlob3V5N1ljaTlubVhpR1dGTFdFQzJfTFZxbTctZFBfZ3d1ZEZ3UjNNIiwidGlkIjoiYTIwOGZhMzUtNDRlZS00ZDYxLTk1ODktOTQ3ZjExZmY3ZWQ2IiwidW5pcXVlX25hbWUiOiJhZG1pbkBNMzY1eDUxOTM5OTYzLm9ubWljcm9zb2Z0LmNvbSIsInVwbiI6ImFkbWluQE0zNjV4NTE5Mzk5NjMub25taWNyb3NvZnQuY29tIiwidXRpIjoiak5VQlhnQnpxMHlDQTdSblREUW1BQSIsInZlciI6IjEuMCIsIndpZHMiOlsiNjJlOTAzOTQtNjlmNS00MjM3LTkxOTAtMDEyMTc3MTQ1ZTEwIiwiYjc5ZmJmNGQtM2VmOS00Njg5LTgxNDMtNzZiMTk0ZTg1NTA5Il19.n7_L6OvZwjGWTd4pd_OSmuUmHP8WTA6rpYtBYmEx6HxQ5wjLX7asiZQ2H3LQfkq6Ys1Bd7kR5lhLwwfiSUJxFR7T4Ydvk9LwKPDB3t15o43sCfdr_WbdaQnfIM5a4MAxMbq17tER_ja_OGuENMVo_lhxxgg115TKcoQeML_6gdrCWmY7J2JodUaBuWX3YoPgGsKxmHqvwvOdnZ7Uyq2E64tj8LOtiLEBPqSXGi5v803lZklRVKROYFqV9YRp54-yKDGY-vpEHUyZao12FNPJtNBdsDgwTeFxY5BbR-k4zFJsVZg7QVjk6EWugjgLUP4KpfkKY8i846Ch5dYf1mIFEg"
                self.token_expiration = datetime.datetime.utcnow() + datetime.timedelta(seconds=response.json()["expires_in"])
                self.authz_header = self.get_authz_header()
            else:
                logging.error(f"Failed to retrieve access token for client id {self.client_id}.")
                self.force_raise_http_error(response)
    
    def check_token_expiration(self):
        if self.token_expiration < datetime.datetime.utcnow():
            self.request_bearer_token()

    def force_raise_http_error(response: requests.Response, expected_codes: Union[List[int], int] = http_ok_code) -> NoReturn:
        logging.error(f"Expected response code(s) {expected_codes}, got {response.status_code}: {response.text}.")
        response.raise_for_status()
        raise requests.HTTPError(response)
    