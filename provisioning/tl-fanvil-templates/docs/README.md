# tl-fanvil-templates documentation

Provisioning templates and model definitions for Fanvil IP phones.

## Overview

This package provides configuration templates used to generate per-phone provisioning files for Fanvil devices. A model registry (`fanvil-model.txt`) defines each supported phone model and points to device configs, firmware, and templates for lines and buttons. A separate panel registry (`fanvil-panel.txt`) defines expansion module types (DSS and Side).

## Conventions

- **Generic device config:** All models use `input_1=fanvil_device_generic.cfg` as the primary device config. Model-specific firmware is specified via the `firmware=` field in each section.
- **Firmware field:** Each model section includes `firmware=<filename>.z` (e.g. `firmware=x301.z`) so the provisioning system knows which firmware to serve for that model.
- **Protocol variable:** All URLs (firmware, contact XML, etc.) use `${PROTO}://` instead of hardcoded `http://` or `https://`, allowing deployments to switch between HTTP and HTTPS without editing templates.

## Model registry: `fanvil-model.txt`

The registry is an INI-style file. Each section is a phone model, keyed by `[fanvil-<model>]` (e.g. `[fanvil-x301]`, `[fanvil-v66]`).

### Section fields

| Field | Description |
|-------|-------------|
| `translationmap` | Translation set (e.g. `fanvil`) |
| `label` | Human-readable model name |
| `lines` | Number of lines (2–20) |
| `firmware` | Firmware filename (e.g. `x301.z`) |
| `check_sync` | SIP Notify check-sync command (e.g. `fanvil-check-cfg`) |
| `phone_template` | Main phone config template |
| `line_template` | Line config template |
| `linekey_template` | Line key template |
| `blf_template` | BLF button template |
| `speeddial_template` | Speed dial template |
| `n_a_template` | Not-assigned key template |
| (others) | Optional: `dnd_template`, `vm_template`, `callpark_template`, `mcpage_template`, `prefix_template`, `record_template` |
| `output` | Output filename pattern (e.g. `${mac}.cfg`) |
| `input_1` | Device config merged into output (typically `fanvil_device_generic.cfg`) |
| `output_1` | Model-specific base config name (e.g. `F0VX30100000.cfg`) |
| `input_2`, `output_2` | Optional: second device config and output for model variant (e.g. X6U / X6U-V2) |
| `command_1` | Post-process command (e.g. `generate_compdir_fanvil.py ${TENANT}` or `${TENANT} ${TENANT}`) |

Templates are merged with variable substitution (e.g. `${mac}`, `${SERVER}`, `${PROTO}`, `${HTTP_USER}`, `${HTTP_PASSWORD}`, `${TENANT}`).

### Variables

| Variable | Description |
|----------|-------------|
| `${mac}` | Device MAC address |
| `${SERVER}` | Provisioning server hostname or IP |
| `${PROTO}` | Protocol scheme (`http`, `https`, or `ftp`) – used for firmware URLs and contact XML URLs so deployment can switch between HTTP and HTTPS |
| `${HTTP_USER}` | HTTP authentication username |
| `${HTTP_PASSWORD}` | HTTP authentication password |
| `${TENANT}` | Tenant identifier |

## Panel registry: `fanvil-panel.txt`

Defines expansion module types (DSS and Side panels) with their button and page counts, and template mappings.

| Field | Description |
|-------|-------------|
| `label` | Human-readable panel name |
| `buttons` | Number of buttons |
| `pages` | Number of pages |
| `*_template` | Button templates (blf, dnd, linekey, mcpage, callpark, prefix, speeddial, record, vm) |

## Device configs

All models use `fanvil_device_generic.cfg` as the primary device config (`input_1`). The model registry’s `firmware=` field specifies the firmware filename per model, and the provisioning system injects the correct firmware URL during template merge.

Device configs are XML files that supply:

- Firmware URL for OTA updates (using `${PROTO}` for protocol flexibility)

Example:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<sysConf>
<ota>
<FirmwareUrl>${PROTO}://${SERVER}/provisioning/FIRMWARE-FANVIL/x301.z</FirmwareUrl>
</ota>
</sysConf>
```

- **Protocol:** All URLs use `${PROTO}://` instead of hardcoded `http://` or `https://`, so deployments can choose HTTP or HTTPS.
- **Firmware files:** Served from the `FIRMWARE-FANVIL` directory. Each model’s `firmware=` value in `fanvil-model.txt` names the `.z` file for that model.

## Templates

- **Phone:** `fanvil_phone.cfg`, `fanvil_phone_v6.cfg` (V66 series)
- **Line:** `fanvil_line.cfg`
- **Buttons:** `fanvil_button_*.cfg` (linekey, blf, speeddial, dnd, vm, park, park_bxfer, mcpage, prefix, record, na)
- **DSS (expansion module):** `fanvil_dss_*.cfg` for X5U/X6U/X4U and V66
- **Panels:** `fanvil_panel_dss_*.cfg`, `fanvil_panel_side_*.cfg` for DSS and Side expansion modules

Model sections reference the templates they need via `*_template=` keys. DSS-capable models use `fanvil_dss_*` templates for programmable keys.

## Scripts

### `generate_compdir_fanvil.py`

Called by the provisioning system (see `command_1` in the model registry). Generates or updates the composition directory (XML directory) for the tenant at `/home/PlcmSpIp/CONTACTS/<tenant>/fanvil_compdir.xml`. Accepts one or two tenant arguments depending on model configuration.

## Build

- **Make templates:** `make_templates-fanvil.sh`
- **RPM:** see `rpm/build-fanvil.sh` and `rpm/tl-fanvil-templates.spec`

## File layout (summary)

```text
fanvil-model.txt           # Model registry (sections, template refs, firmware= per model)
fanvil-panel.txt           # Panel registry (DSS, Side expansion modules)
fanvil_device_generic.cfg  # Generic device config (used by all models via input_1)
fanvil_device_*.cfg        # Legacy device-specific configs (firmware URL); used by input_2 for variants
fanvil_phone*.cfg          # Phone templates
fanvil_line.cfg            # Line template
fanvil_button_*.cfg        # Button templates
fanvil_dss_*.cfg           # DSS expansion module button templates
fanvil_panel_*.cfg         # Panel templates (DSS, Side)
generate_compdir_fanvil.py
make_templates-fanvil.sh
rpm/                       # RPM build
docs/                      # This documentation
```
