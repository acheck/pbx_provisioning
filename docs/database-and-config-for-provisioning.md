# Database and Config Objects Used for Phone Provisioning

This document lists **database tables** and **config/settings objects** that pbx_manager uses when generating phone config files and running provisioning (see `pbx_manager/server`, mainly `ast-lib-funcs.pl` and `json-funcs.pl`).

---

## 1. Database Tables

### 1.1 Devices (per-phone provisioning data)

| Table | Purpose | Key columns (provisioning-relevant) |
|-------|---------|-------------------------------------|
| **devices** | One row per physical phone. | `mac`, `serial_number`, `tenantid`, `model`, `description`, `tag`, `panel`, `accounts` (JSON: line/account assignments), `buttons` (JSON: BLF/speeddial/etc.), `variables` (JSON: map category/original for translation), `override` (raw config snippet), `tz` |
| **device_buttons** | Optional normalized button definitions per device. | `device_id`, `type`, `line`, `label`, `value`, `line_keys`, `account` |
| **device_variables** | Optional per-device variable overrides (category/original for provisioning_maps). | `device_id`, `category`, `original` |

- **devices** is the main source for MAC, model, accounts, buttons, variables, override, and timezone when `provision_device` runs.
- **device_db_config**, **device_button_db_config**, **device_variables_db_config** in `ast-db-defs.pl`.

---

### 1.2 Phone templates (extended templates)

| Table | Purpose | Key columns |
|-------|---------|-------------|
| **phone_templates** | Custom "model" that maps to a base model + overrides. | `name`, `tenantid`, `model` (base model, e.g. snom-320), `description`, `buttons` (JSON), `override` (text), `tz` |
| **phone_templates_buttons** | Default button layout for the template. | `phone_template_id`, `type`, `line`, `label`, `value`, `account` |
| **phone_templates_variables** | Default variable mappings for the template. | `phone_template_id`, `category`, `name`, `original` |

- When a device's `model` is not in `models.txt`, it is resolved via **get_phone_template(name, tenant)** from these tables; the template's `model` is then used for the actual provisioning model.
- **phone_template_db_config**, **phone_template_button_db_config**, **phone_template_variables_db_config** in `ast-db-defs.pl`.

---

### 1.3 Provisioning maps (translation / timezone)

