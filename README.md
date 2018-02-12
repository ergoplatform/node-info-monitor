This repository provide API `/info` monitoring tool.

## Usage

You should have preinstalled InfluxDB and/or have credentials like username/password for it. Create your `config.ini` file somewhere on host system and mount it as a volume to Docker container:

    sudo docker -d -v /your/config.ini:/app/config.ini ergoplatform/node-info-monitor

The command above will start monitoring daemon as docker container and start requesting `/info` Ergo node API endpoint to collect data and store it to InfluxDB.
