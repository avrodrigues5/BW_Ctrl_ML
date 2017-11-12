import os
from jinja2.environment import Environment
from jinja2 import FileSystemLoader
import pygal
import MySQLdb
import data_dump

#rows=[['1-2-3 1:01',400],['1-2-3 1:02',500],['1-2-3 1:03',400],['1-2-3 1:04',600],['1-2-3 1:05',400],['1-2-3 1:06',500],['1-2-3 1:07',800]]
#predictedrows=[['1-2-3 1:01',410],['1-2-3 1:01',502],['1-2-3 1:01',410],['1-2-3 1:01',620],['1-2-3 1:01',500],['1-2-3 1:01',800],['1-2-3 1:01',500]]

class bandwidth:
    def __init__(self,rows,predictedrows):
        self.rows=rows
        self.predictedrows=predictedrows
        self.xlist=list()
        self.ylist=list()
    def xcordinates(self):
        for row in self.rows:
            self.xlist.append(row[0])
        return self.xlist
    def ycordinates(self):
        for row in self.rows:
            self.ylist.append(row[1])
        return self.ylist
    def predictedxcordinates(self):
        for row in self.predictedrows:
            self.xlist.append(row[0])
        return self.xlist
    def predictedycordinates(self):
        for row in self.predictedrows:
            self.ylist.append(row[1])
        return self.ylist


TEMPLATE = 'presentation.html'
BASEPATH = os.path.dirname(__file__)
OUTPUTFILE='output.html'
def generate_plan(template_file, outfile, host,xlist,ylist,predictedxlist,predictedylist):
    env = Environment()
    env.loader = FileSystemLoader(os.path.join(BASEPATH, 'template'))
    template = env.get_template(template_file)
    html = template.render({'planner': host})
    line_chart = pygal.Line()
    line_chart.title = 'Bandwidth vs time'
    line_chart.x_labels = map(str, xlist)
    line_chart.add('bandwidth', ylist)
    line_chart2 = pygal.Line()
    line_chart2.title = 'predicted Bandwidth vs time'
    line_chart2.x_labels = map(str, predictedxlist)
    line_chart2.add('predictedbandwidth', predictedylist)
    #line_chart.add('Chrome', [None, None, None, None, None, None, 0, 3.9, 10.8, 23.8, 35.3])
    # line_chart.add('IE', [85.8, 84.6, 84.7, 74.5, 66, 58.6, 54.7, 44.8, 36.2, 26.6, 20.1])
    # line_chart.add('Others', [14.2, 15.4, 15.3, 8.9, 9, 10.4, 8.9, 5.8, 6.7, 6.8, 7.5])
    #html2 = pygal.Bar()(1, 3, 3, 7)(1, 6, 6, 4).render()
    html2=line_chart.render()
    html=line_chart2.render()
    with open(os.path.join(BASEPATH, outfile), 'w') as f:
        f.write(html2)
        f.write(html)





if __name__ == '__main__':
    db = MySQLdb.connect(host=data_dump.ConfigSectionMap("Controller")['address'],
                         user=data_dump.ConfigSectionMap("Controller")['username'],
                         passwd=data_dump.ConfigSectionMap("Controller")['password'],
                         db="bandwidth",
                         port=3306)

    cur = db.cursor()

    # Need to get a list of tables
    cur.execute("show tables;")
    try:
        tables = cur.fetchall()
    except db.Error:
        print "Unable to read from bandwidth db"
    table_list = [table[0] for table in tables]

    for table in table_list:
        query = "select * from (SELECT * FROM " + table + " order by currentdatetime desc limit 60)sub order by currentdatetime ASC"
        cur.execute(query)

        try:
            entries = cur.fetchall()
        except db.Error:
            print "Unable fetch entries from %s table", table
    db = MySQLdb.connect(host=data_dump.ConfigSectionMap("Controller")['address'],
                         user=data_dump.ConfigSectionMap("Controller")['username'],
                         passwd=data_dump.ConfigSectionMap("Controller")['password'],
                         db="predicted_bandwidth",
                         port=3306)

    cur = db.cursor()

    # Need to get a list of tables
    cur.execute("show tables;")
    try:
        tables = cur.fetchall()
    except db.Error:
        print "Unable to read from predicted_bandwidth db"
    table_list = [table[0] for table in tables]
    for table in table_list:
        query = "select * from (SELECT * FROM " + table + " order by futuredatetime desc limit 60)sub order by futuredatetime ASC"
        cur.execute(query)

        try:
            predictedentries = cur.fetchall()
        except db.Error:
            print "Unable fetch entries from %s table", table
    bandwidthObj=bandwidth(entries,predictedentries)
    xlist=bandwidthObj.xcordinates()
    ylist = bandwidthObj.ycordinates()
    predictedxlist=bandwidthObj.predictedxcordinates()
    predictedylist = bandwidthObj.predictedycordinates()

    generate_plan(TEMPLATE, OUTPUTFILE, bandwidthObj,xlist,ylist,predictedxlist,predictedylist)
