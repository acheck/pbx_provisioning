BuildArch:     noarch
Name:          tl-fanvil-templates-%{type}
Version:       %{version}
Release:       %{release}%{?dist}
License:       GPL 
Group:         Utilities/System
Summary:       Fanvil Provisioning Templates for Thirdlane PBX
URL:           http://www.thirdlane.com
Source:        %{name}.tar.gz

Requires:      /usr/bin/python  
Requires:      MySQL-python  
Requires:      pbxmw-%{type} > 7.5.0
Requires:      fanvil-firmware


%description

%prep

%setup -q -n %{name}

%build

%install
mkdir -p %{buildroot}/etc/asterisk/provisioning/models.d/
mkdir -p %{buildroot}/usr/local/sbin
install -m 644 *cfg %{buildroot}/etc/asterisk/provisioning/
install -m 644 fanvil.txt %{buildroot}/etc/asterisk/provisioning/models.d/
install -m 755 generate_compdir_fanvil.py %{buildroot}/usr/local/sbin/
mkdir -p %{buildroot}/home/PlcmSpIp

%files
%defattr(644,root,root)
/etc/asterisk/provisioning/models.d/fanvil.txt
/etc/asterisk/provisioning/fanvil_*.cfg
%attr(755, root, root) /usr/local/sbin/generate_compdir_fanvil.py
%dir %attr(751, root, root) /home/PlcmSpIp

%post -p /usr/bin/python2

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
   if model.startswith("fanvil"): 
      PhoneModels.remove_section(model)

with open(modelsfile, "w") as modelfile:
   PhoneModels.write(modelfile)

notifyfile = "/etc/asterisk/sip_notify.conf"
notifyConfig = MyConfigParser()
notifyConfig.optionxform = str 
with open(notifyfile, "r") as modelfile:
      notifyConfig.readfp(modelfile)
if notifyConfig.has_section('fanvil-check-cfg'):
   print "sync command already in %%s" %% notifyfile
else:
   with open(notifyfile, 'a') as file:
      file.write("\n[fanvil-check-cfg]\nEvent=>check-sync\\;reboot=true\nContent-Length=>0\n")
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
   if c.execute ("select (1) from provisioning_maps where name = 'fanvil' and category = 'tz' limit 1"):
      print "Timezone maps already installed in DB"
   else:
      c.executemany(
      """INSERT INTO  provisioning_maps (name, category, description, original, replacement)
      VALUES (%%s, %%s, %%s, %%s, %%s)""",
         [
         ('fanvil', 'tz', 'Fanvil', 'default', '-20'),
         ('fanvil', 'tz', 'Fanvil', 'EST5EDT', '-20'),
         ('fanvil', 'tz', 'Fanvil', 'CST6CDT', '-24'),
         ('fanvil', 'tz', 'Fanvil', 'MST7MDT', '-28'),
         ('fanvil', 'tz', 'Fanvil', 'PST8PDT', '-32')
         ] )
      db.commit()
      print "inserting TZ mappings into DB"
except:
   print "Error: unable to connect to DB"
db.close()

%changelog
