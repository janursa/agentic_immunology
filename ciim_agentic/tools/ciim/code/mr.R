## mr.R — Mendelian Randomization (format-agnostic)
##
## Receives pre-formatted exposure and outcome summary stats from Python.
## All data loading and locus subsetting is handled upstream (Python side).
##
## Required arguments:
##   --gene            gene symbol / label for output file names
##   --outdir          output directory
##   --exposure_file   CSV: snp, beta_exp, se_exp, ea_exp, nea_exp, [eaf_exp], pval_exp
##   --outcome_file    CSV: snp, beta_out, se_out, ea_out, nea_out, [eaf_out]
##   --kg_bfile        plink bfile prefix for LD clumping
##
## Optional arguments:
##   --exposure_label  label for plots            [default: Exposure]
##   --outcome_label   label for plots            [default: Outcome]
##   --pval_iv         IV p-value threshold       [default: 5e-8]
##   --pval_iv_fb      fallback if no SNPs pass   [default: 1e-3]
##   --clump_r2        LD r² for clumping         [default: 0.1]
##   --clump_kb        window (kb) for clumping   [default: 10000]
##   --plink           plink binary               [default: plink]

suppressPackageStartupMessages({
  library(data.table)
  library(ggplot2)
})

## ── Argument parsing ──────────────────────────────────────────────────────────

parse_args <- function() {
  args <- commandArgs(trailingOnly = TRUE)
  p <- list(
    gene           = NULL,
    outdir         = NULL,
    exposure_file  = NULL,
    outcome_file   = NULL,
    exposure_label = "Exposure",
    outcome_label  = "Outcome",
    pval_iv        = 5e-8,
    pval_iv_fb     = 1e-3,
    clump_r2       = 0.1,
    clump_kb       = 10000L,
    kg_bfile       = NULL,
    plink          = "plink"
  )

  i <- 1L
  while (i <= length(args)) {
    switch(args[i],
      `--gene`           = { p$gene           <- args[i+1];             i <- i+2 },
      `--outdir`         = { p$outdir         <- args[i+1];             i <- i+2 },
      `--exposure_file`  = { p$exposure_file  <- args[i+1];             i <- i+2 },
      `--outcome_file`   = { p$outcome_file   <- args[i+1];             i <- i+2 },
      `--exposure_label` = { p$exposure_label <- args[i+1];             i <- i+2 },
      `--outcome_label`  = { p$outcome_label  <- args[i+1];             i <- i+2 },
      `--pval_iv`        = { p$pval_iv        <- as.numeric(args[i+1]); i <- i+2 },
      `--pval_iv_fb`     = { p$pval_iv_fb     <- as.numeric(args[i+1]); i <- i+2 },
      `--clump_r2`       = { p$clump_r2       <- as.numeric(args[i+1]); i <- i+2 },
      `--clump_kb`       = { p$clump_kb       <- as.integer(args[i+1]); i <- i+2 },
      `--kg_bfile`       = { p$kg_bfile       <- args[i+1];             i <- i+2 },
      `--plink`          = { p$plink          <- args[i+1];             i <- i+2 },
      { stop(sprintf("Unknown argument: %s", args[i])) }
    )
  }

  if (is.null(p$gene))          stop("--gene is required")
  if (is.null(p$outdir))        stop("--outdir is required")
  if (is.null(p$exposure_file)) stop("--exposure_file is required")
  if (is.null(p$outcome_file))  stop("--outcome_file is required")
  if (is.null(p$kg_bfile))      stop("--kg_bfile is required")
  p
}

## ── MR statistical methods ────────────────────────────────────────────────────

mr_wald_ratio <- function(beta_exp, se_exp, beta_out, se_out) {
  ratio <- beta_out / beta_exp
  se_r  <- abs(se_out / beta_exp)
  pval  <- 2 * pnorm(-abs(ratio / se_r))
  data.table(method="Wald ratio", nsnp=1L,
             beta=ratio, se=se_r, pval=pval,
             egger_intercept=NA_real_, egger_intercept_se=NA_real_, egger_intercept_pval=NA_real_,
             q_stat=NA_real_, q_pval=NA_real_, i2=NA_real_)
}

