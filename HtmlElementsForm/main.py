#!/usr/bin/env python

import SMCApi
import SmcUtils
from typing import List


class InputObj:
    def __init__(self, objectElement):
        # type: (SMCApi.ObjectElement) -> None
        self.type = SmcUtils.getStringField(objectElement.findField("type"))
        self.params = SmcUtils.getObjectElement(objectElement.findField("params"))
        self.headers = SmcUtils.getObjectElement(objectElement.findField("headers"))
        self.multipart = SmcUtils.getObjectArrayField(objectElement.findField("multipart"))
        cache = SmcUtils.getObjectElement(objectElement.findField("cache"))
        self.cache = None  # type: List[SMCApi.ObjectElement]
        if cache:
            objectArray = SmcUtils.getObjectArrayField(cache.findField("data"))
            if SmcUtils.isArrayContainObjectElements(objectArray):
                self.cache = []  # type: List[SMCApi.ObjectElement]
                for i in range(objectArray.size()):
                    self.cache.append(objectArray.get(i))


class HtmlElementsOutput:
    def __init__(self, objectElement):
        # type: (SMCApi.ObjectElement) -> None
        self.id = SmcUtils.toStringField(objectElement.findField("id"))
        self.htmlHead = SmcUtils.toStringField(objectElement.findField("htmlHead"))
        self.htmlBody = SmcUtils.toStringField(objectElement.findField("htmlBody"))
        self.htmlScript = SmcUtils.toStringField(objectElement.findField("htmlScript"))
        self.data = SmcUtils.toObjectElementField(objectElement.findField("data"))
        if len(self.data.fields) == 0:
            self.data = None  # type: SMCApi.ObjectElement


