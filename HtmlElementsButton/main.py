#!/usr/bin/env python

import SMCApi
import SmcUtils
from typing import List


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
        self.color = obj.color  # type: int
        self.strokeWidth = obj.strokeWidth  # type: int
        self.description = obj.description  # type: str
        self.descriptionList = []  # type: List[str]
        if self.description:
            self.descriptionList = map(lambda s: s.strip(), filter(lambda s: s and s.strip(), self.description.strip().split(" ")))
        if len(self.descriptionList) == 0:
            self.descriptionList.append("")
        self.text = None  # type: str
        if 'text' in keys:
            self.text = obj.text  # type: str
        self.filled = None  # type: bool
        if 'filled' in keys:
            self.filled = obj.filled  # type: bool
        self.imageBytes = None  # type: bytes
        if 'imageBytes' in keys:
            self.imageBytes = obj.imageBytes  # type: bytes


class ModuleMain(SMCApi.Module):
    def __init__(self):
        self.id = None  # type: str
        self.type = None  # type: str
        self.htmlHead = None  # type: str
        self.htmlScript = None  # type: str
        self.elementAttrs = None  # type: str
        self.text = None  # type: str

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
                    lambda s: s.type == "rectangle" and s.descriptionList[0].startswith(self.id), objList)))  # type: Shape
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
        self.elementAttrs = ""
        self.text = "button"
        if shape:
            position1X = shape.point1X
            position1Y = shape.point1Y
            position2X = shape.point2X
            position2Y = shape.point2Y
            if shapeParent:
                parentPositionX = shapeParent.point1X
                parentPositionY = shapeParent.point1Y
            if len(shape.descriptionList) > 1:
                self.elementAttrs = ' '.join(shape.descriptionList[1:])
            styleBackgroundColor = ""
            if shape.filled:
                styleBackgroundColor = "background-color: #" + '{0:06X}'.format(shape.color) + ";"
            self.elementAttrs += " style=\"border-style: solid; border-width: %dpx; border-color: #%s; %s \"" % (
                shape.strokeWidth, '{0:06X}'.format(shape.color), styleBackgroundColor)
            self.text = shape.text
            configurationTool.loggerDebug(
                "Find shape %s %d:%d, parent: %d:%d" % (self.id, shape.point1X, shape.point1Y, parentPositionX, parentPositionY))

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
            executionContextTool.addMessage(self.genResponse())

    def genResponse(self):
        # type: () -> SMCApi.ObjectArray
        objOutput = SMCApi.ObjectElement([
            SMCApi.ObjectField("id", self.id),
            SMCApi.ObjectField("htmlHead", self.htmlHead),
            SMCApi.ObjectField("htmlScript", self.htmlScript),
        ])
        objOutput.fields.append(SMCApi.ObjectField(
            "htmlBody",
            "<button id=\"%s\" name=\"%s\" type=\"%s\" %s >%s</button>" %
            (self.id, self.id, self.type, self.elementAttrs, self.text)))
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
        self.text = None  # type: str
