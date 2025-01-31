#!/usr/bin/env python

import SMCApi
import SmcUtils
import requests
from typing import List


class ModuleMain(SMCApi.Module):
    def __init__(self):
        self.apy_key = None
        self.type = None
        self.api_url = None
        self.headers = None
        self.max_tokens = None
        self.model = None

    def start(self, configurationTool):
        # type: (SMCApi.ConfigurationTool) -> None
        self.apy_key = configurationTool.getSetting("apy_key").getValue()
        self.type = configurationTool.getSetting("type").getValue()
        self.max_tokens = configurationTool.getSetting("max_tokens").getValue()
        self.headers = {
            'Authorization': "Bearer %r" % (self.apy_key),
            'Content-Type': 'application/json'
        }
        self.model = configurationTool.getSetting("model").getValue()
        if self.type == "deepseek":
            self.api_url = 'https://api.deepseek.com/v1/chat/completions'
            if not self.model or len(self.model) == 0:
                self.model = "deepseek-chat"
        elif self.type == "chatgpt":
            self.api_url = 'https://api.openai.com/v1/chat/completions'
            if not self.model or len(self.model) == 0:
                self.model = "o1-preview"

    def process(self, configurationTool, executionContextTool):
        # type: (SMCApi.ConfigurationTool, SMCApi.ExecutionContextTool) -> None
        SmcUtils.processMessagesAll(configurationTool, executionContextTool,
                                    lambda id, messages: self.prcessMessages(configurationTool, executionContextTool, messages))

    def prcessMessages(self, configurationTool, executionContextTool, messages):
        # type: (SMCApi.ConfigurationTool, SMCApi.ExecutionContextTool, List[List[SMCApi.IMessage]]) -> None
        type = executionContextTool.getType().lower()
        if type == "default":
            arr = SmcUtils.convertFromObjectArray(SmcUtils.deserializeToObject(messages[0]))  # role and content
            if not arr or len(arr) == 0:
                return

            data = {
                "model": self.model,
                'messages': arr,
                'max_tokens': self.max_tokens
            }

            try:
                if self.type == "deepseek":
                    response = requests.post(self.api_url, headers=self.headers, json=data)
                    response.raise_for_status()
                    response = [{"role": "system", "content": response.json()['choices'][0]['message']['content']}]
                    executionContextTool.addMessage(SmcUtils.convertToObjectArray(response))
                elif self.type == "chatgpt":
                    response = requests.post(self.api_url, headers=self.headers, json=data)
                    response.raise_for_status()
                    response = [{"role": "system", "content": response.json()['choices'][0]['text'][1:]}]
                    executionContextTool.addMessage(SmcUtils.convertToObjectArray(response))
            except Exception as e:
                # configurationTool.loggerWarn("request error: %r" % SmcUtils.getStackTraceAsString(e))
                executionContextTool.addError("request error: %r" % SmcUtils.getErrorMessageOrClassName(e))

    def update(self, configurationTool):
        # type: (SMCApi.ConfigurationTool) -> None
        self.stop(configurationTool)
        self.start(configurationTool)

    def stop(self, configurationTool):
        # type: (SMCApi.ConfigurationTool) -> None
        self.apy_key = None
        self.type = None
        self.api_url = None
        self.headers = None
        self.max_tokens = None
        self.model = None
