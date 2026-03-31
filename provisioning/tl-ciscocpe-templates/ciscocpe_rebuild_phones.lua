#!/usr/bin/tarantool
require'strict'.on()

log    = require('log')
json   = require('json')
lib    = require('lib_sniffer')
pbxm   = require('pbxm')
mysql  = require('mysql')

local debug = false
-- debug = true
output = '/etc/asterisk/sip_peers_cisco.include'
reload_cmd = '/usr/sbin/asterisk -rx "sip reload"'

-- default MySQL config
local mysql_dbs = pbxm.config_dbs()
local db = mysql_dbs.pbxconf
if debug then print(json.encode(db)) end
pbxconf = mysql.connect( { host = db.host, port = 0, user = db.username, password = db.password, db = 'pbxconf', use_numeric_result = true, raise = false } )

local sql = [[
SELECT mac, model, type, value  
FROM devices a LEFT JOIN device_buttons b ON a.id = b.device_id 
WHERE a.model IN ('ciscocp-7821', 'ciscocp-8841', 'ciscocp-8832')
ORDER BY a.id, b.line;
]]

local req, status = pbxconf:execute(sql)
local device, pmac = {}, ''
if type(req[1]) ~= 'table' and type(req[1].rows) ~= 'table' then
  print('no data - exiting...')
  os.exit(0)
end

for k, row in pairs (req[1].rows) do
  local mac, model, ltype, value = row[1], row[2], row[3], row[4]
  if debug then print(mac, model, ltype, value) end
  if mac ~= pmac then pmac = mac; device[mac] = {}; device[mac].blfs = {}; end
  local dev = device[mac]
  if ltype == 'line' then dev.line = value end
  if ltype == 'blf'  then dev.blfs[value] = 1 end
end

-- get unique blfs
for k, v in pairs(device) do
  local blfs = {}
  for k, _ in pairs(v.blfs) do
    table.insert(blfs, k)
  end
  if table.getn(blfs) then
--    print(json.encode(blfs))
    device[k].blfs = blfs
  end
end

if debug then lib.print_r(device) end

local c = ''
for k, v in pairs(device) do
  c = c .. '; '..k..'\n'
  c = c .. '['..v.line..']\n'
  c = c .. [[
type=friend
host=dynamic
qualify=yes
nat=yes
cisco_usecallmanager=yes
dndbusy=yes
]]
  c = c .. 'subscribe='..table.concat(v.blfs, ',')
  c = c .. '\n'
  local t = string.match(v.line, '^%d+-(%g+)$')
  if t ~= nil then -- MTE
    c = c .. string.format('parkinglot=parkinglot_%s_default\n', t)
  else -- STE
    c = c .. 'parkinglot=parkinglot_default\n'
  end
end

fio.umask(tonumber('644', 8))
local fh = fio.open(output, {'O_CREAT', 'O_WRONLY', 'O_TRUNC'} )
if fh == nil then
  error("cannot create file ["..output.."]")
  os.exit(1)
end

fh:write(c)
fh:close()

print('file ['..output..'] has been updated - reloading sip config...')

if not debug then os.execute(reload_cmd) end

os.exit(0)
