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


class ZWNotificationCode(IntEnum):
    msg_complete = 0    # completed message
    timeout      = 1    # issued by message(s) timing out
    no_operation = 2    # NoOperation message sent completion
    awake = 3           # reported on node -> wake-up
    sleep = 4           # reported on node -> sleep
    dead  = 5           # node considered dead currently by the ctrl
    alive = 6           # node revive (due to connection or similar)

class NodeValueType(IntEnum):
    bit_set   =  0
    boolean   =  1
    button    =  2
    byte      =  3
    decimal   =  4
    uid       =  5
    integer   =  6
    container =  7
    raw       =  8
    schedule  =  9
    short     = 10
    store     = 11
    string    = 12




