from json import dumps

from ._Action import Action
from ._Conditions import Conditions


class Benefit(object):
    """Benefit - Represents a benefit/benefit object"""

    def __init__(self, benefit_id, name, user_description, priority, automatic, conditions, actions):
        # type: (str, str, str, int, bool, Conditions, list[Action]) -> None
        self.id = benefit_id
        self.name = name
        self.user_description = user_description
        self.priority = priority
        self.automatic = automatic
        self.conditions = conditions
        self.actions = actions

    @staticmethod
    def from_self_stored_json(obj):
        return Benefit(
            obj.get("id"),
            obj.get("name"),
            obj.get("user_description"),
            int(obj.get("priority")) if obj.get("priority") else None,
            bool(obj.get("automatic")),
            Conditions.from_self_stored_json(obj.get("conditions")),
            [Action(o) for o in object.get("actions", [])]
        )

    @staticmethod
    def from_benefit_json(benefit):
        # type: (dict) -> Benefit

        benefit_id = benefit.get("id")
        name = benefit.get("name")
        user_description = benefit.get("userDescription")
        priority = int(benefit.get("priority")) if benefit.get("priority") else None
        automatic = bool(benefit.get("automatic"))
        conditions = Conditions.from_benefit_json(benefit.get("conditions") if benefit.get("conditions") else dict())
        actions = [
            Action({"order": e[0], "name": e[1].items()[0][0], "value": e[1].items()[0][1]})
            for e in benefit.get("actions", {}).items()
        ]

        return Benefit(
            benefit_id=benefit_id,
            name=name,
            user_description=user_description,
            priority=priority,
            automatic=automatic,
            conditions=conditions,
            actions=actions
        )

    def to_json(self):
        return dumps(self, default=lambda o: o.__dict__ if hasattr(o, '__dict__') else str(o), sort_keys=True)
