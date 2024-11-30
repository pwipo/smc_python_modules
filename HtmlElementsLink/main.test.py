import os

import SMCApi
import SmcEmulator
from typing import Optional

import main

process = SmcEmulator.Process(
    SmcEmulator.ConfigurationToolImpl(
        "test",
        None,
        None,
        {
            "id": SmcEmulator.Value("link1"),
            "htmlHead": SmcEmulator.Value("<meta name='5' value='5'/>"),
            "htmlScript": SmcEmulator.Value("console.info(\"test div1\")"),
            "href": SmcEmulator.Value("http://www.shelfmc.ru"),
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
                    SMCApi.ObjectField("point2Y", 200),
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
                ]),
                SMCApi.ObjectElement([
                    SMCApi.ObjectField("type", "rectangle"),
                    SMCApi.ObjectField("description", "div1 df1"),
                    SMCApi.ObjectField("point1X", 20),
                    SMCApi.ObjectField("point1Y", 100),
                    SMCApi.ObjectField("point2X", 80),
                    SMCApi.ObjectField("point2Y", 150),
                    SMCApi.ObjectField("color", 1),
                    SMCApi.ObjectField("strokeWidth", 1),
                    SMCApi.ObjectField("filled", True),
                ]),
                SMCApi.ObjectElement([
                    SMCApi.ObjectField("type", "rectangle"),
                    SMCApi.ObjectField("description", "image1 if3"),
                    SMCApi.ObjectField("point1X", 20),
                    SMCApi.ObjectField("point1Y", 150),
                    SMCApi.ObjectField("point2X", 80),
                    SMCApi.ObjectField("point2Y", 199),
                    SMCApi.ObjectField("color", 1),
                    SMCApi.ObjectField("strokeWidth", 1),
                    SMCApi.ObjectField("filled", True),
                    SMCApi.ObjectField("imageBytes", b'23556'),
                ]),
                SMCApi.ObjectElement([
                    SMCApi.ObjectField("type", "text"),
                    SMCApi.ObjectField("description", "text1 if3"),
                    SMCApi.ObjectField("point1X", 20),
                    SMCApi.ObjectField("point1Y", 150),
                    SMCApi.ObjectField("point2X", 80),
                    SMCApi.ObjectField("point2Y", 199),
                    SMCApi.ObjectField("color", 1),
                    SMCApi.ObjectField("strokeWidth", 1),
                    SMCApi.ObjectField("filled", True),
                    SMCApi.ObjectField("text", "hello world"),
                    SMCApi.ObjectField("fontSize", 10),
                ]),
                SMCApi.ObjectElement([
                    SMCApi.ObjectField("type", "text"),
                    SMCApi.ObjectField("description", "link1 if3"),
                    SMCApi.ObjectField("point1X", 20),
                    SMCApi.ObjectField("point1Y", 150),
                    SMCApi.ObjectField("point2X", 80),
                    SMCApi.ObjectField("point2Y", 199),
                    SMCApi.ObjectField("color", 1),
                    SMCApi.ObjectField("strokeWidth", 1),
                    SMCApi.ObjectField("filled", True),
                    SMCApi.ObjectField("text", "link"),
                    SMCApi.ObjectField("fontSize", 10),
                ])
            ])
        )
    return None


process.configurationTool.getInfo = getInfo

process.start()

executionContextTool = SmcEmulator.ExecutionContextToolImpl(
    [[SmcEmulator.Action([SmcEmulator.Message(SmcEmulator.Value(SMCApi.ObjectArray(SMCApi.ObjectType.OBJECT_ELEMENT, [SMCApi.ObjectElement([
        SMCApi.ObjectField("type", "get"),
    ])])))])]], [], [], [], "default", "request"
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
            SMCApi.ObjectField("formId", "text1"),
            SMCApi.ObjectField("input1", 189)
        ])),
    ])])))])]], [], [], [], "default", "request"
)

output = process.execute(executionContextTool)
for strVar in output:
    print("{}: {} - {}".format(strVar.getMessageType(), strVar.getType(), strVar.getValue()))
executionContextTool.output = []

process.stop()