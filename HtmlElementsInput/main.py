#!/usr/bin/env python

import SMCApi
import SmcUtils
from typing import List


class HttpReqMultipart:
    def __init__(self, obj):
        # type: (SmcUtils.ObjectDict) -> None
        keys = obj.keys()  # type: List[str]
        self.name = obj.name  # type: str
        self.contentType = obj.contentType  # type: str
        self.headers = obj.headers  # type: SmcUtils.ObjectDict[str,str]
        self.size = obj.size  # type: int
        self.data = None  # type: str or bytes
        if 'data' in keys:
            self.data = obj.data  # type: str or bytes


class InputObj:
    def __init__(self, objectElement):
        # type: (SMCApi.ObjectElement) -> None
        obj = SmcUtils.convertFromObjectElement(objectElement, True)  # type: SmcUtils.ObjectDict
        keys = obj.keys()  # type: List[str]
        self.type = obj.type  # type: str
        self.cache = None  # type: SmcUtils.ObjectDict
        if 'cache' in keys:
            self.cache = obj.cache  # type: SmcUtils.ObjectDict
        self.params = None  # type: SmcUtils.ObjectDict
        if 'params' in keys:
            self.params = obj.params  # type: SmcUtils.ObjectDict
        self.headers = None  # type: SmcUtils.ObjectDict
        if 'headers' in keys:
            self.headers = obj.headers  # type: SmcUtils.ObjectDict
        self.multipart = None  # type: List[HttpReqMultipart]
        if 'multipart' in keys:
            self.multipart = map(lambda o: HttpReqMultipart(o), obj.multipart)  # type: List[HttpReqMultipart]
        self.error = None  # type: str
        if 'error' in keys:
            self.error = obj.error  # type: str


class Shape:
    def __init__(self, obj):
        # type: (SmcUtils.ObjectDict) -> None
        keys = obj.keys()  # type: List[str]
        self.type = obj.type  # type: str
        self.point1X = obj.point1X  # type: int
        self.point1Y = obj.point1Y  # type: int
        self.point2X = obj.point2X  # type: int
        self.point2Y = obj.point2Y  # type: int
        self.offset2X = None  # type: int
        if 'offset2X' in keys:
            self.offset2X = obj.offset2X  # type: int
        self.offset2Y = None  # type: int
        if 'offset2Y' in keys:
            self.offset2Y = obj.offset2Y  # type: int
        self.color = obj.color & 0xffffff # type: int
        self.strokeWidth = obj.strokeWidth  # type: int
        self.descriptionId = ""
        self.descriptionOther = ""
        if obj.description:
            arrStr = obj.description.strip().split(" ", 2)
            self.descriptionId = arrStr[0].strip()
            if len(arrStr) > 1:
                self.descriptionOther = arrStr[1].strip()
        self.text = None  # type: str
        if 'text' in keys:
            self.text = obj.text  # type: str
        self.filled = None  # type: bool
        if 'filled' in keys:
            self.filled = obj.filled  # type: bool
        self.imageBytes = None  # type: bytes
        if 'imageBytes' in keys:
            self.imageBytes = obj.imageBytes  # type: bytes
        self.fontSize = None  # type: int
        if 'fontSize' in keys:
            self.fontSize = obj.fontSize  # type: int


