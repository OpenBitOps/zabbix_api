#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time    : 2020/3/1 16:52
# @Author  : Ethan
# @File    : maintenance_delete_expired_jenkins.py

import sys
import os
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(base_dir)

import zabbix_api
import zabbix_maintenance
import time
import os
import io
import re
import yaml

class maintenance_delete_maintenanceid():
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
        log_file_delete = conf['log']['result_delete_maintenanceid_log']
        f.close()

        return username, password, api_url, log_file_delete

    def delete(self, maintenanceid):
        """
        Enter the maintenance host name to be deleted
        :param hosts:
        :param period:
        :return:
        """
        # for maintenance name use
        active_since = int(time.time())
        date_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(active_since))

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
            f.write('maintanence id delete on zabbix server:\n')
            f.write('delete time: ' + str(date_time) + '\n')
            f.close()

            auth_ = zabbix_api.zabbix_api_authentication(user, password, api_url)
            authentication = auth_.login_authentication()

            maintence_ = zabbix_maintenance.zabbix_maintenance_methods(api_url)
            # get maintenance id of maintenance expired
            for delete_id in maintenanceid:
                context = maintence_.maintenance_delete(delete_id, authentication)

                pattern = re.compile(r'\berror\b')
                mch = pattern.findall(str(context))
                if mch:
                    f_new = io.open(log_file, 'ab')
                    f_new.write('[failed] maintenance id deleted : ' + ' ' + str(delete_id) + '\n')
                    f_new.close()
                else:
                    f_new = io.open(log_file, 'ab')
                    f_new.write('[success] maintenance id deleted : ' + ' ' + str(delete_id) + '\n')
                    f_new.close()

        except Exception as e:
            print(e)


if __name__ == '__main__':
    # Get the variables set by jenkins job
    maintenance_ids = os.getenv('maintenanceid')
    maintenanceid = maintenance_ids.split(',')

    if maintenanceid == None:
        print('hosts and period must be entered.')
        exit(1)
    else:
        maintain = maintenance_delete_maintenanceid()
        maintain.delete(maintenanceid)