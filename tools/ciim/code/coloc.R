## coloc.R — Colocalization of a GWAS locus with immune cell eQTLs
##
## ── Mandatory arguments ───────────────────────────────────────────────────────
##   --gene     STR   Gene symbol to colocalize (e.g. IRF5)
##   --chr      INT   Chromosome number
##   --pos      INT   Centre of locus in bp (usually lead-SNP position)
##   --outdir   STR   Output directory (created if absent)
##
## ── Locus arguments ───────────────────────────────────────────────────────────
##   --lead_rsid STR  Lead SNP rsID; used only for regional plots  [default: NA]
##   --window   INT   Window half-width in bp                      [default: 1e6]
##   --susie_n  INT   Top N cell types passed to coloc.susie       [default: 5]
##
## ── GWAS arguments ────────────────────────────────────────────────────────────
##   --gwas_file STR  Path to harmonised GWAS summary stats (.tsv.gz).
##                    Expected columns: hm_chrom, hm_pos, hm_rsid, hm_beta,
##                                      standard_error, p_value, hm_code.
##                    [default: GCST003156 SLE Bentham 2015]
##   --gwas_n   INT   Total GWAS sample size                       [default: 14267]
##   --gwas_s   NUM   Proportion of cases (cc studies).
##                    Ignored when --gwas_type quant.              [default: 0.3645]
##   --gwas_type STR  "cc" (case-control) or "quant" (quantitative)[default: cc]
##
## ── eQTL arguments ────────────────────────────────────────────────────────────
##   --eqtl_dir    STR  Directory holding one eQTL file per cell type.
##                      [default: DICE full_summary_stats/]
##   --eqtl_n      INT  eQTL study sample size                     [default: 91]
##   --eqtl_sdy    NUM  SD of expression (1 = normalised / inverse-normal).
##                      Used as coloc sdY for the eQTL dataset.   [default: 1]
##   --eqtl_format STR  File format for the eQTL directory:
##                        "dice_vcf"    — DICE-style VCF, bgzip-compressed +
##                                        tabix-indexed (see analysis/dice_reindex/),
##                                        INFO tags (Gene=;GeneSymbol=;Beta=;
##                                        Statistic=;Pvalue=). Looks for
##                                        {cell_type}.vcf.bgz + .tbi in --eqtl_dir.
##                        "generic_tsv" — tab-separated file per cell type;
##                                        use --col_* to map column names
##                      [default: dice_vcf]
##
## ── generic_tsv column-name overrides ─────────────────────────────────────────
##   (only used when --eqtl_format generic_tsv)
##   --col_gene  STR  Column containing the gene symbol            [default: gene_symbol]
##   --col_rsid  STR  Column containing the variant rsID           [default: rsid]
##   --col_beta  STR  Column containing the effect estimate        [default: beta]
##   --col_se    STR  Column containing the standard error         [default: se]
##   --col_pval  STR  Column containing the p-value                [default: pval]
##
## ── LD reference arguments ────────────────────────────────────────────────────
##   --kg_bfile  STR  plink bfile prefix (1KG EUR recommended)
##                    [default: bundled EUR path]
##   --plink     STR  Path to plink binary                         [default: plink]
##
## ── Design notes ─────────────────────────────────────────────────────────────
##   - GWAS is GRCh38; for most loci, GRCh37 ≈ GRCh38 positions.
##     Matching is done by rsID (build-agnostic) — never by raw position.
##   - Both GWAS and eQTL have a column named "varbeta". Rename them
##     (varbeta_g / varbeta_e) BEFORE merging to avoid silent NULL access.
##   - plink --r square does NOT produce a .bim file.
##     Two-step: --make-bed first, then --r square on the subset.
##   - coloc.susie needs strong eQTL signal. If loci have weak eQTLs
##     (p > 1e-3), SuSiE will fail to form credible sets. This is
##     informative (likely a sQTL/pQTL locus) — the script handles it
##     gracefully.

suppressPackageStartupMessages({
  library(coloc)
  library(data.table)
  library(susieR)
  library(ggplot2)
})

## ── Argument parsing ──────────────────────────────────────────────────────────

## Repo root, derived from this script's own path (base R, no packages) —
## tools/ciim/code/coloc.R is 3 levels below the repo root.
.script_path <- sub("^--file=", "", grep("^--file=", commandArgs(trailingOnly = FALSE), value = TRUE)[1])
.REPO_ROOT <- dirname(dirname(dirname(dirname(normalizePath(.script_path)))))

