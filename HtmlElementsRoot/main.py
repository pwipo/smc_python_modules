#!/usr/bin/env python
import datetime

import SMCApi
import SmcUtils
from typing import List


class HttpReq:
    def __init__(self, objectElement):
        # type: (SMCApi.ObjectElement) -> None
        # obj = SmcUtils.convertFromObjectElement(objectElement, True)
        self.method = SmcUtils.toStringField(objectElement.findField("method"))
        self.reqId = SmcUtils.toNumberField(objectElement.findField("reqId"))
        self.uri = SmcUtils.toStringField(objectElement.findField("uri"))
        self.remoteAddr = SmcUtils.toStringField(objectElement.findField("remoteAddr"))
        self.sessionId = SmcUtils.toStringField(objectElement.findField("sessionId"))
        self.params = SmcUtils.getObjectElement(objectElement.findField("params"))
        self.headers = SmcUtils.getObjectElement(objectElement.findField("headers"))
        self.multipart = SmcUtils.getObjectArrayField(objectElement.findField("multipart"))
        # self.size = None  # type: int
        # self.data = None  # type: bytes


class HtmlElementsOutput:
    def __init__(self, objectElement):
        # type: (SMCApi.ObjectElement) -> None
        self.id = SmcUtils.toStringField(objectElement.findField("id"))
        self.htmlHead = SmcUtils.toStringField(objectElement.findField("htmlHead"))
        self.htmlBody = SmcUtils.toStringField(objectElement.findField("htmlBody"))
        self.htmlScript = SmcUtils.toStringField(objectElement.findField("htmlScript"))
        self.data = SmcUtils.toObjectElementField(objectElement.findField("data"))
        if len(self.data.fields) == 0:
            self.data = None


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


class CacheElement:
    def __init__(self, sessionId, data):
        # type: (str, List[HtmlElementsOutput]) -> None
        self.sessionId = sessionId
        self.date = datetime.datetime.now()
        self.data = data  # type: List[HtmlElementsOutput]

    def genHtml(self, title, htmlHead, htmlScript):
        # type: (str, str, str) -> str
        htmlHeadList = []
        if htmlHead:
            htmlHeadList.append(htmlHead)
        htmlBodyList = []
        htmlScriptList = []
        if htmlScript:
            htmlScriptList.append("<script>%s</script>" % htmlScript)

        for e in self.data:
            e = e  # type: HtmlElementsOutput
            if e.htmlHead:
                htmlHeadList.append(e.htmlHead)
            if e.htmlBody:
                htmlBodyList.append(e.htmlBody)
            if e.htmlScript:
                htmlScriptList.append("<script>%s</script>" % e.htmlScript)

        return ("<html>\n<head>\n<title>%s</title>\n%s\n</head>\n<body>\n%s\n%s\n</body>\n</html>" %
                (title, '\n'.join(htmlHeadList), '\n'.join(htmlBodyList), '\n'.join(htmlScriptList)))


