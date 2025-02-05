import os

import SMCApi
import SmcEmulator

import main

with open("../../../Test/nn/DeepSeek/key.txt", 'r') as key:
    API_KEY = key.read().strip()

process = SmcEmulator.Process(
    SmcEmulator.ConfigurationToolImpl(
        "test",
        None,
        None,
        {
            # "api_key": SmcEmulator.Value("dfg"),
            "api_key": SmcEmulator.Value(API_KEY),
            "type": SmcEmulator.Value("deepseek"),
            "max_tokens": SmcEmulator.Value(500),
            # "model": SmcEmulator.Value(""),
            "model": SmcEmulator.Value("deepseek-chat"),
            "url_prefix": SmcEmulator.Value(""),
        },
        os.getcwd()
    ), main.ModuleMain())

process.start()

executionContextTool = SmcEmulator.ExecutionContextToolImpl(None, None, None, None, "default", "get_models")
output = process.execute(executionContextTool)
for strVar in output:
    print("{}: {} - {}".format(strVar.getMessageType(), strVar.getType(), strVar.getValue()))
executionContextTool.output = []

executionContextTool = SmcEmulator.ExecutionContextToolImpl(
    [[SmcEmulator.Action([SmcEmulator.Message(SmcEmulator.Value(SMCApi.ObjectArray(objects=[
        SMCApi.ObjectElement([
            SMCApi.ObjectField("role", "system"),
            SMCApi.ObjectField("content", "You are a useful assistant."),
        ]),
        SMCApi.ObjectElement([
            SMCApi.ObjectField("role", "user"),
            SMCApi.ObjectField("content", "Hello World!"),
        ])
    ])))])]], None, None, None, "default", "get_response"
)
output = process.execute(executionContextTool)
for strVar in output:
    print("{}: {} - {}".format(strVar.getMessageType(), strVar.getType(), strVar.getValue()))
# print(executionContextTool.output[0].getValue() == "Hello world")
executionContextTool.output = []

process.stop()
