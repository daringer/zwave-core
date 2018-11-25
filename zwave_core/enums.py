from enum import IntEnum


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

class FrontendAction(IntEnum):
    update_value = 1
    add_value = 2

