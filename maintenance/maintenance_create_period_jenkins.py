#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Time    : 2020/3/1 16:35
# @Author  : Ethan
# @File    : maintenance_create_period_jenkins.py

import sys
import os
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(base_dir)

import zabbix_api
import zabbix_maintenance
import time
import io
import re
import yaml

class maintenance_create_period():
    """
    I don't understand how to write comments
    """
    def zabbix_api_config(self):
        """
        Get the username / password / URL of the API in the configuration file config
        :return: username, password, api_url
        """
        yaml_path = os.path.join(base_dir, 'zabbix_api_authentication.yaml')

        f = io.open(yaml_path, 'rb')
        conf = yaml.load(f, Loader=yaml.FullLoader)
        username = conf['authenticate']['user']
        password = conf['authenticate']['password']
        api_url = conf['api_url']['url']
        log_file_period = conf['log']['result_create_period_log']
        f.close()

        return username, password, api_url, log_file_period

    def create_period(self, hosts, period, description):
        """
        Enter host name and maintenance duration
        :param hosts:
        :param period:
        :return:
        """
        # time
        active_since = int(time.time())
        active_till = int(time.time()) + period

        # output maintanence start time to log
        start_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(active_since))

        # for maintenance name use
        date_time = time.strftime("%Y%m%d%H%M%S", time.localtime(active_since))

        try:
            conf_read = self.zabbix_api_config()
            user = conf_read[0]
            password = conf_read[1]
            api_url = conf_read[2]
            log_file = conf_read[3]

            # Initialize the log file
            f = io.open(log_file, 'wb')
            f.write('')
            f.write('To zabbix maintenance team:\n')
            f.write(str(hosts) + ' maintanence created on zabbix server:\n')
            f.close()

            auth_ = zabbix_api.zabbix_api_authentication(user, password, api_url)
            authentication = auth_.login_authentication()

            maintence_ = zabbix_maintenance.zabbix_maintenance_methods(api_url)
            for host in hosts:
                # maintenance create
                host_id = maintence_.get_host_id(host, authentication)
                context = maintence_.maintenance_create_period('maintenance_' + date_time + '_' + host, host_id,
                                                               active_since, active_till, period, authentication, description)
                pattern = re.compile(r'\berror\b')
                mch = pattern.findall(str(context))
                if mch:
                    f_new = io.open(log_file, 'ab')
                    f_new.write('[failed] maintenance created : ' + host + '\n')
                    f_new.close()
                else:
                    f_new = io.open(log_file, 'ab')
                    f_new.write('maintenance start time: ' + str(start_time) + '\n')
                    f_new.write('maintenance duration: ' + str(int(period/3600)) + ' hour(s)' + '\n')
                    f_new.write('[success] maintenance created : ' + host + '\n')
                    f_new.close()

        except Exception as e:
            print(e)

if __name__ == '__main__':
    # Get the variables set by jenkins job
    hosts_get = os.getenv('hosts')
    hosts = hosts_get.split(',')

    period_get = os.getenv('period')
    period = int(float(period_get) * 3600)

    # Maintenance description, default None
    description = ''

    if hosts == None or period == None:
        print('hosts and period must be entered.')
        exit(1)
    else:
        mainten = maintenance_create_period()
        mainten.create_period(hosts, period, description)
