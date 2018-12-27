

NODE_SUB_ATTRS = {
  "main": ["node_id", "name", "location", "product_name", "manufacturer_name"],
  "status_props": ["is_awake", "is_beaming_device", "is_failed",
                   "is_frequent_listening_device", "is_info_received",
                   "is_listening_device", "is_locked", "is_ready",
                   "is_routing_device", "is_security_device", "is_sleeping",
                   "is_zwave_plus"],
  "props": ["query_stage", "type", "specific", "product_type", "product_id", "manufacturer_id",
            "basic", "capabilities", "command_classes", "device_type",
            "generic", "max_baud_rate", "neighbors", "num_groups",
            "role", "security", "version"],
  #"sub": ["values", "groups"] <---- good? bad? exclude here seems to be more convienient
}
NODE_EXTRA_ATTRS = []
NODE_ATTRS = sum(NODE_SUB_ATTRS.values(), []) + NODE_EXTRA_ATTRS

NODE_SUB_ACTIONS = {
  "show":   ["assign_return_route",  "heal", "network_update", "neighbor_update", "set_field",
             "refresh_info", "request_state", "send_information", "test", "stats"],
  "__hide": ["get_command_class_genres", "get_max_associations",
             "get_stats_label", "has_command_class"]}
NODE_WRAPPED = {
  "remove_failed": lambda node, action, args, zwave: zwave.ctrl[0].remove_failed_node(node.node_id)
}
NODE_ACTIONS = NODE_SUB_ACTIONS["show"] + list(NODE_WRAPPED.keys())
NODE_MEMBERS = NODE_ATTRS + sum(NODE_SUB_ACTIONS.values(), [])
NODE_MEMBERS.sort()






NET_SUB_ATTRS = {
  "main": ["home_id", "noes_count", "scenes_count", "state"],
  "status_props": ["is_ready"],
  "props": ["sleeping_nodes_count"]}
NET_EXTRA_ATTRS = []
NET_ATTRS = sum(NET_SUB_ATTRS.values(), []) + NET_EXTRA_ATTRS

NET_SUB_ACTIONS = {
  "show": ["heal", "stop", "write_config", "get_scenes", "test" ],
  "__hide": []}
NET_WRAPPED = {
    "start": lambda net, action, args, zwave: zwave.start()
}
NET_ACTIONS = NET_SUB_ACTIONS["show"] + list(NET_WRAPPED.keys())
NET_MEMBERS = NET_ATTRS + sum(NET_SUB_ACTIONS.values(), [])
NET_MEMBERS.sort()





CTRL_SUB_ATTRS = {
  "main": ["device", "stats", "name", "node", "node_id"],
  "status_props": ["is_primary_controller"],
  "props": ["capabilities", "options", "owz_library_version", "python_library_config_version",
            "library_config_path", "library_description", "library_type_name",
            "library_user_path", "library_version"]}
CTRL_EXTRA_ATTRS = []
CTRL_ATTRS = sum(CTRL_SUB_ATTRS.values(), []) + CTRL_EXTRA_ATTRS

CTRL_SUB_ACTIONS = {
  "show":    ["start", "stop", "add_node",  "assign_return_route", "cancel_command",
              "remove_node", "create_new_primary"],
  "__hide":  ["hard_reset", "soft_reset", "remove_failed_node"]
}
CTRL_WRAPPED = {
    "add_secure_node": lambda ctrl, action, args, zwave: ctrl.add_node(doSecurity=True)
}
CTRL_ACTIONS = CTRL_SUB_ACTIONS["show"] + list(CTRL_WRAPPED.keys())
CTRL_MEMBERS = CTRL_ATTRS + sum(CTRL_SUB_ACTIONS.values(), [])
CTRL_MEMBERS.sort()





VALUE_SUB_ATTRS = {
    "main": ["data", "value_id"],
    "status_props": ["is_polled", "is_read_only", "is_set", "is_write_only"],
    "props": ["command_class", "data_as_string", "data_items", "genre", "help", "label", "max",
              "min", "id_on_network", "index", "instance", "parent_id", "poll_intensity",
              "precision", "type", "units"]}
VALUE_EXTRA_ATTRS = []
VALUE_ATTRS = sum(VALUE_SUB_ATTRS.values(), []) + VALUE_EXTRA_ATTRS

VALUE_SUB_ACTIONS = {
  "show":    ["check_data", "disable_poll", "enable_poll", "refresh", "set_change_verified", "is_change_verified"],
  "__hide":  []
}
VALUE_WRAPPED = {}
VALUE_ACTIONS = VALUE_SUB_ACTIONS["show"] + list(VALUE_WRAPPED.keys())
VALUE_MEMBERS = VALUE_ATTRS + sum(VALUE_SUB_ACTIONS.values(), [])
VALUE_MEMBERS.sort()




GROUP_SUB_ATTRS = {
    "main": ["associations", "index", "label"],
    "status_props": [],
    "props": ["associations_instances", "max_associations"]}
GROUP_EXTRA_ATTRS = ["cur_associations", "max_count", "cur_count"]
GROUP_ATTRS = sum(GROUP_SUB_ATTRS.values(), []) + GROUP_EXTRA_ATTRS

GROUP_SUB_ACTIONS = {
  "show":    ["add_association", "remove_association"],
  "__hide":  []
}
GROUP_WRAPPED = {
    #"cur_associations": lambda group, action, args, zwave: len(group.associations),
    #"max_count": lambda group, action, args, zwave: group.max_associations,
    #"cur_count": lambda group, action, args, zwave: len(group.associations)
}
GROUP_ACTIONS = GROUP_SUB_ACTIONS["show"] + list(GROUP_WRAPPED.keys())
GROUP_MEMBERS = GROUP_ATTRS + sum(GROUP_SUB_ACTIONS.values(), [])
GROUP_MEMBERS.sort()

