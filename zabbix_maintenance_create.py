#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import requests
import json
import time
import configparser
import os


class zabbix_api():
    """
    zabbix api, used for maintenance mode creation and deletion
    """
    globals()
    header = {'Content-Type': 'application/json'}

    def __init__(self, user, password, api_url):
        self.user = user
        self.password = password
        self.api_url = api_url
        self.sses = requests.session()

    def login(self):
        """
        login zabbix and get authentication
        :return: authentication
        """
        data = {
            'jsonrpc': '2.0',
            'method': 'user.login',
            'params': {
                'user': ""+self.user+"",
                'password': ""+self.password+"",
            },
            'auth': None,
            'id': 1,
        }

        auth = self.sses.post(
            url=self.api_url,
            headers=zabbix_api.header,
            data=json.dumps(data)
        )

        authentication_data = auth.json()
        authentication = authentication_data['result']

        return authentication

    def get_host_id(self, hostname, authentication):
        """
        get host id
        :param hostname: hosts
        :param authentication: from def login
        :return: host_id
        """
        data = {
            'jsonrpc': '2.0',
            'method': 'host.get',
            'params': {
                'filter':{
                    'host': hostname,
                }
            },
            'auth': authentication,
            'id': 1,
        }

        content = self.sses.post(
            url=self.api_url,
            headers=zabbix_api.header,
            data=json.dumps(data)
        )

        host_data = content.json()
        host_id = host_data['result'][0]['hostid']

        return host_id

    def maintenance_create(self, maintenance_name, host_id, active_since, active_till, period, authentication, description):
        """

        :param maintenance_name:
        :param host_id:
        :param active_since: start time
        :param active_till: end time
        :param period: time of duration
        :param authentication:
        :param description:
        :return: maintenance data
        """
        timeperiods = [
            {
                "timeperiod_type": 0,
                "start_time": 64800,
                "period": period
            }
        ]

        data = {
            'jsonrpc': '2.0',
            'method': 'maintenance.create',
            'params': {
                'name': maintenance_name,
                'active_since': active_since,
                'active_till': active_till,
                'hostids': [host_id,],
                'timeperiods': timeperiods
            },
            'auth': authentication,
            'id': 1,
            'description': description
        }

        content = self.sses.post(
            url=self.api_url,
            headers=zabbix_api.header,
            data=json.dumps(data)
        )

        result_data = content.json()
        print(result_data)

    def maintenance_expired_get(self, hostid, authentication):
        """

        :param hostname:
        :param authentication:
        :return:
        """
        data = {
            'jsonrpc': '2.0',
            'method': 'maintenance.get',
            'params': {
                'output': 'extend',
                'hostids': hostid,
                'selectTimeperiods': 'extend'
            },
            'auth': authentication,
            'id': 1,
        }

        content = self.sses.post(
            url=self.api_url,
            headers=zabbix_api.header,
            data=json.dumps(data)
        )

        result_data = content.json()

        # get data(result) of dist(result_data)
        result = result_data['result']

        # new maintenanceid list
        maintenance_expired_id = []

        for i in range(len(result)):
            active_till_time = result[i]['active_till']
            if ( int(time.time()) - int(active_till_time) ) > 0:
                expired = result[i]['maintenanceid']
                maintenance_expired_id.append(expired)
        print(maintenance_expired_id)
        return maintenance_expired_id


    def maintenance_delete(self, maintenanceid, authentication):
        data = {
            'jsonrpc': '2.0',
            'method': 'maintenance.delete',
            'params': [
                maintenanceid,
            ],
            'auth': authentication,
            'id': 1,
        }

        content = self.sses.post(
            url=self.api_url,
            headers=zabbix_api.header,
            data=json.dumps(data)
        )

        result_data = content.json()
        print(result_data)


def zabbix_api_config():
    config = configparser.ConfigParser()
    config.read('config', encoding='utf-8')

    username = config.get('auth', 'user')
    password = config.get('auth', 'password')
    api_url = config.get('api_url', 'url')

    return username, password, api_url


def create():
    hosts_get = os.getenv('host')
    hosts = hosts_get.split(',')

    period_get = int(os.getenv('period'))
    period = int(period_get * 3600)
    description = ''

    date_time = time.strftime("%Y-%m-%d %X",time.localtime())
    active_since = int(time.time())
    active_till = int(time.time()) + period

    user = zabbix_api_config()[0]
    password = zabbix_api_config()[1]
    api_url = zabbix_api_config()[2]

    maintenance_api = zabbix_api(user, password, api_url)
    auth_code = maintenance_api.login()

    f = open('zabbix_maintenance_create_result.log', 'w', encoding='utf-8')
    f.write(str(date_time) + '\n')
    f.close()

    for host_new in hosts:
        # maintenance create
        host_id = maintenance_api.get_host_id(host_new, auth_code)
        maintenance_api.maintenance_create('AutoMaintenance_' + date_time + '_' + host_new, host_id, active_since, active_till, period, auth_code, description)

        f_new = open('zabbix_maintenance_create_result.log', 'a', encoding='utf8')
        f_new.write(host_new + ' maintenance create for ' + str(period_get) + ' hours')
        f_new.close()


if __name__ == '__main__':
    create()

