Regulatory network remodeling defines human immune aging and reveals modifiable immune states 

 

Jalil Nourisa 1,2, Ali Ehsani 1,2, Yihan Zhang 1,2, Liang Zhou 1,2, Ahmed Alaswad 1,2, Jierong Han 1,2, Nienke van Unen 1,2, Elisabeth Dulfer ?, Anaisa Valido Ferreira ?, Mihai G. Netea 3,4, Cheng-Jian Xu 1,2, Yang Li 1,2,5,6, * 

 

Department of Computational Biology for Individualised Medicine, Centre for Individualised Infection Medicine (CiiM), a joint venture between the Helmholtz-Centre for Infection Research (HZI) and the Hannover Medical School (MHH), Hannover, Germany 

TWINCORE, a joint venture between the Helmholtz-Centre for Infection Research (HZI) and the Hannover Medical School (MHH), Hannover, Germany 

Department of Internal Medicine and Radboud Center for Infectious Diseases, Radboud University Medical Center, Nijmegen, Netherlands 

Department of Immunology and Metabolism, Life and Medical Sciences Institute (LIMES), University of Bonn, Bonn, Germany  

Cluster of Excellence Resolving Infection Susceptibility (RESIST; EXC 2155), Hannover Medical School, Hannover, Germany 

Lower Saxony Center for Artificial Intelligence and Causal Methods in Medicine (CAIMed), Hannover, Germany 

*: Corresponding author: 	 

Prof. Dr. Yang Li 

E-mail: Yang.Li@helmholtz-hzi.de 

 

Abstract 

Aging progressively compromises immune function, increasing susceptibility to infection, blunting vaccine responsiveness and promoting chronic inflammation. However, the regulatory architecture that drives immune aging, and whether it can be quantitatively measured and therapeutically modulated, remain incompletely understood. Here we integrated more than 18 million single-cell transcriptomes from over 2,000 individuals aged 20-90 years across five population cohorts and multiple ancestries to generate the Human Immune Regulatory Aging (HIRA) atlas, a cross-cohort framework for defining age-associated regulatory state transitions across the human immune system. We identified more than 600 transcription factors with age-associated changes in inferred activities, revealing extensive remodeling of gene regulatory networks, most prominently in T cells, where aging was characterized by loss of naïve-state regulators and activation of inflammatory and effector programs. Building on this framework, we developed interpretable, cell type-specific aging clocks based on regulatory network architecture rather than global transcriptional profiles. These models robustly predicted chronological age, outperformed transcriptome-wide approaches and revealed accelerated immune aging in systemic lupus erythematosus, particularly in younger individuals, indicating that autoimmune activation converges on core regulatory programs of physiological aging. Applying these clocks to cytokine and pharmacological perturbation datasets uncovered IL-10 and JAK-STAT inhibitor ruxolitinib as modulators that oppose age-associated regulatory states. Ex vivo validation further showed that ruxolitinib attenuated both baseline and inflammation-induced immune aging signatures and reversed key aging associated transcription factor programs. Together, our findings define immune aging as a progressive rewiring of gene regulatory state, establish a framework for quantifying clinically relevant immune aging, and nominate immunoregulatory interventions that may help restore more youthful immune function.  

 

Introduction 

Aging is a fundamental biological process and a major driver of morbidity and mortality worldwide, contributing to increased risk of cancer, cardiovascular disease, and neurodegeneration​1–3​. Among the organ systems most profoundly affected is the immune system, which undergoes a progressive decline in function known as immunosenescence ​4,5​. Clinically, immune aging manifests as increased susceptibility to infections, reduced vaccine responsiveness, and chronic low-grade inflammation ​6,7​,  collectively contributing to frailty and multimorbidity in older adults. 

 

Despite extensive descriptive work, a central question remains unsolved: what regulatory architecture organizes immune aging across cell types and individuals, and can this architecture be measured in a way that is both mechanistically interpretable and actionable. At the molecular level, immune aging reflects coordinated transcriptional, epigenetic and proteomic changes  ​8–11​ that alter immune-cell identity and function. These processes are governed by gene-regulatory networks (GRNs), which integrate transcription factor (TF) activity, chromatin accessibility and signaling cues to maintain immune homeostasis. Age-associated disruption of TF programs and chromatin remodeling can destabilize GRNs, contributing to dysregulated gene expression, altered differentiation trajectories and impaired immune responsiveness ​12​. A systems-level view of immune aging as progressive remodeling of regulatory network state could therefore provide a unifying framework for identifying core drivers of immune decline and for prioritizing intervention points. 

 

Single-cell studies have begun to map age-associated transcriptional changes in immune cells ​13–18​, but many have been limited by small sample size, demographic diversity, cross-cohort heterogeneity or incomplete coverage of immune lineages. As a result, the field still lacks a robust, cross-cohort reference of how regulatory programs change with age across the human immune system. In parallel, molecular aging clocks have emerged as tools to quantify biological age and nominate interventions that modulate aging trajectories  ​9,11,17,19–25​. However, most transcriptomic clocks are trained on global gene expression profiles and therefore emphasize downstream consequences of aging, offering limited interpretability of upstream regulators and reduced mechanistic resolution. 

 

Here we present the Human Immune Regulatory Aging (HIRA) atlas, a cross-cohort single-cell framework for defining age-associated regulatory state transitions across the human immune system. HIRA integrates more than 18 million single cell transcriptomes from over 2,000 individuals aged 20 to 90 years across five cohorts spanning multiple ancestries (Fig. 1). Using cell type-specific GRN inference and TF activity modeling, we identify more than 600 TFs with age-associated shifts in inferred activity across immune lineages, with the most extensive regulatory remodeling observed in T cells. We then develop interpretable, GRN-informed, cell type–specific aging clocks that quantify immune aging through regulatory network architecture and enable upstream regulators to be traced.  

We apply this framework to human disease and perturbation data to assess clinical relevance and nominate candidate modulators. The clocks detect accelerated T-cell immune aging in systemic lupus erythematosus (SLE), particularly in younger individuals, and show that autoimmune activation converges on regulatory programs observed during physiological aging. Leveraging published cytokine and small-molecule perturbation resources, we identify IL10 and the clinically approved JAK-STAT modulator ruxolitinib as perturbations associated with reduced predicted immune age and opposing age-associated regulatory states. Finally, ex vivo experiments provide additional support that ruxolitinib attenuates baseline and inflammation-associated immune aging signatures at the level of transcriptional regulation. 

