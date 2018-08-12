curl -X PATCH -d device=/dev/ttyACM0 -d logging=false http://localhost:5000/net/opts
curl -X DELETE http://localhost:5000/net/opts
curl -X PATCH -d device=/dev/ttyACM0 -d logging=false http://localhost:5000/net/opts
curl -X POST http://localhost:5000/net/opts
curl -X POST http://localhost:5000/net/action/start
sleep 3
curl -X GET http://localhost:5000/net 
curl -X GET http://localhost:5000/net/signals

curl -X GET http://localhost:5000/nodes
curl -X POST http://localhost:5000/net/action/test?count=[int]2
curl -X POST http://localhost:5000/net/action/get_scenes
curl -X POST http://localhost:5000/net/action/scenes_count
curl -X POST http://localhost:5000/net/ctrl/action/capabilities



#curl -X POST http://localhost:5000/net/action/stop
