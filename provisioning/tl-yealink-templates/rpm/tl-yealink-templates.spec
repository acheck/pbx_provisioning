BuildArch:     noarch
Name:          tl-yealink-templates-%{type}
Version:       %{version}
Release:       %{release}%{?dist}
License:       GPL 
Group:         Utilities/System
Summary:       yealink Provisioning Templates for Thirdlane PBX
URL:           http://www.thirdlane.com
Source:        %{name}.tar.gz

Requires:      /usr/bin/python2
Requires:      MySQL-python  
Requires:      pbxmw-%{type} > 7.5.0
Requires:      yealink-firmwareT19P_E2 = 80.0.130
Requires:      yealink-firmwareT21P_E2 = 80.0.130
Requires:      yealink-firmwareT23 = 80.0.130
Requires:      yealink-firmwareT27P = 80.0.130
Requires:      yealink-firmwareT40 = 80.0.130
Requires:      yealink-firmwareT41 = 80.0.130
Requires:      yealink-firmwareT42 = 80.0.130
Requires:      yealink-firmwareT46 = 80.0.130
Requires:      yealink-firmwareT48 = 80.0.130
Requires:      yealink-firmwareW52P = 80.0.15

%description

%prep

%setup -q -n %{name}

%build

%install
mkdir -p %{buildroot}/etc/asterisk/provisioning/models.d/
mkdir -p %{buildroot}/usr/local/sbin
install -m 644 *cfg %{buildroot}/etc/asterisk/provisioning/
install -m 644 yealink.txt %{buildroot}/etc/asterisk/provisioning/models.d/
install -m 755 generate_compdir_yealink.py %{buildroot}/usr/local/sbin/
mkdir -p %{buildroot}/home/PlcmSpIp

%files
%defattr(644,root,root)
/etc/asterisk/provisioning/models.d/yealink.txt
/etc/asterisk/provisioning/yealink_*.cfg
%attr(755, root, root) /usr/local/sbin/generate_compdir_yealink.py
%dir %attr(751, root, root) /home/PlcmSpIp

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
   if model.startswith("yealink"): 
      PhoneModels.remove_section(model)

with open(modelsfile, "w") as modelfile:
   PhoneModels.write(modelfile)

notifyfile = "/etc/asterisk/sip_notify.conf"
notifyConfig = MyConfigParser()
notifyConfig.optionxform = str 
with open(notifyfile, "r") as modelfile:
      notifyConfig.readfp(modelfile)
if notifyConfig.has_section('yealink-check-cfg'):
   print "sync command already in %%s" %% notifyfile
else:
   with open(notifyfile, 'a') as file:
      file.write("\n[yealink-check-cfg]\nEvent=>check-sync\\;reboot=true\nContent-Length=>0\n")
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
   if c.execute ("select (1) from provisioning_maps where name = 'yealink' and category = 'tz' limit 1"):
      print "Timezone maps already installed in DB"
   else:
      c.executemany(
      """INSERT INTO  provisioning_maps (name, category, description, original, replacement)
      VALUES (%%s, %%s, %%s, %%s, %%s)""",
         [
         ('yealink', 'tz', 'Yealink', 'default', '-5'),
         ('yealink', 'tz', 'Yealink', 'EST5EDT', '-5'),
         ('yealink', 'tz', 'Yealink', 'CST6CDT', '-6'),
         ('yealink', 'tz', 'Yealink', 'MST7MDT', '-7'),
         ('yealink', 'tz', 'Yealink', 'PST8PDT', '-8')
         ] )
      db.commit()
      print "inserting TZ mappings into DB"
except:
   print "Error: unable to connect to DB"
db.close()

%changelog
* Fri Feb 08 2019 Erik Smith <esmith.bgnv@gmail.com>
- Added support for XML Remote Phonebook of Thirdlane Company Directory created when any device gets provisioned.
* Tue May 23 2017 Erik Smith <eeman@bluegrassnetvoice.com>
- Changed phone_setting.common_power_led_enable to 0 as it was interfering with MWI
* Tue Jan 03 2017 Erik Smith <eeman@bluegrassnetvoice.com>
- Added support for the W56H handset for the W52P/W56P base unit.
* Mon Nov 07 2016 Erik Smith <eeman@bluegrassnetvoice.com>
- Fixed yealink_device template files to correctly address ${SERVER} instead of ${SIPSERVER}
* Mon Oct 31 2016 Erik Smith <eeman@bluegrassnetvoice.com>
- added post-install script to ensure models.txt stripped, sip_notify checked, and rows inserted into provisioning_maps.
* Tue Sep 20 2016 Erik Smith <eeman@bluegrassnetvoice.com>
- added support for T48G and T40P
* Tue Sep 20 2016 Erik Smith <eeman@bluegrassnetvoice.com>
- added support for new button types
* Wed Aug 17 2016 Erik Smith <eeman@bluegrassnetvoice.com>
- added support for T41P
* Fri Aug 12 2016 Erik Smith <eeman@bluegrassnetvoice.com>
- added support for new linekey button type
* Fri Aug 12 2016 Erik Smith <eeman@bluegrassnetvoice.com>
- initial build for basic support for the following models: T46G, T42G, T27P, T23P/G, T21P E2, T19P E2, W52P
