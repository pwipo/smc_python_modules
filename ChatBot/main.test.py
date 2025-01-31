import os

import SMCApi
import SmcEmulator

import main

process = SmcEmulator.Process(
    SmcEmulator.ConfigurationToolImpl(
        "test",
        None,
        None,
        {
            "apy_key": SmcEmulator.Value("dfg"),
            "type": SmcEmulator.Value("deepseek"),
            "max_tokens": SmcEmulator.Value(500),
            "model": SmcEmulator.Value(""),
        },
        os.getcwd()
    ), main.ModuleMain())

process.start()

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
    ])))])]], None, None, None, "default", "default"
)

process.execute(executionContextTool)
output = process.execute(executionContextTool)
for strVar in output:
    print("{}: {} - {}".format(strVar.getMessageType(), strVar.getType(), strVar.getValue()))
# print(executionContextTool.output[0].getValue() == "Hello world")
executionContextTool.output = []

process.stop()
