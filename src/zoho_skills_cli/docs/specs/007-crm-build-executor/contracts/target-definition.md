# Contract: `target.yaml` (non-secret)

```yaml
data_center: US          # US | AU | EU | IN | CN | JP
accounts_url: https://accounts.zoho.com   # must match data_center [VERIFY per DC]
org_id: "<org id>"
org_name: "<org name>"
edition: Enterprise      # default
allowlist:
  - { data_center: US, org_id: "<sandbox org id>" }
```
Validation: unknown keys rejected; `accounts_url` must match `data_center`; live org info
must equal `org_id`/`org_name` before the first write and at session start; org not on the
allowlist aborts. File contains no secrets and may be committed.
