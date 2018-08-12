baseurl="http://localhost:5000"

curl -X PATCH -d device=/dev/ttyACM0 -d logging=false ${baseurl}/net/opts
curl -X DELETE ${baseurl}/net/opts
curl -X PATCH -d device=/dev/ttyACM0 -d logging=false ${baseurl}/net/opts
curl -X POST ${baseurl}/net/opts
curl -X POST ${baseurl}/net/action/start
sleep 3
curl -X GET ${baseurl}/net 
curl -X GET ${baseurl}/net/signals

curl -X GET ${baseurl}/net/ctrl/actions
curl -X GET ${baseurl}/net/actions

curl -X GET ${baseurl}/nodes
curl -X POST ${baseurl}/net/action/test?count=[int]2
curl -X POST ${baseurl}/net/action/get_scenes
curl -X POST ${baseurl}/net/action/scenes_count
curl -X POST ${baseurl}/net/ctrl/action/capabilities

curl -X GET ${baseurl}/net/signals/latest/10

curl -X GET ${baseurl}/node/1
curl -X GET ${baseurl}/node/1/values
#curl -X GET ${baseurl}/node/1/value/1

curl -X POST ${baseurl}/net/action/write_config
#curl -X POST ${baseurl}/net/action/stop

