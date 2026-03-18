# Tools — Overview

This folder contains the biomni tool library (`tool/`) and per-module function reference docs.

## `tool/` — Python Modules

| File | Description |
|------|-------------|
| `__init__.py` | Imports tool-decorated functions from all biomni tool modules. |
| `tool_registry.py` | Manages registration and indexing of tools with a pandas DataFrame for organising tool metadata and IDs. |
| `biochemistry.py` | Analyses circular dichroism spectroscopy data to determine secondary structure and thermal stability of biomolecules. |
| `bioimaging.py` | Performs medical image segmentation and analysis using deep learning models (nnU-Net). |
| `bioengineering.py` | Predicts intrinsically disordered regions in protein sequences using the IUPred2A web server. |
| `biophysics.py` | Analyses DNA Damage Response network alterations and dependencies in cancer samples from genomic data. |
| `cancer_biology.py` | Reconstructs DNA Damage Response networks and identifies disruptions in cancer genomic samples. |
| `cell_biology.py` | Quantifies cell cycle phases from Calcofluor white-stained microscopy images. |
| `database.py` | Retrieves HPO term names and performs sequence analysis with NCBI BLAST. |
| `genetics.py` | Performs liftover of genomic coordinates between hg19 and hg38 genome builds. |
| `genomics.py` | Transfers cell type annotations between single-cell RNA-seq datasets using multiple alignment and classification methods. |
| `glycoengineering.py` | Scans protein sequences for N-linked glycosylation sequons and provides other glycoengineering utilities. |
| `immunology.py` | Performs ATAC-seq peak calling and differential accessibility analysis using MACS2. |
| `lab_automation.py` | Loads PyLabRobot documentation and provides tools for robotic liquid handling automation setup. |
| `literature.py` | Fetches supplementary information and materials for scientific papers given their DOI. |
| `microbiology.py` | Optimises anaerobic digestion process conditions to maximise methane yield or VFA production. |
| `molecular_biology.py` | Annotates open reading frames in DNA sequences and analyses molecular biology features. |
| `pathology.py` | Analyses aortic diameter and geometry from cardiovascular imaging data. |
| `pharmacology.py` | Runs protein-ligand docking simulations using DiffDock with SMILES strings. |
| `physiology.py` | Reconstructs 3D facial anatomy models from MRI head scans. |
| `protocols.py` | Integrates with the protocols.io API to search and retrieve biological protocols based on natural language queries. |
| `support_tools.py` | Executes Python code in a persistent REPL environment with matplotlib plotting support. |
| `synthetic_biology.py` | Engineers bacterial genomes by integrating therapeutic genetic parts for delivery applications. |
| `systems_biology.py` | Answers questions about DNA sequences using the ChatNT language model. |
| `example_mcp_tools/pubmed_mcp.py` | Provides an MCP server tool for searching PubMed articles and retrieving article metadata. |

## Per-Module Function Reference Docs (`.md` files)

Each `.md` file in this folder documents the public functions of the corresponding module:
`database.md`, `genetics.md`, `genomics.md`, `immunology.md`, `literature.md`, `pharmacology.md`, `physiology.md`, `protocols.md`, `support_tools.md`, `synthetic_biology.md`, `systems_biology.md`.
