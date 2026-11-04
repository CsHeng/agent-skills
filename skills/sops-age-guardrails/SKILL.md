---
name: sops-age-guardrails
description: "Use for SOPS/age secret editing and review: .sops.yaml creation_rules, encrypted_regex/unencrypted_regex, age recipients and identity environment boundaries, avoiding whole-file encryption, decrypt/edit/re-encrypt workflows, and repo-local secret placement."
---

# SOPS Age Guardrails

Edit SOPS-managed files with age recipients so that only secret keys are encrypted and no private identity reaches tracked files.

## Workflow

1. Read the nearest `.sops.yaml` before editing encrypted files, and confirm the path matches a `creation_rules.path_regex` entry.
2. Before `sops -e -i`, confirm a narrow `encrypted_regex`, `encrypted_suffix` or `unencrypted_regex` rule limits encryption to secret keys such as `secrets`, `data` or `stringData`, and keep operational metadata plaintext.
3. Write only through SOPS read, edit and encrypt commands.
4. Verify the diff keeps non-secret metadata readable and shows no broad ciphertext churn outside the intended secret subtree.
5. Read a single secret with `sops -d --extract`, which keeps the rest of the file out of logs and shell history.
6. Fix a MAC mismatch by re-saving the final plaintext through SOPS.
7. Keep `.sops.yaml` tracked with public recipients and path rules, and supply age identities through the caller environment, ignored local config, or CI secret surfaces. Age identity paths live only there.

## Commands

```bash
sops -d --extract '["secrets"]["KEY"]' path/to/file.yml
sops path/to/file.yml
sops -e -i path/to/file.yml
sops updatekeys path/to/file.yml   # rotate recipients after a `.sops.yaml` recipient change
```
