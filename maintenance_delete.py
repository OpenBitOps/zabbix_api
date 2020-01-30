#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import requests
import json
import time
import os
import re
import yaml

class zabbix_maintenance_api():
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
        self.sses = requests.session()

    def login(self):
        """
        Zabbix login, get authenticated token
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
            headers=self.header,
            data=json.dumps(data)
        )

        authentication_data = json.loads(auth.text)
        authentication = authentication_data['result']

        return authentication

    def get_host_id(self, hostname, authentication):
        """
        Get host ID in Zabbix
        :param hostname: hosts
        :param authentication: get from login function
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
            headers=self.header,
            data=json.dumps(data)
        )

        host_data = json.loads(content.text)
        host_id = host_data['result'][0]['hostid']

        return host_id

    def maintenance_create_period(self, maintenance_name, host_id, active_since, \
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
                'hostids': [host_id,],
                'timeperiods': timeperiods
            },
            'auth': authentication,
            'id': 1,
            'description': description
        }

        content = self.sses.post(
            url=self.api_url,
            headers=self.header,
            data=json.dumps(data)
        )

        result_data = json.loads(content.text)

        print(result_data)

    def maintenance_create_start_end(self,maintenance_name, host_id, active_since, \
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

        content = self.sses.post(
            url=self.api_url,
            headers=self.header,
            data=json.dumps(data)
        )

        result_data = json.loads(content.text)

        print(result_data)

    def maintenance_expired_get(self, hostid, authentication):
        """
        Get expired maintenance id (a list)
        :param hostid:
        :param authentication:
        :return: maintenance_expired_id
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
            headers=self.header,
            data=json.dumps(data)
        )

        result_data = json.loads(content.text)

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
        """
        Delete expired maintenance
        :param maintenanceid:
        :param authentication:
        :return:
        """
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
            headers=self.header,
            data=json.dumps(data)
        )

        result_data = json.loads(content.text)
        print(result_data)

class main():
    """
    I don't understand how to write comments
    """
    def __init__(self):
        pass

    def zabbix_api_config(self):
        """
        Get the username / password / URL of the API in the configuration file config
        :return: username, password, api_url
        """
        file_name_path = os.path.split(os.path.realpath(__file__))[0]
        yaml_path = os.path.join(file_name_path, 'zabbix_api.yaml')

        with open(yaml_path, 'r', encoding='utf-8') as f:
            conf = yaml.load(f, Loader=yaml.FullLoader)
            username = conf['authenticate']['user']
            password = conf['authenticate']['password']
            api_url = conf['api_url']['url']

        return username, password, api_url


    def delete(self, hosts):
        """
        Enter the maintenance host name to be deleted
        :param hosts:
        :return:
        """
        hosts_new = hosts.split(',')

        # Initialize the log file
        log_file = 'maintenance_delete_result.log'
        with open(log_file, 'w', encoding='utf-8') as f1:
            f1.write('')

        # for maintenance name use
        active_since = int(time.time())
        date_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(active_since))

        try:
            conf_read =  self.zabbix_api_config()
            user = conf_read[0]
            password = conf_read[1]
            api_url = conf_read[2]

            mainten = zabbix_maintenance_api(user, password, api_url)
            auth_code = mainten.login()

            # Log file
            with open(log_file, 'a', encoding='utf-8') as f2:
                f2.write('To zabbix maintenance team:\n')
                f2.write(hosts + ' maintanence delete on zabbix server:\n')
                f2.write('delete time: ' + str(date_time) + '\n')

                # maintenance delete
                for host in hosts_new:
                    # get maintenance id of maintenance expired
                    host_id = mainten.get_host_id(host, auth_code)
                    maintenanceid_expired = mainten.maintenance_expired_get(host_id, auth_code)

                    for i in range(len(maintenanceid_expired)):
                        delete_id = maintenanceid_expired[i]
                        context = mainten.maintenance_delete(delete_id, auth_code)

                        pattern = re.compile(r'\berror\b')
                        mch = pattern.findall(str(context))
                        if mch:
                            f2.write('[failed] maintenance id deleted : ' + host + ' ' + str(delete_id) + '\n')
                        else:
                            f2.write('[success] maintenance id deleted : ' + host + ' ' + str(delete_id) + '\n')

        except Exception as e:
            print(e)

if __name__ == '__main__':
    hosts = input("please input host (test001 or test001,test002): ")
    if hosts == None:
        print('hosts must be entered.')
        exit(1)
    else:
        mm = main()
        mm.delete(hosts)