parse_args <- function() {
  args <- commandArgs(trailingOnly = TRUE)
  p <- list(
    ## Locus
    gene        = NULL,
    chr         = NULL,
    pos         = NULL,
    lead_rsid   = NA_character_,
    window      = 1e6,
    susie_n     = 5L,
    outdir      = NULL,
    ## GWAS
    gwas_file   = file.path(.REPO_ROOT, "datalake/gwas/GCST003156_SLE_Bentham2015.h.tsv.gz"),
    gwas_n      = 14267L,
    gwas_s      = 5201 / 14267,   # proportion cases (Bentham 2015)
    gwas_type   = "cc",
    ## eQTL
    eqtl_dir    = file.path(.REPO_ROOT, "datalake/dice/eqtls/full_summary_stats"),
    eqtl_n      = 91L,
    eqtl_sdy    = 1,
    eqtl_format = "dice_vcf",
    ## generic_tsv column names
    col_gene    = "gene_symbol",
    col_rsid    = "rsid",
    col_beta    = "beta",
    col_se      = "se",
    col_pval    = "pval",
    ## LD reference
    kg_bfile    = file.path(.REPO_ROOT, "datalake/gwas/1kg/EUR"),
    plink       = "plink"
  )

  i <- 1
  while (i <= length(args)) {
    switch(args[i],
      ## Locus
      `--gene`        = { p$gene        <- args[i+1];             i <- i+2 },
      `--chr`         = { p$chr         <- as.integer(args[i+1]); i <- i+2 },
      `--pos`         = { p$pos         <- as.numeric(args[i+1]); i <- i+2 },
      `--lead_rsid`   = { p$lead_rsid   <- args[i+1];             i <- i+2 },
      `--window`      = { p$window      <- as.numeric(args[i+1]); i <- i+2 },
      `--susie_n`     = { p$susie_n     <- as.integer(args[i+1]); i <- i+2 },
      `--outdir`      = { p$outdir      <- args[i+1];             i <- i+2 },
      ## GWAS
      `--gwas_file`   = { p$gwas_file   <- args[i+1];             i <- i+2 },
      `--gwas_n`      = { p$gwas_n      <- as.integer(args[i+1]); i <- i+2 },
      `--gwas_s`      = { p$gwas_s      <- as.numeric(args[i+1]); i <- i+2 },
      `--gwas_type`   = { p$gwas_type   <- args[i+1];             i <- i+2 },
      ## eQTL
      `--eqtl_dir`    = { p$eqtl_dir    <- args[i+1];             i <- i+2 },
      `--eqtl_n`      = { p$eqtl_n      <- as.integer(args[i+1]); i <- i+2 },
      `--eqtl_sdy`    = { p$eqtl_sdy    <- as.numeric(args[i+1]); i <- i+2 },
      `--eqtl_format` = { p$eqtl_format <- args[i+1];             i <- i+2 },
      ## generic_tsv columns
      `--col_gene`    = { p$col_gene    <- args[i+1];             i <- i+2 },
      `--col_rsid`    = { p$col_rsid    <- args[i+1];             i <- i+2 },
      `--col_beta`    = { p$col_beta    <- args[i+1];             i <- i+2 },
      `--col_se`      = { p$col_se      <- args[i+1];             i <- i+2 },
      `--col_pval`    = { p$col_pval    <- args[i+1];             i <- i+2 },
      ## LD reference
      `--kg_bfile`    = { p$kg_bfile    <- args[i+1];             i <- i+2 },
      `--plink`       = { p$plink       <- args[i+1];             i <- i+2 },
      { stop(sprintf("Unknown argument: %s", args[i])) }
    )
  }

  required <- c("gene", "chr", "pos", "outdir")
  missing  <- required[sapply(required, function(k) is.null(p[[k]]))]
  if (length(missing))
    stop(sprintf("Missing required arguments: %s", paste(missing, collapse=", ")))
  if (!p$eqtl_format %in% c("dice_vcf", "generic_tsv"))
    stop(sprintf("--eqtl_format must be 'dice_vcf' or 'generic_tsv', got: %s", p$eqtl_format))
  if (!p$gwas_type %in% c("cc", "quant"))
    stop(sprintf("--gwas_type must be 'cc' or 'quant', got: %s", p$gwas_type))
  p
}

