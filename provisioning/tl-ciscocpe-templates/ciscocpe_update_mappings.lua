#!/usr/bin/tarantool
require'strict'.on()

log    = require('log')
json   = require('json')
lib    = require('lib_sniffer')
pbxm   = require('pbxm')
mysql  = require('mysql')
sf     = string.format

tz_map = [[
default = Central Europe Standard/Daylight Time
GMT-8   = Pacific Standard/Daylight Time
GMT-7   = Mountain Standard/Daylight Time
GMT-6   = Central Standard/Daylight Time
GMT-5   = Eastern Standard/Daylight Time
GMT-4   = Atlantic Standard/Daylight Time
GMT-3   = SA Eastern Standard Time
GMT-2   = Mid-Atlantic Standard/Daylight Time
GMT-1   = Azores Standard/Daylight Time
GMT     = GMT Standard/Daylight Time
GMT+1   = W. Europe Standard/Daylight Time
GMT+2   = Central Europe Standard/Daylight Time
GMT+3   = Saudi Arabia Standard Time
GMT+4   = Arabian Standard Time
GMT+5   = West Asia Standard Time
GMT+6   = Central Asia Standard Time
GMT+7   = SE Asia Standard Time
GMT+8   = China Standard/Daylight Time
GMT+9   = Tokyo Standard Time
GMT+10  = E. Australia Standard Time
GMT+11  = Central Pacific Standard Time
GMT+12  = New Zealand Standard/Daylight Time
]]

tz_list = lib.split2hash(tz_map, '\n')
tz_list['default'] = tz_list['GMT+1']

local debug = false
--debug = true

-- default MySQL config
local mysql_dbs = pbxm.config_dbs()
local db = mysql_dbs.pbxconf
if debug then print(json.encode(db)) end
pbxconf = mysql.connect( { host = db.host, port = 0, user = db.username, password = db.password, db = 'pbxconf', use_numeric_result = true, raise = false } )

name, desc = 'cisco88xx', 'Cisco CPE 88XX'

local sql = sf("DELETE FROM provisioning_maps WHERE name='%s' AND category='tz'", name)
pbxconf:execute(sql)

for k, v in pairs(tz_list) do
  if debug then print(k, v) end
  sql = sf("DELETE FROM provisioning_maps WHERE name='%s' AND category='tz' AND original='%s'", name, k)
  if debug then print(sql) end
  pbxconf:execute(sql)
  sql = sf("INSERT INTO provisioning_maps (`name`, category, description, original, replacement) VALUES ('%s', 'tz', '%s','%s', '%s')", name, desc, k, v)
  if debug then print(sql) end
  pbxconf:execute(sql)
end

os.exit(0)
