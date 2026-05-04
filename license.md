# License & Commercial Use Restrictions


## 📋 Tools & Software Licenses

### Agentic Immunology Code
- **License**: Internal (will depend on our terms)

### BiomNI Integration
- **Code License**: Apache 2.0 (commercial-friendly)
- **⚠️ Data sources**: Many BiomNI integrated datasets have non-commercial restrictions (see above)
- **Mitigation**: BiomNI provides `commercial_mode=True` flag to exclude restricted datasets


#### 🚩 Non-Commercial Only 

These datasets **prohibit commercial use entirely**. Do not include in any commercial product without purchasing a commercial license.

| Dataset | License | Used For | Contact |
|---------|---------|----------|---------|
| **DDInter** | Non-commercial | Drug-drug interactions | [DDInter](http://ddinter.scbdd.com/) |
| **DisGeNET** | CC BY-NC-SA 4.0 | Gene-disease associations | [DisGeNET Support](https://support.disgenet.com/) |
| **BindingDB** | CC BY-NC | Drug binding affinities | [BindingDB](https://www.bindingdb.org/) |
| **Enamine** | Proprietary | Compound library | [Enamine](https://www.enamine.net/) |
| **COSMIC** | Non-commercial license | Cancer mutations | [COSMIC](https://cancer.sanger.ac.uk/cosmic) |
| **miRTarBase** | Non-commercial | miRNA targets | [miRTarBase](https://mirtarbase.cuhk.edu.cn/) |
| **miRDB** | Non-commercial | miRNA targets | [miRDB](http://mirdb.org/) |

---

#### ⚠️ Conditional Use — Verify Per Source

These datasets are generally open but may contain restricted sub-components.

| Dataset | License | Notes |
|---------|---------|-------|
| **MSigDB** | Mixed | Some gene sets from Broad Institute require institutional license |
| **ChEMBL** | CC BY 4.0 | Open, but verify source compound licenses |
| **OpenGWAS** | Varies | Depends on underlying GWAS study permissions |

---

#### 🟢 Safe for Commercial Use — Open Licenses

These datasets and tools are fully open and suitable for commercial applications.

| Dataset | License | Used For |
|---------|---------|----------|
| **Gene Ontology** | CC BY 4.0 | Gene annotation |
| **Human Protein Atlas** | CC BY-SA 3.0 | Protein expression |
| **DepMap** | CC BY 4.0 | Gene dependency screens |
| **OmniPath** | CC BY 4.0 | Signaling networks |
| **NicheNet** | CC0 / Public Domain | Cell-cell communication |
| **DICE** | Published study (Schmiedel et al. 2018) | Immune cell eQTLs |
| **PrimeKG** | Open knowledge graph | Biomedical knowledge |
| **Reactome** | CC BY 4.0 | Pathway database |
| **UniProt** | CC BY 4.0 | Protein sequences |
| **AlphaFold DB** | CC BY 4.0 | Protein structures |
| **String DB** | CC BY 4.0 | Protein interactions |

---


## ✅ Commercial Use Checklist

If commercializing this project:

- [ ] **Remove or license** all datasets marked 🚩 above
- [ ] **Document data sources** in terms of service / privacy policy
- [ ] **Use `commercial_mode=True`** if using BiomNI integration
- [ ] **Update terms of service** to disclose data sources and restrictions
- [ ] **Create separate codebase** if maintaining both academic and commercial versions

---

## 🔄 Recommended Alternatives

For commercial-safe replacements:

| Restricted Dataset | Open Alternative | Notes |
|-------------------|------------------|-------|
| DDInter | DrugBank, PubChem | Requires attribution |
| DisGeNET | OpenTargets | Open platform, CC BY 4.0 |
| BindingDB | PDBbind, ChEMBL | Verify sub-components |
| COSMIC | OpenTargets Platform | Cancer mutations |
| miRTarBase | TargetScan, miRDB API (with restrictions) | Limited alternatives |