mr_ivw <- function(beta_exp, beta_out, se_out) {
  w      <- 1 / se_out^2
  beta   <- sum(beta_exp * beta_out * w) / sum(beta_exp^2 * w)
  se     <- sqrt(1 / sum(beta_exp^2 * w))
  pval   <- 2 * pnorm(-abs(beta / se))
  ratio  <- beta_out / beta_exp
  q_stat <- sum(w * (beta_out - beta * beta_exp)^2)
  q_df   <- length(beta_exp) - 1L
  q_pval <- pchisq(q_stat, df=q_df, lower.tail=FALSE)
  i2     <- max(0, (q_stat - q_df) / q_stat)
  data.table(method="IVW", nsnp=length(beta_exp),
             beta=beta, se=se, pval=pval,
             egger_intercept=NA_real_, egger_intercept_se=NA_real_, egger_intercept_pval=NA_real_,
             q_stat=q_stat, q_pval=q_pval, i2=i2)
}

mr_egger <- function(beta_exp, beta_out, se_out) {
  w   <- 1 / se_out^2
  fit <- lm(beta_out ~ beta_exp, weights=w)
  s   <- summary(fit)$coefficients
  beta   <- s[2, 1]; se_b  <- s[2, 2]; pval  <- s[2, 4]
  intcpt <- s[1, 1]; se_i  <- s[1, 2]; pval_i <- s[1, 4]
  data.table(method="MR-Egger", nsnp=length(beta_exp),
             beta=beta, se=se_b, pval=pval,
             egger_intercept=intcpt, egger_intercept_se=se_i, egger_intercept_pval=pval_i,
             q_stat=NA_real_, q_pval=NA_real_, i2=NA_real_)
}

.weighted_median_val <- function(x, w) {
  ord  <- order(x)
  x    <- x[ord]; w <- w[ord]
  cumw <- cumsum(w) / sum(w)
  x[which(cumw >= 0.5)[1]]
}

mr_weighted_median <- function(beta_exp, beta_out, se_out, boot=1000L) {
  ratio    <- beta_out / beta_exp
  ratio_se <- abs(se_out / beta_exp)
  w        <- (1 / ratio_se^2); w <- w / sum(w)
  beta     <- .weighted_median_val(ratio, w)
  set.seed(42L)
  betas_boot <- vapply(seq_len(boot), function(.) {
    perturbed <- ratio + rnorm(length(ratio), sd=ratio_se)
    .weighted_median_val(perturbed, w)
  }, numeric(1))
  se   <- sd(betas_boot)
  pval <- 2 * pnorm(-abs(beta / se))
  data.table(method="Weighted median", nsnp=length(beta_exp),
             beta=beta, se=se, pval=pval,
             egger_intercept=NA_real_, egger_intercept_se=NA_real_, egger_intercept_pval=NA_real_,
             q_stat=NA_real_, q_pval=NA_real_, i2=NA_real_)
}

run_all_mr <- function(beta_exp, beta_out, se_out, se_exp=NULL) {
  n <- length(beta_exp)
  if (n == 0) return(NULL)
  results <- list()
  if (n == 1L) {
    results$wald <- mr_wald_ratio(beta_exp, if (!is.null(se_exp)) se_exp else rep(0, n),
                                  beta_out, se_out)
  } else {
    results$ivw  <- mr_ivw(beta_exp, beta_out, se_out)
    if (n >= 3L) {
      results$egger <- tryCatch(mr_egger(beta_exp, beta_out, se_out), error=function(e) NULL)
      results$wm    <- tryCatch(mr_weighted_median(beta_exp, beta_out, se_out), error=function(e) NULL)
    }
  }
  rbindlist(results, fill=TRUE)
}

## ── Allele harmonization ──────────────────────────────────────────────────────

.complement <- function(a) {
  map <- c(A='T', T='A', G='C', C='G', a='t', t='a', g='c', c='g')
  unname(ifelse(a %in% names(map), map[a], NA_character_))
}

harmonize_dt <- function(dt) {
  dt <- copy(dt)
  dt[, ea_exp_c  := .complement(ea_exp)]
  dt[, nea_exp_c := .complement(nea_exp)]
  dt[, palindromic := (ea_exp == nea_exp_c)]

  dt[(!palindromic),
     flip := (ea_exp == ea_out  | ea_exp_c == ea_out) == FALSE &
             (ea_exp == nea_out | ea_exp_c == nea_out) == TRUE]
  dt[(!palindromic),
     keep := (ea_exp == ea_out | ea_exp_c == ea_out |
              ea_exp == nea_out | ea_exp_c == nea_out)]

  if ("eaf_exp" %in% names(dt) && "eaf_out" %in% names(dt)) {
    dt[palindromic == TRUE,
       keep := !is.na(eaf_exp) & !is.na(eaf_out) & abs(eaf_exp - 0.5) > 0.1]
    dt[palindromic == TRUE & keep == TRUE,
       flip := abs((1 - eaf_exp) - eaf_out) < abs(eaf_exp - eaf_out)]
  } else {
    dt[palindromic == TRUE, keep := FALSE]
  }

  dt <- dt[keep == TRUE]
  dt[flip == TRUE, beta_exp := -beta_exp]
  dt[, .(snp, beta_exp, se_exp, beta_out, se_out)]
}

