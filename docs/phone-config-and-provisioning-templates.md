# Phone Config Generation and Provisioning Templates (pbx_manager)

This document describes how **pbx_manager** (at `/home/acheck/pbx_manager/server`) generates phone configuration files and uses provisioning templates.

---

## 1. Overview

- **Config generation** is driven by **device model** and **templates** (`.cfg` and similar files).
- **Templates** use variable substitution: `${VAR}` is replaced by values from a `%vars` hash.
- **Output files** are written to the provisioning directory (default `/home/PlcmSpIp`) and served to phones via FTP/HTTP/HTTPS/TFTP.

---

## 2. Key Paths and Locations

| Purpose | Path / Location |
|--------|------------------|
| **System provisioning templates** | `ast_provisioning_directory` → e.g. `$asterisk_root/provisioning` (server `provisioning/` or `/etc/asterisk/provisioning`) |
| **User/tenant provisioning templates** | `ast_user_provisioning_directory` → e.g. `$asterisk_root/user_provisioning` |
| **System models definition** | `ast_models` → e.g. `$asterisk_root/provisioning/models.txt` |
| **User models override** | `ast_user_models` → e.g. `$asterisk_root/user_provisioning/models.txt` |
| **Extra model packages** | `/etc/asterisk/provisioning/models.d/` (one file per package) |
| **Panel models (BLF, etc.)** | `/etc/asterisk/provisioning/panels.d/` |
| **Output directory** | `provisioning_default_dir` = `/home/PlcmSpIp` (from `ast_provisioning` settings) |

Defined in **ast-lib-funcs.pl** (e.g. `$provisioning_default_dir`, `location('ast_provisioning_directory')`, etc.).

---

## 3. Device Models (models.txt and categories.txt)

### 3.1 Model definition (models.txt)

- **File**: `server/provisioning/models.txt` (and optional user override).
- **Format**: INI-style `[model-name]` sections with key/value pairs.

**Important keys per model:**

| Key | Meaning |
|-----|--------|
| `label` | Human-readable model name (e.g. "Snom 320") |
| `lines` | Number of lines/accounts |
| `phone_template` | Template file for main phone config (e.g. `snom3xx_phone.cfg`) |
| `line_template` | Template file for each line/account (e.g. `snom3xx_line.cfg`) |
| `blf_template` | BLF (Busy Lamp Field) template |
| `speeddial_template` | Speed-dial template |
| `output` | Output filename pattern, e.g. `${MAC}.cfg`, `snom3xx-${MAC}.cfg`, `spa${mac}.cfg` |
| `input_1`, `output_1` | Optional extra template → output file pairs |
| `required_1`, `required_2`, ... | Required static files copied as-is into provisioning directory |
| `command_1`, ... | Optional shell commands run after generating config (e.g. reload script) |

**Example (from models.txt):**

```ini
[snom-320]
label=Snom 320
lines=12
phone_template=snom3xx_phone.cfg
line_template=snom3xx_line.cfg
blf_template=snom3xx_blf.cfg
speeddial_template=snom3xx_speeddial.cfg
output=snom3xx-${MAC}.cfg
input_1=snom3xx_settings.cfg
output_1=snom3xx.cfg
```

### 3.2 Categories (categories.txt)

- **File**: `server/provisioning/categories.txt`.
- **Purpose**: Groups models by vendor; maps category to `conf_file_phone`, `conf_file_line`, etc. (used for reference/UI, not the main generation flow which uses **models.txt**).

### 3.3 Loading models

- **Function**: `list_device_models()` in **ast-lib-funcs.pl**.
- **Logic**:
  1. Load system models from `ast_models` (e.g. `provisioning/models.txt`).
  2. Load user models from `ast_user_models` (overrides).
  3. Load all files under `/etc/asterisk/provisioning/models.d/` via `list_device_models_in_one_file()`.
  4. Merge; user/models.d entries override. Result is cached in `$session{device_models}`.

---

## 4. Template Resolution (process_template)

- **Function**: `process_template( $vars, $model_label, $template_file )` in **ast-lib-funcs.pl**.

**Lookup order for `$template_file`:**