## ── eQTL loaders ──────────────────────────────────────────────────────────────

## DICE VCF loader — bgzip + tabix-indexed (see analysis/dice_reindex/)
## INFO field format: Gene=..;GeneSymbol=..;Pvalue=..;Beta=..;Statistic=..;FDR=..
## se = |Beta / Statistic|  (Statistic is a t-statistic)
## Region-filters via tabix on the cis-window run_coloc already computes,
## instead of scanning the whole ~3GB file per gene.
load_eqtl_dice_vcf <- function(gene_symbol, cell_type, eqtl_dir, chr, win_start, win_end) {
  vcf_path <- file.path(eqtl_dir, paste0(cell_type, ".vcf.bgz"))
  region <- sprintf("chr%d:%d-%d", chr, win_start, win_end)
  cmd <- sprintf(
    "tabix -h %s %s | grep -v '^##' | awk 'NR==1 || /GeneSymbol=%s;/'",
    vcf_path, region, gene_symbol
  )
  dt <- fread(cmd = cmd, header = TRUE)
  if (nrow(dt) == 0) return(NULL)

  if ("#CHROM" %in% colnames(dt)) setnames(dt, "#CHROM", "CHROM")
  if ("INFO"   %in% colnames(dt)) setnames(dt, "INFO",   "INFO_COL")

  info <- dt$INFO_COL
  dt[, Beta      := as.numeric(sub(".*Beta=([^;]+).*",      "\\1", info))]
  dt[, Statistic := as.numeric(sub(".*Statistic=([^;]+).*", "\\1", info))]
  dt[, Pvalue    := as.numeric(sub(".*Pvalue=([^;]+).*",    "\\1", info))]
  dt[, se        := abs(Beta / Statistic)]
  dt[, varbeta_e := se^2]

  dt <- dt[!is.na(Beta) & !is.na(se) & se > 0 & !is.na(Pvalue) &
             ID != "." & ID != ""]
  dt <- dt[!duplicated(ID)]
  dt[, .(rsid = ID, Beta, varbeta_e, Pvalue)]
}

## Generic TSV loader
## Expects one file per cell type: {eqtl_dir}/{cell_type}.(tsv|txt)[.gz]
## Column names are controlled by p$col_* args.
load_eqtl_generic_tsv <- function(gene_symbol, cell_type, eqtl_dir,
                                   col_gene, col_rsid, col_beta, col_se, col_pval) {
  candidates <- list.files(eqtl_dir,
                            pattern    = sprintf("^%s\\.(tsv|txt)(\\.gz)?$", cell_type),
                            full.names = TRUE)
  if (length(candidates) == 0) return(NULL)

  dt <- fread(candidates[1])

  for (col in c(col_gene, col_rsid, col_beta, col_se, col_pval)) {
    if (!col %in% colnames(dt))
      stop(sprintf("Column '%s' not found in %s. Use --col_* to override.", col, candidates[1]))
  }

  dt <- dt[get(col_gene) == gene_symbol]
  if (nrow(dt) == 0) return(NULL)

  out <- data.table(
    rsid      = dt[[col_rsid]],
    Beta      = as.numeric(dt[[col_beta]]),
    varbeta_e = as.numeric(dt[[col_se]])^2,
    Pvalue    = as.numeric(dt[[col_pval]])
  )
  out <- out[!is.na(Beta) & !is.na(varbeta_e) & varbeta_e > 0 &
               !is.na(Pvalue) & rsid != "." & rsid != ""]
  out[!duplicated(rsid)]
}

## Dispatcher — picks the right loader based on p$eqtl_format
load_eqtl <- function(gene_symbol, cell_type, p, win_start, win_end) {
  if (p$eqtl_format == "dice_vcf") {
    load_eqtl_dice_vcf(gene_symbol, cell_type, p$eqtl_dir, p$chr, win_start, win_end)
  } else {
    load_eqtl_generic_tsv(gene_symbol, cell_type, p$eqtl_dir,
                           p$col_gene, p$col_rsid, p$col_beta, p$col_se, p$col_pval)
  }
}

