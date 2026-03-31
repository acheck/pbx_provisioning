<html>
<pre>

# snom 7xx general settings file

# After each setting (before the colon) you can set a flag, which means respectively:
# ! means writeable by the user, but will not overwrite existing 
# $ means writeable by the user, but will overwrite existing (available since version 4.2)
# & (or no flag) means read only, but will overwrite existing

# more settings can be found at the settings (dump) page of the phone's build in webinterface

# securuty
http_user!: admin
http_pass!: 31337
admin_mode_password!: 31337
admin_mode_password_confirm!: 31337


# Language and Time settings
 
language$: English
web_language$: English
## specify timezone as needed
timezone$: USA-5
date_us_format&: on
time_24_format&: off

# Default ring 
ring_sound$: Ringer6

# specify DST if needed
## dst: 

tone_scheme$: USA
# Volume
vol_speaker$: 13
vol_ringer$: 13
vol_handset$: 13
vol_headset$: 10
vol_speaker_mic$: 5
vol_handset_mic$: 5
vol_headset_mic$: 6

# Intercom
intercom_enabled$: on
answer_after_policy$: idle

# in order to perform automated updates, define the firmware setting file URL
# where you specify the final firmware image URL
firmware_status: https://${HTTP_USER}:${HTTP_PASSWORD}@${SERVER}/provisioning/snom%model-firmware.htm

#define also the update policy here
# valid values are <auto_update>, <ask_for_update>, <never_update_firm>,
# <never_update_boot>, <settings_only>
update_policy: auto_update

#define the firmware update interval here, amount in minutes, default is 1440 = 1 day
## firmware_interval: 2880
logon_wizard: off
firmware: ${PROTO}://${PROV_USER}:${PROV_PASSWORD}@${FIRMWARE_SERVER}${FIRMWARE_PATH}/FIRMWARE-SNOM/%firmware

</pre>
</html>
