# TF Motif & Binding Site Databases — File List

Reference motif and TFBS resources for GRN inference or motif analysis.
Base path: `/vol/projects/jnourisa/genernbi/resources/supp_data/databases/`

- `granie/H12INVIVO/` — HOCOMOCO v12 H12INVIVO per-TF TFBS `.bed.gz` files (948 TFs, 1,442 files)
- `granie/PWMScan_HOCOMOCOv12_H12INVIVO.tar.gz` — PWMScan archive for the full HOCOMOCO v12 H12INVIVO motif set
- `celloracle/gimme.vertebrate.v5.0.pfm` — GIMME vertebrate v5.0 motif PFM database

- `scenicplus/db.regions_vs_motifs.rankings.feather` — cisTarget region-vs-motif rankings (feather)
- `scenicplus/db.regions_vs_motifs.scores.feather` — cisTarget region-vs-motif scores (feather)
- `scenicplus/motifs-v10-nr.hgnc-m0.00001-o0.0.tbl` — motif-to-TF annotation table (strict threshold, 1e-5)
- `scenicplus/hg38-blacklist.v2.bed` — ENCODE hg38 blacklist regions v2

- `scenic/hg38_10kbp_up_10kbp_down_full_tx_v10_clust.genes_vs_motifs.rankings.feather` — gene-vs-motif rankings, ±10 kb window
- `scenic/hg38_500bp_up_100bp_down_full_tx_v10_clust.genes_vs_motifs.rankings.feather` — gene-vs-motif rankings, 500 bp up / 100 bp down window
- `scenic/motifs-v10nr_clust-nr.hgnc-m0.001-o0.0.tbl` — motif-to-TF annotation table (relaxed threshold, 1e-3)

- `scglue/JASPAR2022-hg38.bed.gz` — JASPAR2022 TF motif hits on hg38
- `scglue/ENCODE-TF-ChIP-hg38.bed.gz` — ENCODE TF ChIP-seq peaks on hg38