## Enumerate cell types from the eQTL directory
list_cell_types <- function(eqtl_dir, eqtl_format) {
  if (eqtl_format == "dice_vcf") {
    gsub("\\.vcf\\.bgz$", "", list.files(eqtl_dir, pattern = "\\.vcf\\.bgz$"))
  } else {
    files <- list.files(eqtl_dir, pattern = "\\.(tsv|txt)(\\.gz)?$")
    gsub("\\.(tsv|txt)(\\.gz)?$", "", files)
  }
}

## ── Step 1: Load GWAS locus ──────────────────────────────────────────────────

load_gwas_locus <- function(gwas_file, chr, win_start, win_end) {
  # Filter by hm_chrom (col 3) and hm_pos (col 4) via awk before R reads the file.
  # hm_code 10 = direct match, 11 = palindromic resolved — both are reliable.
  cmd <- sprintf(
    "zcat %s | awk 'NR==1 || ($3==%d && $4>=%d && $4<=%d)'",
    gwas_file, chr, win_start, win_end
  )
  dt <- fread(cmd = cmd, sep = "\t")

  dt <- dt[hm_code %in% c(10L, 11L) &
             !is.na(hm_beta) & !is.na(standard_error) &
             !is.na(hm_rsid) & hm_rsid != "" & hm_rsid != "NA"]
  dt <- dt[!duplicated(hm_rsid)]
  dt[, varbeta_g := standard_error^2]

  cat(sprintf("  GWAS: %d variants in locus (after QC)\n", nrow(dt)))
  dt
}

## ── Step 3: coloc.abf for one cell type ──────────────────────────────────────

run_coloc_abf_one <- function(gwas_dt, eqtl_dt, p) {
  merged <- merge(
    gwas_dt[, .(hm_rsid, hm_beta, varbeta_g, p_value)],
    eqtl_dt[, .(rsid,    Beta,    varbeta_e, Pvalue)],
    by.x = "hm_rsid", by.y = "rsid"
  )
  merged <- merged[!duplicated(hm_rsid)]
  if (nrow(merged) < 50) return(NULL)

  d1 <- list(snp     = merged$hm_rsid,
             beta    = merged$hm_beta,
             varbeta = merged$varbeta_g,
             type    = p$gwas_type,
             N       = p$gwas_n)
  if (p$gwas_type == "cc") d1$s <- p$gwas_s

  d2 <- list(snp     = merged$hm_rsid,
             beta    = merged$Beta,
             varbeta = merged$varbeta_e,
             type    = "quant",
             sdY     = p$eqtl_sdy,
             N       = p$eqtl_n)

  res <- tryCatch(
    coloc.abf(d1, d2, p1=1e-4, p2=1e-4, p12=1e-5),
    error = function(e) { cat(sprintf("    coloc.abf error: %s\n", e$message)); NULL }
  )
  if (is.null(res)) return(NULL)

  s <- res$summary
  list(nSNP  = nrow(merged),
       PP.H0 = s["PP.H0.abf"],
       PP.H1 = s["PP.H1.abf"],
       PP.H2 = s["PP.H2.abf"],
       PP.H3 = s["PP.H3.abf"],
       PP.H4 = s["PP.H4.abf"])
}

## ── Step 4: coloc.susie for top cell types ────────────────────────────────────

build_ld_matrix <- function(rsid_list, out_prefix, kg_bfile, plink_bin) {
  # Two-step plink:
  #   1. --make-bed → produces .bim (SNP order) + .bed + .fam
  #   2. --r square → produces .ld (R matrix in BIM order)
  # plink --r square alone does NOT write a .bim file.
  snp_file   <- paste0(out_prefix, "_snplist.txt")
  sub_prefix <- paste0(out_prefix, "_sub")

  writeLines(rsid_list, snp_file)

  cmd1 <- sprintf("%s --bfile %s --extract %s --make-bed --out %s --silent",
                  plink_bin, kg_bfile, snp_file, sub_prefix)
  cmd2 <- sprintf("%s --bfile %s --r square --out %s --silent",
                  plink_bin, sub_prefix, out_prefix)

  ret1 <- system(cmd1); ret2 <- system(cmd2)
  if (ret1 != 0 || ret2 != 0) { cat("  plink failed\n"); return(NULL) }

  bim <- fread(paste0(sub_prefix, ".bim"), header=FALSE,
               col.names=c("chr","rsid","cm","pos","a1","a2"))
  ld_file <- paste0(out_prefix, ".ld")
  if (!file.exists(ld_file)) { cat("  .ld file missing\n"); return(NULL) }
  LD <- as.matrix(fread(ld_file, header=FALSE))
  rownames(LD) <- colnames(LD) <- bim$rsid
  cat(sprintf("  LD matrix: %d × %d\n", nrow(LD), ncol(LD)))
  LD
}

