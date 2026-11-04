# The remedy was never probed — evidence spent on the option being rejected

## Category: `asymmetric-verification`

## Failure card

```text
SYMPTOM: The founder could not satisfy a gate the agent had just armed on his own
         repository: "está exigindo um aprovador e eu não sirvo". The main branch
         carried a required review that no human could clear.
CLAIMED: A control was rejected on evidence — "a key the assistant can read does not
         bind the assistant" — and replaced by an identity described as "a credential
         the assistant cannot forge, guarded by his second factor".
TRUE:    The acting CLI was authenticated AS THAT SAME PERSON, with org-admin and repo
         scopes. Every push and every pull request that day was made under that
         identity. The second factor guards interactive login, not the CLI token. The
         replacement was readable by the agent in exactly the way the rejected option
         had been — the identical defect, one paragraph later.
COST:    The claim passed an 11-round architecture council, a written decision record,
         an explicit founder ratification, two merged pull requests, a supersession
         note merged into another repository's own decision record, and armed branch
         protection — before anything tested it. It surfaced by accident, as an
         ergonomics complaint, not by any check.
```

## Root process failure (not just technical bug)

The agent ran the disproving probe for the option it was **eliminating** (it actually
read the secret store, in one command) and ran **no probe at all** for the option it
was **adopting**. Evidence was spent proving a negative and inference was accepted for
the positive.

That asymmetry is the whole failure. It is not carelessness about a fact; it is a
systematic misallocation of scrutiny — the option being discarded is interrogated
because the agent is arguing against it, while the option being recommended rides on
its reputation because the agent is arguing *for* it.

The verification owed was a single command in the same family as the one already run:
*who is this credential, actually?* Nothing about it was hard, slow, or unavailable.

A second, compounding failure: the claim was **load-bearing in a control designed to
prevent unverified claims**. Its own stated premise was that an unverified claim about
a barrier is worse than no claim, because it stops people looking for the other way in.
The claim was exactly that, inside the document that condemned it.

## Rule (MUST / NEVER — generalized, category-level)

- **MUST — a remedy is owed the evidence its predecessor was denied.** When one control
  is rejected on measured grounds and another is adopted in its place, the replacement
  carries the **same class of probe, run before the decision is written down**. An
  option eliminated by evidence and an option adopted by reputation is not a comparison;
  it is an argument.
- **MUST — identity is a measurement, never an attribute.** Before relying on "only
  <principal> can do this", read back **who the acting credential actually is** in the
  environment that will act. Reputation of a credential class (hardware-backed, MFA,
  human-held) says nothing about which principal the local tooling is currently
  presenting.
- **NEVER — a control may not be armed on an untested assent path.** Prove the intended
  approver can actually clear the gate before it becomes required; an unsatisfiable gate
  is an outage wearing the costume of security.

## Detection (how the next agent notices the category)

- You are writing "X cannot be forged / cannot be read / only Y can do this" about a
  credential, key, identity or approval, and **no command in the transcript reads that
  property back**. Stop; run one.
- A decision record contains both "rejected because measured" and "adopted because
  <property>". The asymmetry between those two verbs is the signature.
- You are about to make a gate **required**. Ask: has the intended approver cleared this
  exact gate once, in this exact configuration? If not, it is untested.
- Grep your own reasoning for a property inherited from a vendor's marketing (MFA,
  hardware-backed, tamper-proof) standing in for a probe of the local environment.

## Related skills

`research-before-asserting` (the gate this bypassed on the recommended option) ·
`mandatory-soft-skills-for-agents` (evidence over inference, definitively) ·
lesson `2026-08-30-self-reported-effect-without-readback` — the sibling: that one
reported an **effect** from the actor's own success signal; this one reports a
**property** from a credential's reputation. Both are "read the state back
independently", applied to different objects.

## Evidence pointers (no secrets)

- The one-command probe that was never run: read back the authenticated principal of
  the acting CLI (`<cli> api user`), and compare it to the principal the control names.
- The counter-example in the same body of work: two sibling controls in the *same*
  decision were verified empirically before being claimed — a privilege separation
  proved by seven refused bypass attempts, and a self-attestation proved by a live
  tamper-and-restore cycle. Both hold. Only the layer that rested on an assumed identity
  fell, which is the cleanest possible evidence for this rule.
