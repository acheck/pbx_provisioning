# pbx_provisioning

Documentation and derived data for **pbx_manager** phone config generation, provisioning templates, and vendor output patterns.

## Contents

- **`provisioning/`** — Vendor template bundles (tl-*-templates; model files with `output=`).
- **`unique-output-patterns.txt`** — Sorted list of unique `output` filename patterns from `provisioning/`. Regenerate with **`./refresh-output-patterns.sh`**.
- **`docs/`** — Project documentation.
  - [docs/README.md](docs/README.md) — Doc index, layout, data sources.
  - [docs/provisioning-tree.md](docs/provisioning-tree.md) — Structure of the **provisioning/** tree (vendor folders, model files, templates).
  - [docs/phone-config-and-provisioning-templates.md](docs/phone-config-and-provisioning-templates.md) — How phone config files and provisioning templates are generated (models, templates, variables, `provision_device` flow, DB phone templates, template bundles).
  - [docs/database-and-config-for-provisioning.md](docs/database-and-config-for-provisioning.md) — Database tables and config objects used for phone provisioning (devices, phone_templates, provisioning_maps, tenants, servers, sip_users, user_extensions, ast_provisioning, paths).
  - [docs/output-patterns.md](docs/output-patterns.md) — Output patterns from vendor model files with vendor and file reference.

## Related paths

- **pbx_manager** — `/home/acheck/pbx_manager/server` (ast-lib-funcs.pl, json-funcs.pl, ast-db-defs.pl, provisioning/).
- **Vendor template bundles** — `provisioning/` in this project (tl-*-templates, model files with `output=`).