run_coloc_susie_one <- function(gwas_dt, eqtl_dt, LD, p) {
  merged <- merge(
    gwas_dt[, .(hm_rsid, hm_beta, varbeta_g, p_value)],
    eqtl_dt[, .(rsid,    Beta,    varbeta_e, Pvalue)],
    by.x = "hm_rsid", by.y = "rsid"
  )
  merged <- merged[!duplicated(hm_rsid)]

  common <- intersect(merged$hm_rsid, rownames(LD))
  if (length(common) < 50) return(NULL)
  merged <- merged[hm_rsid %in% common]
  LD_sub <- LD[common, common, drop=FALSE]

  d1 <- list(snp=merged$hm_rsid, beta=merged$hm_beta, varbeta=merged$varbeta_g,
             type=p$gwas_type, N=p$gwas_n, LD=LD_sub)
  if (p$gwas_type == "cc") d1$s <- p$gwas_s

  d2 <- list(snp=merged$hm_rsid, beta=merged$Beta, varbeta=merged$varbeta_e,
             type="quant", sdY=p$eqtl_sdy, N=p$eqtl_n, LD=LD_sub)

  S1 <- tryCatch(runsusie(d1),
                 error=function(e) { cat(sprintf("    d1 SuSiE error: %s\n", e$message)); NULL })
  S2 <- tryCatch(runsusie(d2),
                 error=function(e) { cat(sprintf("    d2 SuSiE error: %s\n", e$message)); NULL })
  if (is.null(S1) || is.null(S2)) return(NULL)

  res <- tryCatch(coloc.susie(S1, S2),
                  error=function(e) { cat(sprintf("    coloc.susie error: %s\n", e$message)); NULL })
  if (is.null(res) || is.null(res$results) || nrow(res$results) == 0) return(NULL)
  as.data.table(res$results)
}

## ── Step 5: Plots ─────────────────────────────────────────────────────────────

plot_pp_h4_barplot <- function(abf_df, gene, outdir) {
  p <- ggplot(abf_df, aes(x=reorder(cell_type, PP.H4), y=PP.H4, fill=PP.H4)) +
    geom_col() +
    geom_hline(yintercept=0.5, linetype="dashed",  colour="red",     linewidth=0.6) +
    geom_hline(yintercept=0.8, linetype="dotted",  colour="darkred", linewidth=0.6) +
    coord_flip() +
    scale_fill_gradient(low="#fee8c8", high="#d7301f") +
    labs(title    = sprintf("%s × GWAS colocalization (coloc.abf)", gene),
         subtitle = "PP.H4 = probability of shared causal variant",
         x = "cell type", y = "PP.H4") +
    theme_bw(base_size=12) +
    theme(legend.position="none", plot.title=element_text(face="bold"))
  ggsave(file.path(outdir, sprintf("coloc_abf_%s_PP.H4_barplot.png", gene)),
         p, width=7, height=6, dpi=150)
}

plot_posteriors_stacked <- function(abf_df, gene, outdir) {
  abf_long <- melt(abf_df, id.vars="cell_type",
                   measure.vars=c("PP.H1","PP.H2","PP.H3","PP.H4"),
                   variable.name="hypothesis", value.name="posterior")
  abf_long[, hypothesis := factor(hypothesis, levels=c("PP.H4","PP.H3","PP.H2","PP.H1"))]
  abf_long[, cell_type  := factor(cell_type, levels=abf_df$cell_type)]

  p <- ggplot(abf_long, aes(x=cell_type, y=posterior, fill=hypothesis)) +
    geom_col() + coord_flip() +
    scale_fill_manual(
      values=c(PP.H4="#d7301f", PP.H3="#fc8d59", PP.H2="#fdcc8a", PP.H1="#fef0d9"),
      labels=c("H4: shared causal","H3: distinct causal","H2: eQTL only","H1: GWAS only")
    ) +
    labs(title=sprintf("%s × GWAS — coloc posteriors", gene),
         x="cell type", y="Posterior probability", fill="Hypothesis") +
    theme_bw(base_size=12) + theme(plot.title=element_text(face="bold"))
  ggsave(file.path(outdir, sprintf("coloc_abf_%s_posteriors_stacked.png", gene)),
         p, width=8, height=6, dpi=150)
}

