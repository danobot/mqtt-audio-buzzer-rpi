docker stop buzz
docker rm buzz

docker build -t danobot/buzz .
docker run --restart=unless-stopped --device=/dev/gpiomem --name buzz -d -e MQTT_HOST="tower.local" -e MQTT_TOPIC="/buzz"  danobot/buzz:latest
