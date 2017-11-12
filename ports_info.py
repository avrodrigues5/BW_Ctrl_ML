import ConfigParser
import paramiko
from data_collection import ProjectId

projectIDObj = ProjectId()
instDict = projectIDObj.project_id_map_to_instance()
instPortDict = projectIDObj.project_id_map_to_ports()

CONFIG_FILE = "connection.conf"
config = ConfigParser.RawConfigParser()


def ConfigSectionMap(section):
    config.read(CONFIG_FILE)
    dict1 = {}
    try:
        options = config.options(section)
        for option in options:
            try:
                dict1[option] = config.get(section, option)
            except:
                print "exception on {]".format(option)
                dict1[option] = None
    except:
        print "exception on {}".format(section)
    return dict1


class portInfo(object):

    def __init__(self):
        self.tenantPorts = dict()
        self.bandwidthDict = dict()
        self.ssh = paramiko.SSHClient()
        self.outputList = list()
        self.outputList1 = list()
        self.instDict = dict()
        self.instPortDict = dict()

    def sshConnect(self):
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.connect(ConfigSectionMap("Controller")['address'],
                         username=ConfigSectionMap("Controller")['username'],
                         password=ConfigSectionMap("Controller")['password'])
        stdin, stdout, stderr = self.ssh.exec_command(
            "sudo ovs-ofctl dump-ports-desc br-int")
        self.outputList1 = stdout.read().split("\n")
        stdin, stdout, stderr = self.ssh.exec_command(
            "sudo ovs-ofctl dump-ports br-int")
        self.outputList = stdout.read().split("\n")
        projectIDObj = ProjectId()
        self.instDict = projectIDObj.project_id_map_to_instance()
        self.instPortDict = projectIDObj.project_id_map_to_ports()
        if self.ssh:
            self.ssh.close()

    def instanceToPortNumber(self):

        for x in self.outputList1:
            for projectID, portID in self.instPortDict.iteritems():
                for individualPortID in portID:
                    if individualPortID in x:
                        if projectID in self.tenantPorts:
                            self.tenantPorts[projectID].append(
                                x.split("(")[0].split(" ")[1])
                        else:
                            self.tenantPorts[projectID] = [
                                x.split("(")[0].split(" ")[1]]
        return self.tenantPorts

    def instanceToBandwidth(self):

        i = 0
        for x in self.outputList:
            for projectID, portNumber in self.tenantPorts.iteritems():
                for individualPortNumber in portNumber:
                    if "tx pkts" in x:
                        if individualPortNumber in self.outputList[i - 1].split(":")[0]:
                            if projectID in self.bandwidthDict:
                                self.bandwidthDict[projectID].append(int(x.split(",")[0].
                                                                         split("=")[1]))
                            else:
                                self.bandwidthDict[projectID] = [
                                    int(x.split(",")[0].split("=")[1])]
            i = i + 1
        return self.bandwidthDict


# print bandwidthDict

# print tenantPorts

# print outputList
