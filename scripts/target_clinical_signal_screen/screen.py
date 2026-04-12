from __future__ import annotations

import argparse
import math
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import fisher_exact


DEFAULT_INPUT = Path(
    "/vol/projects/CIIM/agentic_central/datalake/biomni/"
    "broad_repurposing_hub_phase_moa_target_info.parquet"
)


def explode_targets(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for row in df[["pert_iname", "clinical_phase", "label", "target", "disease_area"]].itertuples(
        index=False
    ):
        drug, phase, label, target_str, disease_area = row
        targets = sorted(
            {
                token.strip()
                for token in str(target_str).split("|")
                if token and token.strip() and token.strip().lower() != "none"
            }
        )
        if pd.isna(disease_area):
            disease_areas = []
        else:
            disease_areas = sorted(
                {
                    token.strip()
                    for token in str(disease_area).split("|")
                    if token and token.strip() and token.strip().lower() != "none"
                }
            )
        if not targets:
            continue
        for target in targets:
            rows.append(
                {
                    "pert_iname": drug,
                    "clinical_phase": phase,
                    "label": int(label),
                    "target": target,
                    "disease_areas": tuple(disease_areas),
                }
            )
    return pd.DataFrame(rows).drop_duplicates(["pert_iname", "target"])


def benjamini_hochberg(p_values: pd.Series) -> pd.Series:
    pvals = p_values.to_numpy()
    order = np.argsort(pvals)
    ranks = np.empty(len(pvals), dtype=int)
    ranks[order] = np.arange(1, len(pvals) + 1)
    fdr = pvals * len(pvals) / ranks
    fdr_ordered = np.minimum.accumulate(fdr[order][::-1])[::-1]
    out = np.empty_like(fdr_ordered)
    out[:] = np.clip(fdr_ordered, 0, 1)
    result = np.empty(len(pvals))
    result[order] = out
    return pd.Series(result, index=p_values.index)


def score_targets(df: pd.DataFrame, positive_labels: set[str], negative_labels: set[str]) -> tuple[dict, pd.DataFrame]:
    subset = df[df["clinical_phase"].isin(positive_labels | negative_labels)].copy()
    subset["label"] = np.where(subset["clinical_phase"].isin(positive_labels), 1, 0)
    subset = subset[subset["target"].notna()].copy()

    exploded = explode_targets(subset)
    all_pos = int(subset.loc[subset["label"] == 1, "pert_iname"].nunique())
    all_neg = int(subset.loc[subset["label"] == 0, "pert_iname"].nunique())

    results = []
    for target, group in exploded.groupby("target"):
        pos = int(group.loc[group["label"] == 1, "pert_iname"].nunique())
        neg = int(group.loc[group["label"] == 0, "pert_iname"].nunique())
        a, b, c, d = pos, all_pos - pos, neg, all_neg - neg
        _, p_value = fisher_exact([[a, b], [c, d]], alternative="two-sided")
        log2_or = math.log2(((a + 0.5) * (d + 0.5)) / ((b + 0.5) * (c + 0.5)))
        breadth = len({area for areas in group["disease_areas"] for area in areas})
        results.append(
            {
                "target": target,
                "pos_drugs": pos,
                "neg_drugs": neg,
                "pos_rate": pos / (pos + neg),
                "disease_area_breadth": breadth,
                "log2_or": log2_or,
                "p_value": p_value,
            }
        )

    result_df = pd.DataFrame(results).sort_values(["p_value", "pos_drugs"], ascending=[True, False])
    result_df["fdr"] = benjamini_hochberg(result_df["p_value"])

    summary = {
        "positive": all_pos,
        "negative": all_neg,
        "total_drugs_with_targets": int(subset["pert_iname"].nunique()),
        "unique_targets": int(result_df.shape[0]),
    }
    return summary, result_df


def print_screen(title: str, summary: dict, result_df: pd.DataFrame, min_pos: int = 8, min_neg: int = 3) -> None:
    print(f"\n=== {title} ===")
    print(summary)

    positive = result_df[(result_df["pos_drugs"] >= min_pos) & (result_df["log2_or"] > 0)].sort_values(
        ["fdr", "pos_drugs", "log2_or"], ascending=[True, False, False]
    )
    negative = result_df[(result_df["neg_drugs"] >= min_neg) & (result_df["log2_or"] < 0)].sort_values(
        ["fdr", "neg_drugs", "log2_or"], ascending=[True, False, True]
    )

    cols = ["target", "pos_drugs", "neg_drugs", "disease_area_breadth", "log2_or", "fdr"]
    print("\nTop positive-enriched targets")
    print(positive[cols].head(15).to_string(index=False, float_format=lambda x: f"{x:.3g}"))

    print("\nTop negative-enriched targets")
    print(negative[cols].head(15).to_string(index=False, float_format=lambda x: f"{x:.3g}"))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Screen Broad Repurposing Hub targets against withdrawn drugs.")
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT,
        help="Path to broad_repurposing_hub_phase_moa_target_info.parquet",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    df = pd.read_parquet(args.input)

    launched_summary, launched_df = score_targets(df, {"Launched"}, {"Withdrawn"})
    print_screen("LAUNCHED vs WITHDRAWN", launched_summary, launched_df)

    late_summary, late_df = score_targets(df, {"Launched", "Phase 3"}, {"Withdrawn"})
    print_screen("LAUNCHED/PHASE3 vs WITHDRAWN", late_summary, late_df)


if __name__ == "__main__":
    main()
