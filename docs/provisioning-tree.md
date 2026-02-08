# Provisioning Tree (provisioning/)

This document describes the **provisioning/** directory in this project: vendor template bundles used to generate phone config files. Each vendor folder contains model definitions (INI-style `.txt` files) and config templates (`.cfg`, etc.) that pbx_manager (or a compatible provisioner) uses when provisioning devices.

---

## 1. Overview

- **Location:** `provisioning/` at the project root (i.e. `pbx_provisioning/provisioning/`).
- **Purpose:** One subfolder per **vendor** (e.g. `tl-yealink-templates`). Each folder holds:
  - **Model definition file(s)** — INI-style `[model-id]` sections with `output=`, `phone_template=`, `line_template=`, etc.
  - **Config templates** — `.cfg` (and sometimes `.xml`/other) files referenced by the model; they use variables like `${MAC}`, `${mac}`, `${TENANT}`.
  - **Build/package scripts** — `make_templates-*.sh`, `rpm/`, Python/Lua helpers, optional READMEs.
- **Output patterns** from these model files are collected into **`unique-output-patterns.txt`** at the project root (see [output-patterns.md](output-patterns.md)).

---

## 2. Top-level structure

```
provisioning/
├── tl-ciscocpe-templates/    # Cisco CPE (78xx, 88xx)
├── tl-ciscospa-templates/    # Cisco SPA
├── tl-fanvil-templates/      # Fanvil
├── tl-grandstream-templates/ # Grandstream
├── tl-htek-templates/        # Htek
├── tl-polycom-templates/     # Polycom (SP, VVX, etc.)
├── tl-snom-templates/        # Snom (7xx, D-series)
└── tl-yealink-templates/     # Yealink
```

All vendor folders follow the pattern **`tl-<vendor>-templates`**.

---

## 3. Model definition files

Model files define each phone model: label, line count, which templates to use, and the **output** filename pattern. Format is INI-style: `[model-id]` sections with `key=value`.

### 3.1 Where model files live

| Vendor folder | Model file(s) | Notes |
|---------------|---------------|--------|
| **tl-ciscocpe-templates** | `models.d/ciscocp-7800.txt`, `models.d/ciscocp-8800.txt` | CPE uses a `models.d/` subdir |
| **tl-ciscospa-templates** | `ciscospa.txt` | |
| **tl-fanvil-templates** | `fanvil-model.txt` | |
| **tl-grandstream-templates** | `gs.txt` | |
| **tl-htek-templates** | `htek-model.txt` | |
| **tl-polycom-templates** | `polycom.txt` | |
| **tl-snom-templates** | `snom.txt` | |
| **tl-yealink-templates** | `yealink_model.txt` | |

### 3.2 Panel / sidecar files (no `output`)

Some vendors have a separate file for **expansion panels / sidecars** (BLF, DSS, etc.). These define button layouts and templates but do **not** define `output=` (they are referenced by the main device’s `panel` setting).

| File | Purpose |
|------|---------|
| `tl-yealink-templates/yealink_panel.txt` | Yealink EXP panels |
| `tl-fanvil-templates/fanvil-panel.txt` | Fanvil DSS / side pages |

### 3.3 Common model keys

Keys commonly used in `[model-id]` sections:

| Key | Meaning |
|-----|--------|
| `label` | Human-readable model name (e.g. "Snom D140") |
| `lines` | Number of lines/accounts |
| `output` | **Output filename pattern** (e.g. `${mac}.cfg`, `SEP${MAC}.cnf.xml`). Used to write the main generated config. |
| `phone_template` | Template for main phone config |
| `line_template` | Template for each line/account |
| `blf_template`, `speeddial_template`, … | Button/feature templates (BLF, speed dial, DND, park, VM, etc.) |
| `input_1`, `output_1`, … | Extra template → output file pairs (e.g. firmware, settings) |
| `command_1`, … | Commands run after config generation (e.g. convert to XML, update compdir) |
| `translationmap` | Name of provisioning map for timezone/variable translation (from DB `provisioning_maps`) |
| `check_sync` | Sync/check method (e.g. `snom-check-cfg`, `cisco-reset`) |
| `firmware` | Firmware file or identifier (vendor-specific) |
| `use_span` | Optional (e.g. 0/1 for Cisco SPA) |

Variables in values: `${MAC}`, `${mac}`, `${TENANT}`, etc. are substituted at provision time.

---

## 4. Per-vendor summary

### 4.1 Cisco CPE (tl-ciscocpe-templates)

- **Model files:** `models.d/ciscocp-7800.txt`, `models.d/ciscocp-8800.txt`
- **Output pattern:** `SEP${MAC}.cnf.xml`
- **Templates:** `cisco-88xx_phone.cfg`, `cisco-88xx_line.cfg`, button templates, dial/ctl/softkey; extra outputs for `DialTemplate.xml`, `CTLSEP${MAC}.tlv`, `ITLSEP${MAC}.tlv`, `softkeyDefault.xml`
- **Scripts:** `make_templates-ciscocpe.sh`, `ciscocpe_rebuild_phones.lua`, `ciscocpe_update_mappings.lua`; patches and SIP notify config

### 4.2 Cisco SPA (tl-ciscospa-templates)

- **Model file:** `ciscospa.txt`
- **Output pattern:** `spa${mac}.cfg`
- **Templates:** `ciscospa_phone_5xx.cfg`, `ciscospa_line.cfg`, button templates, console units; optional `input_1`/`output_1` for model-specific static files

### 4.3 Fanvil (tl-fanvil-templates)

- **Model file:** `fanvil-model.txt`
- **Panel file:** `fanvil-panel.txt`
- **Output pattern:** `${mac}.cfg`
- **Templates:** `fanvil_phone.cfg`, `fanvil_line.cfg`, device/button templates; `input_1`/`output_1` for device-specific file (e.g. `F0VW611W0000.cfg`)
- **Scripts:** `make_templates-fanvil.sh`, `generate_compdir_fanvil.py`; `rpm/`, `docs/`

### 4.4 Grandstream (tl-grandstream-templates)

- **Model file:** `gs.txt`
- **Output pattern:** `${mac}.txt` (then converted to XML by script)
- **Templates:** `gs_gxp21xx_phone.cfg`, `gs_gxp21xx_line.cfg`, linekey and button templates
- **Aux file:** `gs_pval_dict.txt` (parameter/value dictionary)
- **Scripts:** `make_templates-grandstream.sh`, `gs-convert-to-xml.py`, `generate_compdir_gs.py`; `rpm/`

### 4.5 HTek (tl-htek-templates)

- **Model file:** `htek-model.txt`
- **Output pattern:** `${mac}.txt` (then converted to XML by script)
- **Templates:** `htek_phone.cfg`, `htek_line.cfg`, `htek_device.cfg`, button templates; `input_1`/`output_1` for device XML (e.g. `cfg0111.xml`)
- **Aux file:** `htek_pval_dict.txt`
- **Scripts:** `make_templates-htek.sh`, `htek-convert-to-xml.py`, `generate_compdir_htek.py`

### 4.6 Polycom (tl-polycom-templates)

- **Model file:** `polycom.txt`
- **Output patterns:** `${mac}-registration.cfg` (SP series); `${MAC}.xml` (VVX series)
- **Templates:** `polycom_phone.cfg`, `polycom_line.cfg`, optional `polycom_blf.cfg`; `input_*`/`output_*` for `${mac}.cfg`, `${TENANT}-settings.cfg`, `${TENANT}-settings-uc.cfg`
- **Scripts:** `make_templates-polycom.sh`, `generate_compdir_polycom.py`, `generate_compdir_obi.py`; `rpm/`

### 4.7 Snom (tl-snom-templates)

- **Model file:** `snom.txt`
- **Output pattern:** `snomD<model>-${MAC}.htm` (e.g. `snomD140-${MAC}.htm`)
- **Templates:** Shared `snom7xx_phone.cfg`, `snom7xx_line.cfg`, BLF/speeddial; per-model `snomD140_settings.cfg`, `snomD140_firmware.cfg`, etc.; `input_1`/`output_1` (e.g. `snomD140.htm`), `input_2`/`output_2` (firmware)
- **Scripts:** `make_templates-snom.sh`; `snom-gen/` (Lua/tpl); `rpm/`

### 4.8 Yealink (tl-yealink-templates)

- **Model file:** `yealink_model.txt`
- **Panel file:** `yealink_panel.txt`
- **Output pattern:** `${mac}.cfg`
- **Templates:** `yealink_phone.cfg`, `yealink_line.cfg`, many `yealink_device_*.cfg`, `yealink_button_*.cfg`, `yealink_panel_*.cfg`; `input_1`/`output_1` for device-specific file (e.g. `y000000000037.cfg`)
- **Scripts:** `make_templates-yealink.sh`, `add_firmware_to_model.py`, `generate_compdir_yealink.py`; `rpm/`, `docs/`

---

## 5. Other file types

- **\*_pval_dict.txt** — Parameter/value dictionaries (Grandstream, HTek) for conversion or validation.
- **make_templates-*.sh** — Build or pack templates (often for RPM).
- **rpm/** — Spec files and build scripts for packaging the bundle (e.g. `tl-yealink-templates.spec`).
- **generate_compdir_*.py**, **\*-convert-to-xml.py** — Post-provision steps: generate company directory, convert config to XML.
- **README**, **docs/README.md** — Vendor-specific notes (some bundles only).

---

## 6. Relation to pbx_manager and this project

- **pbx_manager** (e.g. at `/home/acheck/pbx_manager/server`) can load model definitions from a provisioning tree. When bundles are installed (e.g. under `/etc/asterisk/provisioning/models.d/` or a configured path), `list_device_models()` merges system models, user overrides, and `models.d/` so that models from this tree are available for provisioning.
- **unique-output-patterns.txt** — Generated by **`./refresh-output-patterns.sh`** from all `output=` lines in `provisioning/**/*.txt`. See [output-patterns.md](output-patterns.md) for the list and vendor mapping.
- **Phone config generation flow** — See [phone-config-and-provisioning-templates.md](phone-config-and-provisioning-templates.md) and [database-and-config-for-provisioning.md](database-and-config-for-provisioning.md) for how pbx_manager uses models and templates.
