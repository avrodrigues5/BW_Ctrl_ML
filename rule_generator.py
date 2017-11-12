#!/usr/bin/python
#
# Copyright 2016, Mithil Arun
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import datetime
import time
import shlex
import subprocess

import MySQLdb as db
import data_dump
from ports_info import portInfo

# Global constants
FREQUENCY = 5


class RuleGenerator(object):

    def __init__(self):
        # Nothing to do for now
        return

    @staticmethod
    def fetch_port_desc():
        cmd = "sudo ovs-ofctl dump-ports-desc br-int"

        args = shlex.split(cmd)

        output = subprocess.check_output(args)
        port_desc = []
        output = output.split("\n")
        for line in output:
            if "addr" not in line:
                continue
            port_desc.append(line)

        return port_desc

    @staticmethod
    def run_cmd(cmd=None):
        if cmd is None:
            return

        args = shlex.split(cmd)

        try:
            subprocess.check_call(args)
        except subprocess.CalledProcessError:
            print "Failed to run command " + cmd

    @staticmethod
    def make_cmd(rule=None):
        if rule is None:
            return

        cmd = "sudo ovs-vsctl set interface "
        cmd += rule['port']
        cmd += " ingress_policing_burst="
        cmd += str(rule['bw'])

        print cmd
        return cmd

    @staticmethod
    def read_data():
        data = []

        predicted_db = db.connect(host=data_dump.ConfigSectionMap("db")['address'],
                                  user=data_dump.ConfigSectionMap("db")['username'],
                                  passwd=data_dump.ConfigSectionMap("db")['password'],
                                  db="predicted_bandwidth", port=3306)
        cursor = predicted_db.cursor()

        tenant_mapper = db.connect(host=data_dump.ConfigSectionMap("db")['address'],
                                  user=data_dump.ConfigSectionMap("db")['username'],
                                  passwd=data_dump.ConfigSectionMap("db")['password'],
                                  db="tenant_mapper", port=3306)

        ten_cursor = tenant_mapper.cursor()

        # Need to get a list of tables
        cursor.execute("show tables;")
        try:
            tables = cursor.fetchall()
        except db.Error:
            print "Unable to read from predicted_bandwidth db"
            return None

        table_list = [table[0] for table in tables]

        portInfoObj = portInfo()
        portInfoObj.sshConnect()
        tenantPorts = portInfoObj.instanceToPortNumber()
        port_desc = RuleGenerator.fetch_port_desc()

        for table in table_list:
            query = "select * from " + table + " order by futuredatetime desc limit 1"
            cursor.execute(query)

            try:
                entries = cursor.fetchall()
            except db.Error:
                print "Unable fetch entries from %s table", table

            for entry in entries:
                ten_query = "select tenantid from mapper where tenantname='" + table + "'"
                ten_cursor.execute(ten_query)

                try:
                    tenants = ten_cursor.fetchall()
                except db.Error:
                    print "Unable to fetch entries from mapper table"

                for tenant_tup in tenants:
                    tenant = ''.join(tenant_tup)
                    port_list = tenantPorts[tenant]
                    for port in port_list:
                        interface = ""
                        for line in port_desc:
                            line = line.strip()
                            if line.startswith(port):
                                interface = line[line.index("(") + 1:line.index(")")]
                                break

                        temp = {}
                        temp['time'] = entry[0]
                        temp['bw'] = entry[1]
                        temp['port'] = interface

                        data.append(temp)

            predicted_db.close()
            tenant_mapper.close()

        return data

    def publish_rule(self, rule=None):
        if rule is None:
            return

        cmd = self.make_cmd(rule)
        self.run_cmd(cmd)

    def create_rules(self):
        # do whatever
        data = self.read_data()

        if data is None:
            return -1

        for entry in data:
            self.publish_rule(entry)

        return 0


def main():
    rule_gen = RuleGenerator()
    if rule_gen.create_rules() != 0:
        print "Failed to generate rules. Exiting."

if __name__ == '__main__':
    main()
