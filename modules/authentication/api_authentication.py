#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/3/15 13:13
# @Author  : Ethan
# @File    : api_authentication.py

import requests
import json


class zabbix_api_authentication():
    """
    zabbix API for maintenance settings
    this method only provides 2 functions for creating and deleting
    """
    globals()
    header = {'Content-Type': 'application/json'}

    def __init__(self, user, password, api_url):
        self.user = user
        self.password = password
        self.api_url = api_url

    def login_authentication(self):
        """
        Zabbix login, get authenticated token
        :return: authentication
        """
        data = {
            'jsonrpc': '2.0',
            'method': 'user.login',
            'params': {
                'user': "" + self.user + "",
                'password': "" + self.password + "",
            },
            'auth': None,
            'id': 1,
        }

        auth = requests.post(
            url=self.api_url,
            headers=self.header,
            data=json.dumps(data)
        )

        authentication_data = json.loads(auth.text)
        authentication = authentication_data['result']

        return authentication

    def get_host_id(self, hostname):
        """
        Get host ID in Zabbix
        :param hostname: hosts
        :return: host_id
        """
        authentication = self.login_authentication()

        data = {
            'jsonrpc': '2.0',
            'method': 'host.get',
            'params': {
                'filter': {
                    'host': hostname,
                }
            },
            'auth': authentication,
            'id': 1,
        }

        content = requests.post(
            url=self.api_url,
            headers=self.header,
            data=json.dumps(data)
        )

        host_data = json.loads(content.text)
        host_id = host_data['result'][0]['hostid']

        return host_id
