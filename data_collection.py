import ConfigParser
import MySQLdb

# dir_path=os.path.dirname(os.path.realpath(__file__))
# fname=dir_path+"/data.txt"
# if os.path.isfile(fname):
#    os.remove(fname)
#    f=open(fname,"w")
# else:
#    f=open(fname,"w")
CONFIG_FILE = "connection.conf"


def config_section_map(section):
    config = ConfigParser.RawConfigParser()
    config.read(CONFIG_FILE)
    dict1 = {}
    try:
        options = config.options(section)
        for option in options:
            try:
                dict1[option] = config.get(section, option)
            except ConfigParser.Error:
                print "exception on {}".format(option)
                dict1[option] = None
    except ConfigParser.Error:
        print "exception on {}".format(section)
    
    return dict1


class ProjectId(object):

    def __init__(self):
        self.inst_dict = dict()
        self.inst_port_dict = dict()

    def project_id_map_to_instance(self):
        nova_db = MySQLdb.connect(host=config_section_map("Controller")['address'],
                                  user=config_section_map("Controller")[
            'username'],
            passwd=config_section_map("Controller")[
            'password'],
            db="nova",
            port=3306)

        # cursor object to execute command
        cur = nova_db.cursor()

        cur.execute("SELECT * FROM instances")

        for row in cur.fetchall():
            if row[6] in self.inst_dict:
                self.inst_dict[row[6]].append(row[17])
            else:
                self.inst_dict[row[6]] = [row[17]]

        nova_db.close()
        return self.inst_dict

    def project_id_map_to_ports(self):
        neutron_db = MySQLdb.connect(host=config_section_map("Controller")['address'],
                                     user=config_section_map("Controller")[
            'username'],
            passwd=config_section_map("Controller")[
            'password'],
            db="neutron",
            port=3306)

        cur = neutron_db.cursor()

        cur.execute("SELECT * FROM ports")

        for row in cur.fetchall():
            if "compute:nova" in row[8]:
                if row[0] in self.inst_dict:
                    if row[0] in self.inst_port_dict:
                        self.inst_port_dict[row[0]].append(
                            row[1].split('-')[0])
                    else:
                        self.inst_port_dict[row[0]] = [row[1].split('-')[0]]
# for it in inst_port_dict.items():
#        f.write("%s:%s" %it)
# f.write("\n")
# fwrite(inst_port_dict)
        neutron_db.close()
        return self.inst_port_dict
