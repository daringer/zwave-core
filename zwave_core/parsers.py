from flask_restful import reqparse


new_parser = reqparse.RequestParser


###
### ZWave Start-up Options Parser
###
opt_parse = new_parser()
add = opt_parse.add_argument
add("device", type=str,
     help="(file) path to the (zwave) serial device", default="/dev/ttyACM0")
add("config_path", type=str,
     help="where to put/find all the configs", default="/etc/openzwave/")
add("user_path", type=str,
     help="user path to be used", default=".")
add("cmd_line", type=str,
     help="commandline to be used", default="")
add("logging", type=bool,
     help="shall the logging be activated", default=False)
add("log_file", type=str,
     help="where to put the open-zwave logfile", default="OZWLog.log")
add("append_log_file", type=bool,
     help="append or re-create and truncate logfile?", default=False)
add("console_output", type=bool,
     help="write log output to console/stdout?", default=False)
# add("save_log_level", type=int,
#     help="which log-level will be used for saving", default=5)
# add("queue_log_level", type=int,
#     help="which log-level will be used for queueing", default=5)
add("associate", type=bool,
     help="set up all associations during network init?", default=True)
add("poll_interval", type=int,
     help="polling shall be done every n seconds", default=300)
add("save_configuration", type=bool,
     help="on exit save z-wave configuration?", default=True)
add("driver_max_attempts", type=int,
     help="set the driver max attempts", default=5)
# add("dump_trigger_level", type=bool,
#     help="set the driver max attempts", default=5)
add("exclude", type=str,
     help="remove support for the seted command classes.", default="")
add("include", type=str,
     help="only handle the specified command classes, ignore exlude", default="")
add("interval_between_polls", type=bool,
     help="true: means keep time between polling each node", default=False)
add("notify_transactions", type=bool,
     help="notifcations when transaction complete is reported", default=False)
add("suppress_value_refresh", type=bool,
     help="true: notifications for (unchanged) values will not be sent.", default=False)


nodes_parse = new_parser()
add = nodes_parse.add_argument
add("fields", action="append", required=True, help="which fields shall be extracted for the nodes")

value_parse = new_parser()
add = value_parse.add_argument
add("data", required=True, help="The 'data' the value will be set to")

group_parse = new_parser()
add = group_parse.add_argument
add("target_node_id", required=True, type=int, help="NodeID related to group")






