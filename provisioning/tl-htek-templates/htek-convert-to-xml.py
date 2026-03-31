#!/usr/bin/python2

import sys, re, os, syslog


# Verify MAC address passed to script
if len(sys.argv) > 1 :
   macaddr = str(sys.argv[1])
else:
   print "Usage: %s <mac_address>" % str(sys.argv[0])
   syslog.syslog(syslog.LOG_ERR, "Usage: %s <mac_address>" % str(sys.argv[0]))
   sys.exit(1)

# check for valid MAC format
if not re.match("[0-9a-f]{12}$", macaddr):
   syslog.syslog(syslog.LOG_ERR, "%s invoked with an invalid MAC Address %s" % (str(sys.argv[0]), macaddr))
   sys.exit("Not a valid MAC Address")

# check if MAC is a Htek device
if not macaddr.startswith("001fc1"):
   syslog.syslog(syslog.LOG_ERR, "%s : This is not a Htek device  %s" % (str(sys.argv[0]), macaddr))
   sys.exit("This is not a Htek device")

dictfile = "/etc/asterisk/provisioning/htek_pval_dict.txt"
directory = "/home/PlcmSpIp"
tempfile = "%s/%s.txt" % (directory, macaddr)
outfile = "%s/cfg%s.xml" % (directory, macaddr)
gsdict = {}

#check to see if the dictionary is redefined in the provisioning override directory
if os.path.isfile("/etc/asterisk/user_provisioning/htek_pval_dict.txt"):
   dictfile = "/etc/asterisk/user_provisioning/htek_pval_dict.txt"

try:
   with open(dictfile) as myfile:
      for line in myfile:
	 line = line.strip()
	 if not line:  # line is blank
	    continue
	 if line.startswith("#"):  # line is comment
	    continue
	 name, pval = line.partition("=")[::2]
	 name = name.strip()
	 pval = pval.strip()
	 if not pval:  # attribute missing
	    continue
	 gsdict[name] = str(pval)
except:
   syslog.syslog(syslog.LOG_ERR, "%s : Error opening dictionary  %s" % (str(sys.argv[0]), dictfile))
   sys.exit("Error opening dictionary")

file = open(outfile, "w")

file.write("<?xml version=\"1.0\" encoding=\"UTF-8\" ?>\n")
file.write("<!-- Thirdlane XML Provisioning Configuration -->\n")
file.write("<hl_provision version=\"1\">\n")
#file.write("  <mac>%s</mac>\n" % macaddr) 
file.write("  <config version=\"1\">\n")

try:
   with open(tempfile) as conffile:
      for line in conffile:
	 line = line.strip()
	 if not line:
	    continue
	 if line.startswith("#"):
	    continue
	 x, y = line.partition("=")[::2]
	 if not y:
	    continue
	 #print "    <%s>%s</%s>" % (gsdict[x.strip()],y.strip(),gsdict[x.strip()])
         if '%s' % (x.strip()) in gsdict.keys():
	    file.write("    <%s para=\"%s\">%s</%s>\n" % (gsdict[x.strip()],x.strip(),y.strip(),gsdict[x.strip()]))
         else:
            syslog.syslog(syslog.LOG_ERR, "Key %s missing from dictoinary file %s" % (x.strip(), dictfile))
except:
   syslog.syslog(syslog.LOG_ERR, "%s : Error opening Tempfile  %s" % (str(sys.argv[0]), tempfile))
   sys.exit("Error opening Tempfile")

file.write("  </config>\n")
file.write("</hl_provision>\n")
file.close()
#check to ensure outfile exiss and delete tempfile
if os.path.isfile(outfile):
   os.remove(tempfile)
