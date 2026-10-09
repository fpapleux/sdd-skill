# SDD Build, Package and Deployment Approach

- Status: approach agreed 2026-10-09 (see Decisions at the end); implemented through SDD changes on this repository, not by this note.
- Request (operator, 2026-10-08): formalize deployment by software type/platform as part of SDD. Record the approach here first.
- Target guidance (operator, 2026-10-09): the user selects compatible target platforms and agrees the installer format and installation procedure complexity before implementation.
- Principle: specify delivery behavior, build a package once, verify it installed, approve its digest, deploy the same bytes and record recovery evidence.

## What SDD Does Today

- Design: design.md records approach, interfaces and one test command; it has no required build/package/target profile.
- Tasks: scenario-linked tasks drive test-first implementation, including operational behavior when specified.
- Verify: runs tests, audits scenario assertions/red evidence and reports coverage; source verification does not require an installed-package check or a release artifact identity.
- Approval: standard results approval marks the change verified; the current script checks structural verification validity but does not itself bind approval to a package digest or parse a PASS verdict.
- Archive: merges approved requirements/known gaps into capabilities and retains change evidence; it does not build, package, deploy or establish observed live behavior.
- Gap: no release record, deploy phase, package promotion gate or deployment/rollback receipt. A verified/archived change can therefore still be undeployed.

## Proposed SDD Integration

1. Specify: describe observable build, installation, upgrade, failure preservation and recovery requirements when they are in scope. Keep platform/package choices in design, not behavioral requirements. Record delivery as required or N/A with a reason.
2. Design: agree target platforms and acceptable installation complexity with the user; verify OS, architecture and runtime compatibility, then select the delivery profile. Record installer format, supported platform/runtime, build/package commands, dependency policy, installed-package test command, deployment/acceptance/rollback commands and data/config boundaries.
3. Tasks/implement: derive tests from those scenarios. Packaging must be tested for missing assets/dependencies, bad platform/config, corrupt input, interrupted preparation, failed startup and recovery as applicable. Do not add untraced operational steps after approval.
4. Build/package: after implementation, produce a versioned candidate from an identified source revision in an isolated builder. Bind build tools, lockfiles, artifact inventory and SHA-256 to a manifest. A rebuild creates a new candidate; never rebuild at deployment time.
5. Verify: test the completed package installed in a clean target-compatible environment, without developer checkout imports. Retain source scenario/coverage evidence and add package, deployment-rehearsal and rollback evidence required by the profile. Record source revision and exact package digest together.
6. Results approval: approve the verified change and identify the package when one is required. SDD should reject missing/weak verification and stale evidence. This approval establishes a deliverable, not permission to deploy to a live target.
7. Deploy: a proposed separate phase prepares a concrete target/package/configuration plan and rehearsal evidence, then obtains deployment approval bound to those exact inputs. After approval, verify identity and prerequisites before side effects, activate, run live acceptance, and roll back on failure under the approved plan.
8. Archive: retain the current meaning of closing verified specification work. Record release/deployment separately so archive never implies the software is running. Support a release containing several verified/archived changes and several target deployments of the same package.

Proposed commands such as `$sdd build` and `$sdd deploy` do not exist yet. Decide tomorrow whether build/package is a dedicated phase or a required part of verify; keep the contract the same either way.

## Delivery Profiles

Profiles define technique and checks; assurance determines their depth. Do not force every project into the same packaging system or require deployment for a library/documentation change.

- Selection: present appropriate targets and installer choices, recommend the simplest supported procedure, and record the user's selection. Do not infer additional target platforms from the implementation language.
- Compatibility: distinguish build host from installation target. Verify OS/version, architecture, runtime/ABI and host prerequisites; cross-platform output requires an appropriate builder and target validation.
- Output: for host-installed software, deliver a standard installer or native package, not a source archive requiring manual build/install steps. Examples: `.deb` for Debian/Ubuntu, `.rpm` for RPM-based Linux, `.exe` or `.msi` for Windows, `.pkg` for macOS. `dpkg` installs `.deb` packages; it is not a separate artifact format.
- Complexity: agree one-command/interactive/unattended installation, administrator privileges, prerequisite handling, configuration/secrets entry, service startup, upgrades/removal and recovery. Put required manual steps in the agreement; automate the rest.
- Validation: prove the selected installer and agreed procedure on compatible targets, including preservation during upgrade/removal. An internal wheel or tar bundle may be a build input; the user receives the agreed installer.

| Software and target | Package | Activation and recovery |
| --- | --- | --- |
| Python CLI on managed Linux | native package containing wheel/locked dependencies | package-manager install and launcher; restore previous runtime |
| Python service/worker on Linux/systemd | native package containing wheel/dependency bundle and unit | package-manager install; explicit or agreed startup; restore previous release/config/unit |
| Service on container platform | OCI image digest and deployment descriptors | platform rollout/readiness; previous digest/descriptors |
| Static site on storage/CDN | built site/assets and manifest | upload/switch publication; restore previous site |
| Server-rendered web application | production build and locked runtime dependencies | target-specific service activation; previous build |
| Serverless application | platform package/image and infrastructure plan | approved version/alias/plan; compatible previous version |
| Desktop/native application | platform installer and required signing | OS installation/update; previous installer and compatible data |
| Library or documentation | versioned distributable/content artifact | publish only when requested; deployment N/A where appropriate |

