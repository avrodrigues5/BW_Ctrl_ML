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

import os
import time

#
# The following scripts are run in a loop in main:
# 1. data_dump.py (every minute)
# 2. holt_winters.py (every hour)
# 3. rule_generator.py (every hour)


COUNT = 0
while True:
    print "Sleeping for 1 minute"
    time.sleep(60)
    COUNT = COUNT + 1
    # every minute
    print "Running data_dump.py"
    os.system("python data_dump.py")
    print "Running rule_generator.py"
    os.system("python rule_generator.py")

    # every hour
    if COUNT < 60:
        continue

    print "Running holt_winters.py"
    os.system("python holt_winters.py")
    COUNT = 0
