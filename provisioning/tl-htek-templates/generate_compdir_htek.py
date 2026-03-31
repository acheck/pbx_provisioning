#!/usr/bin/python2

import sys, os, pwd, grp, re, ConfigParser, MySQLdb, syslog

# Verify MAC address passed to script
if len(sys.argv) > 1 :
   tenantname = str(sys.argv[1])
else:
   print "Usage: %s tenant_name" % str(sys.argv[0])
   syslog.syslog(syslog.LOG_ERR, "Usage: %s tenant_name" % str(sys.argv[0]))
   sys.exit(1)

filename = "/home/PlcmSpIp/CONTACTS/%s/htek_remotePhonebook.xml" % tenantname
dir = os.path.dirname(filename)

dbConfig = ConfigParser.ConfigParser()
dbConfig.read ("/etc/asterisk/res_config_mysql.conf")
dbhost = dbConfig.get('pbxconf', 'dbhost')
dbname = dbConfig.get('pbxconf', 'dbname')
dbuser = dbConfig.get('pbxconf', 'dbuser')
dbpass = dbConfig.get('pbxconf', 'dbpass')

try:
    os.stat(dir)
except:
    os.mkdir(dir, 0755)

os.chmod(dir, 0755)
uid = pwd.getpwnam("PlcmSpIp").pw_uid
gid = grp.getgrnam("PlcmSpIp").gr_gid
os.chown(dir, uid, gid)

file = open(filename, "w")

file.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<PhoneDirectory>\n")

# Open database connection
db = MySQLdb.connect(dbhost,dbuser,dbpass,dbname)

# prepare a cursor object using cursor() method
cursor = db.cursor()

id = 1

try:
   # Execute the SQL command
   sql1= "SELECT id from tenants where tenant = '%s'" % (tenantname)
   cursor.execute(sql1)
   tid = cursor.fetchone()
   sql2= "SELECT firstname, lastname, email, note, image_url, company, department, ext, office, home, mobile, other FROM directory where tenantid = '%d' and owner = '' order by lastname asc" % tid
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
      mob = row[10]
      oth = row[11]
      if ext != "" and ext is not None:
         ct = ext
      elif office !="" and office is not None:
         ct = office
      else:
         ct = ""
      if oth != "" and oth is not None:
         ct2 = oth
      elif home != "" and home is not None:
         ct2 = home
      else:
         ct2 = ""
      if mob == "" or mob is None:
         mobile = ""
      else:
         mobile = re.sub(r"[^0-9+]", "", mob)
      other = re.sub(r"[^0-9+]", "", ct2)
      work = re.sub(r"[^0-9+]", "", ct)
      # Now print fetched result
      diruser = "   <DirectoryEntry>\n      <Name>%s %s</Name>\n      <Telephone>%s</Telephone>\n      <Telephone>%s</Telephone>\n      <Telephone>%s</Telephone>\n   </DirectoryEntry>\n" % (firstname, lastname, work, other, mobile)
      file.write(diruser)
      id += 1
except:
   print "Error: unable to fecth data"


# disconnect from server
db.close()

file.write("</PhoneDirectory>")
file.close()
