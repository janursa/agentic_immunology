# CLAMBER: A Benchmark of Identifying and Clarifying Ambiguous Information Needs in Large Language Models

## Abstract
Large language models (LLMs) are increasingly used to meet user information needs, but their effectiveness in dealing with user queries that contain various types of ambiguity remains unknown, ultimately risking user trust and satisfaction. To this end, we introduce CLAMBER, a benchmark for evaluating LLMs using a well-organized taxonomy. Building upon the taxonomy, we construct ∼12K high-quality data to assess the strengths, weaknesses, and potential risks of various off-the-shelf LLMs. Our findings indicate the limited practical utility of current LLMs in identifying and clarifying ambiguous user queries, even enhanced by chain-of-thought (CoT) and few-shot prompting. These techniques may result in overconfidence in LLMs and yield only marginal enhancements in identifying ambiguity. Furthermore, current LLMs fall short in generating high-quality clarifying questions due to a lack of conflict resolution and inaccurate utilization of inherent knowledge. In this paper, CLAMBER presents a guidance and promotes further research on proactive and trustworthy LLMs. Dataset: https://github.com/SCUNLP/CLAMBER.

## Methods

### Taxonomy
CLAMBER organizes query ambiguity into three primary dimensions, spanning input understanding and task completion, further split into eight fine-grained categories:

**1. Epistemic Misalignment (EM)** — occurs when the LLM's inherent knowledge conflicts with the query.
- *Unfamiliar*: query contains entities/facts unfamiliar to (or contradicting) the LLM's knowledge (e.g., "Find the price of Samsung Chromecast").
- *Contradiction*: query contains self-contradictions inferable from the LLM's knowledge (e.g., a classification task where provided examples support two different category interpretations).

**2. Linguistic Ambiguity (LA)** — a word, phrase, or statement can be interpreted in multiple ways due to imprecise meaning (syntactic/pragmatic ambiguity omitted as uncommon in IR).
- *Lexical*: individual terms with multiple meanings (e.g., "source of Nile" — the river or the board game).
- *Semantic*: lack of context leads to multiple interpretations, focused on referent/pronoun ambiguity (e.g., "When did he land on the moon?").

**3. Aleatoric Output (AO)** — input is well-formed but the output is confounded by missing elements, based on the type of missing element:
- *Whom*: missing personal details (e.g., "Suggest me some gifts for my mother").
- *Where*: missing spatial information (e.g., "Tell me how to reach New York").
- *When*: missing temporal elements (e.g., "How many goals did Argentina score in the World Cup?").
- *What*: remaining/other missing task-specific elements (e.g., which version of "Guardians of the Galaxy").

### Data Collection
Each data instance comprises a user query, a binary ambiguity label, and a clarifying question (for ambiguous queries). Sources per category:
- *Unfamiliar*: built from ALCUNA (fabricated new entities to avoid training-data bias); queries with new entities labeled ambiguous, GPT-4 generates clarifying questions.
- *Contradiction*: built from AmbiTask (encodes contradictions between instructions and examples); clarifying questions created via rule-based templates; unambiguous versions created manually by resolving contradictions.
- *Lexical*: built from AmbER (ambiguous entity names) and AmbiPun (ambiguous polysemous words); GPT-4 generates ambiguous queries, clarifying questions, and unambiguous queries.
- *Semantic*: built from AmbiCoref (minimal pairs of ambiguous/unambiguous referents); ambiguous queries obtained by reducing context to a single sentence; unambiguous queries via GPT-4; clarifying questions via rule-based templates.
- *Whom/Where/When/What*: built from AmbigQA (queries with multiple answers = ambiguous, manually categorized into the four subtypes) and Dolly-16K (GPT-4 labels ambiguity, manually verified/classified). All four AO categories share the same set of unambiguous queries due to difficulty crafting category-specific ones.

### Validation
Five linguistic experts validate/revise the dataset: each instance is validated by four experts and consolidated by a fifth, who resolves discrepancies in ambiguity labels and clarifying-question quality.

### Dataset Statistics
∼12K total instances (7,167 non-ambiguous; the ambiguous set spans Unfamiliar 684, Contradiction 600, Lexical 815, Semantic 400, What/Whom/When/Where totaling 3,884 across their sources). Test set: 3,600 instances randomly sampled with balanced positive/negative examples per category (200 each; AO negatives are 800 due to their uniform/shared nature).

