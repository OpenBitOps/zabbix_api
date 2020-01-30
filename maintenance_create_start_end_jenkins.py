#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import requests
import json
import time
import os
import re
import io
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

        f = io.open(yaml_path, 'rb')
        conf = yaml.load(f, Loader=yaml.FullLoader)
        username = conf['authenticate']['user']
        password = conf['authenticate']['password']
        api_url = conf['api_url']['url']
        log_file_start_end = conf['log']['result_create_start_end_log']
        f.close()

        return username, password, api_url, log_file_start_end

    def create_start_end(self, hosts, start_time, end_time):
        """
        Enter host name and maintenance start time and end time
        :param hosts:
        :param start_time:
        :param end_time:
        :return:
        """
        timeArray_start = time.strptime(start_time, "%Y-%m-%d %H:%M:%S")
        active_since = int(time.mktime(timeArray_start))

        timeArray_end = time.strptime(end_time, "%Y-%m-%d %H:%M:%S")
        active_till = int(time.mktime(timeArray_end))

        # Maintenance description, default None
        description = ''

        # 维护名使用
        date_time = time.strftime("%Y%m%d%H%M%S", time.localtime(active_since))

        try:
            conf_read = self.zabbix_api_config()
            user = conf_read[0]
            password = conf_read[1]
            api_url = conf_read[2]
            log_file = conf_read[3]

            # Initialize the log file
            f1 = io.open(log_file, 'wb')
            f1.write('')
            f1.write('To zabbix maintenance team:\n')
            f1.write(str(hosts) + ' maintanence created on zabbix server:\n')
            f1.close()

            mainten = zabbix_maintenance_api(user, password, api_url)
            auth_code = mainten.login()

            # maintenance create
            for host in hosts:
                host_id = mainten.get_host_id(host, auth_code)
                context = mainten.maintenance_create_start_end('maintenance_' + date_time + '_' + host, host_id, \
                                                               active_since, active_till, auth_code, description)

                pattern = re.compile(r'\berror\b')
                mch = pattern.findall(str(context))
                if mch:
                    f_new = io.open(log_file, 'ab')
                    f_new.write('[failed] maintenance created : ' + host + '\n')
                    f_new.close()
                else:
                    f_new = io.open(log_file, 'ab')
                    f_new.write('maintenance start time: ' + str(start_time) + '\n')
                    f_new.write('maintenance end time: ' + str(end_time) + '\n')
                    f_new.write('[success] maintenance created : ' + host + '\n')

        except Exception as e:
            print(e)


if __name__ == '__main__':
    # Get the variables set by jenkins job
    hosts_get = os.getenv('hosts')
    hosts = hosts_get.split(',')

    start_time = os.getenv('start_time')
    end_time = os.getenv('end_time')

    if hosts == None or start_time == None or end_time == None:
        print('hosts and start_time and end_time must be entered.')
        exit(1)
    else:
        mm = main()
        mm.create_start_end(hosts, start_time, end_time)