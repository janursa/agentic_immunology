"""
Retrieve all SLE drug targets from OpenTargets Platform.
Disease ID: MONDO_0007915 (systemic lupus erythematosus)

Outputs:
  sle_drug_targets.csv        full drug × target table
  sle_targets_summary.csv     unique targets with max_phase and drug count
"""

import sys
import os
import json
import requests
import pandas as pd

OUTDIR = '/vol/projects/CIIM/agentic_immunology/temp/sle_drug_targets'
OT_URL = 'https://api.platform.opentargets.org/api/v4/graphql'
SLE_ID = 'MONDO_0007915'

# Phase ordering for sorting
PHASE_ORDER = {
    'APPROVAL': 5,
    'PHASE_4': 4,
    'PHASE_3': 3,
    'PHASE_2': 2,
    'PHASE_1': 1,
    'PHASE_0': 0,
    'UNKNOWN': -1,
}

# ── 1. Query OpenTargets Platform ─────────────────────────────────────────────

QUERY = """
{
  disease(efoId: "MONDO_0007915") {
    name
    drugAndClinicalCandidates {
      count
      rows {
        id
        maxClinicalStage
        drug {
          id
          name
          drugType
          maximumClinicalStage
          mechanismsOfAction {
            rows {
              mechanismOfAction
              actionType
              targetName
              targets { id approvedSymbol approvedName }
            }
          }
        }
        clinicalReports {
          clinicalStage
          phaseFromSource
          trialOverallStatus
          source
          type
        }
      }
    }
  }
}
"""

print("=== Querying OpenTargets Platform for SLE drug-target pairs ===")
r = requests.post(OT_URL, json={'query': QUERY}, timeout=60)
r.raise_for_status()
d = r.json()

disease = d['data']['disease']
drug_rows = disease['drugAndClinicalCandidates']['rows']
total = disease['drugAndClinicalCandidates']['count']
print(f"Disease: {disease['name']}")
print(f"Drugs/candidates returned: {total}")

# ── 2. Flatten into drug × target rows ───────────────────────────────────────

records = []
for row in drug_rows:
    drug = row['drug']
    max_stage_sle = row['maxClinicalStage']

    # Phase of drug specifically in SLE trials (max across clinical reports)
    report_phases = [
        PHASE_ORDER.get(cr['clinicalStage'], -1)
        for cr in (row['clinicalReports'] or [])
    ]
    max_trial_phase = max(report_phases) if report_phases else -1

    # Is approved in any indication
    is_approved_any = drug.get('maximumClinicalStage') == 'APPROVAL'
    # Is approved specifically for SLE
    is_approved_sle = max_stage_sle == 'APPROVAL'

    # Collect trial statuses
    statuses = list({cr['trialOverallStatus'] for cr in (row['clinicalReports'] or []) if cr['trialOverallStatus']})

    # Targets via mechanisms of action
    moa_rows = (drug.get('mechanismsOfAction') or {}).get('rows') or []

    if not moa_rows:
        # Drug with no known MoA target — still record it
        records.append({
            'target_gene':         '',
            'target_name':         '',
            'target_id':           '',
            'drug_name':           drug['name'],
            'drug_id':             drug['id'],
            'drug_type':           drug['drugType'],
            'max_phase_sle':       max_stage_sle,
            'is_approved_sle':     is_approved_sle,
            'is_approved_any':     is_approved_any,
            'moa':                 '',
            'action_type':         '',
            'trial_statuses':      '|'.join(statuses),
        })
    else:
        for moa in moa_rows:
            targets = moa.get('targets') or []
            if not targets:
                targets = [{'id': '', 'approvedSymbol': '', 'approvedName': moa.get('targetName', '')}]
            for tgt in targets:
                records.append({
                    'target_gene':     tgt.get('approvedSymbol', ''),
                    'target_name':     tgt.get('approvedName', moa.get('targetName', '')),
                    'target_id':       tgt.get('id', ''),
                    'drug_name':       drug['name'],
                    'drug_id':         drug['id'],
                    'drug_type':       drug['drugType'],
                    'max_phase_sle':   max_stage_sle,
                    'is_approved_sle': is_approved_sle,
                    'is_approved_any': is_approved_any,
                    'moa':             moa.get('mechanismOfAction', ''),
                    'action_type':     moa.get('actionType', ''),
                    'trial_statuses':  '|'.join(statuses),
                })

df = pd.DataFrame(records)
print(f"\nFlattened drug×target rows: {len(df)}")
print(f"Unique drugs: {df['drug_name'].nunique()}")
print(f"Unique targets: {df[df['target_gene'] != '']['target_gene'].nunique()}")

# Save full table
full_path = os.path.join(OUTDIR, 'sle_drug_targets.csv')
df.to_csv(full_path, index=False)
print(f"\nSaved: {full_path}")

# ── 3. Summary: one row per unique target ─────────────────────────────────────

df_with_targets = df[df['target_gene'] != ''].copy()
df_with_targets['phase_rank'] = df_with_targets['max_phase_sle'].map(lambda x: PHASE_ORDER.get(x, -1))

summary = (
    df_with_targets.groupby(['target_gene', 'target_name', 'target_id'])
    .agg(
        max_phase_sle=('max_phase_sle', lambda x: max(x, key=lambda v: PHASE_ORDER.get(v, -1))),
        n_drugs=('drug_name', 'nunique'),
        drugs=('drug_name', lambda x: '|'.join(sorted(set(x)))),
        approved_in_sle=('is_approved_sle', 'any'),
        approved_any=('is_approved_any', 'any'),
        moas=('moa', lambda x: '|'.join(sorted(set(str(v) for v in x if v)))),
        action_types=('action_type', lambda x: '|'.join(sorted(set(str(v) for v in x if v)))),
    )
    .reset_index()
)
summary['phase_rank'] = summary['max_phase_sle'].map(lambda x: PHASE_ORDER.get(x, -1))
summary = summary.sort_values('phase_rank', ascending=False).drop(columns='phase_rank')

summary_path = os.path.join(OUTDIR, 'sle_targets_summary.csv')
summary.to_csv(summary_path, index=False)
print(f"Saved: {summary_path}")

# ── 4. Print results ──────────────────────────────────────────────────────────

print("\n=== Phase distribution (SLE-specific) ===")
print(df.groupby('max_phase_sle')['drug_name'].nunique().sort_values(ascending=False))

print("\n=== Approved drugs in SLE ===")
approved = df[df['is_approved_sle']].drop_duplicates('drug_name')[['drug_name', 'drug_type', 'target_gene', 'moa']]
print(approved.to_string(index=False))

print(f"\n=== Top targets by phase (unique targets: {len(summary)}) ===")
print(summary[['target_gene', 'target_name', 'max_phase_sle', 'n_drugs', 'approved_in_sle', 'action_types']].head(40).to_string(index=False))
