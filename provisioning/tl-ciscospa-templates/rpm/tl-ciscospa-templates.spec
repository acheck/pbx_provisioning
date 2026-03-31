BuildArch:     noarch
Name:          tl-ciscospa-templates-%{type}
Version:       %{version}
Release:       %{release}%{?dist}
License:       GPL 
Group:         Utilities/System
Summary:       Cisco SPA Provisioning Templates for Thirdlane PBX Multi-Tenant Edition
URL:           http://www.thirdlane.com
Source:        %{name}.tar.gz

Requires:      /usr/bin/python2
Requires:      MySQL-python  
Requires:      ciscospa-firmwareSPA30x_SPA50x  
Requires:      ciscospa-firmwareSPA51x  
Requires:      ciscospa-firmwareSPA525G  

%description

%prep

%setup -q -n %{name}

%build

%install
mkdir -p %{buildroot}/etc/asterisk/provisioning/models.d/
mkdir -p %{buildroot}/usr/local/sbin/
mkdir -p %{buildroot}/home/PlcmSpIp/
install -m 644 *cfg %{buildroot}/etc/asterisk/provisioning/
install -m 644 ciscospa.txt %{buildroot}/etc/asterisk/provisioning/models.d/

%files
%defattr(644,root,root)
/etc/asterisk/provisioning/ciscospa_button_blf.cfg
/etc/asterisk/provisioning/ciscospa_button_linekey.cfg
/etc/asterisk/provisioning/ciscospa_button_speeddial.cfg
/etc/asterisk/provisioning/ciscospa_console_unit1.cfg
/etc/asterisk/provisioning/ciscospa_console_unit2.cfg
/etc/asterisk/provisioning/ciscospa_line.cfg
/etc/asterisk/provisioning/ciscospa_model_30x50x.cfg
/etc/asterisk/provisioning/ciscospa_model_51x.cfg
/etc/asterisk/provisioning/ciscospa_model_525G.cfg
/etc/asterisk/provisioning/ciscospa_model_525G2.cfg
/etc/asterisk/provisioning/ciscospa_phone_5xx.cfg
/etc/asterisk/provisioning/models.d/ciscospa.txt
%dir %attr(0751, root, root) /home/PlcmSpIp

%post -p /usr/bin/python

import sys, os, pwd, grp, re, ConfigParser, MySQLdb

class MyConfigParser(ConfigParser.ConfigParser):
    def write(self, fp):
        """Write an .ini-format representation of the configuration state."""
        if self._defaults:
            fp.write("[%%s]\n" %% ConfigParser.DEFAULTSECT)
            for (key, value) in self._defaults.items():
                fp.write("%%s=%%s\n" %% (key, str(value).replace('\n', '\n\t')))
            fp.write("\n")
        for section in self._sections:
            fp.write("[%%s]\n" %% section)
            for (key, value) in self._sections[section].items():
                if key == "__name__":
                    continue
                if (value is not None) or (self._optcre == self.OPTCRE):
                    key = "=".join((key, str(value).replace('\n', '\n\t')))
                fp.write("%%s\n" %% key)
            fp.write("\n")

modelsfile = "/etc/asterisk/provisioning/models.txt"
PhoneModels = MyConfigParser()
PhoneModels.optionxform = str
with open(modelsfile, "r") as modelfile:
      PhoneModels.readfp(modelfile)

devices = PhoneModels.sections()

for model in devices:
   if model.startswith("ciscospa"): 
      PhoneModels.remove_section(model)

with open(modelsfile, "w") as modelfile:
   PhoneModels.write(modelfile)

notifyfile = "/etc/asterisk/sip_notify.conf"
notifyConfig = MyConfigParser()
notifyConfig.optionxform = str 
with open(notifyfile, "r") as modelfile:
      notifyConfig.readfp(modelfile)
if notifyConfig.has_section('cisco-check-cfg'):
   print "sync command already in %%s" %% notifyfile
else:
   with open(notifyfile, 'a') as file:
      file.write("\n[cisco-check-cfg]\nEvent=>check-sync\n")
      print "adding SIP Notify cmd to %%s" %% notifyfile
      os.system("/usr/sbin/asterisk -rx \"sip reload\"")
      print "reloading sip module to re-read %%s" %% notifyfile
   file.close()


dbConfig = MyConfigParser()
dbConfig.read ("/etc/asterisk/res_config_mysql.conf")
dbhost = dbConfig.get('pbxconf', 'dbhost')
dbname = dbConfig.get('pbxconf', 'dbname')
dbuser = dbConfig.get('pbxconf', 'dbuser')
dbpass = dbConfig.get('pbxconf', 'dbpass')
dbuser = dbConfig.get('pbxconf', 'dbuser')
# Open database connection
db = MySQLdb.connect(dbhost,dbuser,dbpass,dbname)
# prepare a cursor object using cursor() method
c = db.cursor()
try:
   if c.execute ("select (1) from provisioning_maps where name = 'ciscospa' and category = 'tz' limit 1"):
      print "Timezone maps already installed in DB"
   else:
      c.executemany(
      """INSERT INTO  provisioning_maps (name, category, description, original, replacement)
      VALUES (%%s, %%s, %%s, %%s, %%s)""",
         [
         ('ciscospa', 'tz', 'Cisco Small Business', 'default', 'GMT-05:00'),
         ('ciscospa', 'tz', 'Cisco Small Business', 'EST5EDT', 'GMT-05:00'),
         ('ciscospa', 'tz', 'Cisco Small Business', 'CST6CDT', 'GMT-06:00'),
         ('ciscospa', 'tz', 'Cisco Small Business', 'MST7MDT', 'GMT-07:00'),
         ('ciscospa', 'tz', 'Cisco Small Business', 'PST8PDT', 'GMT-08:00')
         ] )
      db.commit()
      print "inserting TZ mappings into DB"
except:
   print "Error: unable to connect to DB"
db.close()
%changelog
* Fri Sep 3 2021 Erik Smith <eeman@bluegrassnetvoice.com>
- Updated firmware to final version now that these models have gone end of sale
* Tue Jan 31 2017 Erik Smith <eeman@bluegrassnetvoice.com>
- fixed invalid output of model.cfg for 508G and fixed firmware input model.cfg template for the 50x to reference correct firmware.

* Mon Nov 14 2016 Erik Smith <eeman@bluegrassnetvoice.com>
- fixed the tag for outbound sip proxy.

* Wed Nov 02 2016 Erik Smith <eeman@bluegrassnetvoice.com>
- added Interdigit timeouts to config to allow faster dialing of unmatched dialplan entries. Now set to 5 seconds instead of 10.

