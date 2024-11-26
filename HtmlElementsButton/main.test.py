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
            "id": SmcEmulator.Value("button1"),
            "htmlHead": SmcEmulator.Value("<meta name='4' value='4'/>"),
            "htmlScript": SmcEmulator.Value("console.info(\"test button1\")"),
            "type": SmcEmulator.Value("button"),
        },
        os.getcwd()
    ), main.ModuleMain())


def getInfo(key):
    # type: (str) -> Optional[SMCApi.IValue]
    if key == "decorationShapes":
        return SmcEmulator.Value(
            SMCApi.ObjectArray(SMCApi.ObjectType.OBJECT_ELEMENT, [
                SMCApi.ObjectElement([
                    SMCApi.ObjectField("type", "rectangle"),
                    SMCApi.ObjectField("description", "root"),
                    SMCApi.ObjectField("point1X", 1),
                    SMCApi.ObjectField("point1Y", 1),
                    SMCApi.ObjectField("point2X", 100),
                    SMCApi.ObjectField("point2Y", 100),
                    SMCApi.ObjectField("color", 1),
                    SMCApi.ObjectField("strokeWidth", 1),
                ]),
                SMCApi.ObjectElement([
                    SMCApi.ObjectField("type", "rectangle"),
                    SMCApi.ObjectField("description", "form1 df"),
                    SMCApi.ObjectField("point1X", 20),
                    SMCApi.ObjectField("point1Y", 20),
                    SMCApi.ObjectField("point2X", 80),
                    SMCApi.ObjectField("point2Y", 85),
                    SMCApi.ObjectField("color", 1),
                    SMCApi.ObjectField("strokeWidth", 1),
                ]),
                SMCApi.ObjectElement([
                    SMCApi.ObjectField("type", "rectangle"),
                    SMCApi.ObjectField("description", "input1 df"),
                    SMCApi.ObjectField("point1X", 30),
                    SMCApi.ObjectField("point1Y", 30),
                    SMCApi.ObjectField("point2X", 70),
                    SMCApi.ObjectField("point2Y", 50),
                    SMCApi.ObjectField("color", 1),
                    SMCApi.ObjectField("strokeWidth", 1),
                ]),
                SMCApi.ObjectElement([
                    SMCApi.ObjectField("type", "rectangle"),
                    SMCApi.ObjectField("description", "button1 df1"),
                    SMCApi.ObjectField("point1X", 30),
                    SMCApi.ObjectField("point1Y", 60),
                    SMCApi.ObjectField("point2X", 70),
                    SMCApi.ObjectField("point2Y", 80),
                    SMCApi.ObjectField("color", 1),
                    SMCApi.ObjectField("strokeWidth", 1),
                    SMCApi.ObjectField("filled", True),
                ])
            ])
        )
    return None


process.configurationTool.getInfo = getInfo


def funcEC(lst):
    # type: (List[SmcEmulator.Value]) -> SMCApi.IAction
    for s in lst:
        print(s.value)
    return SmcEmulator.Action([
        SmcEmulator.Message(SmcEmulator.Value(1), SMCApi.MessageType.ERROR)
    ], SMCApi.ActionType.EXECUTE)


process.start()

executionContextTool = SmcEmulator.ExecutionContextToolImpl(
    [[SmcEmulator.Action([SmcEmulator.Message(SmcEmulator.Value(SMCApi.ObjectArray(SMCApi.ObjectType.OBJECT_ELEMENT, [SMCApi.ObjectElement([
        SMCApi.ObjectField("type", "get"),
    ])])))])]], [], [], [funcEC], "default", "request"
)

output = process.execute(executionContextTool)
for strVar in output:
    print("{}: {} - {}".format(strVar.getMessageType(), strVar.getType(), strVar.getValue()))
executionContextTool.output = []

output = process.execute(executionContextTool)
for strVar in output:
    print("{}: {} - {}".format(strVar.getMessageType(), strVar.getType(), strVar.getValue()))
executionContextTool.output = []

executionContextTool = SmcEmulator.ExecutionContextToolImpl(
    [[SmcEmulator.Action([SmcEmulator.Message(SmcEmulator.Value(SMCApi.ObjectArray(SMCApi.ObjectType.OBJECT_ELEMENT, [SMCApi.ObjectElement([
        SMCApi.ObjectField("type", "update"),
        SMCApi.ObjectField("params", SMCApi.ObjectElement([
            SMCApi.ObjectField("formId", "form1"),
            SMCApi.ObjectField("input1", 189)
        ])),
    ])])))])]], [], [], [funcEC], "default", "request"
)

output = process.execute(executionContextTool)
for strVar in output:
    print("{}: {} - {}".format(strVar.getMessageType(), strVar.getType(), strVar.getValue()))
executionContextTool.output = []

process.stop()