### Experimental Design
Two tasks: (1) identifying ambiguity, (2) asking clarifying questions. Models evaluated: Llama2-13B-Chat, Llama2-13B-Instruct, Vicuna-13B, Llama2-70B-Chat, and GPT-3.5-Turbo-16k (ChatGPT). Four prompting schemes: Zero-shot w/o CoT, Zero-shot w/ CoT, Few-shot w/o CoT (2 examples, one ambiguous/one not), Few-shot w/ CoT. Results averaged over 3 prompts per scheme for statistical robustness. Temperature 0 for ChatGPT, 0.5 for open-source LLMs; max 128 new tokens; top-p sampling (p=0.8) for open-source LLMs. Metrics: Accuracy and weighted F1 for identification; BertScore and human-judged "Helpfulness" (binary) for clarifying-question quality; Expected Calibration Error (ECE) and AUROC for confidence/overconfidence analysis (via self-consistency over 4 candidate answers).

## Results

### Task 1: Identifying Ambiguity
- Overall, current LLMs struggle to identify ambiguities. Small-scale LLMs show large accuracy–F1 gaps (e.g., Llama2-70B: 50.37 Acc vs. 34.27 F1 under Zero-shot w/o CoT), tending to over-predict "ambiguous." ChatGPT is the best model but reaches only 54.25% accuracy / 52.77% F1 on average across prompting schemes — leaving considerable room for improvement.
- CoT and few-shot prompting do not reliably help, and can induce overconfidence in small-scale LLMs (e.g., Llama2-13B's ECE rises by +16.66 with CoT and +15.62 with few-shot), degrading calibration and accuracy.
- Increasing the number of few-shot examples yields only marginal gains for ChatGPT; a considerable number of shots (e.g., 12) is needed to beat zero-shot, at the cost of longer inputs that risk exceeding context limits for smaller models. Few-shot examples can teach superficial patterns conflicting with the model's inherent knowledge.
- Fine-grained results (Few-shot w/ CoT): ChatGPT outperforms small-scale LLMs on all Aleatoric Output categories (+5% accuracy, +8% F1 on average), doing best on "whom" but worse on "when"/"where." All LLMs perform poorly on the semantic (pronoun/referent) category. ChatGPT specifically underperforms on the contradiction category (38.00 Acc, 28.17 F1), with 81.97% of its errors being false negatives — attributed to SFT/RLHF training biasing it toward always answering rather than flagging contradictions.

### Task 2: Asking Clarifying Questions
- ChatGPT again outperforms small-scale LLMs, with an average improvement of 10.29 (BertScore/Helpfulness) over the best small-scale model (Vicuna-13B).
- Fine-grained error analysis (400 sampled failure cases from ChatGPT + Few-shot w/CoT, the best-performing configuration) across four error types — Wrong Aspect, Under-specified, Over-specified, Generation error — shows that for Epistemic Misalignment and Linguistic Ambiguity, errors concentrate in Under-specified and Over-specified questions, while for Aleatoric Output, Wrong Aspect dominates (52.25% average error rate). This indicates ChatGPT cannot reliably assess its own knowledge boundaries, fails to fully resolve semantic/conflict nuances, and inaccurately applies inherent knowledge to identify missing elements.

## Conclusions
We introduce CLAMBER, a benchmark for evaluating LLMs in identifying and clarifying ambiguous user queries through a well-organized, three-dimension/eight-category taxonomy. CLAMBER comprises ∼12K high-quality data covering a wide range of ambiguity categories. Using CLAMBER, we assess strengths, weaknesses, and potential risks of various off-the-shelf LLMs. Results show current LLMs still face difficulties achieving optimal performance in both ambiguity identification and clarification, limiting their practical utility in advanced information search applications. CLAMBER is intended as a foundation for enhancing the proactive capabilities of LLMs in addressing ambiguity. Future work will integrate more challenging and comprehensive datasets into CLAMBER based on the proposed taxonomy.

**Limitations**: (1) Sensitivity of Prompts — results likely sensitive to prompt choice; three prompts were used and averaged, but optimality is not guaranteed. (2) Limited LLMs — only 5 LLMs evaluated due to computational constraints; additional models (e.g., PaLM 540B) were not included.
