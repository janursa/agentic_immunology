# Target Safety & Druggability — Reference

Methodology for the "Safety & tractability" pillar of disease-implication assessment. Assesses whether a target is **drug-modulatable** (tractability) and whether modulating it is **likely to be safe** (mechanism-based / on-target toxicity risk) — independent of whether it's disease-causal.

---

## Conceptual Framework

**Open Targets tractability buckets** (Open Targets Platform docs; Ochoa et al. 2021). Each target is scored per modality — small molecule, antibody, PROTAC, other — against evidence buckets (clinical precedent > structure with known pocket > predicted pocket > no evidence). Report the bucket per modality, not a single yes/no.

**Genetic constraint as a safety proxy** (gnomAD; Minikel et al. 2024, *Nature*, "Refining the impact of genetic evidence on clinical efficacy"). Loss-of-function-intolerant genes (high pLI / low LOEUF) are more likely to cause adverse effects when inhibited — constraint is a cheap prior for on-target toxicity before any compound exists.

**Essentiality as a safety proxy** (DepMap; Hingorani et al. 2019, *Nat Rev Drug Discov*, "genetics-led safety"). Pan-essential genes (broad CRISPR dependency across cell lines) flag mechanism-based toxicity risk in normal tissue, not just tumor cells.

**Open Targets safety liabilities** — literature/regulatory-curated target-level adverse effects (organ toxicity, withdrawn programs) attached to the target in the Platform API. This is the most direct "has this exact target caused trouble before" signal, when available.

**Tissue specificity** (GTEx / Open Targets baseline expression) — broad, high essential-organ expression (heart, liver, CNS) raises on-target toxicity concern relative to a tissue-restricted target.

These are independent axes — score each, don't average them into one number. A target can be highly tractable (existing approved drug) and high-risk (essential, broadly expressed), or the reverse.

---

## Tools

- [`tools/ciim/genetics.md`](../tools/ciim/genetics.md) — `query_opentarget_platform(query, variables)`: raw GraphQL against Platform API v4. Use for `tractability`, `safetyLiabilities`, `knownDrugs`, and baseline `expressions` fields on the `target` type.
- [`tools/biomni/database_biomni.md`](../tools/biomni/database_biomni.md) — `query_gnomad` (constraint/LoF intolerance), `query_chembl` (precedented ligands/clinical-phase chemistry), `query_gtopdb` (pharmacology family, known ligands), `query_clinicaltrials` (clinical precedent for the target/mechanism), `query_pdb` / `query_alphafold` (structure for pocket assessment).
- [`tools/biomni/pharmacology_biomni.md`](../tools/biomni/pharmacology_biomni.md) — `predict_admet_properties`, `calculate_physicochemical_properties`, `predict_binding_affinity_protein_1d_sequence` (once a candidate chemical series exists — usually not needed for target-level scoring), `query_fda_adverse_events`, `check_fda_drug_recalls`, `analyze_fda_safety_signals`, `query_drug_interactions` (clinical safety of an *existing* drug against the target, not the target itself).
- DepMap essentiality has no local query tool — use `WebSearch`/`WebFetch` against the DepMap portal as a targeted grounding check, and state it's a literature lookup, not a local query.

Always prefer these existing tools over reimplementing methods yourself.

## Image selection

| Step | Image |
|---|---|
| `query_opentarget_platform`, `get_disease_credible_sets` | `ciim.sif` |
| `query_gnomad`, `query_chembl`, `query_gtopdb`, `query_clinicaltrials`, `query_pdb`, `query_alphafold` | `biomni_full.sif` |
| `predict_admet_properties`, FDA/DDI safety functions | `biomni_full.sif` |

---

## Workflow

### 1. Tractability
Query Open Targets Platform for the target's modality buckets:
```python
import sys; sys.path.insert(0, 'agentic_immunology/tools/ciim/code')
from genetics import query_opentarget_platform

q = '''query Tractability($ensemblId: String!) {
  target(ensemblId: $ensemblId) {
    approvedSymbol
    tractability { label modality value }
    knownDrugs(size: 10) { rows { drug { name } phase mechanismOfAction } }
  }
}'''
result = query_opentarget_platform(q, variables={"ensemblId": "ENSG00000XXXXXX"})
```
Report the bucket per modality (small molecule / antibody / PROTAC / other) and list any drug already in clinical use against the target (`knownDrugs`) — existing clinical precedent is the strongest tractability signal.

Cross-check precedented chemistry with `query_chembl(molecule_name=..., chembl_id=...)` or `query_gtopdb` for known ligands/pharmacology family if Open Targets shows no known drugs but the target is a classic druggable family member (GPCR, kinase, ion channel, nuclear receptor).

If no PDB/AlphaFold structure or known ligand exists, state tractability as **low-confidence / structure-based prediction only** — don't imply a drug program is feasible without precedent.

### 2. Genetic constraint
`query_gnomad(prompt=..., gene_symbol=...)` → pLI / LOEUF. High constraint (LoF-intolerant) → flag elevated on-target toxicity risk for inhibition; low constraint → de-risked for LoF-mimicking modalities (antagonists, degraders).

### 3. Essentiality (if relevant — disease context involves normal-tissue toxicity risk)
Targeted DepMap lookup via `WebSearch`/`WebFetch` for pan-essential status. State this as a literature check, not a queried database.

### 4. Safety liabilities & tissue exposure
Same `query_opentarget_platform` call, extend with `safetyLiabilities` and `expressions` fields:
```python
q = '''query Safety($ensemblId: String!) {
  target(ensemblId: $ensemblId) {
    safetyLiabilities { event eventId effects { direction dosing } datasource }
    expressions { tissue { label } rna { value } }
  }
}'''
```
Report any curated liability verbatim with its source. Flag broad high-essential-organ expression (heart, liver, CNS) as elevated on-target toxicity concern.

### 5. Clinical safety (only if a specific drug/modality is already in hand, e.g. drug repurposing context)
`query_fda_adverse_events`, `check_fda_drug_recalls`, `analyze_fda_safety_signals`, `query_drug_interactions` — these assess a *compound's* safety record, not the target's. Use when this knowhow is invoked as part of a drug repurposing assessment; skip for target-level-only assessments.

### 6. Integrate
Report tractability and safety as two separate statements, not a merged score:
- **Tractability**: best modality bucket + precedent (existing drugs, known ligands, structure availability).
- **Safety**: constraint, essentiality (if checked), curated liabilities, tissue exposure — and which of these were silent (no data) vs. genuinely reassuring (checked, clean).

Name explicitly which checks were skipped and why (e.g. no structure available, DepMap lookup not performed because toxicity-in-normal-tissue wasn't in scope).