## ── LD clumping ──────────────────────────────────────────────────────────────

clump_snps <- function(snp_dt, out_prefix, kg_bfile, plink_bin, r2=0.1, kb=10000L, pval_iv=5e-8) {
  pval_file <- paste0(out_prefix, "_clump_input.txt")
  fwrite(snp_dt[, .(SNP=snp, P=pval_exp)], pval_file, sep=" ", quote=FALSE)

  cmd <- sprintf(
    "%s --bfile %s --clump %s --clump-p1 %g --clump-r2 %g --clump-kb %d --out %s --silent 2>/dev/null",
    plink_bin, kg_bfile, pval_file, pval_iv, r2, kb, out_prefix)
  system(cmd)

  clumped_file <- paste0(out_prefix, ".clumped")
  if (!file.exists(clumped_file)) {
    cat("    Clumping: no output (no LD-independent instruments)\n")
    return(character(0))
  }
  cl <- tryCatch(fread(clumped_file), error=function(e) NULL)
  if (is.null(cl) || nrow(cl) == 0) return(character(0))
  cat(sprintf("    Clumping: %d → %d index SNPs\n", nrow(snp_dt), nrow(cl)))
  cl$SNP
}

## ── Plots ─────────────────────────────────────────────────────────────────────

plot_mr_scatter <- function(harm_dt, mr_res, gene, label_exp, label_out, outdir) {
  if (nrow(harm_dt) == 0) return()
  mr_lines <- mr_res[method %in% c("IVW", "MR-Egger", "Weighted median", "Wald ratio")]
  if (nrow(mr_lines) == 0) return()

  rng_x  <- range(harm_dt$beta_exp, na.rm=TRUE)
  x_seq  <- seq(rng_x[1] * 1.2, rng_x[2] * 1.2, length.out=100)
  line_dt <- rbindlist(lapply(seq_len(nrow(mr_lines)), function(i) {
    r <- mr_lines[i]
    if (r$method == "MR-Egger")
      data.table(x=x_seq, y=r$egger_intercept + r$beta * x_seq, method=r$method)
    else
      data.table(x=x_seq, y=r$beta * x_seq, method=r$method)
  }))

  cols <- c("IVW"="#1f77b4", "MR-Egger"="#d62728",
            "Weighted median"="#2ca02c", "Wald ratio"="#1f77b4")

  p <- ggplot(harm_dt, aes(x=beta_exp, y=beta_out)) +
    geom_point(shape=21, fill="grey70", size=2) +
    geom_errorbar(aes(ymin=beta_out-1.96*se_out, ymax=beta_out+1.96*se_out),
                  width=0, colour="grey50", linewidth=0.4) +
    geom_errorbarh(aes(xmin=beta_exp-1.96*se_exp, xmax=beta_exp+1.96*se_exp),
                   height=0, colour="grey50", linewidth=0.4) +
    geom_line(data=line_dt, aes(x=x, y=y, colour=method), linewidth=0.8) +
    geom_hline(yintercept=0, linetype="dashed", colour="grey40", linewidth=0.4) +
    geom_vline(xintercept=0, linetype="dashed", colour="grey40", linewidth=0.4) +
    scale_colour_manual(values=cols) +
    labs(title=sprintf("MR: %s → %s", label_exp, label_out),
         x=sprintf("SNP effect on %s (β)", label_exp),
         y=sprintf("SNP effect on %s (β)", label_out),
         colour="Method") +
    theme_bw(base_size=12) + theme(plot.title=element_text(face="bold"))

  ggsave(file.path(outdir, sprintf("mr_%s_scatter.png", gene)), p, width=7, height=6, dpi=150)
}

