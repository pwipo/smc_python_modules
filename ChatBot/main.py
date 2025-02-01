#!/usr/bin/env python
import os

import SMCApi
import SmcUtils
import requests
import urllib3
import uuid
from typing import List


class ModuleMain(SMCApi.Module):
    def __init__(self):
        self.api_key = None
        self.type = None
        self.url_chat_completions = None
        self.url_get_models = None
        self.headers = None
        self.max_tokens = None
        self.model = None
        self.authorization_key = None
        self.cert_root = None

    def start(self, configurationTool):
        # type: (SMCApi.ConfigurationTool) -> None
        self.api_key = configurationTool.getSetting("api_key").getValue()
        self.type = configurationTool.getSetting("type").getValue()
        self.max_tokens = configurationTool.getSetting("max_tokens").getValue()
        self.headers = {
            'Authorization': "Bearer {}".format(self.api_key),
            'Content-Type': 'application/json'
        }
        self.model = configurationTool.getSetting("model").getValue()
        if self.type == "deepseek":
            self.url_chat_completions = 'https://api.deepseek.com/v1/chat/completions'
            self.url_get_models = 'https://api.deepseek.com/v1/models'
            if not self.model or len(self.model) == 0:
                self.model = "deepseek-chat"
        elif self.type == "chatgpt":
            self.url_chat_completions = 'https://api.openai.com/v1/chat/completions'
            self.url_get_models = 'https://api.openai.com/v1/models'
            if not self.model or len(self.model) == 0:
                self.model = "o1-preview"
        elif self.type == "gigachat":
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            cert_path = configurationTool.getWorkDirectory() + os.path.sep + "gigachat_ca.cer"
            self.cert_root = False
            if os.path.isfile(cert_path):
                self.cert_root = cert_path
            self.authorization_key = self.api_key
            self.api_key = None
            self.headers = None
            self.url_chat_completions = 'https://gigachat.devices.sberbank.ru/api/v1/chat/completions'
            self.url_get_models = 'https://gigachat.devices.sberbank.ru/api/v1/models'
            if not self.model or len(self.model) == 0:
                self.model = "GigaChat"

    def process(self, configurationTool, executionContextTool):
        # type: (SMCApi.ConfigurationTool, SMCApi.ExecutionContextTool) -> None
        SmcUtils.processMessagesAll(configurationTool, executionContextTool,
                                    lambda id, messages: self.prcessMessages(configurationTool, executionContextTool, messages))

    def prcessMessages(self, configurationTool, executionContextTool, messages):
        # type: (SMCApi.ConfigurationTool, SMCApi.ExecutionContextTool, List[List[SMCApi.IMessage]]) -> None
        type = executionContextTool.getType().lower()

        if type == "get_response":
            response = []
            arr = SmcUtils.convertFromObjectArray(SmcUtils.deserializeToObject(messages[0]))  # role and content
            if not arr or len(arr) == 0:
                return

            data = {
                'model': self.model,
                'messages': arr,
                'max_tokens': self.max_tokens
            }
            if self.type == "deepseek":
                response = requests.post(self.url_chat_completions, headers=self.headers, json=data)
                response.raise_for_status()
                response = [{"role": "system", "content": response.json()['choices'][0]['message']['content']}]
            elif self.type == "chatgpt":
                response = requests.post(self.url_chat_completions, headers=self.headers, json=data)
                response.raise_for_status()
                response = [{"role": "system", "content": response.json()['choices'][0]['text'][1:]}]
            elif self.type == "gigachat":
                response = self.gigachat_send_request(data)
                response = [{"role": "system", "content": response.json()['choices'][0]['message']['content']}]
            executionContextTool.addMessage(SmcUtils.convertToObjectArray(response))
        elif type == "get_models":
            response = []
            if self.type == "deepseek":
                response = requests.get(self.url_get_models, headers=self.headers)
                response.raise_for_status()
                response = response.json()['data']
            elif self.type == "chatgpt":
                response = requests.get(self.url_get_models, headers=self.headers)
                response.raise_for_status()
                response = response.json()['data']
            elif self.type == "gigachat":
                response = self.gigachat_get_modules()
                response = response.json()['data']
            executionContextTool.addMessage(SmcUtils.convertToObjectArray(response))

    def update(self, configurationTool):
        # type: (SMCApi.ConfigurationTool) -> None
        self.stop(configurationTool)
        self.start(configurationTool)

    def stop(self, configurationTool):
        # type: (SMCApi.ConfigurationTool) -> None
        self.api_key = None
        self.type = None
        self.url_chat_completions = None
        self.headers = None
        self.max_tokens = None
        self.model = None
        self.authorization_key = None
        self.cert_root = None

    def gigachat_get_new_api_key(self):
        if not self.authorization_key:
            return
        url_auth = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
        payload = {
            'scope': 'GIGACHAT_API_PERS'
        }
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json',
            'RqUID': str(uuid.uuid4()),
            'Authorization': 'Basic {}'.format(self.authorization_key)
        }

        response = requests.request("POST", url_auth, headers=headers, data=payload, verify=self.cert_root)
        if response.status_code == 200:
            return response.json()['access_token']
        else:
            raise Exception("Error get token: {}".format(response.text))

    def gigachat_send_request(self, data):
        if not self.api_key:
            self.api_key = self.gigachat_get_new_api_key()
            self.headers = {
                'Authorization': "Bearer {}".format(self.api_key),
                'Content-Type': 'application/json'
            }

        response = requests.post(self.url_chat_completions, headers=self.headers, json=data, verify=self.cert_root)

        if response.status_code == 401:
            self.api_key = None
            self.headers = None
            return self.gigachat_send_request(data)
        elif response.status_code == 200:
            return response
        else:
            raise Exception(response.text)

    def gigachat_get_modules(self):
        if not self.api_key:
            self.api_key = self.gigachat_get_new_api_key()
            self.headers = {
                'Authorization': "Bearer {}".format(self.api_key),
                'Content-Type': 'application/json'
            }

        payload = {
            'scope': 'GIGACHAT_API_PERS'
        }
        response = requests.request("GET", self.url_get_models, headers=self.headers, data=payload, verify=self.cert_root)

        if response.status_code == 401:
            self.api_key = None
            self.headers = None
            return self.gigachat_get_modules()
        elif response.status_code == 200:
            return response
        else:
            raise Exception(response.text)