class ModuleMain(SMCApi.Module):
    def __init__(self):
        self.id = None  # type: str
        self.cache = None  # type: List[CacheElement]
        self.headers = None  # type: List[str]
        self.title = None  # type: str
        self.htmlHead = None  # type: str
        self.htmlScript = None  # type: str
        self.position1X = None  # type: int
        self.position1Y = None  # type: int
        self.position2X = None  # type: int
        self.position2Y = None  # type: int

    def start(self, configurationTool):
        # type: (SMCApi.ConfigurationTool) -> None
        self.cache = []  # type: List[CacheElement]
        self.id = SmcUtils.getString(configurationTool.getSetting("id"))

        strValue = SmcUtils.getString(configurationTool.getSetting("headers"))
        self.headers = []
        if strValue:
            self.headers = strValue.split("\n")

        self.title = SmcUtils.getString(configurationTool.getSetting("title"))
        self.htmlHead = SmcUtils.getString(configurationTool.getSetting("htmlHead"))
        htmlScript = SmcUtils.getString(configurationTool.getSetting("htmlScript"))

        shape = None  # type: Shape
        objectArray = SmcUtils.getObjectArray(configurationTool.getInfo("decorationShapes"))
        if SmcUtils.isArrayContainObjectElements(objectArray):
            objList = map(lambda s: Shape(s), SmcUtils.convertFromObjectArray(objectArray, True))  # type: List[Shape]
            shape = next(iter(
                filter(
                    lambda s: s.type == "rectangle" and s.descriptionList[0].startswith(self.id), objList)))  # type: Shape

        self.position1X = 0
        self.position1Y = 0
        self.position2X = 640
        self.position2Y = 480
        if shape:
            self.position1X = shape.point1X
            self.position1Y = shape.point1Y
            self.position2X = shape.point2X
            self.position2Y = shape.point2Y
            configurationTool.loggerDebug("Find shape: %s %d %d" % (self.id, shape.point1X, shape.point1Y))

        self.htmlScript = """
var position1X = %d;
var position1Y = %d;
var position2X = %d;
var position2Y = %d;
var width = Math.max(position2X - position1X);

var multiX = window.screen.width/width; //works but looks weird
var screenRation = window.screen.width/window.screen.height;
var multiY = window.screen.height/(width/screenRation); //works but looks weird

function convertCoordX(x) {
    // let result = position1X - x;
    // return result > 0 ? Math.min(result, width) : 0;
    return Math.floor(x*multiX);
}

function convertCoordY(y) {
    // let result = position1Y - y;
    // return result > 0 ? Math.min(result, height) : 0;
    return Math.floor(y*multiY);
}
""" % (self.position1X, self.position1Y, self.position2X, self.position2Y)
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
            httpInput = None  # type: HttpReq
            if SmcUtils.isArrayContainObjectElements(objectArray):
                httpInput = HttpReq(objectArray.get(0))
            if httpInput is None:
                executionContextTool.addError("wrong input format")
                return

            cacheElement = next(iter(filter(lambda c: c.sessionId == httpInput.sessionId, self.cache)), None)  # type: CacheElement
            dataList = []  # type: List[HtmlElementsOutput]
            if cacheElement is None:
                cacheElement = CacheElement(httpInput.sessionId, dataList)
                self.cache.append(cacheElement)

            configurationTool.loggerTrace("request session=%s method=%s" % (httpInput.sessionId, httpInput.method))
            paramObj = SMCApi.ObjectElement()
            if httpInput.method == "GET":
                paramObj.fields.append(SMCApi.ObjectField("type", "get"))
                for i in range(executionContextTool.getFlowControlTool().countManagedExecutionContexts()):
                    paramObjCopy = SMCApi.ObjectElement()
                    paramObjCopy.fields = paramObj.fields[:]
                    if cacheElement is not None and cacheElement.data and len(cacheElement.data) > i and cacheElement.data[i].data:
                        paramObjCopy.fields.append(SMCApi.ObjectField("cache", cacheElement.data[i].data))
                    dataList.append(HtmlElementsOutput(
                        SmcUtils.executeAndGetElement(executionContextTool, i,
                                                      [SMCApi.ObjectArray(SMCApi.ObjectType.OBJECT_ELEMENT, [paramObjCopy])])))
            elif httpInput.method == "POST":
                paramObj.fields.append(SMCApi.ObjectField("type", "update"))
                for i in range(executionContextTool.getFlowControlTool().countManagedExecutionContexts()):
                    paramObjCopy = SMCApi.ObjectElement()
                    paramObjCopy.fields = paramObj.fields[:]
                    if cacheElement is not None and cacheElement.data and len(cacheElement.data) > i and cacheElement.data[i].data:
                        paramObjCopy.fields.append(SMCApi.ObjectField("cache", cacheElement.data[i].data))
                    if httpInput.params:
                        paramObjCopy.fields.append(SMCApi.ObjectField("inputParams", httpInput.params))
                    if httpInput.headers:
                        paramObjCopy.fields.append(SMCApi.ObjectField("inputHeaders", httpInput.headers))
                    if httpInput.multipart:
                        paramObjCopy.fields.append(SMCApi.ObjectField("inputMultipart", httpInput.multipart))
                    dataList.append(HtmlElementsOutput(
                        SmcUtils.executeAndGetElement(executionContextTool, i,
                                                      [SMCApi.ObjectArray(SMCApi.ObjectType.OBJECT_ELEMENT, [paramObjCopy])])))

            cacheElement.date = datetime.datetime.now()
            cacheElement.data = dataList

            executionContextTool.addMessage(200)
            if self.headers:
                for header in self.headers:
                    executionContextTool.addMessage(header)

            executionContextTool.addMessage(cacheElement.genHtml(self.title, self.htmlHead, self.htmlScript))

    def update(self, configurationTool):
        # type: (SMCApi.ConfigurationTool) -> None
        self.stop(configurationTool)
        self.start(configurationTool)

    def stop(self, configurationTool):
        # type: (SMCApi.ConfigurationTool) -> None
        self.id = None  # type: str
        self.cache = None  # type: List[CacheElement]
        self.headers = None  # type: List[str]
        self.title = None  # type: str
        self.htmlHead = None  # type: str
        self.htmlScript = None  # type: str
        self.position1X = None  # type: int
        self.position1Y = None  # type: int
        self.position2X = None  # type: int
        self.position2Y = None  # type: int