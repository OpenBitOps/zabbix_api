#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/3/15 13:20
# @Author  : Ethan
# @File    : api_maintenance.py

import requests
import json
import time


class zabbix_maintenance_methods():
    """
    zabbix maintenance function
    """
    globals()
    header = {'Content-Type': 'application/json'}

    def __init__(self, api_url):
        self.api_url = api_url

    def maintenance_create_period(self, maintenance_name, host_id, active_since,
                                  active_till, period, authentication, description):
        """
        Maintenance setting method 1: Create a maintenance period period, such as 1hour / 2hour
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
                'hostids': [host_id, ],
                'timeperiods': timeperiods
            },
            'auth': authentication,
            'id': 1,
            'description': description
        }

        content = requests.post(
            url=self.api_url,
            headers=self.header,
            data=json.dumps(data)
        )

        result_data = json.loads(content.text)
        print(result_data)

    def maintenance_create_start_end(self, maintenance_name, host_id, active_since,
                                     active_till, authentication, description):
        """
        Maintenance setting method 2: Create a maintenance mode with start and end time,
        such as 2019-12-18 10:10:00 to 2019-12-18 11:10:00
        :param maintenance_name:
        :param host_id:
        :param active_since:
        :param active_till:
        :param authentication:
        :param description:
        :return:
        """
        timeperiods = [
            {
                "timeperiod_type": 0,
            }
        ]

        data = {
            'jsonrpc': '2.0',
            'method': 'maintenance.create',
            'params': {
                'name': maintenance_name,
                'active_since': active_since,
                'active_till': active_till,
                'hostids': [host_id, ],
                'timeperiods': timeperiods
            },
            'auth': authentication,
            'id': 1,
            'description': description
        }

        content = requests.post(
            url=self.api_url,
            headers=self.header,
            data=json.dumps(data)
        )

        result_data = json.loads(content.text)
        print(result_data)

    def maintenance_expired_get(self, host_id, authentication):
        """
        Get expired maintenance id (a list)
        :param host_id:
        :param authentication:
        :return: maintenance_expired_id
        """
        data = {
            'jsonrpc': '2.0',
            'method': 'maintenance.get',
            'params': {
                'output': 'extend',
                'hostids': host_id,
                'selectTimeperiods': 'extend'
            },
            'auth': authentication,
            'id': 1,
        }

        content = requests.post(
            url=self.api_url,
            headers=self.header,
            data=json.dumps(data)
        )

        result_data = json.loads(content.text)

        # get data(result) of dist(result_data)
        result = result_data['result']

        # new maintenance id list
        maintenance_expired_id = []

        for i in range(len(result)):
            active_till_time = result[i]['active_till']
            if (int(time.time()) - int(active_till_time)) > 0:
                expired = result[i]['maintenanceid']
                maintenance_expired_id.append(expired)

        print(maintenance_expired_id)
        return maintenance_expired_id

    def maintenance_delete(self, maintenance_id, authentication):
        """
        Delete expired maintenance
        :param maintenance_id:
        :param authentication:
        :return:
        """
        data = {
            'jsonrpc': '2.0',
            'method': 'maintenance.delete',
            'params': [
                maintenance_id,
            ],
            'auth': authentication,
            'id': 1,
        }

        content = requests.post(
            url=self.api_url,
            headers=self.header,
            data=json.dumps(data)
        )

        result_data = json.loads(content.text)
        print(result_data)
