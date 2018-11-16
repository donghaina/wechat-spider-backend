#!/usr/bin/env bash
dockerimage="spider"
dockerport=8888
echo "stop present docker image"dod
pid=$(docker ps | grep $dockerimage | awk '{print $1}')
echo "${pid} variable"
if [ ! -z ${pid} ]; then
        exec docker stop $pid
fi
echo "build new docker image"
output=`exec docker build -t $dockerimage .`

echo "run new docker image"
# exec sudo docker run -it --rm -p 8888:8888 spider
exec sudo docker run -it --rm -p $dockerport:$dockerport $dockerimage