class Shape:
    def __init__(self, obj):
        # type: (SmcUtils.ObjectDict) -> None
        keys = obj.keys()  # type: List[str]
        self.type = obj.type  # type: str
        self.name = obj.name  # type: str
        self.parentName = None  # type: str
        if "parentName" in obj:
            self.parentName = obj.parentName  # type: str
        self.x = obj.x  # type: int
        self.y = obj.y  # type: int
        self.width = obj.width  # type: int
        self.height = obj.height  # type: int
        self.offset2X = None  # type: int
        if 'offset2X' in keys:
            self.offset2X = obj.offset2X  # type: int
        self.offset2Y = None  # type: int
        if 'offset2Y' in keys:
            self.offset2Y = obj.offset2Y  # type: int
        self.color = obj.color & 0xffffff  # type: int
        self.strokeWidth = obj.strokeWidth  # type: int
        self.description = obj.description  # type: str
        # self.descriptionId = ""
        # self.descriptionOther = ""
        # if obj.description:
        #     arrStr = obj.description.strip().split(" ", 2)
        #     self.descriptionId = arrStr[0].strip()
        #     if len(arrStr) > 1:
        #         self.descriptionOther = arrStr[1].strip()
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
        self.htmlHead = None  # type: str
        self.htmlScript = None  # type: str
        self.elementAttrs = None  # type: str

    def start(self, configurationTool):
        # type: (SMCApi.ConfigurationTool) -> None
        self.id = SmcUtils.getString(configurationTool.getSetting("id"))
        self.htmlHead = SmcUtils.getString(configurationTool.getSetting("htmlHead"))
        htmlScript = SmcUtils.getString(configurationTool.getSetting("htmlScript"))

        objectArray = SmcUtils.getObjectArray(configurationTool.getInfo("decorationShapes"))
        shape = None  # type: Shape
        # shapeParent = None  # type: Shape
        if SmcUtils.isArrayContainObjectElements(objectArray):
            objList = map(lambda s: Shape(s), SmcUtils.convertFromObjectArray(objectArray, True))  # type: List[Shape]
            shape = next(iter(
                filter(
                    lambda s: s.type == "rectangle" and s.name == self.id, objList)))  # type: Shape
            # if shape:
            #     shapeParent = next(iter(
            #         sorted(
            #             filter(
            #                 lambda
            #                     s: s.type == "rectangle" and s.point1X < shape.point1X and s.point1Y < shape.point1Y and s.point2X > shape.point2X and s.point2Y > shape.point2Y,
            #                 objList),
            #             lambda s1, s2: cmp(abs(s1.point2X - s1.point1X) * abs(s1.point2Y - s1.point1Y),
            #                                abs(s2.point2X - s2.point1X) * abs(s2.point2Y - s2.point1Y))
            #         )))  # type: Shape

        position1X = 100
        position1Y = 20
        width = 500
        height = 200
        # parentPositionX = 1
        # parentPositionY = 1
        self.elementAttrs = ""
        if shape:
            position1X = shape.x
            position1Y = shape.y
            width = shape.width
            height = shape.height
            # if shapeParent:
            #     parentPositionX = shapeParent.point1X
            #     parentPositionY = shapeParent.point1Y
            if shape.description:
                self.elementAttrs = shape.description
            configurationTool.loggerDebug(
                "Find shape %s %d:%d, parent: %s" % (self.id, shape.x, shape.y, shape.parentName))

        self.htmlScript = """
var elementId = "%s";
var element = document.getElementById(elementId);
if(element){
    const position1X = %d;
    const position1Y = %d;
    const width = %d;
    const height = %d;
    if(element){
        element.style.position = "absolute";
        element.style.left = position1X + "px";
        element.style.top = position1Y + "px";
        element.style.width = width + "px";
        element.style.height = height + "px";
    }
}
        """ % (self.id, position1X, position1Y, width, height)
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

            dataList = []  # type: List[HtmlElementsOutput]
            paramObj = SMCApi.ObjectElement()
            paramObj.fields.append(SMCApi.ObjectField("type", inputObj.type))
            error = None

            configurationTool.loggerTrace("request type=%s" % (inputObj.type))
            if inputObj.type == "get":
                for i in range(executionContextTool.getFlowControlTool().countManagedExecutionContexts() - 1):
                    paramObjCopy = SMCApi.ObjectElement()
                    paramObjCopy.fields = paramObj.fields[:]
                    if inputObj.cache and len(inputObj.cache) > i and inputObj.cache[i]:
                        paramObjCopy.fields.append(SMCApi.ObjectField("cache", inputObj.cache[i]))
                    resultElement = SmcUtils.executeAndGetElement(
                        executionContextTool, i + 1, [SMCApi.ObjectArray(SMCApi.ObjectType.OBJECT_ELEMENT, [paramObjCopy])])
                    if resultElement:
                        dataList.append(HtmlElementsOutput(resultElement))
            elif inputObj.type == "update":
                resultCommand = None  # type: SMCApi.ICommand
                if (executionContextTool.getFlowControlTool().countManagedExecutionContexts() > 0 and inputObj.params and
                        SmcUtils.toStringField(inputObj.params.findField("formId")) == self.id):
                    paramObjCopyMain = SMCApi.ObjectElement()
                    paramObjCopyMain.fields = paramObj.fields[:]
                    if inputObj.params:
                        paramObjCopyMain.fields.append(SMCApi.ObjectField("params", inputObj.params))
                    if inputObj.headers:
                        paramObjCopyMain.fields.append(SMCApi.ObjectField("headers", inputObj.headers))
                    if inputObj.multipart:
                        paramObjCopyMain.fields.append(SMCApi.ObjectField("multipart", inputObj.multipart))
                    executionContextTool.getFlowControlTool().executeNow(SMCApi.CommandType.EXECUTE, 0,
                                                                         [SMCApi.ObjectArray(SMCApi.ObjectType.OBJECT_ELEMENT, [paramObjCopyMain])])
                    resultCommands = executionContextTool.getFlowControlTool().getCommandsFromExecuted(0, 0)
                    resultCommand = None
                    if resultCommands:
                        resultCommand = resultCommands[0]
                if SmcUtils.hasErrors(resultCommand):
                    error = ' '.join(map(lambda m: SmcUtils.toString(m), SmcUtils.getErrors(resultCommand)))
                    paramObj.fields.append(SMCApi.ObjectField("error", error))
                for i in range(executionContextTool.getFlowControlTool().countManagedExecutionContexts() - 1):
                    paramObjCopy = SMCApi.ObjectElement()
                    paramObjCopy.fields = paramObj.fields[:]
                    if inputObj.params:
                        paramObjCopy.fields.append(SMCApi.ObjectField("params", inputObj.params))
                    if inputObj.headers:
                        paramObjCopy.fields.append(SMCApi.ObjectField("headers", inputObj.headers))
                    if inputObj.multipart:
                        paramObjCopy.fields.append(SMCApi.ObjectField("multipart", inputObj.multipart))
                    if inputObj.cache and len(inputObj.cache) > i and inputObj.cache[i]:
                        paramObjCopy.fields.append(SMCApi.ObjectField("cache", inputObj.cache[i]))
                    resultElement = SmcUtils.executeAndGetElement(
                        executionContextTool, i + 1, [SMCApi.ObjectArray(SMCApi.ObjectType.OBJECT_ELEMENT, [paramObjCopy])])
                    if resultElement:
                        dataList.append(HtmlElementsOutput(resultElement))
                if error is None:
                    # if update succeess - get empty values
                    dataList = []
                    for i in range(executionContextTool.getFlowControlTool().countManagedExecutionContexts() - 1):
                        paramObjCopy = SMCApi.ObjectElement()
                        paramObjCopy.fields = paramObj.fields[:]
                        fieldType = paramObjCopy.findField("type")
                        if fieldType:
                            fieldType.setValue("get")
                        resultElement = SmcUtils.executeAndGetElement(
                            executionContextTool, i + 1, [SMCApi.ObjectArray(SMCApi.ObjectType.OBJECT_ELEMENT, [paramObjCopy])])
                        if resultElement:
                            dataList.append(HtmlElementsOutput(resultElement))

            executionContextTool.addMessage(self.genResponse(dataList, error))

    def genResponse(self, dataList, error):
        # type: (List[HtmlElementsOutput], str) -> SMCApi.ObjectArray
        htmlHeadList = []  # type: List[str]
        if self.htmlHead:
            htmlHeadList.append(self.htmlHead)
        htmlBodyList = []  # type: List[str]
        htmlScriptList = []  # type: List[str]
        if self.htmlScript:
            htmlScriptList.append(self.htmlScript)
        errorElement = ""
        if error:
            errorElement = "<strong style=\"color:Red;\">%s</strong>" % error
        dataChilds = []  # type: List[SMCApi.ObjectElement]

        for dataChild in dataList:
            if dataChild.htmlHead:
                htmlHeadList.append(dataChild.htmlHead)
            if dataChild.htmlBody:
                htmlBodyList.append(dataChild.htmlBody)
            if dataChild.htmlScript:
                htmlScriptList.append(dataChild.htmlScript)
            if dataChild.data:
                dataChilds.append(dataChild.data)
            else:
                dataChilds.append(SMCApi.ObjectElement())

        objOutput = SMCApi.ObjectElement([
            SMCApi.ObjectField("id", self.id),
            SMCApi.ObjectField("htmlHead", '\n'.join(htmlHeadList)),
            SMCApi.ObjectField("htmlBody",
                               "<form id=\"%s\" action=\"?\" method=\"post\" %s>\n<input type=\"hidden\" name=\"formId\" value=\"%s\">\n%s\n%s\n</form>" %
                               (self.id, self.elementAttrs, self.id, errorElement, '\n'.join(htmlBodyList))),
            SMCApi.ObjectField("htmlScript", '\n'.join(htmlScriptList)),
        ])
        if dataChilds:
            SMCApi.ObjectField("data", SMCApi.ObjectArray(SMCApi.ObjectType.OBJECT_ELEMENT, dataChilds))
        return SMCApi.ObjectArray(SMCApi.ObjectType.OBJECT_ELEMENT, [objOutput])

    def update(self, configurationTool):
        # type: (SMCApi.ConfigurationTool) -> None
        self.stop(configurationTool)
        self.start(configurationTool)

    def stop(self, configurationTool):
        # type: (SMCApi.ConfigurationTool) -> None
        self.id = None  # type: str
        self.htmlHead = None  # type: str
        self.htmlScript = None  # type: str
        self.elementAttrs = None  # type: str