plot_mr_forest <- function(harm_dt, mr_res, gene, outdir) {
  if (nrow(harm_dt) == 0) return()
  iv_dt <- harm_dt[, .(label=snp, beta=beta_out/beta_exp, se=abs(se_out/beta_exp), type="Instrument")]
  overall <- mr_res[method %in% c("IVW", "MR-Egger", "Weighted median", "Wald ratio"),
                    .(label=method, beta, se, type="Method")]
  forest_dt <- rbindlist(list(iv_dt, overall), fill=TRUE)
  forest_dt[, lo := beta - 1.96 * se]
  forest_dt[, hi := beta + 1.96 * se]
  forest_dt[, label := factor(label, levels=rev(label))]

  p <- ggplot(forest_dt, aes(x=beta, y=label, colour=type, shape=type)) +
    geom_point(size=2.5) +
    geom_errorbarh(aes(xmin=lo, xmax=hi), height=0.25, linewidth=0.5) +
    geom_vline(xintercept=0, linetype="dashed", colour="grey40", linewidth=0.5) +
    scale_colour_manual(values=c(Instrument="grey55", Method="#1f77b4")) +
    scale_shape_manual(values=c(Instrument=16L, Method=18L)) +
    labs(title=sprintf("MR forest: %s", gene),
         x="Causal effect estimate (β)", y=NULL, colour=NULL, shape=NULL) +
    theme_bw(base_size=12) +
    theme(plot.title=element_text(face="bold"), legend.position="bottom")

  ggsave(file.path(outdir, sprintf("mr_%s_forest.png", gene)), p,
         width=7, height=max(4, 0.35 * nrow(forest_dt) + 2), dpi=150)
}

plot_mr_funnel <- function(harm_dt, mr_res, gene, outdir) {
  if (nrow(harm_dt) == 0) return()
  best_method <- intersect(c("IVW", "MR-Egger", "Wald ratio"), mr_res$method)[1]
  if (is.na(best_method)) return()
  causal_est <- mr_res[method == best_method, beta][1]

  iv_dt <- harm_dt[, .(ratio=beta_out/beta_exp, prec=1/abs(se_out/beta_exp))]

  p <- ggplot(iv_dt, aes(x=ratio, y=prec)) +
    geom_point(colour="steelblue", size=2) +
    geom_vline(xintercept=causal_est, colour="red", linetype="dashed", linewidth=0.8) +
    geom_vline(xintercept=0, linetype="dashed", colour="grey50", linewidth=0.4) +
    labs(title=sprintf("MR funnel: %s", gene),
         x="IV ratio estimate", y="Precision (1/SE)",
         caption=sprintf("Red: %s estimate", best_method)) +
    theme_bw(base_size=12) + theme(plot.title=element_text(face="bold"))

  ggsave(file.path(outdir, sprintf("mr_%s_funnel.png", gene)), p, width=6, height=6, dpi=150)
}

## ── Main MR function ──────────────────────────────────────────────────────────

`%||%` <- function(a, b) if (length(a) && !is.null(a) && !is.na(a[1])) a else b

