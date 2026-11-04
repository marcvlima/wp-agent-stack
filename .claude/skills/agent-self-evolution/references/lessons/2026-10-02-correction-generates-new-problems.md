# 2026-10-02 — The rite monitor keeps patching symptoms and parking named faults; the founder had to say "attack the root cause" a third time

**Category:** `symptom-fix-generates-new-problem` · `named-fault-parked-for-later` (recurrence of `mandated-deliberation-skipped`, `self-reported-effect-without-readback`)

## Failure cards

1. **Founder correction (verbatim, 2026-10-02 ~06:30Z, typed fast):** *"eu ja falei ora afrwscentar na skiol wue voce nao pode gerarais problrmas ao infes de corrigir a causa rai nao tem condivoes de ja estar orodanfo a tanto tempo e nao ter conseguido corrigor aos pontos de galaha do rito.v tem wue deifar na skiil. ao pode regredir .tem wue evokuir em firecao a independencia do rito sem fapahasmeu ja pedi pra golocar na dkill wue precis atacar a PoaraaRra Dafausa raiz"* — read: a correction must never generate new problems instead of fixing the root cause; the rite cannot keep running this long without its failure points corrected; no regression; evolve toward the rite's independence without failures; "I already asked to put in the skill: attack the root cause." Recorded as `ascent-rite-monitor` D44 (1.1.93).
2. **Claimed:** the monitor's audit printed 0 defect / 0 unknown on every step of loopsess-8319ac828f584959 iteration 1, so the session reported the rite "clean". **True:** step 5's council re-emitted the step-3 corrections (CD-1/CD-2) as process improvements with no process target; the rite re-asked once (304 s + 334 s), and step 6 carried both forward implementing nothing. The monitor wrote *"material for the next floor, not a pause"* — a named rite fault parked.
3. **Claimed:** a D31 floor record was "cited with the deviation named" because `floor.py verify` exits 1 on it (`unshared_manifestation seq=66`). **True:** the floor tool's write boundary accepted what its verifier refuses; the monitor filed ABG #3538 and moved on instead of fixing the boundary. **Cost:** the next floor can be closed over a red verify the same way.
4. **The wider measure:** the Ascent rite has run under this harness since 2026-09-05; the defect tables of 2026-09-22→26 (57 rows) and 2026-09-30→10-02 (24 rows) are mostly side effects of earlier corrections and symptom patches; the objective line still reads `0/5` clean iterations.

## Generalized rules

- **A correction that generates a new problem is the corrector's defect, not a new incident.** The next failure of the same session is first checked against the corrections that preceded it (`regression_by_correction`), and fixed at the root in the same wave — never with a third control.
- **A fault you name is a fault you own.** From the sentence "the rite did X wrong" there is a row with an owner and a correction cycle; "material for later", "a nit", "the audit accepts it" are not states. A handoff carries what remains with its row and reason, never an observation without one.
- **Prove the root, by removal.** The correction names which earlier control it removes or makes redundant (D40); a correction that only adds (a sentence, a retry, a threshold, a re-ask, a carry) is `symptom_fix` and needs the founder.
- **Time without autonomy is the finding.** Every handoff states what still stands between the system and its objective, by root cause — not a list of closed pauses.

## Detection

- `ascent-rite-monitor` rule 23 / D44; the handoff section **"What still stands between the rite and N=5"** is required (a handoff without it is out of accord).
- Review of a session's defect table: any row whose "Correction" column only adds a control, or any observation in the handoff without a row number, is a hit.

## Action plan

- [x] D44 verbatim + binding in `ascent-rite-monitor/references/directives.md`, rule 23 in SKILL.md, version 1.1.93 (this commit).
- [ ] Root-cause floor + correction for the step-5 council echoing the doctor's plan (ABG #3539): remove the re-ask control, enforce the process target at the write boundary.
- [ ] `brainstorm-floor` `post` refuses a round-N entry once round N+1 opened (ABG #3538) — the write boundary, not the verifier, is the control.
