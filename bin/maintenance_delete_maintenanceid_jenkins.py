#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/3/15 14:34
# @Author  : Ethan
# @File    : maintenance_delete_maintenanceid_jenkins.py

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


def maintenanceid_delete(maintenanceid):
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
    f.write(u'maintanence id delete on zabbix server:\n')
    f.write(u'delete time: ' + str(date_time) + u'\n')
    f.close()

    # init zabbix api form modules
    authen_ = api_authentication.zabbix_api_authentication(user, password, api_url)
    authentication = authen_.login_authentication()

    maintence_ = api_maintenance.zabbix_maintenance_methods(api_url)

    for delete_id in maintenanceid:
        id_ = delete_id.strip()
        context = maintence_.maintenance_delete(id_, authentication)

        pattern = re.compile(r'error')
        mch = pattern.findall(str(context))
        if mch:
            f_new = io.open(log_file, 'a', encoding='utf-8')
            f_new.write(u'[failed] maintenance id deleted: ' + str(id_) + u'\n')
            f_new.close()
        else:
            f_new = io.open(log_file, 'a', encoding='utf-8')
            f_new.write(u'[success] maintenance id deleted: ' + str(id_) + u'\n')
            f_new.close()


if __name__ == '__main__':
    # Get the variables set by jenkins job
    maintenance_ids = os.getenv('maintenanceid')
    maintenanceid = maintenance_ids.split(',')

    if maintenanceid is None:
        print('maintenanceid must be entered.')
        sys.exit(1)
    else:
        maintenanceid_delete(maintenanceid)