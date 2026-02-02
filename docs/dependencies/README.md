# Dependencies (source registry)

## Role in the ecosystem

This repository is the authoritative implementation for dependency tracking. The Digital Twin repository is the public, non-authoritative portal for inspection and governance.

This folder records upstream data sources referenced by the Digital Twin (DT)
Dependencies page, without embedding upstream content in this repository.

## Compatibility note

Some code paths referenced by the DT are preserved as *compatibility shims* in
this repository snapshot. See [docs/architecture/dependency_register.md](../architecture/dependency_register.md)
for “used by” path preservation.

## See also

- [README.md](../../README.md)
- [docs/governance/roles_and_workflow.md](../governance/roles_and_workflow.md)
- https://github.com/GeorgeMadlis/eudr-dmi-gil-digital-twin
