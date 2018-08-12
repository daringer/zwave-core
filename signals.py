from openzwave.network import ZWaveNetwork



net_signals = [
######  SIGNAL NAME                                    Handler
 (ZWaveNetwork.SIGNAL_NETWORK_FAILED,                    None,         ),    #   NetworkFailed
 (ZWaveNetwork.SIGNAL_NETWORK_STARTED,                   None,         ),    #   NetworkStarted
 (ZWaveNetwork.SIGNAL_NETWORK_READY,                     None,         ),    #   NetworkReady
 (ZWaveNetwork.SIGNAL_NETWORK_STOPPED,                   None,         ),    #   NetworkStopped
 (ZWaveNetwork.SIGNAL_NETWORK_RESETTED,                  None,         ),    #   DriverResetted
 (ZWaveNetwork.SIGNAL_NETWORK_AWAKED,                    None,         ),    #   DriverAwaked
 (ZWaveNetwork.SIGNAL_DRIVER_FAILED,                     None,         ),    #   DriverFailed
 (ZWaveNetwork.SIGNAL_DRIVER_READY,                      None,         ),    #   DriverReady
 (ZWaveNetwork.SIGNAL_DRIVER_RESET,                      None,         ),    #   DriverReset
 (ZWaveNetwork.SIGNAL_DRIVER_REMOVED,                    None,         ),    #   DriverRemoved
 (ZWaveNetwork.SIGNAL_NODE_ADDED,                        None,         ),    #   NodeAdded
 (ZWaveNetwork.SIGNAL_NODE_EVENT,                        None,         ),    #   NodeEvent
 (ZWaveNetwork.SIGNAL_NODE_NAMING,                       None,         ),    #   NodeNaming
 (ZWaveNetwork.SIGNAL_NODE_NEW,                          None,         ),    #   NodeNew
 (ZWaveNetwork.SIGNAL_NODE_PROTOCOL_INFO,                None,         ),    #   NodeProtocolInfo
 (ZWaveNetwork.SIGNAL_NODE_READY,                        None,         ),    #   NodeReady
 (ZWaveNetwork.SIGNAL_NODE_REMOVED,                      None,         ),    #   NodeRemoved
 (ZWaveNetwork.SIGNAL_SCENE_EVENT,                       None,         ),    #   SceneEvent
 (ZWaveNetwork.SIGNAL_VALUE_ADDED,                       None,         ),    #   ValueAdded
 (ZWaveNetwork.SIGNAL_VALUE_CHANGED,                     None,         ),    #   ValueChanged
 (ZWaveNetwork.SIGNAL_VALUE_REFRESHED,                   None,         ),    #   ValueRefreshed
 (ZWaveNetwork.SIGNAL_VALUE_REMOVED,                     None,         ),    #   ValueRemoved
 (ZWaveNetwork.SIGNAL_POLLING_ENABLED,                   None,         ),    #   PollingEnabled
 (ZWaveNetwork.SIGNAL_POLLING_DISABLED,                  None,         ),    #   PollingDisabled
 (ZWaveNetwork.SIGNAL_CREATE_BUTTON,                     None,         ),    #   CreateButton
 (ZWaveNetwork.SIGNAL_DELETE_BUTTON,                     None,         ),    #   DeleteButton
 (ZWaveNetwork.SIGNAL_BUTTON_ON,                         None,         ),    #   ButtonOn
 (ZWaveNetwork.SIGNAL_BUTTON_OFF,                        None,         ),    #   ButtonOff
 (ZWaveNetwork.SIGNAL_ESSENTIAL_NODE_QUERIES_COMPLETE,   None,         ),    #   EssentialNodeQueriesComplete
 (ZWaveNetwork.SIGNAL_NODE_QUERIES_COMPLETE,             None,         ),    #   NodeQueriesComplete
 (ZWaveNetwork.SIGNAL_AWAKE_NODES_QUERIED,               None,         ),    #   AwakeNodesQueried
 (ZWaveNetwork.SIGNAL_ALL_NODES_QUERIED,                 None,         ),    #   AllNodesQueried
 (ZWaveNetwork.SIGNAL_ALL_NODES_QUERIED_SOME_DEAD,       None,         ),    #   AllNodesQueriedSomeDead
 (ZWaveNetwork.SIGNAL_MSG_COMPLETE,                      None,         ),    #   MsgComplete
 #(ZWaveNetwork.SIGNAL_ERROR,                            None,         ),    #   Error
 (ZWaveNetwork.SIGNAL_NOTIFICATION,                      None,         ),    #   Notification
 (ZWaveNetwork.SIGNAL_CONTROLLER_COMMAND,                None,         ),    #   ControllerCommand
 (ZWaveNetwork.SIGNAL_CONTROLLER_WAITING,                None,         ),    #   ControllerWaiting
]

