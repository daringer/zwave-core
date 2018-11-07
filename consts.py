

NODE_SUB_ATTRS = {
  "main": ["node_id", "name", "location", "product_name", "manufacturer_name"],
  "status_props": ["is_awake", "is_beaming_device", "is_failed",
                   "is_frequent_listening_device", "is_info_received",
                   "is_listening_device", "is_locked", "is_ready",
                   "is_routing_device", "is_security_device", "is_sleeping",
                   "is_zwave_plus"],
  "props": ["query_stage", "type", "specific", "product_type", "product_id", "manufacturer_id",
            "basic", "capabilities", "command_classes", "device_type",
            "generic", "stats", "max_baud_rate", "neighbors", "num_groups",
            "role", "security", "version"]}
NODE_ATTRS = sum(NODE_SUB_ATTRS.values(), [])

NODE_SUB_ACTIONS = {
  "show":   ["assign_return_route",  "heal", "network_update", "neighbor_update",
  "refresh_info", "request_state", "send_information", "test"],
  "__hide": ["get_command_class_genres", "get_max_associations",
  "get_stats_label", "has_command_class"]}
NODE_ACTIONS = NODE_SUB_ACTIONS["show"]

NET_SUB_ATTRS = {
  "main": ["home_id", "noes_count", "scenes_count", "state"],
  "status_props": ["is_ready"],
  "props": ["sleeping_nodes_count"]}
NET_ATTRS = sum(NET_SUB_ATTRS.values(), [])

NET_SUB_ACTIONS = {
  "show": ["heal", "start", "stop", "write_config", "get_scenes", "test" ],
  "__hide": []}
NET_ACTIONS = NET_SUB_ACTIONS["show"]

CTRL_SUB_ATTRS = {
  "main": ["device", "stats", "name", "node", "node_id"],
  "status_props": ["is_primary_controller"],
  "props": ["capabilities", "options", "owz_library_version", "python_library_config_version",
            "library_config_path", "library_description", "library_type_name",
            "library_user_path", "library_version"]}
CTRL_ATTRS = sum(CTRL_SUB_ATTRS.values(), [])

CTRL_SUB_ACTIONS = {
  "show": ["start", "stop", "add_node",  "assign_return_route", "cancel_command"],
  "__hide": ["exclude", "hard_reset", "soft_reset", "remove_node"]}
CTRL_ACTIONS = CTRL_SUB_ACTIONS["show"]

