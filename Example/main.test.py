import os

import SmcEmulator

import main

process = SmcEmulator.Process(
    SmcEmulator.ConfigurationToolImpl(
        "test",
        None,
        None,
        {
            "value": SmcEmulator.Value("Hello world"),
            "param": SmcEmulator.Value("test value"),
        },
        os.getcwd()
    ), main.ModuleMain())

process.start()

executionContextTool = SmcEmulator.ExecutionContextToolImpl()

process.execute(executionContextTool)
output = process.execute(executionContextTool)
for strVar in output:
    print("{}: {} - {}".format(strVar.getMessageType(), strVar.getType(), strVar.getValue()))
print(executionContextTool.output[0].getValue() == "Hello world")
executionContextTool.output = []

process.stop()
