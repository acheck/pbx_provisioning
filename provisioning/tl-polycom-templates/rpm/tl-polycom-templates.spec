BuildArch:     noarch
Name:          tl-polycom-templates-%{type}
Version:       %{version}
Release:       %{release}%{?dist}
License:       GPL 
Group:         Utilities/System
Summary:       Polycom Provisioning Templates for Thirdlane PBX Multi-Tenant Edition
URL:           http://www.thirdlane.com
Source:        %{name}.tar.gz

Requires:      /usr/bin/python2
Requires:      MySQL-python  
Requires:      polycom-bootrom >= 4.4.0
Requires:      polycom-firmware31  
Requires:      polycom-firmware32  
Requires:      polycom-firmware40-combined  
Requires:      polycom-firmware4x  
Requires:      polycom-firmware5x  
Requires:      polycom-firmware6x  
Requires:      polycom-firmwareOBi

%description

%prep

%setup -q -n %{name}

%build

%install
mkdir -p %{buildroot}/etc/asterisk/provisioning/models.d/
mkdir -p %{buildroot}/usr/local/sbin/
install -m 644 *cfg %{buildroot}/etc/asterisk/provisioning/
install -m 644 polycom.txt %{buildroot}/etc/asterisk/provisioning/models.d/
install -m 755 generate_compdir_polycom.py %{buildroot}/usr/local/sbin/
install -m 755 generate_compdir_obi.py %{buildroot}/usr/local/sbin/
mkdir -p %{buildroot}/home/PlcmSpIp/LICENSE
mkdir -p %{buildroot}/home/PlcmSpIp/PROFILES
mkdir -p %{buildroot}/home/PlcmSpIp/CALLLIST
mkdir -p %{buildroot}/home/PlcmSpIp/CONTACTS
mkdir -p %{buildroot}/home/PlcmSpIp/LOGS
mkdir -p %{buildroot}/home/PlcmSpIp/OVERRIDES

%files
%defattr(644,root,root)
/etc/asterisk/provisioning/models.d/polycom.txt
/etc/asterisk/provisioning/polycom_blf.cfg
/etc/asterisk/provisioning/polycom_line.cfg
/etc/asterisk/provisioning/polycom_line_obi.cfg
/etc/asterisk/provisioning/polycom_local.cfg
/etc/asterisk/provisioning/polycom_local_uc.cfg
/etc/asterisk/provisioning/polycom_mac.cfg
/etc/asterisk/provisioning/polycom_phone.cfg
/etc/asterisk/provisioning/polycom_phone_obi.cfg
/etc/asterisk/provisioning/polycom_device_obi3xx.cfg
/etc/asterisk/provisioning/polycom_device_obi5xx.cfg
/etc/asterisk/provisioning/polycom_device_vvxd230.cfg
%attr(755, root, root) /usr/local/sbin/generate_compdir_polycom.py
%attr(755, root, root) /usr/local/sbin/generate_compdir_obi.py
%dir %attr(751, root, root) /home/PlcmSpIp
%dir %attr(755, root, root) /home/PlcmSpIp/LICENSE
%dir %attr(751, root, root) /home/PlcmSpIp/PROFILES
%dir %attr(755, PlcmSpIp, PlcmSpIp) /home/PlcmSpIp/CALLLIST
%dir %attr(755, PlcmSpIp, PlcmSpIp) /home/PlcmSpIp/CONTACTS
%dir %attr(755, PlcmSpIp, PlcmSpIp) /home/PlcmSpIp/LOGS
%dir %attr(755, PlcmSpIp, PlcmSpIp) /home/PlcmSpIp/OVERRIDES

%post -p /usr/bin/python2

import glob, sys, os, pwd, grp, re, ConfigParser, MySQLdb

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
   if model.startswith("polycom"): 
      PhoneModels.remove_section(model)

with open(modelsfile, "w") as modelfile:
   PhoneModels.write(modelfile)

notifyfile = "/etc/asterisk/sip_notify.conf"
notifyConfig = MyConfigParser()
notifyConfig.optionxform = str 
with open(notifyfile, "r") as modelfile:
      notifyConfig.readfp(modelfile)
if notifyConfig.has_section('polycom-check-cfg'):
   print "sync command already in %%s" %% notifyfile
else:
   with open(notifyfile, 'a') as file:
      file.write("\n[polycom-check-cfg]\nEvent=>check-sync\n")
      print "adding SIP Notify cmd to %%s" %% notifyfile
      os.system("/usr/sbin/asterisk -rx \"sip reload\"")
      print "reloading sip module to re-read %%s" %% notifyfile
   file.close()

