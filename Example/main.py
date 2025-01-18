#!/usr/bin/env python

import random

import SMCApi
import camelcase
# import jnumeric
import numpy as np


class ModuleMain(SMCApi.Module):
    def __init__(self):
        self.c = None
        self.counter = None
        self.value = None
        self.param = None
        self.fileTextValue = None

    def start(self, configurationTool):
        # type: (SMCApi.ConfigurationTool) -> None
        # print "call start"
        # get settings
        self.counter = 0
        self.c = camelcase.CamelCase()
        self.value = configurationTool.getSetting("value").getValue()
        self.param = configurationTool.getSetting("param").getValue()

        self.counter = 1

        # reed file from home folder
        self.fileTextValue = None
        fileToolRoot = configurationTool.getHomeFolder()
        lstChildrens = fileToolRoot.getChildrens()
        for fileToolElement in lstChildrens:
            if fileToolElement.getName() == "text.txt":
                self.fileTextValue = fileToolElement.getBytes().decode("utf-8")
                break
        if self.fileTextValue is None:
            raise SMCApi.ModuleException("file text.txt not exist")

        # a = np.array(10)
        # b = np.array([[1, 0], [0, 1]])
        c = np.reshape(np.arange(15), [3, 5])
        configurationTool.loggerTrace(str(c))

    def process(self, configurationTool, executionContextTool):
        # type: (SMCApi.ConfigurationTool, SMCApi.ExecutionContextTool) -> None
        # send messages
        executionContextTool.addMessage(self.counter)
        self.counter += 1
        executionContextTool.addMessage(self.value)
        executionContextTool.addMessage(self.c.hump(self.fileTextValue))

        # read input messages
        for i in range(executionContextTool.countSource()):
            actions = executionContextTool.getMessages(i)
            for j in range(len(actions)):
                for message in actions[j].getMessages():
                    executionContextTool.addMessage(message.getValue())

        # execute all execution contexts and result messages send as own message
        for i in range(executionContextTool.getFlowControlTool().countManagedExecutionContexts()):
            executionContextTool.getFlowControlTool().executeNow(SMCApi.CommandType.EXECUTE, i, [self.param])
            actions = executionContextTool.getFlowControlTool().getMessagesFromExecuted(0, i)
            for j in range(len(actions)):
                for message in actions[j].getMessages():
                    executionContextTool.addMessage(message.getValue())

        # read managed configurations
        for i in range(executionContextTool.getConfigurationControlTool().countManagedConfigurations()):
            executionContextTool.addMessage(executionContextTool.getConfigurationControlTool().getManagedConfiguration(i).getName())

        # create new random configuration
        modules = executionContextTool.getConfigurationControlTool().getModules()
        module = modules[random.randint(0, len(modules) - 1)]
        configuration = executionContextTool.getConfigurationControlTool().createConfiguration(
            executionContextTool.getConfigurationControlTool().countManagedConfigurations(),
            configurationTool.getContainer(), module, "cfg-" + str(random.randint(0, 1000000))
        )
        executionContextTool.addMessage("created cfg " + configuration.getName())
        if executionContextTool.getConfigurationControlTool().countManagedConfigurations() > 1:
            configurationManaged = executionContextTool.getConfigurationControlTool().getManagedConfiguration(0)
            if configurationManaged.countExecutionContexts() > 0:
                ec = configurationManaged.getExecutionContext(0)
                if ec is not None:
                    moduleMain = configurationManaged.getModule()
                    configurationTool.loggerInfo("%s %s" % (ec.getName(), ec.getType()))
                    # add first execution context of created configuration to execution context list of first execution context first managed configuration
                    if (moduleMain.getMinCountExecutionContexts(0) <= ec.countExecutionContexts() + 1) and (
                            moduleMain.getMaxCountExecutionContexts(0) == -1 or
                            moduleMain.getMaxCountExecutionContexts(0) > ec.countExecutionContexts()):
                        iExecutionContextManaged1 = configuration.getExecutionContext(0)
                        ec.insertExecutionContext(ec.countExecutionContexts(), iExecutionContextManaged1)
                        executionContextTool.addMessage(
                            "add " + configuration.getName() + "." + iExecutionContextManaged1.getName() + " to " +
                            configurationManaged.getName() + "." + ec.getName())
                    # add created configuration to managed configuration list of first execution context first managed configuration
                    if (moduleMain.getMinCountManagedConfigurations(0) <= ec.countManagedConfigurations() + 1) and (
                            moduleMain.getMaxCountManagedConfigurations(0) == -1 or
                            moduleMain.getMaxCountManagedConfigurations(0) > ec.countManagedConfigurations()):
                        ec.insertManagedConfiguration(ec.countManagedConfigurations(), configuration)
                        executionContextTool.addMessage(
                            "add " + configuration.getName() + " to " + configurationManaged.getName() + "." + ec.getName())
                    # add first execution context of created configuration as source to first execution context first managed configuration
                    if (moduleMain.getMinCountSources(0) <= ec.countSource() + 1) and (
                            moduleMain.getMaxCountSources(0) == -1 or moduleMain.getMaxCountSources(0) > ec.countSource()):
                        iExecutionContextManaged2 = configuration.getExecutionContext(0)
                        sourceManaged = ec.createSourceExecutionContext(iExecutionContextManaged2, SMCApi.SourceGetType.NEW, 0)
                        sourceManaged.createFilterPosition([0, -1])
                        executionContextTool.addMessage(
                            "add " + configuration.getName() + "." + iExecutionContextManaged2.getName() + " to " +
                            configurationManaged.getName() + "." + ec.getName() + " as source")

    def update(self, configurationTool):
        # type: (SMCApi.ConfigurationTool) -> None
        self.stop(configurationTool)
        self.start(configurationTool)

    def stop(self, configurationTool):
        # type: (SMCApi.ConfigurationTool) -> None
        self.c = None
        self.counter = None
        self.value = None
        self.param = None
        self.fileTextValue = None