Together, HIRA provides a comprehensive and mechanistically grounded map of regulatory remodeling in human, establishes interpretable tools for quantifying clinically relevant immune aging, and offers a general strategy for prioritizing immunomodulatory interventions that counteract age-associated immune programs. The atlas and associated resources are made available through an interactive web portal (https://lab-li.ciim-hannover.de/hira).  

Results 

Age-related trajectories of gene regulation across immune cell types 

To define how gene-regulatory programs change with age across the human immune system, we analyzed more than 18 million single-cell transcriptomes from over 2,000 donors aged 20–90 years across five independent cohorts spanning multiple ancestries and balanced for sex and age (Methods, Fig. 1, Supplementary Fig. 1A). Peripheral blood mononuclear cells (PBMCs) from OneK1K ​26​, ABF300 ​27​, AIDA ​28​, and Perez ​29​ cohorts were used for discovery, and the SoundLife cohort ​18​ was reserved for validation. All datasets were processed through a harmonized analytical pipeline to enable across-cohort analysis of immune aging. 

We next inferred cell type–specific GRNs from these single-cell datasets and quantified TF activity for each donor as a functional readout of regulatory influence (Methods). Within each immune cell type, TF activity was modeled as a function of chronological age in within each cohort, followed by meta-analysis across the discovery cohorts to identify robust, directionally consistent age-associated TFs. TFs were considered significantly when they exhibited a concordant directional change (increase or decrease) across discovery cohorts, a meta-analyzed false discovery rate (FDR) below 0.05, and a Spearman correlation of over 0.1 across all cohorts (Methods).  

 

Using this framework, we identified more than 600 TFs with age-associated changes across immune lineages (Fig. 2A). These changes included both gains and losses in TF activity, indicating that immune aging reflects bidirectional extensive remodeling rather than a uniform decline. The most extensive notable rewiring occurred in T cells, with approximately 350 3 and 120 age-associated TFs detected in CD8+ and CD4+ subsets, respectively (Fig. 2A–B).). In CD8+ T cells, TFs with reduced activity included the markers of naïve and stem-like identity such as TCF7, LEF1, FOXO1, BACH2, BCL11B, and MYB, while TFs with increased activity included the markers of effector differentiation such as TBX21, PRDM1, ZEB2, RUNX3, EOMES, BATF, IRF4, and STAT4 ​30–37​. These changes indicate a coordinated shift from naïve-state regulatory programs toward effector differentiation with age. 

 This pervasive transcriptional rewiring mirrors the established features of T-cell immunosenescencerewiring aligns with the central role of T cells in immunosenescence,  including contraction of naïve T-cell populations, expansion of effector memory and terminally differentiated effector (TEMRA) cells, and reduced clonal diversity characterized by contraction of naïve populations, expansion of effector memory and terminally differentiated effector populations (TEMRA) subsets, and reduced clonal diversity ​38,39​. Consistent with this shift,Age age-associated TFs were enriched in inflammatory and effector pathways such as TNF-α signaling via NF-κB, IL-2/STAT5, and Interferon Gamma response, indicating heightened immune activation with age (Methods, Extended Data Fig. 1A). In contrast, activity of TFs associated with Wnt–β-catenin signaling declined, consistent with reduced maintenance of naïve T cells, a hallmark of immunosenescence.  

These patterns were strongly reproduced in the validation cohort (Extended Data Fig. 1B, Supplementary Table 1). More than 95% of age-associated TFs showed consistent directionality of changes (increasing or decreasing with age) across all lineages and discordant cases were restricted to TFs with weak age correlations in the validation cohort (Spearman |ρ| < 0.2). In addition, approximately 20% of age-associated TFs did not reach statistical significance in the validation cohort (Supplementary Fig. 1B, Supplementary Table 2). These included IRF2, IRF4, and IRF9 in CD8⁺ T-cell subsets, known regulators of effector–memory fate decisions ​40,41​, which displayed strong age associations in the discovery analysis (FDR < 1´ 10−32) and showed similar age-associated trajectories in the validation cohort despite not reaching statistical significance, likely owing to the substantially smaller size of the validation cohort (96 donors) relative to the discovery analysis (approximately 1,900 donors). 

Age-associated TFs tended to occupy highly central positions within their respective GRNs (Methods, Fig. 2C), suggesting that aging affects fundamental cellular programs. Among the most important altered TFs, PRDM1, TBX21, and KLF6 exhibited increased activity with age across T and NK cells, whereas LEF1, TCF7, and BACH2 decreased. These patterns mirror known functional trajectories: PRDM1 and TBX21 promote effector differentiation ​13​ whereas BACH2 and LEF1 sustain naïve and regulatory programs ​42​. Comparative analysis further revealed considerable overlap of age-associated TFs between CD4+, CD8+ T cells, and NK cells (Supplementary Fig. 1C), supporting a shared lymphoid aging program alongside lineage-specific changes. Ten transcription factors were shared across all three cell types, with some showing conserved age-associated trends, such as the decline in SATB1, whereas others diverged by lineage, such as GATA3, which increased in T cells but decreased in NK cells (Fig. 2D-F).  

Because inferred TF activity integrates coordinated expression across target genes, it can capture regulatory changes not apparent from TF expression alone. Although some TFs, including SATB1 and GATA3, showed concordant age-associated changes in both activity and expression, others, such as NME2, a critical TF for T-cell activation and calcium signaling ​43,44​, displayed marked age-associated shifts in activity without detectable changes in expression (Supplementary Fig. 1D). These findings underscore the added value of TF activity analysis beyond conventional expression-based approaches.  

