import simplejson

import actions
from context import Context
from rules import Rule

def __stringise(d):
    new_d = {}
    for k in d.iterkeys():
        new_d[str(k)] = d[k]
    return new_d

def parse():
    result = {}

    for (context_name, context_data) in simplejson.load(open("config.json")).iteritems():
        context = Context(context_name)
        result[context_name] = context

        for data in context_data["rules"]:
            rule_name = data.pop("source")
            context.addRule(Rule(rule_name, **__stringise(data)))
        
        for data in context_data.get("enter", []):
            action_name = data.pop("action")
            cls = getattr(actions, action_name, None)
            if cls:
                action = cls(**__stringise(data))
                context.addEnterAction(action)

        for data in context_data.get("leave", []):
            action_name = data.pop("action")
            cls = getattr(actions, action_name, None)
            if cls:
                action = cls(**__stringise(data))
                context.addLeaveAction(action)
    
    return result


if __name__ == "__main__":
    print parse()
