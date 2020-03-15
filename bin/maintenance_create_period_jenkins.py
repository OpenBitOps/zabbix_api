#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/3/15 13:33
# @Author  : Ethan
# @File    : maintenance_create_period_jenkins.py

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


def maintenance_create_period(hosts, period, description):
    """
    Enter host name and maintenance duration
    :param hosts:
    :param period:
    :param description:
    :return:
    """
    # time
    active_since = int(time.time())
    active_till = int(time.time()) + period

    # output maintanence start time to log
    start_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(active_since))

    # for maintenance name use
    date_time = time.strftime("%Y%m%d%H%M%S", time.localtime(active_since))

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
    f.write(str(hosts) + u' maintanence created on zabbix server:\n')
    f.close()

    # init zabbix api form modules
    authen_ = api_authentication.zabbix_api_authentication(user, password, api_url)
    authentication = authen_.login_authentication()

    maintence_ = api_maintenance.zabbix_maintenance_methods(api_url)

    # maintenance create
    for hostname in hosts:
        # maintenance create
        host_id = authen_.get_host_id(hostname)
        context = maintence_.maintenance_create_period('maintenance_' + date_time + '_' + hostname, host_id,
                                                       active_since, active_till, period, authentication, description)

        pattern = re.compile(r'error')
        mch = pattern.findall(str(context))
        if mch:
            f_new = io.open(log_file, 'a', encoding='utf-8')
            f_new.write(u'[failed] maintenance created : ' + hostname + u'\n')
            f_new.close()
        else:
            f_new = io.open(log_file, 'a', encoding='utf-8')
            f_new.write(u'[success] maintenance created: ' + hostname + u'\n')
            f_new.write(u'maintenance start time: ' + str(start_time) + u'\n')
            f_new.write(u'maintenance duration: ' + str(period) + u' hour(s)\n')
            f_new.close()


if __name__ == '__main__':
    # Get the variables set by jenkins job
    hosts_get = os.getenv('hosts')
    hosts = hosts_get.split(',')

    period_get = os.getenv('period')
    period = int(float(period_get) * 3600)

    # Maintenance description, default None
    description = ''

    if hosts is None or period is None:
        print('hosts and period must be entered.')
        sys.exit(1)
    else:
        maintenance_create_period(hosts, period, description)
