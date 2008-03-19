# TODO: make running leave on startup optional

import gobject

import logging
logger = logging.getLogger("Context")

# TODO: add flag for "silent" so that context changes are not announced

class Context(gobject.GObject):

    __gsignals__ = {
        'changed': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ())
        }
    
    def __init__(self, name):
        gobject.GObject.__init__(self)
        self.name = name
        self.rules = []
        self.entering_actions = []
        self.leaving_actions = []
    
    def getName(self):
        return self.name

    def addRule(self, rule):
        def changed(source):
            self.emit("changed")
        rule.source.connect("changed", changed)
        self.rules.append(rule)

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

    def evaluateRules(self):
        # TODO: Provide other ways to evaluate rules with OR and AND? Let's have
        # only AND for now.  Maybe add "confidence" to the rules, which can be
        # use to implement this.
        for r in self.rules:
            if not r.evaluate():
                return False
        return True 

    def getPollInterval(self):    
        return reduce (lambda x, y: min(x, y or x), [r.source.getPollInterval() for r in self.rules])

    def __str__(self):
        return self.name

gobject.type_register(Context)