plot_regional <- function(gwas_dt, eqtl_dt, gene, cell_type, lead_rsid, outdir) {
  gwas_dt <- copy(gwas_dt)
  gwas_dt[, log10p := -log10(as.numeric(p_value))]

  merged <- merge(gwas_dt[, .(snp=hm_rsid, pos=hm_pos, log10p)],
                  eqtl_dt[, .(snp=rsid, eqtl_log10p=-log10(Pvalue))],
                  by="snp")

  p1 <- ggplot(merged, aes(x=pos/1e6, y=log10p)) +
    geom_point(alpha=0.4, size=0.8) +
    { if (!is.na(lead_rsid) && lead_rsid %in% merged$snp)
        geom_point(data=merged[snp==lead_rsid], colour="red", size=3, shape=18) } +
    labs(title=sprintf("%s locus — GWAS", gene), x="position (Mb)", y="-log10(p)") +
    theme_bw(base_size=12)
  ggsave(file.path(outdir, sprintf("regional_gwas_%s.png", gene)), p1, width=8, height=4, dpi=150)

  p2 <- ggplot(merged, aes(x=pos/1e6, y=eqtl_log10p)) +
    geom_point(alpha=0.4, size=0.8, colour="steelblue") +
    { if (!is.na(lead_rsid) && lead_rsid %in% merged$snp)
        geom_point(data=merged[snp==lead_rsid], colour="red", size=3, shape=18) } +
    labs(title=sprintf("%s eQTL — %s", gene, cell_type), x="position (Mb)", y="-log10(p) eQTL") +
    theme_bw(base_size=12)
  ggsave(file.path(outdir, sprintf("regional_eqtl_%s_%s.png", cell_type, gene)),
         p2, width=8, height=4, dpi=150)
}

## ── Main ─────────────────────────────────────────────────────────────────────

