# TODO: make running leave on startup optional

import logging
logger = logging.getLogger("Context")

class Context:
    def __init__(self, name):
        self.name = name
        self.entering_actions = []
        self.leaving_actions = []
    
    def getName(self):
        return self.name

    def addEnterAction(self, action):
        self.entering_actions.append(action)

    def addLeaveAction(self, action):
        self.leaving_actions.append(action)

    def runEnteringActions(self):
        logger.info ("Entering %s" % self)
        [a.run() for a in self.entering_actions]

    def runLeavingActions(self):
        logger.info ("Leaving %s" % self)
        [a.run() for a in self.leaving_actions]

    def __str__(self):
        return self.name
