This repository provide Ergo node REST API `/info` route monitoring tool.


## Usage with Docker

You should have preinstalled InfluxDB and/or have credentials like username/password for it. Create your `config.ini` file somewhere on host system and mount it as a volume to Docker container:

    sudo docker container run -d --restart=unless-stopped -v /your/config.ini:/app/config.ini ergoplatform/node-info-monitor

The command above will start monitoring daemon as docker container and start requesting `/info` Ergo node API endpoint to collect data and store it into InfluxDB. Also it will always will try to restart monitoring when something go wrong unless you stop container explicitly.


Another example shows how to print data that goes to InfluxDB:

    sudo docker run --rm -e INFLUXDB_PASSWORD="" -e MONITORING_NODE_URL="http://209.97.134.210:9052" ergoplatform/node-info-monitor show


## Usage without Docker

Instruction below was tested on Ubuntu 16.04

You should have Python 3 installed. If it is not true: `sudo apt install python3`

You also should have Python 3 pip tool to install needed libraries. If you have not, do: `sudo apt install python3-pip`

1. Clone this repo and change directory into it:

        git clone https://github.com/ergoplatform/node-info-monitor.git
        cd node-info-monitor

    Following instructions assume that your current directory is `node-info-monitor`

2. Install dependencies:

        pip3 install -r requirements.txt

3. Clone [andyceo's libraries](https://github.com/andyceo/pylibs) for script (they are not packaged into pip):

        git clone https://github.com/andyceo/pylibs.git

4. Copy default config and change it if needed:

        cp config-sample.ini config.ini

5. Start monitoring:

        ./node-info-monitor.py sync-daemon

You also can sync just current values and exit with `sync` argument, view current API `/info` data and exit with `show`, and view last 1 day values from InfluxDB with `show-influx`. Run script with `-h` option to view help message: `./node-info-monitor.py -h`.
