#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/3/15 14:46
# @Author  : Ethan
# @File    : maintenance_delete_expired_jenkins.py

import time
import io
import re
import sys
import os

base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(base_dir)

from zabbix_api.modules.authentication import api_authentication
from zabbix_api.modules.maintenance import api_maintenance
from zabbix_api.config import config_get


def maintenanceid_expired_delete(hosts):
    """
    Enter the maintenance host name to be deleted
    :param hosts:
    :param period:
    :return:
    """
    # for maintenance name use
    active_since = int(time.time())
    date_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(active_since))

    # config file get
    conf_data = config_get.config()
    user = conf_data[0]
    password = conf_data[1]
    api_url = conf_data[2]
    log_file = conf_data[3]

    # Initialize the log file
    f = io.open(log_file, 'w', encoding='utf-8')
    f.write(u'')
    f.write(u'To zabbix maintenance team:\n')
    f.write(str(hosts) + u' maintanence delete on zabbix server:\n')
    f.write(u'delete time: ' + str(date_time) + u'\n')
    f.close()

    # init zabbix api form modules
    authen_ = api_authentication.zabbix_api_authentication(user, password, api_url)
    authentication = authen_.login_authentication()

    maintence_ = api_maintenance.zabbix_maintenance_methods(api_url)

    # get maintenance id of maintenance expired
    for hostname in hosts:
        host = hostname.strip()
        host_id = authen_.get_host_id(host)
        maintenanceid_expired = maintence_.maintenance_expired_get(host_id, authentication)

        for i in range(len(maintenanceid_expired)):
            delete_id = maintenanceid_expired[i]
            context = maintence_.maintenance_delete(delete_id, authentication)

            pattern = re.compile(r'error')
            mch = pattern.findall(str(context))
            if mch:
                f_new = io.open(log_file, 'a', encoding='utf-8')
                f_new.write(u'[failed] maintenance id deleted: ' + hostname + u' ' + str(delete_id) + u'\n')
                f_new.close()
            else:
                f_new = io.open(log_file, 'ab')
                f_new.write(u'[success] maintenance id deleted: ' + hostname + u' ' + str(delete_id) + u'\n')
                f_new.close()


if __name__ == '__main__':
    # Get the variables set by jenkins job
    hosts_get = os.getenv('hosts')
    hosts = hosts_get.split(',')

    if hosts is None:
        print('hosts must be entered.')
        sys.exit(1)
    else:
        maintenanceid_expired_delete(hosts)