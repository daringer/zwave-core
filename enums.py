from enum import IntEnum


# @todo: return states or exceptions everywhere?1
class ReturnState(IntEnum):
    ok = 1

    zwave_offline = 64
    zwave_options_not_locked = 65

    error = 128
    unknown = 256


class OptionState(IntEnum):
    editable = 1
    failed   = 32
    empty    = 64
    locked   = 128
    unknown  = 256


class NetState(IntEnum):
    stopped   = 0
    failed    = 1
    resetted  = 3
    started   = 5
    awaked    = 7
    ready     = 10