sipfile = "/etc/asterisk/sip.conf"
inc = str()
with open(sipfile) as myfile:
   for line in myfile:
      line = line.strip()
      if not line:  # line is blank
         continue
      if line.startswith("#include"):  # line is include
         inc = inc + line + "\n"

sipConfig = MyConfigParser()
sipConfig.optionxform = str
sipConfig.read(sipfile)
if sipConfig.has_section('general'):
   if sipConfig.has_option('general', 'notifycid'):
      notifyc = sipConfig.get('general', 'notifycid')
      if notifyc == "yes" :
         print "notifycid already set in sip.conf"
      else:
         sipConfig.set('general', 'notifycid', 'yes')
         with open(sipfile, 'wb') as sipfile2:
            sipConfig.write(sipfile2)
            sipfile2.write(inc)
            print "setting notifycid=yes in [general] of sip.conf"
         sipfile2.close()
   else:
      sipConfig.set('general', 'notifycid', 'yes')
      with open(sipfile, 'wb') as sipfile2:
         sipConfig.write(sipfile2)
         sipfile2.write(inc)
         print "setting notifycid=yes in [general] of sip.conf"
      sipfile2.close()
else:
   print "[general] section missing from file"

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
   if c.execute ("select (1) from provisioning_maps where name = 'polycom' and category = 'tz' limit 1"):
      print "Polycom Timezone maps already installed in DB"
   else:
      c.executemany(
      """INSERT INTO  provisioning_maps (name, category, description, original, replacement)
      VALUES (%%s, %%s, %%s, %%s, %%s)""",
         [
         ('polycom', 'tz', 'Polycom', 'default', '-18000'),
         ('polycom', 'tz', 'Polycom', 'EST5EDT', '-18000'),
         ('polycom', 'tz', 'Polycom', 'CST6CDT', '-21600'),
         ('polycom', 'tz', 'Polycom', 'MST7MDT', '-25200'),
         ('polycom', 'tz', 'Polycom', 'PST8PDT', '-28800')
         ] )
      db.commit()
      print "inserting TZ mappings into DB"
   if c.execute ("select (1) from provisioning_maps where name = 'obipoly' and category = 'tz' limit 1"):
      print "OBi Timezone maps already installed in DB"
   else:
      c.executemany(
      """INSERT INTO  provisioning_maps (name, category, description, original, replacement)
      VALUES (%%s, %%s, %%s, %%s, %%s)""",
         [
         ('obipoly', 'tz', 'OBi/Poly', 'default', 'GMT-05:00(Eastern Time)'),
         ('obipoly', 'tz', 'OBi/Poly', 'EST5EDT', 'GMT-05:00(Eastern Time)'),
         ('obipoly', 'tz', 'OBi/Poly', 'CST6CDT', 'GMT-06:00(Central Time)'),
         ('obipoly', 'tz', 'OBi/Poly', 'MST7MDT', 'GMT-07:00(Mountain Time)'),
         ('obipoly', 'tz', 'OBi/Poly', 'PST8PDT', 'GMT-08:00(Pacific Time)')
         ] )
      db.commit()
      print "inserting OBi TZ mappings into DB"
   if os.path.isfile('/var/vsftpd/PlcmSpIp'):
      os.remove('/var/vsftpd/PlcmSpIp')
   deletefiles = '/etc/nginx/conf.d/https/service/sec__provisioning_*conf'
   r = glob.glob(deletefiles)
   for deleteme in r:
      os.remove(deleteme)
except:
   print "Error: unable to connect to DB"
db.close()

%changelog
* Wed Jul 8 2020 Erik Smith <esmith.bgnv@gmail.com>
- Added support for the VVX D230 and other OBi devices
* Tue Feb 26 2019 Erik Smith <esmith.bgnv@gmail.com>
- Added support for STUN servers
* Thu Feb 08 2018 Erik Smith <eeman@bluegrassnetvoice.com>
- Added support for VVX D60 cordless handset.
* Thu Mar 16 2017 Erik Smith <eeman@bluegrassnetvoice.com>
- Added sip keepalives, time settings, and impossible match handling to the local settings file for polycom phones. Added notifycid=yes to the post install script of RPM so that directed call pickup works correctly.
* Mon Nov 14 2016 Erik Smith <eeman@bluegrassnetvoice.com>
- Added translationmap to models file
* Mon Oct 31 2016 Erik Smith <eeman@bluegrassnetvoice.com>
- Added post-install script to ensure models.txt stripped, sip_notify checked, and rows inserted into provisioning_maps.
