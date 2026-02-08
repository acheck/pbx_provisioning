# pbx_provisioning — Documentation

This project holds **documentation and derived data** for phone provisioning: pbx_manager’s config generation and DB/config reference, plus output patterns from vendor template bundles.

---

## Contents

| Document | Description |
|----------|-------------|
| [README.md](README.md) | This overview and doc index. |
| [provisioning-tree.md](provisioning-tree.md) | Structure of the **provisioning/** tree: vendor folders, model files, templates, and per-vendor summary. |
| [phone-config-and-provisioning-templates.md](phone-config-and-provisioning-templates.md) | How pbx_manager generates phone config and uses templates (models, process_template, %vars, provision_device flow, DB phone templates, template bundles). |
| [database-and-config-for-provisioning.md](database-and-config-for-provisioning.md) | Database tables and config/settings used for provisioning (devices, phone_templates, provisioning_maps, tenants, servers, sip_users, user_extensions, ast_provisioning, paths). |
| [output-patterns.md](output-patterns.md) | Unique `output` patterns from vendor model files and how they map to vendors. |

---

## Project layout

```
pbx_provisioning/
├── README.md
├── refresh-output-patterns.sh
├── unique-output-patterns.txt
├── provisioning/          # Vendor template bundles (tl-*-templates)
└── docs/
    ├── README.md
    ├── provisioning-tree.md
    ├── phone-config-and-provisioning-templates.md
    ├── database-and-config-for-provisioning.md
    └── output-patterns.md
```

---

## Data sources

- **Vendor output patterns** — Extracted from this project's `provisioning/` (tl-*-templates, *model*.txt and other model `.txt` files). See [output-patterns.md](output-patterns.md) and `../unique-output-patterns.txt`.
- **pbx_manager behavior** — Documented from `/home/acheck/pbx_manager/server` (ast-lib-funcs.pl, json-funcs.pl, ast-db-defs.pl, provisioning/). See the two docs above.

---

## Regenerating unique output list

To rebuild **`unique-output-patterns.txt`** from the provisioning tree:

1. From this project's `provisioning/` directory, find all `.txt` files that contain `output=` in model sections (vendor model files and `models.d/*.txt`).
2. Extract every line matching `output=<value>`.
3. Deduplicate and sort the values.
4. Write one pattern per line to `unique-output-patterns.txt`.
