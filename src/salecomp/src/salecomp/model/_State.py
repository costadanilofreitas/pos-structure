from enum import Enum


class State(Enum):
    undefined = 0
    in_progress = 1
    stored = 2
    totaled = 3
    voided = 4
    paid = 5
    recalled = 6
    system_voided = 7
    abandoned = 8
