# tl-yealink-templates documentation

Provisioning templates and model definitions for Yealink IP phones.

## Overview

This package provides configuration templates used to generate per-phone provisioning files for Yealink devices. A model registry (`yealink_model.txt`) defines each supported phone model and points to device configs, firmware, and templates for lines and buttons.

## Model registry: `yealink_model.txt`

The registry is an INI-style file. Each section is a phone model, keyed by `[yealink-<model>]` (e.g. `[yealink-cp860]`, `[yealink-w70b]`).

### Section fields

| Field | Description |
|-------|-------------|
| `translationmap` | Translation set (e.g. `yealink`) |
| `label` | Human-readable model name |
| `lines` | Number of lines (1–16) |
| `firmware` | Firmware filename (e.g. `W70B-146.85.0.40.rom`) |
| `phone_template` | Main phone config template |
| `line_template` | Line config template |
| `linekey_template` | Line key template |
| `blf_template` | BLF button template |
| `speeddial_template` | Speed dial template |
| `n_a_template` | Not-assigned key template |
| (others) | Optional: `dnd_template`, `vm_template`, `callpark_template`, etc. |
| `output` | Output filename pattern (e.g. `${mac}.cfg`) |
| `input_1` | Device config merged into output (e.g. `yealink_device_generic.cfg`) |
| `output_1` | Model-specific base config name (e.g. `y000000000146.cfg`) |
| `command_1` | Post-process command (e.g. `generate_compdir_yealink.py`) |

Templates are merged with variable substitution (e.g. `${mac}`, `${SERVER}`, `${HTTP_USER}`, `${HTTP_PASSWORD}`, `${TENANT}`).

## Device configs

Device configs (e.g. `yealink_device_w70b.cfg`, or the generic `yealink_device_generic.cfg`) supply:

- Provisioning server URL
- Optional `firmware.url` (full URL to the `.rom` file)

Example:

```text
#!version:1.0.0.1
auto_provision.server.url = http://${HTTP_USER}:${HTTP_PASSWORD}@${SERVER}/provisioning
auto_provision.server.username = ${HTTP_USER}
firmware.url = http://${HTTP_USER}:${HTTP_PASSWORD}@${SERVER}/provisioning/FIRMWARE-YEALINK/W70B-146.85.0.40.rom
```

The filename at the end of `firmware.url` is the value used for the `firmware=` field in the model registry.

## Templates

- **Phone:** `yealink_phone.cfg`, `yealink_phone_70.cfg`, `yealink_phone_73.cfg`
- **Line:** `yealink_line.cfg`, `yealink_line_dect.cfg`
- **Buttons:** `yealink_button_*.cfg` (linekey, blf, speeddial, dnd, vm, park, etc.)
- **Panels:** `yealink_panel_*.cfg` for expansion modules

Model sections reference the templates they need via `*_template=` keys.

## Scripts

### `add_firmware_to_model.py`

Updates `yealink_model.txt` with a `firmware=` line in each section:

1. For each section, reads the file named in `input_1`.
2. Finds a line `firmware.url = .../FILENAME.rom` and takes `FILENAME.rom`.
3. Inserts `firmware=FILENAME.rom` after the `lines=N` line in that section.

Run from the project root:

```bash
python3 add_firmware_to_model.py
```

Sections whose `input_1` file has no `firmware.url` are left unchanged.

### `generate_compdir_yealink.py`

Called by the provisioning system (see `command_1` in the model registry). Generates or updates the composition directory for the tenant.

## Build

- **Make templates:** `make_templates-yealink.sh`
- **RPM:** see `rpm/build-yealink.sh` and `rpm/tl-yealink-templates.spec`

## File layout (summary)

```text
yealink_model.txt          # Model registry (sections and template refs)
yealink_device_*.cfg      # Device-specific or generic device config
yealink_phone*.cfg        # Phone templates
yealink_line*.cfg         # Line templates
yealink_button_*.cfg      # Button templates
yealink_panel_*.cfg       # Panel templates
yealink_console_unit*.cfg # Console unit configs
add_firmware_to_model.py  # Sync firmware= from device configs
generate_compdir_yealink.py
make_templates-yealink.sh
rpm/                      # RPM build
docs/                     # This documentation
```