Each profile records OS/version, architecture/runtime ABI, builder, package/dependency formats, commands, validation, secrets/config/state ownership, activation, recovery and evidence. Unsupported targets require design clarification rather than guessed commands. Only implement profiles actually needed; start with the first one a real product needs.

## Release Record and Checks

- Storage proposal: specs/releases/<version>/manifest.json plus build, acceptance and deployment evidence. Keep this independent of the active-change pointer; one release may include several changes.
- Identity: version, included change IDs, source commit, previous release and artifact digest; reject mutable/unidentified release inputs.
- Build: exact builder/runtime/tool versions, commands, lockfile digests, package contents and dependency inventory. Build failure cannot publish a successful candidate.
- Integrity: whole-package and file hashes, approved provenance and required notices; exclude secrets/live data/developer caches. Hash checks detect modification, not trusted provenance by themselves.
- Verification: installed-package and required rehearsal results bound to digest/platform; changing package or source invalidates affected evidence/approval. Byte-reproducible rebuilds are a separate tested claim.
- Deployment plan: explicit target, compatible configuration revision/schema, scoped secret references, current deployment, prerequisites, activation, acceptance and rollback triggers. Never place secret values in release evidence.
- Receipt: target, attempted/active package digest, configuration revision, approval source, timestamps, commands, live results and rollback outcome. Failed deployment must remain visibly failed/recovered, never deployed-successful.
- Separation: approval for specification/results/archive is distinct from target deployment. A direct operator instruction to deploy can supply authorization once its concrete scope is identified; do not ask twice for the same authorized action.
- Check/status: report change verification, package readiness and each target's observed deployment separately. Enforce evidence, stale-digest checks and required approvals through sdd.py rather than relying on prose alone.
- Cleanup: retain approved packages/evidence and verified rollback material; remove temporary build/install staging after use without losing recovery inputs or unrelated work.

## Tomorrow's Skill Work

- Add user target/installer/complexity selection to intake/design and persist the agreement; validate compatibility before planning installer implementation.
- Decide minimal phase/record shape and archive semantics before modifying commands; preserve existing archived changes and constitution assurance.
- Extend SKILL.md, overview/format, design/task/verification templates, phase/role instructions and sdd.py checks/status together; add release records/profile schemas only as needed.
- Test SDD guards for missing profiles/commands, corrupt or stale artifacts, missing approval/evidence, failed deployment and rollback status; test backward compatibility and N/A delivery.
- Each product gets its own approved SDD change for its build/package/installer/activation behavior; this note is not implementation approval.
- Start with Python/systemd; add other profiles when a product needs them.

## Decisions (operator, 2026-10-09)

1. **Build and package at release level.** A release bundles one or more
   verified changes. Its candidate package is built once, from an identified
   source revision. That exact package (its digest) is what gets verified
   installed, approved, and deployed. Changes keep verifying source behavior,
   and add packaging scenarios only when they change packaging.
2. **Deployment is its own lifecycle.** It is separate from the change status
   machine, because one package can go to several targets and a failed
   deployment doesn't un-verify a change. Each deployment needs its own
   approval, bound to the exact target, package digest and configuration, and
   leaves a receipt. Archive keeps meaning "spec work closed", and the living
   spec describes **approved** behavior, not what is running somewhere.
3. **Install options are a choice offered to the user, never a fixed rule.**
   In design, the Architect presents the install options that fit the
   software and its targets, with their trade-offs, and recommends the
   simplest. The operator selects one, and the selection is recorded with its
   source. Options include:
   - running from source (prototype only);
   - a language package manager (pip/pipx, npm, cargo…);
   - a native OS package (`.deb`, `.rpm`, `.msi`/`.exe`, `.pkg`, Homebrew,
     winget);
   - a container image;
   - a self-contained binary with an install script;
   - a platform deploy (PaaS, serverless, static hosting).

   Each option states its targets, prerequisites, privileges, upgrade and
   rollback story, and installation complexity. A project may set a default
   preference in its constitution.
4. **Assurance sets delivery depth:**

   | | `prototype` | `internal` | `production` | `critical` |
   | --- | --- | --- | --- | --- |
   | Package | Run from source allowed | The selected install option, built from an identified revision | The same, plus a manifest with digest and dependency inventory (SBOM) | The same, plus signing and build provenance |
   | Verification | Smoke run | Installed-package test | Clean-target install, upgrade and rollback rehearsal | The same, plus reproducible-build check where claimed |

5. **Standards to reuse rather than invent:**
   - SBOM (SPDX or CycloneDX) for the dependency inventory;
   - SLSA-style provenance;
   - explicit data-migration reversibility, because code rollback doesn't
     undo data changes;
   - idempotent install and upgrade.
6. **Results gate gap:** `approve results` must also require the Verifier's
   verdict to be PASS.
7. **SDD develops itself from here.** It uses a pinned tool copy, assurance
   `production`, and requirements limited to script-testable behavior. The
   first change is increment 4 (design depth, `analyze`, `next`) together
   with delivery profiles and install options. Releases and deploy come in
   the next change.
