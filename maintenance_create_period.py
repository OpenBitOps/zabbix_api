#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import requests
import json
import time
import configparser


class zabbix_maintenance_api():
    """
    zabbix 维护模式 api, 本方法仅提供创建和删除2个功能
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
        zabbix登录, 获取认证的token
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
            headers=zabbix_maintenance_api.header,
            data=json.dumps(data)
        )

        authentication_data = auth.json()
        authentication = authentication_data['result']

        return authentication

    def get_host_id(self, hostname, authentication):
        """
        获取zabbix中的主机ID
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
            headers=zabbix_maintenance_api.header,
            data=json.dumps(data)
        )

        host_data = content.json()
        host_id = host_data['result'][0]['hostid']

        return host_id

    def maintenance_create_period(self, maintenance_name, host_id, active_since, active_till, period, authentication, description):
        """
        创建维护期间1: 创建一个维护时间段period, 如 1hour/2hour
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
            headers=zabbix_maintenance_api.header,
            data=json.dumps(data)
        )

        result_data = content.json()

        print(result_data)

    def maintenance_create_start_end(self,maintenance_name, host_id, active_since, active_till, authentication, description):
        """
        创建维护期间2: 创建一个维护模式开始和结束时间, 如 2019-12-18 10:10:00 至 2019-12-18 11:10:00
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
            headers=zabbix_maintenance_api.header,
            data=json.dumps(data)
        )

        result_data = content.json()

        print(result_data)

    def maintenance_expired_get(self, hostid, authentication):
        """
        获取已过期的维护id
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
            headers=zabbix_maintenance_api.header,
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
        """
        删除已过期的维护
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
            headers=zabbix_maintenance_api.header,
            data=json.dumps(data)
        )

        result_data = content.json()
        print(result_data)


class main():
    """
    主逻辑方法, 创建zabbix维护
    """
    def __init__(self):
        pass

    def zabbix_api_config(self):
        """
        读取配置文件config中的用户名/密码/API的url地址
        :return: username, password, api_url
        """
        config = configparser.ConfigParser()
        config.read('config', encoding='utf-8')

        username = config.get('auth', 'user')
        password = config.get('auth', 'password')
        api_url = config.get('api_url', 'url')

        return username, password, api_url


    def create_period(self, hosts, period):
        """
        输入主机名 和 维护时间时长
        :return:
        """

        hosts_new = hosts.split(',')

        period_new = int(period) * 3600

        # 维护名描述, 本方法此处为空, 不做描述内容, 如有需求, 请自行修改
        description = ''

        # 初始化log文件
        log_file = 'maintenance_create_period_result.log'
        f = open(log_file, 'w', encoding='utf-8')
        f.write('')
        f.close()

        # 维护开始时间和结束时间
        active_since = int(time.time())
        active_till = int(time.time()) + period_new

        # 维护名使用
        date_time = time.strftime("%Y%m%d%H%M%S", time.localtime(active_since))

        # 输出到日志
        start_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(active_since))

        try:
            user = self.zabbix_api_config()[0]
            password = self.zabbix_api_config()[1]
            api_url = self.zabbix_api_config()[2]

            mainten = zabbix_maintenance_api(user, password, api_url)
            auth_code = mainten.login()

            # 日志文件操作
            f = open(log_file, 'a', encoding='utf-8')
            f.write('To zabbix maintenance team:\n')
            f.write(hosts + ' maintanence created on zabbix server:\n')
            f.write('maintenance start time: ' + str(start_time) + '\n')
            f.write('Maintenance duration: ' + period + ' hour' + '\n')

            # maintenance create
            for host in hosts_new:
                host_id = mainten.get_host_id(host, auth_code)
                mainten.maintenance_create_period('maintenance_' + date_time + '_' + host, host_id, active_since, active_till, period_new, auth_code, description)

                f.write('[success] maintenance definition with hostname [' + host + '] created')
            f.close()

        except Exception as e:
            print(e)


if __name__ == '__main__':
    hosts = input("please input host (test001 or test001,test002): ")
    period = input("please input int number (1 means 1 hour, 2 means 2 hour): ")
    mm = main()
    mm.create_period(hosts, period)
