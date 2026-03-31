#!/usr/bin/python2

import sys, os, pwd, grp, re, ConfigParser, MySQLdb
tenantname = str(sys.argv[1])
filename = "/home/PlcmSpIp/CONTACTS/%s/obipoly_compdir.xml" % tenantname
dir = os.path.dirname(filename)

dbConfig = ConfigParser.ConfigParser()
dbConfig.read ("/etc/asterisk/res_config_mysql.conf")
dbhost = dbConfig.get('pbxconf', 'dbhost')
dbname = dbConfig.get('pbxconf', 'dbname')
dbuser = dbConfig.get('pbxconf', 'dbuser')
dbpass = dbConfig.get('pbxconf', 'dbpass')
dbuser = dbConfig.get('pbxconf', 'dbuser')

#def ensure_dir(filename):
#    if not os.path.exists(os.path.dirname(filename)):
#         os.makedirs(os.path.dirname(filename))
try:
    os.stat(dir)
except:
    os.mkdir(dir, 0755)

os.chmod(dir, 0755)
uid = pwd.getpwnam("PlcmSpIp").pw_uid
gid = grp.getgrnam("PlcmSpIp").gr_gid
os.chown(dir, uid, gid)

file = open(filename, "w")

#print ("tenant name: %s") % tenantname
file.write("<?xml version=\'1.0\' encoding=\'utf-8\'?>\n<Group>\n  <totalAvailableRecords>1</totalAvailableRecords>\n  <groupDirectory>\n")

# Open database connection
db = MySQLdb.connect(dbhost,dbuser,dbpass,dbname)

# prepare a cursor object using cursor() method
cursor = db.cursor()

sql1 = "SELECT id from tenants where tenant = '%s'" % (tenantname)


try:
   # Execute the SQL command
   cursor.execute(sql1)
   tid = cursor.fetchone()
#   print("tid=%d" % tid)
   sql2 = "SELECT firstname, lastname, email, note, image_url, company, department, ext, office, home, mobile, other FROM directory where tenantid = '%d' and owner = '' order by lastname asc" % (tid)
   cursor.execute(sql2)
   # Fetch all the rows in a list of lists.
   results = cursor.fetchall()
   for row in results:
      firstname = row[0]
      lastname = row[1]
      email = row[2]
      note = row[3]
      image_url = row[4]
      company = row[5]
      department = row[6]
      ext = row[7]
      office = row[8]
      home = row[9]
      mobile = row[10]
      other = row[11]
      if ext != "" and ext is not None:
         ct = ext
      elif office != "" and office is not None:
         ct = office
      elif home != "" and home is not None:
         ct = home
      else:
         ct = other
      contact = re.sub(r"[^0-9+]", "", ct)
      # Now print fetched result
      diruser = "    <directoryDetails>\n      <firstName>%s</firstName>\n      <lastName>%s</lastName>\n      <number>%s</number>\n      <mobile>%s</mobile>\n    </directoryDetails>\n" % (lastname, firstname, contact, mobile)
      file.write(diruser)
except:
   print "Error: unable to fecth data"


# disconnect from server
db.close()

file.write("  </groupDirectory>\n</Group>")
file.close()
