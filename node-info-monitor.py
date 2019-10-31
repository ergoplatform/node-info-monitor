#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Utility that get Ergo node info and put it into InlfuxDB"""
import argparse
import json
import requests
import sys
import tabulate
import time
from pylibs.config import parse
from pylibs import dbinflux
from pylibs import utils


def get_info(url):
    monitor = {
        'fields': {
            'response_time': None,
            'status_code': 0,
        },
        'more': {
            'timestamp_start': time.time(),
            'timestamp_end': None,
            'exception': None
        }
    }

    try:
        # need stream=True for be able read ip
        response = requests.get(url, stream=True, timeout=5)
    except requests.exceptions.HTTPError as err:
        monitor['more']['timestamp_end'] = time.time()
        monitor['more']['exception'] = err
        utils.message('!HTTP Exception while getting Ergo node info at {}: {}'.format(url, err))
    except Exception as err:
        monitor['more']['timestamp_end'] = time.time()
        monitor['more']['exception'] = err
        utils.message('!Exception (non-HTTP) while getting Ergo node info at {}: {}'.format(url, err))
    else:
        # we must read ip first
        monitor['fields']['ip'] = response.raw._connection.sock.getpeername()[0]
        monitor['more']['timestamp_end'] = time.time()
        monitor['fields']['status_code'] = response.status_code

        if response.status_code == 200:
            info = response.json()

            # For mainnet the values of fullBlocksScore=9228554086696091648i,headersScore=9228554086696091648i
            # are too much for InfluxDB, so these fields were removed from monitoring
            for field in ['difficulty', 'peersCount', 'unconfirmedCount', 'fullHeight', 'headersHeight', 'appVersion']:
                if field not in info or info[field] is None:
                    continue
                elif isinstance(info[field], str) and field != 'appVersion':
                    raise ValueError('JSON from Ergo node is incorrect: {} must be integer, not string! '
                                     '(raw value is {})'.format(field, info[field]))
                else:
                    monitor['fields'][field] = info[field]

            # special handling for parameters field
            for field in info['parameters']:
                if isinstance(info['parameters'][field], int):
                    monitor['fields']['parameters_'+field] = info['parameters'][field]

            monitor['more']['name'] = info['name']
            monitor['more']['genesisBlockId'] = info['genesisBlockId']
    finally:
        monitor['fields']['response_time'] = monitor['more']['timestamp_end'] - monitor['more']['timestamp_start']

    return monitor


def sync(monitor):
    name = monitor['more']['name']
    timestamp = monitor['more']['timestamp_start']
    json_body = [{
        "time": round(timestamp * 1000000000),
        "measurement": "node_info",
        "tags": {'name': name, 'genesisBlockId': monitor['more']['genesisBlockId']},
        "fields": monitor['fields']
    }]
    client = dbinflux.connect(config['influxdb'])
    if dbinflux.write_points_with_exception_handling(client, json_body):
        utils.message('Ergo node {} info metrics was saved to InfluxDB at timestamp {}.'.format(name, timestamp))


if __name__ == '__main__':
    config = parse(True)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', nargs=1, metavar="show|show-influx|sync|sync-daemon",
                        help='Choose your action: show or sync Ergo node info')
    args = parser.parse_args()

    if args.action[0] == 'show':
        print(json.dumps(get_info(config['monitoring']['node_url'] + '/info'), indent=4))

    elif args.action[0] == 'show-influx':
        cl = dbinflux.connect(config['influxdb'])
        res = cl.query("SELECT * FROM node_info WHERE time > now() - 1d")
        print(tabulate.tabulate(res.get_points(), headers="keys"))

    elif args.action[0] == 'sync':
        monitor = get_info(config['monitoring']['node_url'] + '/info')
        sync(monitor)

    elif args.action[0] == 'sync-daemon':
        utils.message('Syncing Ergo node info daemon started.')
        while True:
            monitor = get_info(config['monitoring']['node_url'] + '/info')
            if monitor['fields']['status_code'] != 200:
                print('Error {} occurred when processing node info, apply cooldown pause for {} seconds'.format(
                    monitor['fields']['status_code'], config['monitoring']['cooldown_pause']))
                time.sleep(int(config['monitoring']['cooldown_pause']))
            else:
                sync(monitor)
                time.sleep(int(config['monitoring']['pause']))
            sys.stdout.flush()