| Table | Purpose | Key columns |
|-------|---------|-------------|
| **provisioning_maps** | Maps "original" values to "replacement" per category (e.g. timezone, vendor-specific). | `name` (map name, e.g. from model's `translationmap`), `category`, `description`, `original`, `replacement` |

- **load_provisioning_maps()** loads all rows; structure is `$map->{name}->{category}->{original} = replacement`.
- Used for timezone (`tz` → `TL_TIMEZONE`) and for device/template variables (category/original → replacement) during provisioning.
- **provisioning_maps_db_config** in `ast-db-defs.pl`.

---

### 1.4 Tenant and server (provisioning URLs and timezone)

| Table | Purpose | Key columns (provisioning-relevant) |
|-------|---------|-------------------------------------|
| **tenants** | Tenant settings; used for primary/secondary server and default timezone. | `id`, `tenant`, `primary_server` (server id or 'self'), `secondary_server`, `tz` |
| **servers** | Server hostnames/IPs for provisioning URLs. | `id`, `host` (or `internal_ip`) |

- **get_tenant($current_tenant_name)** is used in **provision_devices**; if `primary_server` / `secondary_server` are not 'self', **get_server()** is called to get host and set `PRIMARY_SERVER` / `SECONDARY_SERVER` in template vars.
- Tenant `tz` is used as default device timezone when device `tz` is not set.

---

### 1.5 Phones and users (line/account data for templates)

| Table | Purpose | Key columns (provisioning-relevant) |
|-------|---------|-------------------------------------|
| **sip_users** | SIP credentials and peer config; **list_phones()** reads SIP peers (by tenant). | `name`, `secret`, `callerid`, `host`, `context`, `nat`, etc. |
| **user_extensions** | Extension/user record (name, phones, callerid, etc.). | `id`, `tenantid`, `name`, `ext`, `phones`, `first_name`, `last_name`, `ext_callerid`, `mailbox`, etc. |
| **user_settings** | Per-user call settings (optional for provisioning). | `user_id`, call forwarding, recording, etc. |

- **list_phones()** uses the SIP DB config (e.g. **sip_phone_db_config** → `sip_users`) filtered by tenant to build the list of peers; provisioning uses this for `USERID`, `PASSWORD`, `callerid`, `SERVER`, etc. per line.
- **list_pbx_users()** uses **user_extensions** (and optionally **user_settings**) to build the user list; provisioning uses it for `DISPLAY_NAME`, `FIRST_NAME`, `LAST_NAME`, `EXTENSION`, etc. per account.

---

### 1.6 Parking (optional template var)

| Table | Purpose | Key columns |
|-------|---------|-------------|
| **parking** (or equivalent) | Call parking config. | `parking_ext` (e.g. 700) |

- **list_parking()** is called in **provision_device**; if present, `parkext` is set and used as `DEFAULT_PARKEXT` in template vars.

---

### 1.7 Panels (BLF / sidecar)

| Table | Purpose | Key columns |
|-------|---------|-------------|
| **panels** | Panel/sidecar model and config per tenant. | `name`, `tenantid`, `model`, `description`, `subpanel_1` … `subpanel_4` (JSON) |

- If a device has a `panel` set, **provision_device** looks up the panel model and processes button templates for subpanels; panel data is merged into template vars for button generation.

---

## 2. Config / Settings Objects

### 2.1 Provisioning settings (ast_provisioning)

| Config key | Storage | Purpose |
|------------|---------|---------|
| **ast_provisioning** | File: `$asterisk_root/provisioning.txt` (path from **location('ast_provisioning')**) | Loaded by **load_settings('ast_provisioning')**; defines protocols, server, directory, and user-defined template variables. |

**Typical keys in the loaded hash:**

| Key | Meaning |
|-----|--------|
| `server` | Provisioning server host (used in templates as `SERVER`). If empty, **get_my_host_address()** is used. |
| `directory` | Output directory for generated config files. At runtime overwritten by **$provisioning_default_dir** (e.g. `/home/PlcmSpIp`). |
| `enable_ftp`, `enable_http`, `enable_https`, `enable_tftp` | Which protocols are enabled (at least one required). |
| `ftp_auth`, `http_auth` | `user:password` for FTP and HTTP/HTTPS; split into `HTTP_USER`/`HTTP_PASSWORD`, `FTP_USER`/`FTP_PASSWORD` in template vars. |
| `var_1` … `var_N`, `value_1` … `value_N` | User-defined template variables (N up to **$max_provisioning_variables**, e.g. 49). Merged into `%vars` in **provision_device**. |

- **save_settings('ast_provisioning', $object)** writes back (e.g. from **updateProvisioningSettingsJSON** in json-funcs.pl).

---

### 2.2 Location keys (paths for templates and models)

Resolved via **location($key)** and **get_file_name()** in ast-lib-funcs.pl. Used for template and model file paths.

| Location key | Typical path | Purpose |
|---------------|--------------|---------|
| **ast_provisioning_directory** | `$asterisk_root/provisioning` | System template directory (e.g. `provisioning/*.cfg`). |
| **ast_user_provisioning_directory** | `$asterisk_root/user_provisioning` | User/tenant override templates. |
| **ast_models** | `$asterisk_root/provisioning/models.txt` | System device model definitions (phone_template, line_template, output, etc.). |
| **ast_user_models** | `$asterisk_root/user_provisioning/models.txt` | User override model definitions. |

- **process_template** looks up template files in: `user_provisioning/$tenant/$file`, then `user_provisioning/$file`, then `provisioning/$file`.
- **list_device_models** reads **ast_models**, **ast_user_models**, and files under `/etc/asterisk/provisioning/models.d/`.

---

### 2.3 Other constants / globals

| Symbol | Value / meaning |
|--------|------------------|
| **$provisioning_default_dir** | `/home/PlcmSpIp` — default output directory for generated configs. |
| **$max_provisioning_variables** | 49 — number of user-defined var/value pairs read from ast_provisioning. |

---

## 3. Flow summary

- **provision_devices** loads **ast_provisioning**, **tenants** (current tenant), **servers** (if primary/secondary_server set), **list_device_models** (from files + **ast_models** / **ast_user_models**), **list_phones** (**sip_users**), **list_pbx_users** (**user_extensions** + **user_settings**), **load_provisioning_maps** (**provisioning_maps**), **list_parking**.
- For each MAC, **provision_device** gets the **devices** row (and optionally **device_buttons** / **device_variables**); if model is an extended template, **phone_templates** (and related) are used; then template vars are built from devices, tenants, servers, sip_users, user_extensions, provisioning_maps, ast_provisioning (server, auth, var_1/value_1…), and optional **panels** and **list_parking**.
- Config files are written under **$provisioning_default_dir**; template files are read from **ast_provisioning_directory** and **ast_user_provisioning_directory** as above.

---

## 4. Reference: ast-db-defs.pl config names

| Config variable | Table |
|-----------------|--------|
| **$device_db_config** | devices |
| **$device_button_db_config** | device_buttons |
| **$device_variables_db_config** | device_variables |
| **$phone_template_db_config** | phone_templates |
| **$phone_template_button_db_config** | phone_templates_buttons |
| **$phone_template_variables_db_config** | phone_templates_variables |
| **$provisioning_maps_db_config** | provisioning_maps |
| **$sip_phone_db_config** | sip_users |

Tenants and servers are accessed via their own helpers (e.g. **get_tenant**, **get_server**); user_extensions/user_settings are used inside **list_pbx_users** / **get_pbx_user**.
