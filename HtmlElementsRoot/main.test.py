import os

import SMCApi
import SmcEmulator
from typing import List, Optional

import main

process = SmcEmulator.Process(
    SmcEmulator.ConfigurationToolImpl(
        "test",
        None,
        None,
        {
            "id": SmcEmulator.Value("root"),
            "headers": SmcEmulator.Value("header1=sdf\nheader2=sdf"),
            "title": SmcEmulator.Value("Main page"),
            "htmlHead": SmcEmulator.Value("<meta charset=\"utf-8\"/>"),
            "htmlScript": SmcEmulator.Value("console.info(\"test\")"),
        },
        os.getcwd()
    ), main.ModuleMain())


def getInfo(key):
    # type: (str) -> Optional[SMCApi.IValue]
    if key == "decorationShapes":
        return SmcEmulator.Value(
            SMCApi.ObjectArray(SMCApi.ObjectType.OBJECT_ELEMENT, [SMCApi.ObjectElement([
                SMCApi.ObjectField("type", "rectangle"),
                SMCApi.ObjectField("name", "root"),
                SMCApi.ObjectField("description", "root1"),
                SMCApi.ObjectField("x", 1),
                SMCApi.ObjectField("y", 1),
                SMCApi.ObjectField("width", 100),
                SMCApi.ObjectField("height", 100),
                SMCApi.ObjectField("color", 1),
                SMCApi.ObjectField("strokeWidth", 1),
            ])])
        )
    return None


process.configurationTool.getInfo = getInfo


def funcEC(lst):
    # type: (List[SmcEmulator.Value]) -> SMCApi.IAction
    for s in lst:
        print(s.value)
    return SmcEmulator.Action([
        SmcEmulator.Message(SmcEmulator.Value(
            SMCApi.ObjectArray(SMCApi.ObjectType.OBJECT_ELEMENT, [SMCApi.ObjectElement([
                SMCApi.ObjectField("id", "input1"),
                SMCApi.ObjectField("htmlBody", "<input id='input1' placeholder='input name'/>"),
                SMCApi.ObjectField("htmlScript", "console.info(\"test input1\")"),
                SMCApi.ObjectField("data", SMCApi.ObjectArray(SMCApi.ObjectType.OBJECT_ELEMENT, [SMCApi.ObjectElement([
                    SMCApi.ObjectField("var1", "value1"),
                    SMCApi.ObjectField("var2", "value2")
                ])]))
            ])])
        ))
    ], SMCApi.ActionType.EXECUTE)


def funcEC2(lst):
    # type: (List[SmcEmulator.Value]) -> SMCApi.IAction
    for s in lst:
        print(s.value)
    return SmcEmulator.Action([
        SmcEmulator.Message(SmcEmulator.Value(
            SMCApi.ObjectArray(SMCApi.ObjectType.OBJECT_ELEMENT, [SMCApi.ObjectElement([
                SMCApi.ObjectField("id", "input2"),
                SMCApi.ObjectField("htmlBody", "<input id='input2' placeholder='input pass'/>"),
                SMCApi.ObjectField("htmlScript", "console.info(\"test input2\")"),
                SMCApi.ObjectField("data", SMCApi.ObjectArray(SMCApi.ObjectType.OBJECT_ELEMENT, [SMCApi.ObjectElement([
                    SMCApi.ObjectField("var1", "value3"),
                    SMCApi.ObjectField("var2", "value4")
                ])]))
            ])])
        ))
    ], SMCApi.ActionType.EXECUTE)


process.start()

executionContextTool = SmcEmulator.ExecutionContextToolImpl(
    [[SmcEmulator.Action([SmcEmulator.Message(SmcEmulator.Value(SMCApi.ObjectArray(SMCApi.ObjectType.OBJECT_ELEMENT, [SMCApi.ObjectElement([
        SMCApi.ObjectField("method", "GET"),
        SMCApi.ObjectField("reqId", "1"),
        SMCApi.ObjectField("uri", "path1"),
        SMCApi.ObjectField("remoteAddr", "10.0.0.1"),
        SMCApi.ObjectField("sessionId", "1sfghdljdftnoper6i"),
    ])])))])]], [], [], [funcEC, funcEC2], "default", "request"
)

output = process.execute(executionContextTool)
for strVar in output:
    print("{}: {} - {}".format(strVar.getMessageType(), strVar.getType(), strVar.getValue()))
executionContextTool.output = []

output = process.execute(executionContextTool)
for strVar in output:
    print("{}: {} - {}".format(strVar.getMessageType(), strVar.getType(), strVar.getValue()))
executionContextTool.output = []

process.stop()
