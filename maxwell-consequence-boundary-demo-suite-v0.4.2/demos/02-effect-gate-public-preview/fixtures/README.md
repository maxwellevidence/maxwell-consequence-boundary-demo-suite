# Demo Fixtures

**Important: the private keys in this folder are intentionally public demo material.**

They are committed so reviewers can run the proof locally without external key
custody, Auth0, Okta, Entra ID, Google, Keycloak, or production signing
infrastructure.

They are not leaked secrets. They are not production secrets. They are not
external custody material. They are not an enforceable non-reuse control. Treat
anything signed by these keys as authenticated only for this local proof and
unauthenticated outside it.

Files:

- `manifest_demo_private_key.pem` signs local artifact manifests for the runnable proof.
- `oidc_demo_issuer_private_key.pem` signs demo OIDC tokens.
- `oidc_demo_issuer_public_key.pem` is the demo issuer public key used by the validator.

The manifest verifier trusts the repo-root `MANIFEST_PUBLIC_KEY.pem`, not any key
written beside generated artifacts. Manifest verification assumes that the
repo-root public key has not itself been replaced.