1. Multi-tenant: `$user_template_dir/$current_tenant_name/$template_file`
2. `$user_template_dir/$template_file`
3. `$system_template_dir/$template_file`

Where:

- `$system_template_dir` = `get_file_name( location('ast_provisioning_directory') )`
- `$user_template_dir` = `get_file_name( location('ast_user_provisioning_directory') )`

**Substitution:** The template content is read, then every `${VAR}` is replaced by `$vars->{VAR}`. No other syntax (e.g. conditionals) is applied in this function.

---

## 5. Variable Set (%vars) for Templates

Variables are built in **provision_device** and passed to **process_template** and **process_accounts**.

### 5.1 Global / device-level vars (set once per device)

- **MAC**: `MAC`, `mac` (normalized, with/without colons, case variants).
- **Server**: `SERVER`, optionally `PRIMARY_SERVER`, `SECONDARY_SERVER`.
- **Provisioning auth**: `HTTP_USER`, `HTTP_PASSWORD`, `FTP_USER`, `FTP_PASSWORD`.
- **Tenant**: `TENANT`, `TENANT_ID`.
- **Park**: `DEFAULT_PARKEXT`.
- **Device label**: `LABEL` (device description).
- **Custom/override**: `OVERRIDE` (extended template override + device override).
- **Timezone**: `TL_TIMEZONE`, `TL_TIMEZONE_NAME` (from provisioning_maps if translation map set).
- **Company**: `COMPANY_NAME` (single-tenant from license).
- **Line count**: `LINE_KEYS` = `model{'lines'}`.
- **User-defined**: from `ast_provisioning` settings (`var_1`/`value_1`, …).
- **Extra script**: from `/usr/local/sbin/provisioning_extra` or `provisioning_extra_custom` (JSON output merged into `%vars`).
- **Translation maps**: from DB table `provisioning_maps` by model's `translationmap`; device variables (from `devices.variables` JSON) are translated and added by category.

### 5.2 Per-line vars (set in process_accounts)

For each account/line, **process_accounts** sets (among others):

- `LINE`, `LINE_ZERO_BASED`, `LINE_KEYS`
- `USERID`, `PASSWORD`, `DISPLAY_NAME`, `EXTENSION`
- `FIRST_NAME`, `LAST_NAME`
- `LABEL`, `LINE_LABEL`
- `NAT_MAPPING`, `NAT_KEEPALIVE`
- Global: `STATION_NAME`, `VOICEMAIL_NUMBER`, `USERID`

Then it calls **process_template** with the **line_template**; the result for all lines is concatenated and stored in `$vars{'LINES'}`.

### 5.3 Button vars (process_buttons)

- **process_buttons** uses button type (blf, speeddial, etc.) and model templates (`blf_template`, `speeddial_template`, …).
- For each button it sets type-specific vars (e.g. `BLF_LABEL`, `BLF_TARGET`, `SPEEDDIAL_LABEL`, `SPEEDDIAL_TARGET`) and calls **process_template**.
- Results are appended to the corresponding `%vars` key (e.g. `BLFS`, `SPEEDDIALS`).

---

## 6. Main Generation Flow (provision_device)

**Entry points:** `provision_devices( \@macs )` is called from JSON API (e.g. when user clicks "Provision" or on device save). For each MAC it calls **provision_device**.

**provision_device** (ast-lib-funcs.pl) high-level steps:

1. **Resolve model**
   - Device has `model` (e.g. "snom-320" or an extended phone template name).
   - If `model` is in `list_device_models`, use it.
   - Else treat as **extended phone template**: `get_phone_template( model, tenant )`; take `template->{model}` as real model and merge template's buttons with device buttons.

2. **Build %vars**
   - Set MAC, server, auth, tenant, timezone, override, translation maps, extra script, user-defined vars.
   - Set `LINE_KEYS` from model.
   - Call **process_accounts** to fill `$vars{'LINES'}` (one line_template per account).
   - Call **process_buttons** to fill BLF/speeddial/etc. vars.

3. **Substitute in model keys**
   - Replace `${VAR}` in all keys of `%model` (e.g. in `output`, `output_1`, etc.).