run_main <- function(p) {
  cat(sprintf("=== MR: %s ===\n", p$gene))
  cat(sprintf("Exposure : %s\n", p$exposure_label))
  cat(sprintf("Outcome  : %s\n", p$outcome_label))
  cat(sprintf("IV thresh: p < %g  (fallback: p < %g)\n", p$pval_iv, p$pval_iv_fb))

  ## ── 1. Read inputs ────────────────────────────────────────────────────────
  exp_dt <- fread(p$exposure_file)
  out_dt <- fread(p$outcome_file)
  setnames(exp_dt, names(exp_dt), tolower(names(exp_dt)))
  setnames(out_dt, names(out_dt), tolower(names(out_dt)))
  cat(sprintf("  Exposure: %d variants\n", nrow(exp_dt)))
  cat(sprintf("  Outcome : %d variants\n", nrow(out_dt)))

  ## ── 2. IV selection ───────────────────────────────────────────────────────
  ivs <- exp_dt[pval_exp < p$pval_iv]
  used_thresh <- p$pval_iv
  if (nrow(ivs) == 0) {
    ivs <- exp_dt[pval_exp < p$pval_iv_fb]
    used_thresh <- p$pval_iv_fb
    cat(sprintf("  Fallback threshold: p < %g\n", used_thresh))
  }
  if (nrow(ivs) == 0) {
    msg <- sprintf("No IVs found (best p = %.2e) — skipping", min(exp_dt$pval_exp, na.rm=TRUE))
    cat(msg, "\n")
    writeLines(msg, file.path(p$outdir, "mr_skipped.txt"))
    quit(save="no", status=0)
  }
  cat(sprintf("  IVs at p < %g: %d\n", used_thresh, nrow(ivs)))

  ## ── 3. LD clumping ────────────────────────────────────────────────────────
  if (nrow(ivs) > 1) {
    clump_prefix <- file.path(p$outdir, sprintf("clump_%s", p$gene))
    index_snps <- tryCatch(
      clump_snps(ivs, clump_prefix, p$kg_bfile, p$plink,
                 r2=p$clump_r2, kb=p$clump_kb, pval_iv=used_thresh),
      error=function(e) { cat(sprintf("  Clumping error: %s\n", e$message)); ivs$snp }
    )
    if (length(index_snps) == 0) index_snps <- ivs$snp
    ivs <- ivs[snp %in% index_snps]
  }
  cat(sprintf("  IVs after clumping: %d\n", nrow(ivs)))

  ## ── 4. Merge with outcome ─────────────────────────────────────────────────
  merged <- merge(ivs, out_dt, by="snp")
  if (nrow(merged) == 0) stop("No SNP overlap between exposure IVs and outcome.")
  cat(sprintf("  SNPs overlapping outcome: %d\n", nrow(merged)))

  ## ── 5. Harmonize ─────────────────────────────────────────────────────────
  harm_in <- merged[, .(snp, beta_exp, se_exp, ea_exp, nea_exp,
                        eaf_exp = if ("eaf_exp" %in% names(merged)) eaf_exp else NA_real_,
                        beta_out, se_out, ea_out, nea_out,
                        eaf_out = if ("eaf_out" %in% names(merged)) eaf_out else NA_real_)]
  harm <- tryCatch(harmonize_dt(harm_in), error=function(e) {
    cat(sprintf("  Harmonise warning: %s — skipping strand check\n", e$message))
    merged[, .(snp, beta_exp, se_exp, beta_out, se_out)]
  })
  if (is.null(harm) || nrow(harm) == 0) stop("No SNPs remain after harmonisation.")
  cat(sprintf("  SNPs after harmonisation: %d\n", nrow(harm)))

  ## F-stat check
  harm[, f_stat := (beta_exp / se_exp)^2]
  n_weak <- sum(harm$f_stat < 10, na.rm=TRUE)
  if (n_weak > 0)
    cat(sprintf("  Warning: %d/%d IVs have F < 10 (weak instrument)\n", n_weak, nrow(harm)))

  ## ── 6. Run MR ─────────────────────────────────────────────────────────────
  mr_res <- tryCatch(
    run_all_mr(harm$beta_exp, harm$beta_out, harm$se_out, harm$se_exp),
    error=function(e) stop(sprintf("MR failed: %s", e$message))
  )
  mr_res[, exposure := p$exposure_label]
  mr_res[, outcome  := p$outcome_label]
  mr_res[, n_ivs    := nrow(harm)]
  mr_res[, pval_iv_used := used_thresh]

  cat("\n--- MR results ---\n")
  print(mr_res[, .(method, nsnp, beta, se, pval)])
  eg <- mr_res[method == "MR-Egger"]
  if (nrow(eg) > 0 && !is.na(eg$egger_intercept[1]))
    cat(sprintf("MR-Egger intercept: %.4f (p=%.3g)\n",
                eg$egger_intercept[1], eg$egger_intercept_pval[1]))

  ## ── 7. Save + plot ────────────────────────────────────────────────────────
  out_csv <- file.path(p$outdir, sprintf("mr_%s_results.csv", p$gene))
  fwrite(mr_res, out_csv)

  if (!"se_exp" %in% names(harm)) harm[, se_exp := 0]
  plot_mr_scatter(harm, mr_res, p$gene, p$exposure_label, p$outcome_label, p$outdir)
  plot_mr_forest(harm, mr_res, p$gene, p$outdir)
  plot_mr_funnel(harm, mr_res, p$gene, p$outdir)

  cat(sprintf("\n=== DONE: %s ===\n", p$outdir))
  for (f in list.files(p$outdir, pattern="\\.(csv|png)$", full.names=TRUE))
    cat(sprintf("  %s\n", f))
}

## ── Entry point ───────────────────────────────────────────────────────────────

main <- function() {
  p <- parse_args()
  dir.create(p$outdir, recursive=TRUE, showWarnings=FALSE)
  run_main(p)
}

main()
