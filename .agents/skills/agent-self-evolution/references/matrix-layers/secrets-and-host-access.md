# Layer — secrets and host access

## MUST

1. Classify secrets: general → holding-general-secrets (SOPS); product → product SOPS (`sops-age-secrets`).
2. Before asking the founder for a password, search `~/.config/risegen/**/secrets.env` and project SOPS decrypt paths for `*_PASSWORD`, `*_TOKEN`, `HOST_SUDO_*`.
3. Prefer `ssh` BatchMode + key, then `sudo -S` with env secret — never print the secret into evidence.
4. **Read back the acting principal before designing any control around "who".** A credential's
   reputation (MFA, hardware-backed, human-held) describes a class, not the principal the local
   tooling is presenting right now. Probe it: the authenticated user of each CLI in play, the
   accounts that can reach the host, the members with write access. A control that separates
   "the human" from "the agent" is void wherever both act under one identity — and an agent
   running on an operator's workstation usually inherits that operator's tokens by default.
5. **A separate machine identity is what makes an approval gate real.** Where agents must open
   changes and a human must approve them, the agent needs its own credential; otherwise the
   human is the author of the agent's work and cannot approve it, and any signal the agent can
   produce is a signal it can forge.

## NEVER

- Commit `age.key`, plaintext `secrets.env`, or tokens.
- Block a mandatory security task only because interactive sudo failed once without trying documented secrets.
