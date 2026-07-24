# CellxGene Census — Overview

Remote database accessible via `cellxgene_get_anndata` / `cellxgene_query_obs` in `genomics.py`.
No local files — data is streamed on demand from the Chan Zuckerberg CellxGene Census (S3).

**Snapshot: 2025-11-08**
- 1,845 datasets
- 217.8M total cell records · **125.5M unique cells**
- Human: 158.9M cells · Mouse: 43.7M cells

---

## Modality / Assay

**scRNA-seq dominant** (dissociated cells or nuclei). No standalone ATAC-seq. `10x multiome` (3M cells) provides paired RNA+ATAC but is accessed RNA-side only through the Census.

### Human assays (top)
| Assay | Cells |
|---|---|
| 10x 3' v3 | 97,269,301 |
| 10x 3' v2 | 28,169,666 |
| 10x 5' v2 | 9,863,654 |
| 10x 5' v1 | 7,902,378 |
| sci-RNA-seq3 | 5,230,353 |
| 10x multiome (RNA side) | 3,033,426 |
| 10x 5' transcription profiling | 2,244,607 |
| Drop-seq | 1,048,377 |
| Smart-seq2 | 267,948 |
| + others | … |

### Suspension type
- Dissociated cells: 97.2M
- Single nuclei (snRNA-seq): 61.7M

---

## Tissues (human, top 30)
| Tissue | Cells |
|---|---|
| Brain | 48,581,856 |
| Blood | 31,915,115 |
| Eye | 13,075,889 |
| Lung | 10,181,125 |
| Breast | 7,175,644 |
| Heart | 6,062,531 |
| Small intestine | 4,191,203 |
| Liver | 2,979,976 |
| Lymph node | 2,941,362 |
| Colon | 2,631,544 |
| Kidney | 2,544,478 |
| Endocrine gland | 1,984,496 |
| Bone marrow | 1,491,738 |
| Central nervous system | 1,450,954 |
| Stomach | 1,446,973 |
| Spleen | 1,423,844 |
| Skin | 1,194,301 |
| Respiratory system | 1,181,122 |
| Large intestine | 1,176,404 |
| Adipose tissue | 1,075,748 |
| Musculature | 995,567 |
| Uterus | 993,070 |
| Pancreas | 871,649 |
| Placenta | 760,271 |
| Adrenal gland | 718,211 |
| Esophagus | 684,152 |
| Exocrine gland | 658,495 |
| Intestine | 645,694 |
| Mucosa | 639,300 |

---

## Disease (human, top 30)
| Disease | Cells |
|---|---|
| **normal** | **115,420,765** |
| Cytomegalovirus infection | 7,895,789 |
| COVID-19 | 5,170,841 |
| Dementia | 2,530,515 |
| Parkinson disease | 1,810,127 |
| Glioblastoma | 1,745,435 |
| Malignant ovarian serous tumor | 1,549,547 |
| Alzheimer disease | 1,486,303 |
| Lung adenocarcinoma | 1,425,535 |
| Breast cancer | 1,295,700 |
| Dilated cardiomyopathy | 934,441 |
| **Systemic lupus erythematosus** | **777,258** |
| Colon adenocarcinoma | 646,215 |
| B-cell non-Hodgkin lymphoma | 642,851 |
| Invasive ductal breast carcinoma | 607,905 |
| Neuroblastoma | 592,116 |
| Atherosclerosis | 538,430 |
| Chronic kidney disease | 477,200 |
| **Crohn disease** | **452,965** |
| Gastric cancer | 429,129 |
| Interstitial lung disease | 316,801 |
| Pulmonary fibrosis | 268,932 |
| Acute kidney failure | 256,320 |
| Non-small cell lung carcinoma | 241,592 |

> SLE and Crohn highlighted as directly relevant to CIIM/HiRA work.

---

## Perturbations
No dedicated perturbation atlas in the Census (no drug/cytokine conditions flagged in the `disease` field). For perturbations use the HiRA op/parse datasets in `datalake/omics/`.

---

## Sex & donors (human)
- Male: 77.7M · Female: 69.1M · Unknown: 12.2M

---

## Mouse
43.7M cells — dominated by sci-RNA-seq3 (34M, likely the Tabula Muris Senis whole-organism atlas).
Access via `organism="mus_musculus"` in all `cellxgene_*` functions.

---

## Tabula Sapiens
3,408,625 cells (~2.7% of Census) · 28 organs · healthy only · scRNA-seq (10x + Smart-seq2).
One of many multi-organ atlases in the Census. Dataset IDs per organ listed below for convenience.

| Organ | dataset_id |
|---|---|
| All Cells | 53d208b0-2cfd-4366-9866-c3c6114081bc |
| Immune | c5d88abe-f23a-45fa-a534-788985e93dad |
| Blood | 983d5ec9-40e8-4512-9e65-a572a9c486cb |
| Bone Marrow | 4f1555bc-4664-46c3-a606-78d34dd10d92 |
| Thymus | 0ced5e76-6040-47ff-8a72-93847965afc0 |
| Lymph Node | 18eb630b-a754-4111-8cd4-c24ec80aa5ec |
| Spleen | cee11228-9f0b-4e57-afe2-cfe15ee56312 |
| Lung | 0d2ee4ac-05ee-40b2-afb6-ebb584caa867 |
| Liver | 6d41668c-168c-4500-b06a-4674ccf3e19d |
| Kidney | 2423ce2c-3149-4cca-a2ff-cf682ea29b5f |
| Heart | e6a11140-2545-46bc-929e-da243eed2cae |
| Skin | 0041b9c3-6a49-4bf7-8514-9bc7190067a7 |
| Pancreas | ff45e623-7f5f-46e3-b47d-56be0341f66b |
| Small Intestine | a357414d-2042-4eb5-95f0-c58604a18bdd |
| Large Intestine | 7357cee7-9f7f-4ab0-8cec-90de8f047e38 |
| Stomach | 9ba03780-4b13-44bc-a7d3-ce532ea0a856 |
| Fat | 5e5e7a2f-8f1c-42ac-90dc-b4f80f38e84c |
| Vasculature | a2d4d33e-4c62-4361-b80a-9be53d2e50e8 |
| Endothelium | 5a11f879-d1ef-458a-910c-9b0bdfca5ebf |
| Muscle | 1c9eb291-6d31-47e1-96b2-129b5e1ae64f |
| Eye | a0754256-f44b-4c4a-962c-a552e47d3fdc |
| Mammary | 2ba40233-8576-4dec-a5f1-2adfa115e2dc |
| Ovary | bb78adbb-1428-4468-bad0-63602bb974e9 |
| Uterus | 6ec405bb-4727-4c6d-ab4e-01fe489af7ea |
| Prostate | d77ec7d6-ef2e-49d6-9e79-05b7f8881484 |
| Testis | ec6ef004-5f30-4a40-b282-980cca20a561 |
| Bladder | e5c63d94-593c-4338-a489-e1048599e751 |
| Trachea | d8732da6-8d1d-42d9-b625-f2416c30054b |
| Salivary Gland | f01bdd17-4902-40f5-86e3-240d66dd2587 |
| Tongue | 55cf0ea3-9d2b-4294-871e-bb4b49a79fc7 |
| Ear | d45aca3a-ddb8-4185-a462-eff1e0c7af2e |
| Neural | 6e4acdae-59ef-452b-a6d4-260cba368586 |
| Germline | b806712d-18b0-454c-a0fe-9909159e07c7 |
| Stromal | a68b64d8-aee3-4947-81b7-36b8fe5a44d2 |
| Epithelium | 97a17473-e2b1-4f31-a544-44a60773e2dd |
