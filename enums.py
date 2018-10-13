from enum import IntEnum


class NetState(IntEnum):
    stopped   = 0
    failed    = 1
    resetted  = 3
    started   = 5
    awaked    = 7
    ready     = 10

