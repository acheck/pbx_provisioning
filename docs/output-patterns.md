# Provisioning output filename patterns

This document lists the **unique `output` patterns** used in the vendor model files in this project's **`provisioning/`** directory. Each pattern defines how a generated config file is named (e.g. `${mac}.cfg`, `SEP${MAC}.cnf.xml`). Variables `${mac}` or `${MAC}` are replaced by the device MAC at provision time.

The canonical sorted list is in **`../unique-output-patterns.txt`**.

---

## Sorted list of unique patterns

| # | Output pattern | Vendor(s) | Model file(s) |
|---|----------------|-----------|----------------|
| 1 | `SEP${MAC}.cnf.xml` | Cisco CPE (78xx, 88xx) | `tl-ciscocpe-templates/models.d/ciscocp-7800.txt`, `ciscocp-8800.txt` |
| 2 | `snomD140-${MAC}.htm` | Snom | `tl-snom-templates/snom.txt` |
| 3 | `snomD150-${MAC}.htm` | Snom | `tl-snom-templates/snom.txt` |
| 4 | `snomD713-${MAC}.htm` | Snom | `tl-snom-templates/snom.txt` |
| 5 | `snomD717-${MAC}.htm` | Snom | `tl-snom-templates/snom.txt` |
| 6 | `snomD735-${MAC}.htm` | Snom | `tl-snom-templates/snom.txt` |
| 7 | `snomD785-${MAC}.htm` | Snom | `tl-snom-templates/snom.txt` |
| 8 | `spa${mac}.cfg` | Cisco SPA | `tl-ciscospa-templates/ciscospa.txt` |
| 9 | `${MAC}.xml` | Polycom (VVX) | `tl-polycom-templates/polycom.txt` |
| 10 | `${mac}.cfg` | Yealink, Fanvil | `yealink_model.txt`, `fanvil-model.txt` |
| 11 | `${mac}-registration.cfg` | Polycom (other) | `tl-polycom-templates/polycom.txt` |
| 12 | `${mac}.txt` | Grandstream, HTek | `gs.txt`, `htek-model.txt` |

---

## Notes

- **Case:** Patterns use either `${mac}` (lowercase) or `${MAC}` (uppercase) depending on vendor conventions; both refer to the device MAC address.
- **Extensions:** `.cfg`, `.txt`, `.xml`, `.htm` — vendor- and model-specific.
- **Prefixes:** Some vendors use a fixed prefix (e.g. `spa`, `SEP`, `snomD140-`) before the MAC.

These patterns are written into the provisioning output directory (e.g. `/home/PlcmSpIp`) so phones can request their config by filename (FTP/HTTP/HTTPS/TFTP).