class ModuleMain(SMCApi.Module):
    def __init__(self):
        self.id = None  # type: str
        self.type = None  # type: str
        self.htmlHead = None  # type: str
        self.htmlScript = None  # type: str
        self.elementAttrs = None  # type: str

    def start(self, configurationTool):
        # type: (SMCApi.ConfigurationTool) -> None
        self.id = SmcUtils.getString(configurationTool.getSetting("id"))
        self.type = SmcUtils.getString(configurationTool.getSetting("type"))
        self.htmlHead = SmcUtils.getString(configurationTool.getSetting("htmlHead"))
        htmlScript = SmcUtils.getString(configurationTool.getSetting("htmlScript"))

        objectArray = SmcUtils.getObjectArray(configurationTool.getInfo("decorationShapes"))
        shape = None  # type: Shape
        shapeParent = None  # type: Shape
        if SmcUtils.isArrayContainObjectElements(objectArray):
            objList = map(lambda s: Shape(s), SmcUtils.convertFromObjectArray(objectArray, True))  # type: List[Shape]
            shape = next(iter(
                filter(
                    lambda s: s.type == "rectangle" and s.descriptionId == self.id, objList)))  # type: Shape
            if shape:
                shapeParent = next(iter(
                    sorted(
                        filter(
                            lambda
                                s: s.type == "rectangle" and s.point1X < shape.point1X and s.point1Y < shape.point1Y and s.point2X > shape.point2X and s.point2Y > shape.point2Y,
                            objList),
                        lambda s1, s2: cmp(abs(s1.point2X - s1.point1X) * abs(s1.point2Y - s1.point1Y),
                                           abs(s2.point2X - s2.point1X) * abs(s2.point2Y - s2.point1Y))
                    )))  # type: Shape

        position1X = 110
        position1Y = 30
        position2X = 490
        position2Y = 130
        parentPositionX = 1
        parentPositionY = 1
        styles = ""
        self.elementAttrs = ""
        if shape:
            position1X = shape.point1X
            position1Y = shape.point1Y
            position2X = shape.point2X
            position2Y = shape.point2Y
            if shapeParent:
                parentPositionX = shapeParent.point1X
                parentPositionY = shapeParent.point1Y
            if shape.descriptionOther:
                self.elementAttrs = shape.descriptionOther
            styles += "border-style: solid; border-width: %dpx; border-color: #%s;" % (
                shape.strokeWidth, '{0:06X}'.format(shape.color))
            if shape.filled:
                styles += " background-color: #%s;" % '{0:06X}'.format(shape.color)
            configurationTool.loggerDebug(
                "Find shape %s %d:%d, parent: %d:%d" % (self.id, shape.point1X, shape.point1Y, parentPositionX, parentPositionY))

        self.elementAttrs += " style=\"%s\"" % styles
        self.htmlScript = """
var elementId = "%s";
var element = document.getElementById(elementId);
if(element){
    const position1X = convertCoordX(%d);
    const position1Y = convertCoordY(%d);
    const position2X = convertCoordX(%d);
    const position2Y = convertCoordY(%d);
    const width = Math.abs(position2X - position1X);
    const height = Math.abs(position2Y - position1Y);
    if(element){
        element.style.position = "absolute";
        element.style.left = position1X + "px";
        element.style.top = position1Y + "px";
        element.style.width = width + "px";
        element.style.height = height + "px";
    }
}
        """ % (self.id, abs(parentPositionX - position1X), abs(parentPositionY - position1Y), abs(parentPositionX - position2X),
               abs(parentPositionY - position2Y))
        if htmlScript:
            self.htmlScript += "\n" + htmlScript + "\n"

    def process(self, configurationTool, executionContextTool):
        # type: (SMCApi.ConfigurationTool, SMCApi.ExecutionContextTool) -> None
        SmcUtils.processMessagesAll(configurationTool, executionContextTool,
                                    lambda id, messages: self.prcessMessages(configurationTool, executionContextTool, messages))

    def prcessMessages(self, configurationTool, executionContextTool, messages):
        # type: (SMCApi.ConfigurationTool, SMCApi.ExecutionContextTool, List[List[SMCApi.IMessage]]) -> None
        type = executionContextTool.getType().lower()
        if type == "request":
            objectArray = SmcUtils.deserializeToObject(messages[0])
            inputObj = None  # type: InputObj
            if SmcUtils.isArrayContainObjectElements(objectArray):
                inputObj = InputObj(objectArray.get(0))
            if inputObj is None or inputObj.type is None:
                executionContextTool.addError("wrong input format")
                return

            value = ""
            if inputObj.type == "get":
                if inputObj.cache and "value" in inputObj.cache:
                    value = inputObj.cache["value"]
                elif executionContextTool.getFlowControlTool().countManagedExecutionContexts() > 0:
                    lst = SmcUtils.executeAndGetMessages(executionContextTool, 0, [])
                    if lst and len(lst) > 0:
                        value = SmcUtils.toString(lst[0])
            elif inputObj.type == "update":
                if inputObj.params and self.id in inputObj.params:
                    value = inputObj.params[self.id]
                if executionContextTool.getFlowControlTool().countManagedExecutionContexts() > 1:
                    executionContextTool.getFlowControlTool().executeNow(SMCApi.CommandType.EXECUTE, 1, [value])

            executionContextTool.addMessage(self.genResponse(value))

    def genResponse(self, value):
        # type: (str) -> SMCApi.ObjectArray
        objOutput = SMCApi.ObjectElement([
            SMCApi.ObjectField("id", self.id),
            SMCApi.ObjectField("htmlHead", self.htmlHead),
            SMCApi.ObjectField("htmlScript", self.htmlScript),
            SMCApi.ObjectField("data", SMCApi.ObjectElement([SMCApi.ObjectField("value", value)])),
        ])
        if self.type == "textarea":
            objOutput.fields.append(SMCApi.ObjectField(
                "htmlBody",
                "<textarea id=\"%s\" name=\"%s\" %s >%s</textarea>" %
                (self.id, self.id, self.elementAttrs, value)))
        else:
            objOutput.fields.append(SMCApi.ObjectField(
                "htmlBody",
                "<input id=\"%s\" name=\"%s\" value=\"%s\" %s />" %
                (self.id, self.id, value, self.elementAttrs)))
        return SMCApi.ObjectArray(SMCApi.ObjectType.OBJECT_ELEMENT, [objOutput])

    def update(self, configurationTool):
        # type: (SMCApi.ConfigurationTool) -> None
        self.stop(configurationTool)
        self.start(configurationTool)

    def stop(self, configurationTool):
        # type: (SMCApi.ConfigurationTool) -> None
        self.id = None  # type: str
        self.type = None  # type: str
        self.htmlHead = None  # type: str
        self.htmlScript = None  # type: str
        self.elementAttrs = None  # type: str
