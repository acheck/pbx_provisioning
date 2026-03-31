BuildArch:     noarch
Name:          tl-snom-templates-%{type}
Version:       %{version}
Release:       %{release}%{?dist}
License:       GPL 
Group:         Utilities/System
Summary:       Snom Provisioning Templates for Thirdlane MTE PBX
URL:           http://www.thirdlane.com
Source:        %{name}.tar.gz



Requires:      /usr/bin/python2
Requires:      MySQL-python  
#Requires:      grandstream-firmwareGXP16xx > 1.0.4.100

%description

%prep
%setup -q -n %{name}

%build

%install
mkdir -p %{buildroot}/etc/asterisk/provisioning/models.d/
mkdir -p %{buildroot}/home/PlcmSpIp
install -m 644 *cfg %{buildroot}/etc/asterisk/provisioning/
install -m 644 snom.txt %{buildroot}/etc/asterisk/provisioning/models.d/

%files
%defattr(644,root,root)
/etc/asterisk/provisioning/*.cfg
/etc/asterisk/provisioning/models.d/snom.txt
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
   if model.startswith("snom"): 
      PhoneModels.remove_section(model)

with open(modelsfile, "w") as modelfile:
   PhoneModels.write(modelfile)

notifyfile = "/etc/asterisk/sip_notify.conf"
notifyConfig = MyConfigParser()
notifyConfig.optionxform = str 
with open(notifyfile, "r") as modelfile:
      notifyConfig.readfp(modelfile)
if notifyConfig.has_section('snom-check-cfg'):
   print "sync command already in %%s" %% notifyfile
else:
   with open(notifyfile, 'a') as file:
      file.write("\n[snom-check-cfg]\nEvent=>check-sync\\;reboot=true\nContent-Length=>0\n")
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
   if c.execute ("select (1) from provisioning_maps where name = 'snom' and category = 'tz' limit 1"):
      print "Timezone maps already installed in DB"
   else:
      c.executemany(
      """INSERT INTO  provisioning_maps (name, category, description, original, replacement)
      VALUES (%%s, %%s, %%s, %%s, %%s)""",
         [
         ('snom', 'tz', 'Snom', 'default', 'EST5EDT'),
         ('snom', 'tz', 'Snom', 'EST5EDT', 'EST5EDT'),
         ('snom', 'tz', 'Snom', 'CST6CDT', 'CST6CDT'),
         ('snom', 'tz', 'Snom', 'MST7MDT', 'MST7MDT'),
         ('snom', 'tz', 'Snom', 'PST8PDT', 'PST8PDT')
         ] )
      db.commit()
      print "inserting TZ mappings into DB"
except:
   print "Error: unable to connect to DB"
db.close()

%changelog
* Wed Jul 1 2020 Erik Smith <esmith.bgnv@gmail.com>
- Added support for an additional MAC vendor ID that sGrandstream acquired 
* Tue Feb 26 2019 Erik Smith <esmith.bgnv@gmail.com>
- Added the option to not remove manually edited entries from the remote phonebook. Removed setting for ring tone so user can override.

* Mon Feb 04 2019 Erik Smith <esmith.bgnv@gmail.com>
- Added new values to the dictionary in support of new HTTP password authentication for pro
visioning.

* Mon Jul 09 2018 Erik Smith <eeman@bluegrassnetvoice.com>
- Added button types conference, call park, record, voicemail, dnd, and transfer
 to the templates. Added support for FIXED VPK buttons besides just linekey on p
hones that do not have MPKs. Disabled Weather App and Screensaver based on multi
ple user feedback. Added auto answer warning tone.

* Wed May 16 2018 Erik Smith <eeman@bluegrassnetvoice.com>
- fixed a bug where the file declaration for blf, speeddial, and paging for the
gxp2170 had a typo in the models file

* Wed Aug 02 2017 Erik Smith <eeman@bluegrassnetvoice.com>
- fixed a bug where a key not present in the dictionary file can cause the gs-convert-to-xml script to end prematurely.

* Mon Jul 24 2017 Erik Smith <eeman@bluegrassnetvoice.com>
- Upgraded firmware to 1.0.8.50