4. **Generate main phone config**
   - `phone = process_template( \%vars, $model{'label'}, $model{'phone_template'} );`
   - Output file: `$settings->{'directory'}/$model{'output'}` (e.g. `/home/PlcmSpIp/snom3xx-${MAC}.cfg`).
   - Write `$phone` to that file.

5. **Required files**
   - For each `required_${i}`: copy from system or user template dir into `$settings->{'directory'}`.

6. **Extra input/output pairs**
   - For each `input_${i}` / `output_${i}`: `buffer = process_template( ..., $model{input_${i}} )`, write to `$settings->{'directory'}/$model{output_${i}}`.

7. **Commands**
   - For each `command_${i}`: substitute vars and run with `system()`.

8. **Reboot**
   - Optionally send SIP NOTIFY or similar to phone (model-dependent).

---

## 7. Phone Templates (DB) and Extended Templates

- **Tables**: `phone_templates`, `phone_templates_buttons`, `phone_templates_variables` (see **ast-db-defs.pl**).
- **Purpose**: "Extended" templates allow a custom name (e.g. "My Snom 320") to map to a base model (e.g. `snom-320`) plus override text and button layout.
- **get_phone_template( name, tenant )**: Returns the DB row for that template name in the tenant.
- In **provision_device**, if the device's `model` is not in `list_device_models`, it is looked up as a phone template; the template's `model` is used for the actual model, and template `override` and `buttons` are merged with the device.

---

## 8. Template Bundles

- **Template bundles** are installable packages (e.g. `.noarch` RPMs) that add or override templates/models.
- **getTemplateBundlesRef** (json-funcs.pl) scans installed packages for a pattern like `tl-*-templates-*.noarch` and returns a list for the UI.
- Bundles typically install files under provisioning directories or `models.d` / `panels.d`, so subsequent `list_device_models` / `list_panel_models` and **process_template** use the new files.

---

## 9. Provisioning Settings (ast_provisioning)

- Stored in config (e.g. `ast_provisioning` → `provisioning.txt` or DB-backed).
- **load_settings('ast_provisioning')** returns:
  - `server`, `directory` (overridden at runtime by `provisioning_default_dir` for output),
  - `enable_ftp`, `enable_http`, `enable_https`, `enable_tftp`,
  - `ftp_auth`, `http_auth`,
  - `var_1`/`value_1`, … for user-defined template variables.
- **get_provisioning_methods** uses the enable_* flags to decide which protocols are available; at least one must be enabled for provisioning to run.

---

## 10. Summary Diagram

```
User triggers provision (UI/API)
        ↓
provision_devices( @macs )
        ↓
For each MAC: provision_device(...)
        ↓
Resolve model (models.txt / phone_templates DB)
        ↓
Build %vars (MAC, server, auth, tenant, tz, override, maps, extra script, user vars)
        ↓
process_accounts → LINES (one line_template per account)
process_buttons  → BLFS, SPEEDDIALS, ...
        ↓
process_template( vars, label, phone_template ) → main config
        ↓
Write to $settings->{'directory'}/$model{'output'}
        ↓
Copy required_* files; generate input_*/output_* pairs; run command_*; reboot if needed
```

---

## 11. Relevant Files (pbx_manager/server)

| File | Role |
|------|------|
| **ast-lib-funcs.pl** | `provision_devices`, `provision_device`, `process_template`, `process_accounts`, `process_buttons`, `list_device_models`, `list_device_models_in_one_file`, `get_phone_template`, `load_provisioning_maps`, locations |
| **ast-db-defs.pl** | `phone_templates`, `phone_templates_buttons`, `phone_templates_variables`, `provisioning_maps` DB configs |
| **json-funcs.pl** | API for devices, phone templates, template bundles; calls `provision_devices` |
| **provisioning/*.cfg** | System templates (e.g. snom3xx_phone.cfg, snom3xx_line.cfg) |
| **provisioning/models.txt** | Model definitions (phone_template, line_template, output, …) |
| **provisioning/categories.txt** | Category → conf_file mapping by vendor |

This describes the logic as implemented in the pbx_manager server codebase.
