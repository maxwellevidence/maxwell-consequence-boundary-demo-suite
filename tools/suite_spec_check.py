from __future__ import annotations
import re, sys
from pathlib import Path
REQUIRED_KEYS={"schema_version","suite_index","suite_name","demo_name","package_name","version","python_package","threat_class","headline","cold_open","core_invariant","consequence_boundary","primary_effect_artifact","primary_no_effect_marker","what_this_stresses","audience","standard_commands","cases","public_boundaries"}
EXPECTED={f"{i:02d}" for i in range(1,11)}
SCHEMA="maxwell-demo-spec-v0.3.2"
SUITE_CHECKER_VERSION="maxwell-suite-spec-check-v0.4.2"
def scalar(text,key):
    m=re.search(rf"(?m)^{re.escape(key)}:\s*(.+?)\s*$",text)
    if not m: return None
    v=m.group(1).strip()
    if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")): v=v[1:-1]
    return v.strip()
def main():
    root=Path(sys.argv[1] if len(sys.argv)>1 else '.').resolve(); specs=sorted(root.glob('demos/*/DEMO_SPEC.yml')); failures=[]; indices={}
    for rel in ['THREAT_MODEL.md','ADVERSARIAL_CORPUS.md','MUTATION_AND_FUZZING.md','RED_TEAM_RULES_OF_ENGAGEMENT.md','ADVERSARIAL_TEST_REPORT.md','DECOY_FAIL_OPEN_REGRESSION_NOTE.md','LAUNCH_CANDIDATE_CHECKLIST.md','GITHUB_CI_AND_DECOY_PROOF.md','README.md','SUITE.md','DEMO_INDEX.md','DEMO_CLAIM_MATRIX.md','PUBLIC_LINKS.md']:
        if not (root/rel).exists(): failures.append(f"Missing suite-level file: {rel}")
    if len(specs)!=10: failures.append(f"Expected 10 demo specs under demos/*/DEMO_SPEC.yml; found {len(specs)}")
    for spec in specs:
        demo_root=spec.parent
        text=spec.read_text(encoding='utf-8'); keys=set(re.findall(r"(?m)^([A-Za-z_][A-Za-z0-9_]*):",text)); missing=sorted(REQUIRED_KEYS-keys)
        if missing: failures.append(f"{spec}: missing keys {missing}")
        if scalar(text,'schema_version')!=SCHEMA: failures.append(f"{spec}: schema_version must be {SCHEMA}")
        idx=scalar(text,'suite_index') or ""
        if not re.fullmatch(r"(?:0[1-9]|10)",idx): failures.append(f"{spec}: invalid suite_index {idx!r}")
        elif idx in indices: failures.append(f"Duplicate suite_index {idx}: {indices[idx]} and {spec}")
        else: indices[idx]=spec
        if scalar(text,'suite_name')!='Maxwell Consequence Boundary Demo Suite': failures.append(f"{spec}: invalid suite_name")
        required_demo_assets = [
            'THREAT_MODEL.md',
            'docs/ADVERSARIAL_REVIEW_NOTES.md',
            'docs/ADVERSARIAL_HARNESS_REPORT.md',
            'examples/adversarial_inputs/README.md',
            'tests/adversarial/test_adversarial_corpus.py',
            'tools/public_package_check.py',
            'tools/public_release_boundary.json',
            'docs/ADVERSARIAL_TEST_REPORT.md',
            'docs/RED_TEAM_RULES_OF_ENGAGEMENT.md',
        ]
        for rel in required_demo_assets:
            if not (demo_root/rel).exists(): failures.append(f"{demo_root}: missing adversarial asset {rel}")
        adv_inputs=list((demo_root/'examples'/'adversarial_inputs').glob('*.json')) if (demo_root/'examples'/'adversarial_inputs').exists() else []
        if len(adv_inputs)<3: failures.append(f"{demo_root}: expected at least 3 adversarial input JSON files; found {len(adv_inputs)}")
        makefile=(demo_root/'Makefile').read_text(encoding='utf-8') if (demo_root/'Makefile').exists() else ''
        if 'adversarial:' not in makefile or 'tests/adversarial' not in makefile: failures.append(f"{demo_root}: Makefile missing adversarial target for tests/adversarial")
        workflow_text='\n'.join(p.read_text(encoding='utf-8') for p in (demo_root/'.github'/'workflows').glob('*.yml')) if (demo_root/'.github'/'workflows').exists() else ''
        if 'make adversarial' not in workflow_text: failures.append(f"{demo_root}: CI workflow does not invoke make adversarial")
        if idx=='02':
            for rel in ['docs/MUTATION_AND_FUZZING.md','tools/gate_mutation_smoke.py','tests/fuzz/test_fail_closed_input_space.py']:
                if not (demo_root/rel).exists(): failures.append(f"{demo_root}: missing v0.3.4 flagship mutation/fuzz asset {rel}")
            makefile=(demo_root/'Makefile').read_text(encoding='utf-8') if (demo_root/'Makefile').exists() else ''
            for target in ['fuzz-quick','mutation-smoke']:
                if target not in makefile: failures.append(f"{demo_root}: Makefile missing {target}")
        makefile_text=(demo_root/'Makefile').read_text(encoding='utf-8') if (demo_root/'Makefile').exists() else ''
        if 'adversarial:' not in makefile_text:
            failures.append(f"{demo_root}: Makefile missing adversarial target")
        workflow_dir = demo_root / '.github' / 'workflows'
        workflow_files = list(workflow_dir.glob('*.yml')) + list(workflow_dir.glob('*.yaml')) if workflow_dir.exists() else []
        workflow_text = '\n'.join(p.read_text(encoding='utf-8') for p in workflow_files)
        if 'make adversarial' not in workflow_text:
            failures.append(f"{demo_root}: CI workflow does not invoke make adversarial")
    if set(indices)!=EXPECTED: failures.append(f"Suite indices must be complete 01-10; found {sorted(indices)}")

    root_makefile = (root / 'Makefile').read_text(encoding='utf-8') if (root / 'Makefile').exists() else ''
    for target in ['ci-full:', 'demo-core-check:', 'demo-run:', 'demo-verify:', 'demo-test:', 'demo-adversarial:', 'decoy-proof:']:
        if target not in root_makefile:
            failures.append(f"Root Makefile missing v0.4.1 target {target}")
    root_workflow_dir = root / '.github' / 'workflows'
    root_workflows = list(root_workflow_dir.glob('*.yml')) + list(root_workflow_dir.glob('*.yaml')) if root_workflow_dir.exists() else []
    root_workflow_text = '\n'.join(p.read_text(encoding='utf-8') for p in root_workflows)
    for required in ['pip install --no-build-isolation -e ".[dev]"', 'make ci-full']:
        if required not in root_workflow_text:
            failures.append(f"Root GitHub workflow missing {required!r}")
    for rel in ['tools/decoy_fail_open_proof.py','reports/decoy_fail_open/README.md','reports/decoy_fail_open/fail_open_patch.diff','reports/decoy_fail_open/expected_failure_log.txt','reports/decoy_fail_open/restored_pass_log.txt','reports/decoy_fail_open/summary.json']:
        if not (root/rel).exists():
            failures.append(f"Missing v0.4.1 decoy proof asset: {rel}")

    public_links = ["https://www.maxwellevidence.com/", "https://www.youtube.com/@MaxwellEvidence"]
    for rel in ["README.md", "SUITE.md", "DEMO_INDEX.md", "PUBLIC_LINKS.md"]:
        f = root / rel
        if f.exists():
            body = f.read_text(encoding="utf-8", errors="replace")
            for link in public_links:
                if link not in body:
                    failures.append(f"{rel} missing public Maxwell Evidence link: {link}")
    for readme in sorted(root.glob("demos/*/README.md")):
        body = readme.read_text(encoding="utf-8", errors="replace")
        for link in public_links:
            if link not in body:
                failures.append(f"{readme}: missing public Maxwell Evidence link: {link}")

    if failures:
        print(f'Suite spec check failed ({SUITE_CHECKER_VERSION}):'); [print('-',f) for f in failures]; return 1
    print(f'Suite spec check passed ({SUITE_CHECKER_VERSION}): 10 DEMO_SPEC.yml files, schema v0.3.2, complete indices 01-10, adversarial assets present, Demo 02 mutation/fuzz assets present, v0.4.0 adversarial harness assets present, v0.4.1 root CI and decoy-proof assets present, v0.4.2 public links present.'); return 0
if __name__=='__main__': raise SystemExit(main())
