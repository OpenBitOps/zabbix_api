#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Time    : 2020/3/1 16:20
# @Author  : Ethan
# @File    : maintenance_create_period_jenkins.py

import sys
import os
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(base_dir)

import zabbix_api
import zabbix_maintenance
import time
import os
import re
import io
import yaml

class maintenance_create_start_end():
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
        log_file_start_end = conf['log']['result_create_start_end_log']
        f.close()

        return username, password, api_url, log_file_start_end

    def create_start_end(self, hosts, start_time, end_time, description):
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

        # for maintenance name use
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

            auth_ = zabbix_api.zabbix_api_authentication(user, password, api_url)
            authentication = auth_.login_authentication()

            maintence_ = zabbix_maintenance.zabbix_maintenance_methods(api_url)
            # maintenance create
            for host in hosts:
                host_id = maintence_.get_host_id(host, authentication)
                context = maintence_.maintenance_create_start_end('maintenance_' + date_time + '_' + host, host_id,
                                                               active_since, active_till, authentication, description)

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

    # Maintenance description, default None
    description = ''

    if hosts_get == None or start_time == None or end_time == None:
        print('hosts and start_time and end_time must be entered.')
        exit(1)
    else:
        maintain = maintenance_create_start_end()
        maintain.create_start_end(hosts, start_time, end_time, description)