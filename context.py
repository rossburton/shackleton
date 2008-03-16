class Context:
    def __init__(self, name):
        self.name = name
        self.entering_actions = []
        self.leaving_actions = []
    
    def getName(self):
        return self.name

    def __repr__(self):
        return self.name

    def addEnterAction(self, action):
        self.entering_actions.append(action)

    def addLeaveAction(self, action):
        self.leaving_actions.append(action)

    def runEnteringActions(self):
        [a.run() for a in self.entering_actions]

    def runLeavingActions(self):
        [a.run() for a in self.leaving_actions]

