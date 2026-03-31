#!/usr/bin/tarantool

fio = require('fio')

fw_list = [[
D140	https://downloads.snom.com/fw/10.1.169.13/bin/snomD140-10.1.169.13-SIP-r.bin
D150	https://downloads.snom.com/fw/10.1.169.13/bin/snomD150-10.1.169.13-SIP-r.bin
D713	https://downloads.snom.com/fw/10.1.169.13/bin/snomD713-10.1.169.13-SIP-r.bin
D717	https://downloads.snom.com/fw/10.1.169.13/bin/snomD717-10.1.169.13-SIP-r.bin
D735	https://downloads.snom.com/fw/10.1.169.13/bin/snomD735-10.1.169.13-SIP-r.bin
D785	https://downloads.snom.com/fw/10.1.169.13/bin/snomD785-10.1.169.13-SIP-r.bin
]]

local function readAll(file)
  local f = io.open(file, "rb")
  if f == nil then return nil end
  local content = f:read("*all")
  f:close()
  return content
end

function gen_fw_tab(str)
    local tab = {}
    for s in str:gmatch("[^\r\n]+") do
      local k, v = string.match(s, "(%S+)\t(%S+)")
      if k ~= nil then tab[k] = fio.basename(v) end
    end
    return tab
end

fw_tab = gen_fw_tab(fw_list)

model, firmware = 'model', 'firmware'
function expand (s)
    s = string.gsub(s, "%%(%w+)", function (n)
        return _G[n]
        end)
    return s
end

function gen_file(m, tpl)
    firmware = fw_tab[m]
    local s = expand(tpl)
    return s
end

function write_file(m, n, t)
    model = m
    local fname = string.format(n, m)
    local tpl = readAll(t)
    local string = gen_file(m, tpl)
    print(fname)
    local fh = fio.open(fname, {'O_WRONLY', 'O_CREAT'})
    fh:write(string)
    fh:close()
end

for k in pairs(fw_tab) do
    write_file(k, '../snom%s_firmware.cfg', 'snom_firmware.tpl')
    write_file(k, '../snom%s_settings.cfg', 'snom_settings.tpl')
end
