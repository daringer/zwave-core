from flask_restful import reqparse

###
### ZWave Start-up Options Parser
###
opt_parse = reqparse.RequestParser()
opt_parse.add_argument("device", type=str, 
     help="(file) path to the (zwave) serial device", default="/dev/ttyACM0")
opt_parse.add_argument("config_path", type=str, 
     help="where to put/find all the configs", default="/etc/openzwave/")
opt_parse.add_argument("user_path", type=str, 
     help="user path to be used", default=".")
opt_parse.add_argument("cmd_line", type=str, 
     help="commandline to be used", default="")
opt_parse.add_argument("logging", type=bool, 
     help="shall the logging be activated", default=False)
opt_parse.add_argument("log_file", type=str, 
     help="where to put the open-zwave logfile", default="OZWLog.log")
opt_parse.add_argument("append_log_file", type=bool, 
     help="append or re-create and truncate logfile?", default=False)
opt_parse.add_argument("console_output", type=bool, 
     help="write log output to console/stdout?", default=False)
#opt_parse.add_argument("save_log_level", type=int, 
#     help="which log-level will be used for saving", default=5)
#opt_parse.add_argument("queue_log_level", type=int, 
#     help="which log-level will be used for queueing", default=5)
opt_parse.add_argument("associate", type=bool, 
     help="set up all associations during network init?", default=True)
opt_parse.add_argument("poll_interval", type=int, 
     help="polling shall be done every n seconds", default=300)
opt_parse.add_argument("save_configuration", type=bool, 
     help="on exit save z-wave configuration?", default=True)
opt_parse.add_argument("driver_max_attempts", type=int, 
     help="set the driver max attempts", default=5)
#opt_parse.add_argument("dump_trigger_level", type=bool, 
#     help="set the driver max attempts", default=5)
opt_parse.add_argument("exclude", type=str, 
     help="remove support for the seted command classes.", default="")
opt_parse.add_argument("include", type=str, 
     help="only handle the specified command classes, ignore exlude", default="")
opt_parse.add_argument("interval_between_polls", type=bool, 
     help="true: means keep time between polling each node", default=False)
opt_parse.add_argument("notify_transactions", type=bool, 
     help="notifcations when transaction complete is reported", default=False)
opt_parse.add_argument("suppress_value_refresh", type=bool, 
     help="true: notifications for (unchanged) values will not be sent.", default=False)