main <- function() {
  p <- parse_args()
  dir.create(p$outdir, recursive=TRUE, showWarnings=FALSE)

  win_start <- as.integer(p$pos - p$window)
  win_end   <- as.integer(p$pos + p$window)

  cat(sprintf("=== Coloc: %s × GWAS × eQTL (%s) ===\n", p$gene, p$eqtl_format))
  cat(sprintf("Locus  : chr%d:%d-%d  |  lead SNP: %s\n",
              p$chr, win_start, win_end, p$lead_rsid))
  cat(sprintf("GWAS   : %s  (N=%d, type=%s%s)\n",
              basename(p$gwas_file), p$gwas_n, p$gwas_type,
              if (p$gwas_type == "cc") sprintf(", s=%.4f", p$gwas_s) else ""))
  cat(sprintf("eQTL   : %s  (N=%d, sdY=%g, format=%s)\n",
              p$eqtl_dir, p$eqtl_n, p$eqtl_sdy, p$eqtl_format))

  ## 1. GWAS
  cat("\n[1] Loading GWAS locus...\n")
  gwas <- load_gwas_locus(p$gwas_file, p$chr, win_start, win_end)
  if (nrow(gwas) < 100) stop("Too few GWAS variants — check chr/pos/window.")

  ## 2. eQTL
  cat(sprintf("\n[2] Loading eQTL for %s...\n", p$gene))
  cell_types <- list_cell_types(p$eqtl_dir, p$eqtl_format)
  eqtl_all <- lapply(cell_types, function(ct) {
    cat(sprintf("  %-30s", ct))
    d <- tryCatch(load_eqtl(p$gene, ct, p, win_start, win_end), error=function(e) NULL)
    if (is.null(d)) { cat(" FAILED\n"); return(NULL) }
    cat(sprintf(" %d variants\n", nrow(d)))
    d
  })
  names(eqtl_all) <- cell_types

  ## 3+4. coloc.abf — all cell types
  cat("\n[3+4] Running coloc.abf...\n")
  abf_list <- lapply(cell_types, function(ct) {
    eqtl <- eqtl_all[[ct]]
    if (is.null(eqtl)) return(NULL)
    cat(sprintf("  %-30s", ct))
    r <- tryCatch(run_coloc_abf_one(gwas, eqtl, p),
                  error=function(e) { cat(sprintf(" ERROR: %s\n", e$message)); NULL })
    if (is.null(r)) { cat("\n"); return(NULL) }
    cat(sprintf("  PP.H4=%.3f  PP.H3=%.3f  (n=%d)\n", r$PP.H4, r$PP.H3, r$nSNP))
    data.table(cell_type=ct, nSNP=r$nSNP,
               PP.H0=r$PP.H0, PP.H1=r$PP.H1, PP.H2=r$PP.H2,
               PP.H3=r$PP.H3, PP.H4=r$PP.H4)
  })
  abf_df <- rbindlist(abf_list, use.names=TRUE, fill=TRUE)
  if (nrow(abf_df) == 0) stop("All coloc.abf calls failed.")
  abf_df <- abf_df[order(-PP.H4)]

  cat("\n--- coloc.abf results (sorted by PP.H4) ---\n")
  print(abf_df)
  fwrite(abf_df, file.path(p$outdir, sprintf("coloc_abf_%s_results.csv", p$gene)))

  ## 5. coloc.susie — top N cell types
  cat(sprintf("\n[5] Running coloc.susie (top %d cell types)...\n", p$susie_n))
  top_cts <- abf_df[1:min(p$susie_n, nrow(abf_df)), cell_type]

  all_snps <- unique(unlist(lapply(top_cts, function(ct) {
    d <- eqtl_all[[ct]]
    if (is.null(d)) return(NULL)
    merge(gwas[,.(hm_rsid)], d[,.(rsid)], by.x="hm_rsid", by.y="rsid")$hm_rsid
  })))
  cat(sprintf("  %d SNPs for LD computation\n", length(all_snps)))

  ld_prefix <- file.path(p$outdir, sprintf("ld_%s", p$gene))
  LD <- tryCatch(
    build_ld_matrix(all_snps, ld_prefix, p$kg_bfile, p$plink),
    error=function(e) { cat(sprintf("  LD error: %s\n", e$message)); NULL }
  )

  susie_list <- list()
  if (!is.null(LD)) {
    for (ct in top_cts) {
      cat(sprintf("  SuSiE %-30s", ct))
      eqtl <- eqtl_all[[ct]]
      if (is.null(eqtl)) { cat(" SKIP\n"); next }
      r <- tryCatch(run_coloc_susie_one(gwas, eqtl, LD, p),
                    error=function(e) { cat(sprintf(" ERROR: %s\n", e$message)); NULL })
      if (is.null(r)) { cat(" no coloc signals\n"); next }
      cat(sprintf(" %d signals, max PP.H4=%.3f\n", nrow(r), max(r$PP.H4.abf, na.rm=TRUE)))
      r$cell_type <- ct
      susie_list[[ct]] <- r
    }
  }

  if (length(susie_list) > 0) {
    susie_df <- rbindlist(susie_list, use.names=TRUE, fill=TRUE)
    susie_df <- susie_df[order(-PP.H4.abf)]
    cat("\n--- coloc.susie results ---\n")
    print(susie_df[, .(cell_type, hit1, hit2, nsnps, PP.H3.abf, PP.H4.abf)])
    fwrite(susie_df, file.path(p$outdir, sprintf("coloc_susie_%s_results.csv", p$gene)))
  } else {
    cat("  No colocalized signals from coloc.susie\n")
    cat("  Interpretation: eQTL signal too weak for SuSiE to form credible sets\n")
    cat("  This often indicates a sQTL (splicing) or pQTL locus rather than an eQTL locus\n")
  }

  ## 6. Plots
  cat("\n[6] Generating plots...\n")
  plot_pp_h4_barplot(abf_df, p$gene, p$outdir)
  plot_posteriors_stacked(abf_df, p$gene, p$outdir)

  top_ct <- abf_df[1, cell_type]
  if (!is.null(eqtl_all[[top_ct]])) {
    plot_regional(gwas, eqtl_all[[top_ct]], p$gene, top_ct, p$lead_rsid, p$outdir)
  }

  cat("\n=== DONE ===\n")
  cat(sprintf("Results in: %s\n", p$outdir))
  for (f in list.files(p$outdir, pattern="\\.(csv|png)$", full.names=TRUE)) {
    cat(sprintf("  %s\n", f))
  }
}

main()