Together, these analyses define a cross-lineage regulatory architecture of immune aging, with the strongest remodeling observed in T cells and with both shared and lineage-specific programs contributing to age-associated immune dysfunction. A complete catalogue of age-associated TFs and their target modules is available through our interactive HIRA web portal (https://lab-li.ciim-hannover.de/hira). 

GRN-informed cell type-specific aging clocks  

Building on this regulatory atlas, we next asked whether age-associated network remodeling could be quantified in an interpretable way within specific immune cell types. To this end, we developed cell type–specific aging clocks informed by GRNs (Methods). Rather than using the full transcriptome ​9,22​, we selected predicted GRN target genes as model features for each immune cell type (Supplementary Fig. 1E). This strategy reduces noise, preserves biological interpretability and enables each predictive feature to be traced to upstream TF regulators.  

The clocks were trained on pseudobulk transcriptomes from approximately 1,200 healthy donors from OneK1K and ABF300 cohorts and tested across three independent cohorts of AIDA, Perez, and Zhang [this is different from your earlier text in line 215, keep them consistent; mention the exact cohorts name; Or you actually wanted to say: the clocks were initially trained in X1 cohort and replicated in the X2, X3, and X4 cohorts; If so, where did you talk about the “validation cohort”? ] with over 800 donors, spanning multiple ancestries (Methods). Among the regression approaches tested, ridge regression provided best balance of accuracy and generalizability. Direct single-cell models were less robust and more computationally intensive and were therefore not pursued further.  

GRN-informed clocks predicted chronological age with high accuracy, achieving Spearman correlations of approximately 0.8 in both CD4⁺ and CD8⁺ T cells (Fig. 3A). Performance was lower in NK cells, monocytes, and B cells, consistent with weaker and more heterogeneous age-associated signatures in these lineages (Fig. 1). Previous aging clocks were also less successful in these cell types compared to CD4⁺ and CD8⁺ T cells ​9​. Across the test datasets, the GRN-informed clocks outperformed previous models trained on genome-wide gene expression ​9​ (Extended Data Fig. 2A). Because both approaches were trained on the same datasets, this improvement may reflect the advantages of biologically constrained feature selection and/or the increased robustness conferred by pseudobulking. In addition to improved performance, the models were computationally efficient, requiring only seconds per sample, and are distributed as an open-source Python package [https://github.com/janursa/GRNimmuneClock].  

To examine the biological programs captured by the clocks, we performed pathway enrichment analysis on the selected GRN features. Across cell types, clock features were enriched for immune-related pathways, including interferon-α and interferon-γ responses, TNF-α signaling via NF-κB, and apoptosis (Fig. 3B). These patterns are consistent with our previous observations of enriched pathways among age-associated TFs (Extended Data Fig. 1A) and align with pathways recurrently implicated in immune aging ​45–47​. Inspection of top-weighted features similarly showed that positively weighted genes tend to increase with age, whereas negatively weighted genes declined (Fig. 3C and Extended Data Fig. 2B). Many of the highest-ranked features were established markers of immune aging and senescence, including CD70 ​48​, CDKN2A/p16INK4a ​49–51​, and KLRC1/NKG2A ​52,53​, which have been previously implicated in T-cell exhaustion, senescence-associated phenotypes and age-related immune dysfunction. 

Next, to dissect the regulatory programs underlying these clocks, we integrated GRNs with gene-level clock associations and identified TFs with the strongest regulatory contribution to predicted age (Methods). In CD8+ T cells, the TFs exerting the strongest regulatory influence were JUN, KLF6, GATA3, MAF, and SOX4, while in CD4+ T cells, the top regulators were SOX4, IRF4, RORC, SCML4, and SATB1 (Fig. 3C and Extended Data Fig. 2B). Most of these TFs have previously been implicated in immune aging or organismal senescence, both in our analyses (Supplementary Fig. 2A) and in prior studies ​14,42,54–58​, underscoring their conserved roles in shaping age-related transcriptional programs across T-cell lineages. One notable exception was RORC, a master regulator of Th17 cell differentiation, which showed increased activity with age but a negative regulatory coefficient in the CD4+ T-cell clock. Because the clocks capture multifactorial and conditional relationships among correlated regulatory programs, whereas TF activity analysis reflects marginal age associations, this discrepancy may reflect a context-dependent or compensatory role of RORC within aging-associated CD4⁺ T programs rather than a direct aging-promoting effect. This example highlights the importance of GRN-integrated aging clocks, identifying TFs with different roles within complex multi-regulatory environments versus their isolated age trajectories. 

Together, these findings establish interpretable, cell type–specific aging clocks that quantify immune aging through regulatory networks architecture and provide a framework for testing how disease and perturbations shift immune regulatory state. 

Autoimmune activation accelerates T-cell aging in young individuals with systemic lupus erythematosus 

To assess whether this framework captures clinically relevant deviations from physiological immune aging, we applied the aging clocks to systemic lupus erythematosus (SLE), a prototypical autoimmune disorder characterized by chronic inflammation and premature immune dysfunction. We analyzed transcriptomes from 250 261 individuals, including healthy controls and patients with SLE ​29​, with balanced group sizes, predominantly female donors and ages ranging from 20 to 80 years (Supplementary Fig. 1A). 

Both CD4⁺ and CD8⁺ T cells from SLE patients showed significantly elevated predicted biological ages compared to age-matched controls (Methods; Fig. 3D). This acceleration was most pronounced in younger patients for CD8⁺ T from individuals younger than 50 years, in whom predicted age increased by approximately +6 years (FDR = 1×10⁻11), whereas no significant increase was observed in older individuals (Extended Data Fig. 2C), paralleling clinical patterns in which immune hyperactivation dominates early disease and exhaustion and comorbidities prevails later ​59​. These results suggest that SLE is associated with accelerated transcriptional aging, with the strongest effects observed in younger adults. 

To examine the regulatory basis of this shift, we next identified TFs with significantly altered activity in SLE across immune cell types (Supplementary Fig. 2B). SLE induced widespread transcriptional shift across lineages, with highest concordance observed between CD4⁺ and CD8⁺ T cells. Gene set enrichment analysis revealed upregulation of proinflammatory and effector pathways, including IL-2/STAT5 signaling, interferon-α and interferon-γ responses, and TNF-α signaling via NF-κB, coupled with downregulation of Wnt–β-catenin signaling (Extended Data Fig. 1C). These pathway-level changes mirrored those associated with physiological aging in CD4⁺ and CD8⁺ T cells (Extended Data Fig. 1A), supporting the view that autoimmunity accelerates aging programs.  

Comparison of TF activity profiles between SLE and healthy individuals showed that nearly all age-associated TFs shifted concordantly in SLE across both CD4+ T and CD8+ T cells (Fig. 3E and Supplementary Fig. 2D). This pattern was not observed in older patients (>50 years) in CD8+ T cells, consistent with the aging-clock results. Analysis of the 15 most central age-associated TFs further revealed that SLE reproduced the same directional activity shifts seen during normal aging across both cell types and age groups, with the exception of the older CD8+ T group (Fig. 3F and Supplementary Fig. 2E). For example, LEF1, a regulator of naïve T-cell maintenance ​60,61​, was prematurely downregulated in young patients with SLE, such that its activity in patients around 30 years of age resembled that of healthy controls around 50 years of age. 

Together, these results show that autoimmune activation in SLE engages regulatory programs that overlap with those observed during physiological immune aging, and that this effect is most evident in younger adults, particularly within CD8+ T cells.  

Systematic cytokine perturbation identifies IL-10 as a rejuvenating regulator of T cell aging 

Given the convergence between autoimmune activation and physiological immune aging, we next asked whether age-associated regulatory states could be shifted by defined extracellular signals. To nominate candidate modulators, we applied our cell type-specific aging clocks to a public cytokine perturbation dataset ​62​ comprising transcriptomic profiles of PBMCs stimulated with 90 cytokines across 12 donors and profiled 24 hours post-treatment. For each perturbation, we estimated biological age and quantify age-modifying effects by comparing treated and untreated samples (Methods).  

This analysis stratified cytokines into distinct classes based on their effects on predicted biological age (Fig. 4A, Extended Data Fig. 2D, and Supplementary Fig. 3A). Age-accelerating cytokines were predominantly pro-inflammatory mediators, including interleukin family members such as IL-2, IL-4, IL-7, and IL-15. In contrast, age-rejuvenating cytokines were enriched for anti-inflammatory and immunoregulatory factors, including IL-10, IL-22, IL-6, and OSM. Type I interferons (IFN-β and IFN-ω) exhibited cell type-specific effects, accelerating predicted age in CD4+ T cells while reducing predicted age in CD8+ T cells, indicating divergent interferon responses in the context of immune aging.  

Among all perturbations, IL-10 produced the strongest age-reducing effect in T cells, measured by aging clocks, decreasing predicted biological age by 4.9 years in CD4+ T cells and by 2.0 years in CD8+ T cells (FDR < 0.0001). TF activity analysis further showed that IL-10 induced widespread regulatory remodeling of TF activity across immune lineages (Supplementary Fig. 2B). Pathway analysis of IL-10-responsive TFs showed suppression of multiple immune-related pathways, including IL-2–STAT5 signaling and interferon-α and interferon-γ responses, across both CD4⁺ and CD8⁺ T cell (Extended Data Fig. 1C). These findings are consistent with the established role of IL-10 as a central anti-inflammatory cytokine that signals through the JAK1–TYK2–STAT3 pathway ​63,64​. Importantly, these shifts were directionally opposite to those observed during physiological aging and SLE patients, suggesting restoration toward youthful transcriptional states (Extended Data Fig. 1A and C).  

At the regulatory level, IL-10 restored the activity of the majority of age-associated TFs (Fig. 4B and Supplementary Fig. 3D). In CD8⁺ T cells, IL-10 treatment reversed the activity of ~approximately 300 of ~approximately 370 age-associated TFs, with particularly pronounced effects among highly central TFs within the aging GRN, including LEF1 and TCF7 (Extended Data Fig. 2E), key regulators of naïve and memory T cell programs whose activities decline with age. The concordance between reduced predicted biological age and reversal of aging-associated TF activity indicates that IL-10 counteracts age-related regulatory network remodeling in T cells.  

Together, these analyses identify IL-10 as a potent modulator of immune aging in human T cells. 

Pharmacological reversal of immune-aging signatures 

We next asked whether clinically relevant pharmacological perturbations show similar capacity to oppose age-associated immune regulatory programs. We therefore applied our cell type-specific aging clocks to a public drug perturbation dataset ​65,66​, which includes transcriptomic profiles from PBMCs treated with 146 small molecules, each tested in triplicate donors and profiled 24 hours post-treatment (Methods). For each compound, we estimated the biological age using aging clocks and quantified age-modifying effects by comparing treated versus untreated samples (Methods). 

Compounds caused a broad spectrum of influences on predicted biological age. Some agents, such as CGM-097, an MDM2 inhibitor that activates p53, increased predicted age in both CD4⁺ and CD8⁺ T cells (FDR < 0.05, Supplementary Fig. 3B), consistent with the role of p53 signaling in promoting cellular senescence ​25,67​. In contrast, a subset of compounds reduced predicted age in CD4⁺ and CD8⁺ T cells (FDR < 0.05; Supplementary Fig. 3C). Among these compounds, we prioritized ruxolitinib for follow-up because it is a clinically approved JAK1/2 inhibitor and showed a age-reversal effect of ~9 years in CD4⁺ T cells (FDR = 0.023; Fig. 4C).  

Ruxolitinib suppresses JAK/STAT signaling ​68​ and has been shown to attenuate cellular senescence and ameliorate age-related phenotypes across diverse experimental models ​69–71​. To verify that the observed age shift reflected coordinated changes in immune regulatory programs, we examined TF activity following ruxolitinib treatment. Ruxolitinib broadly counteracted age-associated regulatory programs (Supplementary Fig.3E) and suppressed multiple immune activation pathways in CD4+ cells, including TNF-α signaling via NF-κB, IL-2/STAT5 signaling, and interferon-α and interferon-γ responses (Extended Data Fig. 1C). These changes were directionally opposite to those observed during physiological aging and in SLE, and mirrored the effects observed with IL-10 treatment (Extended Data Fig. 1A, C). Comparative analysis further demonstrated high concordance between ruxolitinib- and IL-10 induced TF activity profiles (Extended Data Fig. 2FSupplementary Fig. 2K). Notably, key JAK-STAT pathway regulators, including STAT1, STAT2, STAT3, IRF1, IRF2, IRF7, IRF9, and NFKB2 ​72–76​ showed consistent directional changes under both perturbations. (Extended Data Fig. 2F). 

We previously demonstrated that acute infections such as SARS-CoV-2 can induce cell type–specific age acceleration within the immune system ​9​. We therefore asked whether ruxolitinib could attenuate inflammation-driven aging signatures in newly generated ex-vivo data. PBMCs from seven healthy donors were treated with ruxolitinib for 18 hours under both basal condition (RPMI) and lipopolysaccharide (LPS)-stimulation (Methods). LPS induced a pronounced immune age acceleration of ~8 years as quantified by the aging clock (P = 1 × 10-16; Fig. 4C), consistent with our previous findings that SARS-CoV-2 infection induces age acceleration ​9​. Ruxolitinib reduced predicted age under baseline conditions (~2 years, P = 0.048) and showed a directionally consistent attenuation of the LPS-induced increase in predicted age, although the latter effect did not reach statistical significance (~2.5 years, P = 0.12).  

Transcriptional analysis of the ex vivo experiments supported these clock-based findings. LPS stimulation induced aging-like regulatory signatures, whereas ruxolitinib consistently opposed these changes, particularly among the 15 most central aging-associated TFs (Fig. 4D and Supplementary Fig. 3E). For example, STAT1 and BATF, whose activities increase with age, were significantly induced by LPS and reduced by ruxolitinib. STAT1 and BATF are key regulators of interferon signaling and T cell differentiation, respectively, and their sustained activation has been linked to chronic inflammatory states ​63,64​ and T cell exhaustion during persistent immune activation​77,78​. Thus, their suppression by ruxolitinib is consistent with a shift toward a less inflammatory and more functionally competent CD4⁺ T-cell state.  

Together, these findings indicate that ruxolitinib opposes age- and inflammation-associated transcriptional programs in human PBMCs, supporting JAK–STAT signaling as a candidate axis for modulating age-associated immune states. 

Discussion  

This study presents the Human Immune Regulatory Aging (HIRA) atlas, a comprehensive single-cell resource that defines the transcriptional regulatory architecture of human immune aging. By integrating over 25 million immune transcriptomes from over 2000 individuals, we identified more than 600 TFs with age-associated changes in regulatory activity, constructed transcriptionally interpretable aging clocks, and demonstrated that immune aging can be quantitatively modeled and modulated through interventions. The study yields four main advances. First, it maps a global landscape of regulatory drift across immune cell types, revealing that T cells—particularly CD8⁺ subsets—undergo the most extensive network rewiring. Second, it establishes fast and accurate GRN-integrated aging clocks implemented as an open-source computational toolkit. Third, it uncovers disease-dependent acceleration of immune aging in SLE, most evident in younger patients. Finally, it identifies JAK-STAT modulators,rs of IL-10 and ruxolitinib, as potent agents that reverse age-associated transcriptional signatures in both healthy and infectious environments. HIRA is made publicly available as an interactive web platform to facilitate exploration of age-, disease-, and intervention-associated regulatory changes across immune lineages. 

The SLE analyses provided molecular evidence that autoimmune activation recapitulates key features of physiological aging. The near-complete overlap between SLE- and age-associated TF signatures suggests that regulatory programs underlying immune decline in aging can be pathologically re-engaged in inflammatory disease. This convergence reinforces the concept that aging presents a modifiable, rather than fixed, biological state. The observation that disease-related age acceleration was most pronounced in younger individuals implies that immunological youth may confer greater susceptibility to pathological aging signals, whereas older individuals, whose immune systems are already extensively remodeled, exhibit smaller additional shifts. Future work should test whether this pattern extends to other autoimmune and inflammatory conditions. 

Our findings also point to pharmacological avenues for rejuvenating immune function. Among 90 cytokines and 146 drugs screened, IL-10 emerged as the strongest cytokine candidate and ruxolitinib as a modest drug candidate for reversing transcriptional aging, reducing predicted biological age and restoring youthful TF-activity profiles. The convergence between aging, SLE activation, and IL-10/ruxolitinib reversal supports a central role for JAK–STAT signaling in immune aging. Despite engaging different nodes of the JAK–STAT pathway, IL-10 signaling and ruxolitinib produce highly concordant effects on age-associated TF activity, suggesting convergence on shared downstream regulatory programs. However, the precise magnitude of identified rejuvenating effects remains uncertain: for example, reductions in predicted age ranged from 2 to 5 years for IL-10 across different T cell lineages to 2 to 10 years for ruxolitinib across discovery and validation analyses. These discrepancies likely reflect technical variation across cohorts and the inherent limitations of transcriptomic clocks compared to epigenetic benchmarks. Future work integrating multi-omics modalities may refine these estimates and better quantify the therapeutic potential of JAK modulation. Moreover, the current analysis focused on ex vivo experiments; longitudinal in vivo and clinical studies are needed to determine the durability, systemic relevance, and safety of pharmacological interventions that target immune aging. Nonetheless, several other candidate compounds in our screen also showed significant age-reversal potential, whereas others accelerated predicted aging. Both categories warrant further mechanistic and translational investigation. 

Despite its scope, this study has several limitations. First, the association of TF activity with age modeled as a monotonic relationship; non-linear trajectories and inflection points across the lifespan ​79​ are likely to exist and could be captured using more flexible statistical frameworks. Second, our cohorts primarily included donors of European and Asian ancestry, potentially limiting generalizability to other populations. Third, sex-specific differences in immune aging were not assessed, despite well-documented sexual dimorphism in immune responses ​80,81​. Fourth, our analysis focused on major immune cell types; finer subpopulation resolution, particularly within B cells and myeloid lineages, may reveal additional regulatory programs, as previous studies have shown that B cells are notably affected by aging ​82–84​. Fifth, HIRA relies on transcriptomic data alone. Integrating chromatin accessibility, proteomic, and epigenomic information will provide a more complete view of regulatory aging. Future analyses could also infer age-resolved or subpopulation-specific GRNs to capture structural shifts in regulatory connectivity over time. Finally, we evaluated SLE as a disease case study and analyzed two perturbation datasets of cytokines and drugs as a proof of principle, demonstrating that our integrated framework combining aging clocks with transcriptional mapping can be broadly applied to immune-mediated and age-related disorders, as well as to the evaluation of therapeutic interventions. 

In summary, HIRA provides a unified framework for dissecting the regulatory underpinnings of immune aging, quantifying biological age at the level of transcriptional control, and identifying candidate interventions to restore immune resilience. By linking single-cell regulatory dynamics to therapeutic screening, this work establishes that the molecular hallmarks of immune aging are not fixed but can be rewired by targeted pharmacological modulation. The atlas and accompanying analytical tools lay a foundation for mechanistically informed interventions aimed at delaying or reversing age-associated immune decline across the human lifespan. 

Acknowledgments 

This project was supported by an ERC Starting Grant 948207 (ModVaccine), the Lower Saxony Center for AI and Causal Methods in Medicine (CAIMed) grant (ZN4257), and the German Federal Ministry of Education and Research (BMBF) grant [01EQ2302A/FEDCOV, 031L0318A/AID-PAIS] and the Deutsche Forschungsgemeinschaft (DFG, German Research Foundation) under Germany's Excellence Strategy - EXC 2155 - project number 390874280. to Y.L.  

 

Competing Interests  

MGN is scientific founder of Biotrip, Salvina, TTxD and Lemba.  

 

 

 

Author Contribution 

Conceptualization and study design: JN, YL 

Sample collection: ED, AVF,  

Data generation: JN, AE, YZ, LZ, AA, JH  

Data analysis and investigation: JN 

Project administration: YL 

Experiments: ED, AVFStudent from Mihai’s lab, YZ, LZ, AA, JH 

Resources: YL, MGN, C-JX 

Funding acquisition: YL 

Writing – original manuscript: JN, YL 

Review-manuscript – All authors 

 

Data availability 

The OneK1K, AIDA, and Perez SLE cohorts were respectively obtained from the CELLxGENE Discover portal (https://cellxgene.cziscience.com) with collection IDs of dde06e0f-ab3b-46be-96a2-a8082383c4a1, ced320a1-29f3-47c1-a735-513c7084d508 Freeze v1, and 436154da-bcf1-4130-9c8b-120ff9a888f2. The ABF300 and Zhang et al. cohorts were obtained via Synapse with accession syn49637038 and syn61609846, respectively. The ParseBiosciences, SoundLife, and drug perturbation datasets were respectively downloaded from: 

-       https://parse-wget.s3.us-west-2.amazonaws.com/10m/Parse_10M_PBMC_cytokines.h5ad 

-       https://apps.allenimmunology.org/aifi/insights/dynamics-imm-health-age 

-       https://openproblems.bio/events/2023-08_neurips 

 

 

Code availability 

 

The code used for this study, including public data acquisition, quality control, single-cell data processing, GRN inference, and TF activity analysis, is available at https://github.com/janursa/HIRA.git under the MIT License. Upon acceptance of this manuscript, the code will be archived in a permanent public repository. 

 

References 

​​1.	Fajemiroye, J. O. et al. Aging-induced biological changes and cardiovascular diseases. Biomed Res. Int. 2018, 7156435 (2018). 

​2.	Farooqui, T. & Farooqui, A. A. Aging: an important factor for the pathogenesis of neurodegenerative diseases. Mech. Ageing Dev. 130, 203–215 (2009). 

​3.	Aunan, J. R., Cho, W. C. & Søreide, K. The biology of aging and cancer: a brief overview of shared and divergent molecular hallmarks. Aging Dis. 8, 628 (2017). 

​4.	Ventura, M. T., Casciaro, M., Gangemi, S. & Buquicchio, R. Immunosenescence in aging: between immune cells depletion and cytokines up-regulation. Clinical and Molecular Allergy 15, 21 (2017). 

​5.	Terekhova, M., Bohacova, P. & Artyomov, M. N. Human immune aging. Immunity (2025). 

​6.	Crooke, S. N., Ovsyannikova, I. G., Poland, G. A. & Kennedy, R. B. Immunosenescence and human vaccine immune responses. Immunity & ageing 16, 25 (2019). 

​7.	Kumar, S. et al. Systemic dysregulation and molecular insights into poor influenza vaccine response in the aging population. Sci. Adv. 10, eadq7006 (2024). 

​8.	Liu, Z. et al. Immunosenescence: molecular mechanisms and diseases. Signal Transduct. Target. Ther. 8, 200 (2023). 

​9.	Li, W. et al. Single-cell immune aging clocks reveal inter-individual heterogeneity during infection and vaccination. Nat. Aging 5, 607–621 (2025). 

​10.	López-Gil, L., Pascual-Ahuir, A. & Proft, M. Genomic instability and epigenetic changes during aging. Int. J. Mol. Sci. 24, 14279 (2023). 

​11.	Wyss-Coray, T. & Topol, E. J. Biological aging clocks in health and disease. Nat. Med. 1–12 (2026). 

​12.	Unger Avila, P. et al. Gene regulatory networks in disease and ageing. Nat. Rev. Nephrol. 20, 616–633 (2024). 

​13.	Goto, M. et al. Age-associated CD4+ T cells with B cell–promoting functions are regulated by ZEB2 in autoimmunity. Sci. Immunol. 9, (2024). 

​14.	Moskowitz, D. M. et al. Epigenomics of human CD8 T cell differentiation and aging. Sci. Immunol. 2, (2017). 

​15.	Gong, Q. et al. Longitudinal multi-omic immune profiling reveals age-related immune cell dynamics in healthy adults. bioRxiv (2024). 

​16.	Yin, J. et al. Chinese Immune Multi-Omics Atlas. Science (1979). 391, eadt3130 (2026). 

​17.	Ping, J. et al. Human immune aging clock identifies RUNX1 as a decelerator of T cell senescence. Immunity 59, 1039–1057 (2026). 

​18.	Gong, Q. et al. Multi-omic profiling reveals age-related immune dynamics in healthy adults. Nature 1–11 (2025). 

​19.	Cohen, N. M. et al. Longitudinal machine learning uncouples healthy aging factors from chronic disease risks. Nat. Aging 4, 129–144 (2024). 

​20.	Bell, C. G. et al. DNA methylation aging clocks: challenges and recommendations. Genome Biol. 20, 249 (2019). 

​21.	Field, A. E. et al. DNA methylation clocks in aging: categories, causes, and consequences. Mol. Cell 71, 882–895 (2018). 

​22.	Meyer, D. H. & Schumacher, B. BiT age: A transcriptome-based aging clock near the theoretical limit of accuracy. Aging Cell 20, e13320 (2021). 

​23.	Buckley, M. T. et al. Cell-type-specific aging clocks to quantify aging and rejuvenation in neurogenic regions of the brain. Nat. Aging 3, 121–137 (2023). 

​24.	Huang, Y. et al. Unraveling aging from transcriptomics. Trends in Genetics (2025). 

​25.	Salignon, J. et al. Pasta, an age-shift transcriptomic clock, maps the chemical and genetic determinants of aging and rejuvenation. bioRxiv 2025–2026 (2025). 

​26.	Yazar, S. et al. Single-cell eQTL mapping identifies cell type–specific genetic control of autoimmune disease. Science (1979). 376, eabf3041 (2022). 

​27.	Terekhova, M. et al. Single-cell atlas of healthy human blood unveils age-related loss of NKG2C+GZMB−CD8+ memory T cells and accumulation of type 2 memory T cells. Immunity 56, (2023). 

​28.	Kock, K. H. et al. Asian diversity in human immune cells. Cell 188, 2288–2306 (2025). 

​29.	Perez, R. K. et al. Single-cell RNA-seq reveals cell type-specific molecular and genetic associations to lupus. Science (1979). 376, (2022). 

​30.	Kurachi, M. et al. The transcription factor BATF operates as an essential differentiation checkpoint in early effector CD8+ T cells. Nat. Immunol. 15, 373–383 (2014). 

​31.	Kallies, A., Xin, A., Belz, G. T. & Nutt, S. L. Blimp-1 transcription factor is required for the differentiation of effector CD8+ T cells and memory responses. Immunity 31, 283–295 (2009). 

​32.	Intlekofer, A. M. et al. Effector and memory CD8+ T cell fate coupled by T-bet and eomesodermin. Nat. Immunol. 6, 1236–1244 (2005). 

​33.	Roychoudhuri, R. et al. BACH2 regulates CD8+ T cell differentiation by controlling access of AP-1 factors to enhancers. Nat. Immunol. 17, 851–860 (2016). 

​34.	Kaech, S. M. & Cui, W. Transcriptional control of effector and memory CD8+ T cell differentiation. Nat. Rev. Immunol. 12, 749–761 (2012). 

​35.	Zhou, X. & Xue, H.-H. Cutting edge: generation of memory precursors and functional memory CD8+ T cells depends on T cell factor-1 and lymphoid enhancer-binding factor-1. The Journal of Immunology 189, 2722–2726 (2012). 

​36.	Roychoudhuri, R. et al. BACH2 regulates CD8+ T cell differentiation by controlling access of AP-1 factors to enhancers. Nat. Immunol. 17, 851–860 (2016). 

​37.	Kaech, S. M. & Cui, W. Transcriptional control of effector and memory CD8+ T cell differentiation. Nat. Rev. Immunol. 12, 749–761 (2012). 

​38.	Zhang, H., Weyand, C. M. & Goronzy, J. J. Hallmarks of the aging T-cell system. FEBS J. 288, 7123–7142 (2021). 

​39.	Rodriguez, I. J. et al. Immunosenescence study of T cells: a systematic review. Front. Immunol. 11, 604591 (2021). 

​40.	Man, K. et al. Transcription factor IRF4 promotes CD8+ T cell exhaustion and limits the development of memory-like T cells during chronic infection. Immunity 47, 1129–1141 (2017). 

​41.	Huber, M. & Lohoff, M. IRF4 at the crossroads of effector T-cell fate decision. Eur. J. Immunol. 44, 1886–1895 (2014). 

​42.	Delpoux, A. et al. FOXO1 constrains activation and regulates senescence in CD8 T cells. Cell Rep. 34, (2021). 

​43.	Boissan, M., Schlattner, U. & Lacombe, M.-L. The NDPK/NME superfamily: state of the art. Laboratory investigation vol. 98 164–174 Preprint at (2018). 

​44.	Di, L. et al. Nucleoside diphosphate kinase B knock-out mice have impaired activation of the K+ channel KCa3. 1, resulting in defective T cell activation. Journal of Biological Chemistry 285, 38765–38771 (2010). 

​45.	Shaw, A. C., Goldstein, D. R. & Montgomery, R. R. Age-dependent dysregulation of innate immunity. Nat. Rev. Immunol. 13, 875–887 (2013). 

​46.	Connors, J. et al. Aging alters antiviral signaling pathways resulting in functional impairment in innate immunity in response to pattern recognition receptor agonists. Geroscience 44, 2555–2572 (2022). 

​47.	Shih, R.-H., Wang, C.-Y. & Yang, C.-M. NF-kappaB signaling pathways in neurological inflammation: a mini review. Front. Mol. Neurosci. 8, 77 (2015). 

​48.	Wang, D. et al. CD70 contributes to age-associated T cell defects and overwhelming inflammatory responses. Aging (Albany NY) 12, 12032 (2020). 

​49.	Janelle, V. et al. p16INK4a regulates cellular senescence in PD-1-expressing human T cells. Front. Immunol. 12, 698565 (2021). 

​50.	Mori, H. et al. Blood CDKN2A gene expression in aging and neurodegenerative diseases. Journal of Alzheimer’s Disease 82, (2021). 

​51.	Baker, D. J., Jin, F. & Van Deursen, J. M. The yin and yang of the Cdkn2a locus in senescence and aging. Cell Cycle vol. 7 Preprint at https://doi.org/10.4161/cc.7.18.6687 (2008). 

​52.	Soto-Heredero, G. et al. KLRG1 identifies regulatory T cells with mitochondrial alterations that accumulate with aging. Nat. Aging 1–17 (2025). 

​53.	Henson, S. M. & Akbar, A. N. KLRG1—more than a marker for T cell senescence. Age (Omaha). 31, 285–291 (2009). 

​54.	Ainciburu, M. et al. Uncovering perturbations in human hematopoiesis associated with healthy aging and myeloid malignancies at single-cell resolution. Elife 12, (2023). 

​55.	Ayoub, M., Abou Jaoude, C., Ayoub, M., Hamade, A. & Rima, M. The immune system and cellular senescence: A complex interplay in aging and disease. Immunology 177, 149–169 (2026). 

​56.	Karakaslar, E. O. et al. Transcriptional activation of Jun and Fos members of the AP-1 complex is a conserved signature of immune aging that contributes to inflammaging. Aging Cell 22, e13792 (2023). 

​57.	Delpoux, A. et al. FOXO1 constrains activation and regulates senescence in CD8 T cells. Cell Rep. 34, (2021). 

​58.	Wang, Y. et al. GATA-3 controls the maintenance and proliferation of T cells downstream of TCR and cytokine signaling. Nat. Immunol. 14, 714–722 (2013). 

​59.	Prevete, I. et al. Similarities and Differences between Younger and Older Disease Onset Patients with Newly Diagnosed Systemic Lupus Erythematosus Similarities and Differences between Younger and Older SLE Patients / I. Prevete et Al. Clinical and Experimental Rheumatology vol. 41 https://www.r-project.org (2022). 

​60.	Okamura, R. M. et al. Redundant regulation of T cell differentiation and TCRα gene expression by the transcription factors LEF-1 and TCF-1. Immunity 8, (1998). 

​61.	Xing, S. et al. Tcf1 and Lef1 are required for the immunosuppressive function of regulatory T cells. Journal of Experimental Medicine 216, (2019). 

​62.	Parse Biosciences. 10 Million Human PBMCs in a Single Experiment. https://www.parsebiosciences.com/datasets/10-million-human-pbmcs-in-a-single-experiment (2025). 

​63.	Niemand, C. et al. Activation of STAT3 by IL-6 and IL-10 in primary human macrophages is differentially modulated by suppressor of cytokine signaling 3. The journal of immunology 170, 3263–3272 (2003). 

​64.	Finbloom, D. S. & Winestock, K. D. IL-10 induces the tyrosine phosphorylation of tyk2 and Jak1 and the differential assembly of STAT1 alpha and STAT3 complexes in human T cells and monocytes. J. Immunol. 155, 1079–1090 (1995). 

​65.	Szałata, A. et al. A benchmark for prediction of transcriptomic responses to chemical perturbations across cell types. Adv. Neural Inf. Process. Syst. 37, 20566–20616 (2024). 

​66.	Nourisa, J. et al. geneRNIB: a living benchmark for gene regulatory network inference. bioRxiv 2022–2025 (2025). 

​67.	Salignon, J. et al. Pasta, an age-shift transcriptomic clock, maps the chemical and genetic determinants of aging and rejuvenation. Preprint at https://doi.org/10.1101/2025.06.04.657785 (2025). 

​68.	Elli, E. M., Baratè, C., Mendicino, F., Palandri, F. & Palumbo, G. A. Mechanisms Underlying the Anti-inflammatory and Immunosuppressive Activity of Ruxolitinib. Frontiers in Oncology vol. 9 Preprint at https://doi.org/10.3389/fonc.2019.01186 (2019). 

​69.	Griveau, A., Wiel, C., Ziegler, D. V., Bergo, M. O. & Bernard, D. The JAK1/2 inhibitor ruxolitinib delays premature aging phenotypes. Aging Cell 19, (2020). 

​70.	Hao, H. et al. Ruxolitinib Delays Nucleus Pulposus Cell Senescence in Rat Intervertebral Discs. JOR Spine 8, e70044 (2025). 

​71.	Yang, B. et al. Ruxolitinib-based senomorphic therapy mitigates cardiomyocyte senescence in septic cardiomyopathy by inhibiting the JAK2/STAT3 signaling pathway. Int. J. Biol. Sci. 20, 4314 (2024). 

​72.	Tamura, T., Yanai, H., Savitsky, D. & Taniguchi, T. The IRF family transcription factors in immunity and oncogenesis. Annu. Rev. Immunol. 26, 535–584 (2008). 

​73.	Yu, H., Pardoll, D. & Jove, R. STATs in cancer inflammation and immunity: a leading role for STAT3. Nat. Rev. Cancer 9, 798–809 (2009). 

​74.	O’Shea, J. J. et al. The JAK-STAT pathway: impact on human disease and therapeutic intervention. Annu. Rev. Med. 66, 311–328 (2015). 

​75.	Darnell Jr, J. E., Kerr, lan M. & Stark, G. R. Jak-STAT pathways and transcriptional activation in response to IFNs and other extracellular signaling proteins. Science (1979). 264, 1415–1421 (1994). 

​76.	Levy, D. E. & Darnell Jr, J. E. Stats: transcriptional control and biological impact. Nat. Rev. Mol. Cell Biol. 3, 651–662 (2002). 

​77.	Quigley, M. et al. Transcriptional analysis of HIV-specific CD8+ T cells shows that PD-1 inhibits T cell function by upregulating BATF. Nat. Med. 16, 1147–1151 (2010). 

​78.	Kurachi, M. et al. The transcription factor BATF operates as an essential differentiation checkpoint in early effector CD8+ T cells. Nat. Immunol. 15, 373–383 (2014). 

​79.	Shen, X. et al. Nonlinear dynamics of multi-omics profiles during human aging. Nat. Aging 4, 1619–1634 (2024). 

​80.	Bronikowski, A. M. et al. Sex-specific aging in animals: perspective and future directions. Aging Cell 21, e13542 (2022). 

​81.	Tower, J. Sex-specific regulation of aging and apoptosis. Mech. Ageing Dev. 127, 705–718 (2006). 

​82.	Kogut, I., Scholz, J. L., Cancro, M. P. & Cambier, J. C. B cell maintenance and function in aging. in Seminars in immunology vol. 24 342–349 (2012). 

​83.	Cancro, M. P. et al. B cells and aging: molecules and mechanisms. Trends Immunol. 30, 313–318 (2009). 

​84.	Frasca, D. & Blomberg, B. B. Effects of aging on B cell function. Curr. Opin. Immunol. 21, 425–430 (2009). 

​85.	Wang, Y. et al. Integrating single-cell RNA and T cell/B cell receptor sequencing with mass cytometry reveals dynamic trajectories of human peripheral immune cells from birth to old age. Nat. Immunol. 26, 308–322 (2025). 

​86.	Biosciences, P. 10 Million Human PBMCs in a Single Experiment. Accessed 2025 September 15 (2025). 

​87.	Nourisa, J. et al. geneRNIB: a living benchmark for gene regulatory network inference. bioRxiv 2022–2025 (2025). 

​88.	Heumos, L. et al. Best practices for single-cell analysis across modalities. Nat. Rev. Genet. 24, 550–572 (2023). 

​89.	Dom\’\inguez Conde, C. et al. Cross-tissue immune cell analysis reveals tissue-specific features in humans. Science (1979). 376, eabl5197 (2022). 

​90.	Antoine, P. & Nourisa, J. 20th Place Solution Writeup For Open Problems - Single-cell Perturbations Competition. Preprint at (2023). 

​91.	Badia-i-Mompel, P. et al. decoupleR: ensemble of computational methods to infer biological activities from omics data. Bioinformatics advances 2, vbac016 (2022). 

​92.	Fisher, D. J. Two-stage individual participant data meta-analysis and generalized forest plots. Stata J. 15, 369–396 (2015). 

​93.	McKnight, P. E. & Najab, J. Mann-whitney U test. The Corsini encyclopedia of psychology 1 (2010). 

​94.	Fang, Z., Liu, X. & Peltz, G. GSEApy: a comprehensive package for performing gene set enrichment analysis in Python. Bioinformatics 39, btac757 (2023). 

​ ​ 

 

Methods 

Curation of public datasets 

Here, we describe the preprocessing of individual public datasets used in this study. Figure 1 and Supplementary Figure 1A summarize the key characteristics of each dataset, including the total number of single cells, the number of donors, and the distribution of samples across age, sex, and ethnicity. All reported statistics were computed after applying the quality control procedures described in the following section. 

OneK1K cohort 

The OneK1K cohort ​26​ was accessed via CELLxGENE (https://cellxgene.cziscience.com/collections/dde06e0f-ab3b-46be-96a2-a8082383c4a1). It includes PBMCs from 981 European individuals aged over 17 years at recruitment. Only healthy, unstimulated individuals were included in this analysis. PBMCs were processed using the 10x Genomics Single Cell 3′ Library and Gel Bead Kit and sequenced on an Illumina NovaSeq 2000 platform. CellRanger (v2.2.0) was used to generate the gene expression matrix.  

 ABF300 cohort 

The ABF300 cohort ​27​ consists of PBMCs from 166 healthy, non-obese, and non-smoking Caucasian individuals aged 25–85 years. This cross-sectional and short-term longitudinal study was conducted between 2018 and 2021. A total of 317 samples were processed using 10x Genomics 3′ single-cell RNA-seq with feature barcoding, along with TCR and BCR sequencing. Libraries were sequenced on an Illumina NovaSeq S4. Data were processed with Cell Ranger (v7.0.0) and Seurat (v4.0.5), with demultiplexing performed using both hashtag- and genotype-based approaches. The dataset is available from the Synapse repository (accession: syn49637038). 

Zhang cohort 

This The immune-aging atlas cohort published was obtained from the Synapse repository (accession: syn61609846) corresponding to the immune-aging atlas published by Zhang et al ​8585​ . This study profileds PBMCs across the entire human lifespan. For our analysis, we included 33 participants aged 20 to 90 years with available scRNA-seq data. PBMCs were processed using the 10x Genomics 5′ single-cell RNA-seq protocol with paired TCR/BCR profiling and sequenced on Illumina platforms. The processed Seurat object (scRNA-seqProcessedLabelledObject.rds) was downloaded, and only healthy donors were retained for analysis. Of note, we only used this cohort for testing the aging clock prediction. 

AIDA cohort 

The AIDA Freeze v1 ​2828​, comprises approximately 1.26 million circulating immune cells profiled from 619 healthy donors across seven population groups in five Asian countries. Library preparation was performed using the 10x Genomics 5′ scRNA-seq protocol, and raw read processing and demultiplexing were performed centrally with the Illumina DRAGEN Single-Cell RNA pipeline. 

Perez SLE cohort 

This cohort, corresponding to the study by Perez et al ​2929​, was accessed via CELLxGENE (https://cellxgene.cziscience.com/collections/436154da-bcf1-4130-9c8b-120ff9a888f2). It includes PBMCs from 162 SLE cases and 99 healthy controls profiled by multiplexed single-cell RNA sequencing (mux-seq). Libraries were prepared using the 10x Genomics Chromium platform and sequenced on an Illumina NovaSeq. Cell Ranger (v3.1) was used for initial data processing. The processed h5ad file was downloaded, Ensembl gene identifiers were converted to gene symbols, and raw counts were extracted. 

 

SoundLife cohort 

The SoundLife cohort was obtained from ​1818​ . It contains approximately 12M single-cell RNA data of PBMCs from 96 donors collected longitudinally, sequenced using the 10x Genomics Chromium 3′ v3 chemistry. The cohort comprises healthy young adults (25–35 years; N = 47) and older adults (55–65 years; N = 45), with balanced sex distribution. Participants were recruited from the greater Seattle, WA area and screened to exclude individuals with a history of chronic or autoimmune diseases, chronic infections, or severe allergies. The dataset includes both cytomegalovirus-positive and -negative individuals, longitudinal measurements at multiple time points following influenza vaccination, as well as baseline samples. The data were provided with prior quality control and cell-type annotations. 

ParseBioscience cohort 

This ParseBioscience cohort , sourced from ​8686​ , contains approximately 10M single-cell RNA-seq profiles of PBMCs from 12 donors (6 male and 6 female). Cells were exposed to 90 cytokine perturbations for 24 hours, with PBS-treated samples serving as controls. Sequencing data were processed using the ParseBiosciences Analysis Pipeline v1.4.0, and the resulting data were provided with quality control and cell-type annotations applied. Since the publicly provided dataset did not include age information for the donors, we obtained this information through direct communication with the authors. 

OPSCA dataset  

We The OPSCA dataset sourced this data from ​8787​ , which originates from the 2023 Open Problems: Single Cell Perturbation competition. It consists of single-cell drug perturbation data on PBMCs, where the cells were distributed across 96-well plates, with two columns reserved for positive controls (Dabrafenib and Belinostat) and one column for the negative control compound dimethyl sulfoxide (DMSO). The positive controls were chosen for their well-characterized transcriptional effects. The remaining wells on each plate were assigned to 144 distinct compounds, one per well. Experiments were performed using cells from three donors, resulting in a total of six plates (two per donor). Samples from each row were pooled prior to sequencing, and read processing was performed by the study organizers using the Cell Ranger pipeline.  

Generation of drug perturbation dataset 

A complementary drug perturbation dataset was generated from PBMCs of seven healthy donors. PBMCs were isolated using SepMate tubes (STEMCELL Technologies) and resuspended in RPMI 1640 medium (Gibco) supplemented with 10% fetal bovine serum (Biowest). In a total volume of 200 μL per well, 0.5 × 10⁶ PBMCs were cultured in round-bottom 96-well plates (SARSTEDT) and stimulated ex vivo with 1 μM ruxolitinib (InvivoGen) plus 10 ng/mL lipopolysaccharide (LPS; Sigma) or maintained in RPMI medium as control for 18 h at 37 °C and 5% CO₂. Single-cell suspensions were processed using the Chromium X instrument and the Chromium GEM-X Single Cell 3′ Reagent Kits (v4, 10x Genomics) to generate single-cell RNA-seq (scRNA-seq) libraries. Libraries were sequenced on Illumina NovaSeq 6000 platform. The resulting dataset underwent the same quality control, cell type annotation, and normalization procedures as described above. 

Data preprocessing 

Quality control was performed at both the gene and cell levels. We applied the following thresholds: minimum 100 genes per cell, maximum 5,000 genes per cell ​8888​, and minimum 10 cells per gene per donor. Cell type annotations were performed consistently across datasets using CellTypist ​8989​. The coarse model classified cells into five major immune populations: CD4+ T cells, CD8+ T cells, NK cells, B cells, and monocytes. For the datasets of SoundLife and ParseBioscience, we used the already available cell labels. For pseudobulk analysis, raw single-cell counts were aggregated by summing counts across cells within each cell type, donor, time (if multiple measurements per donor), and well (if given). We excluded bulked samples with fewer than 10 single cells ​9090​. Data were normalized using a shifted logarithm transformation: sequencing depth was corrected with the Scanpy normalize_total function, followed by a log1p transformation to stabilize variance ​8888​.  

Inference of transcription factor activity 

To estimate TF activity scores, we first inferred GRNs from single-cell data of discovery cohorts. Only genes observed in at least 500 single cells were retained to ensure sufficient statistical power.  GRN inference was performed by computing pairwise Spearman correlations between all genes within each cell type and cohort, followed by restricting the set of putative regulators to a curated list of known TFs ​8787​, retaining only TF–gene pairs with significant correlations (FDR < 0.05), and selecting the top 100,000 edges per cell type and condition.  

We benchmarked this correlation-based GRN inference strategy against state-of-the-art GRN inference methods using the geneRNIB evaluation framework ​8787​. Despite its simplicity, the Spearman correlation approach demonstrated competitive performance across all evaluation metrics while remaining substantially more computationally efficient (Supplementary Note). This computationally efficient approach enabled us to infer GRNs from single-cell data, as single-cell data has shown superior biological relevance in GRN inference compared to pseudobulked alternatives ​8787​.  

The inferred GRN models for each cell type and cohort showed varying degrees of overlap in TF–gene pairs across cohorts (Supplementary Fig. 4C). To harmonize these models, we constructed a consensus GRN for each cell type by retaining TF–gene edges present in at least two cohorts and exhibiting a consistent direction of effect (regulatory weight) across all datasets. The consensus networks contained 60,000–90,000 edges, with the highest overlap observed among CD8T, CD4T, and NK cells, consistent with their shared lineage (Supplementary Fig. 4B). These cell type–specific consensus GRNs were used for all subsequent analyses. 

TF activity scores were then inferred by computing the dot product between each GRN adjacency matrix and the corresponding gene expression matrix (Supplementary Fig. 4A), using Decoupler univariate linear model ​9191​. We used pseudobulked expression data to estimate TF activity, which has been shown to yield more stable results than single-cell level calculations ​9191​.  

Identification of transcription factors associated with aging, disease, and drug perturbation 

To identify TFs associated with aging using discovery cohorts, we computed Spearman correlations between TF activity scores and pseudobulked samples for each cohort and cell type. Of note, for Perez SLE cohort, we only considered the healthy samples for this analysis. This produced correlation coefficients (range: –1 to 1) along with p-values for each TF, cell type, and dataset. We then performed a meta-analysis across cohorts using Fisher’s method ​9292​ to combine evidence. Multiple testing correction was applied to the combined p-values, and TFs with an adjusted meta p-value < 0.05, a consistent slope, and a correlation above 0.1 across cohorts were considered significantly associated with aging. For validation of age-associated TFs in the SoundLife cohort, we correlated TF activity with age for each TF and cell type, and considered associations significant if FDR < 0.05 and correlation > 0.1. 

To identify TFs associated with SLE, we compared SLE patients with healthy individuals in the Perez cohort. Specifically, we applied a Mann–Whitney U test ​9393​ to assess differences in TF activity between healthy and disease samples for each TF and cell type, followed by multiple testing correction within each cell type. For the cytokines and drug perturbation datasets (discovery and validation), we used a mixed-effects model to identify TFs with significantly with altered activities, with perturbation included as a fixed effect and donor as a random effect. Multiple testing correction was applied separately for each cell type, and TFs with adjusted p-values < 0.05 were considered significant.  

Gene set enrichment analysis 

Gene set enrichment analysis was performed using cell type–specific sets of significant TFs associated with aging, SLE, and ruxolitinib. For each cell type and condition, TFs with increased or decreased activity were analyzed separately. Only TFs with adjusted p-values below 0.05 were included in the analysis. Enrichment was conducted using the MSigDB Hallmark 2020 gene set collection as the reference database, implemented via the GSEApy package ​9494​.  

Construction of GRN-integrated aging clocks  

We built cell type–specific aging clocks using genes derived from GRN models as predictor features. The number of genes used per clock ranged from approximately 4,000 to 5,000 depending on the cell type, with roughly 2,000 genes shared across cell types and varying degrees of overlap among other genes (Supplementary Fig. 1E). Models were trained on gene expression data from 1,200 donors across the OneK1K and ABF300 cohorts to predict chronological age.  

We tested multiple regression approaches, including Ridge regression, Gradient Boosting, Elastic Net, and multilayer perceptrons (MLPs). Ridge regression, tuned via leave-one-dataset-out cross-validation, consistently achieved the best performance in both cross-validation predictions and held-out test cohorts (results not shown). We also experimented with training models directly on single-cell data by aggregating median expression values per donor. However, models trained on pseudobulked data outperformed these single-cell based models (results not shown). Predictive performance was evaluated using the Spearman correlation between predicted and actual chronological age. 

Calculation of transcriptional regulators of aging clocks 

Because the aging clocks were built using target genes from GRN models, we quantified the regulatory contribution of TFs to each clock’s predictions. After training the models, we obtained the regression coefficients of the target genes, which are quantitative values where magnitude reflects the strength of the effect and the sign indicates the direction—for example, a positive coefficient means that higher gene expression leads to an increased predicted age. We then estimated the contribution of individual TFs to the aging clock output using: 

[Equation] 

where Am represents the inferred contribution of each TF (m) to the clock, [Equation] is the TF–target gene weight matrix derived from the GRN, and [Equation] corresponds to the learned gene weights from the trained aging clock. This approach allows direct mapping of the model’s predictive features to upstream regulatory factors, providing a transcriptional interpretation of the clocks. Aₘ contains continuous positive and negative values; for example, a positive value indicates that increased activity of the TF is associated with a higher predicted age. 

Age acceleration and rejuvenation analysis using aging clocks 

 We used aging clocks to estimate age acceleration or rejuvenation under given conditions. For the disease analysis in the SLE cohort, predicted age was compared between donors with and without reported SLE. Statistical significance was assessed using a Wilcoxon rank-sum test followed by FDR correction. Age acceleration was defined by a significant adjusted p-value (< 0.05) and an increased slope. This analysis was performed once for all age groups and once separately for young and old age groups to examine the effect of chronological age on SLE-associated age acceleration, using two thresholds (40 and 50 years) to increase robustness. For the cytokine and drug perturbation datasets (discovery and validation), we applied a mixed-effects model with perturbation as a fixed effect and donor as a random effect. Multiple testing correction was applied, and an adjusted p-value <0.05 was used to determine significance. Rejuvenation was defined as a significant decrease in predicted age relative to control, whereas acceleration was defined as a significant increase in predicted age. 

 