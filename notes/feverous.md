# FEVEROUS Notes

**Basics:**
- [Paper](https://arxiv.org/abs/2106.05707)
- [Dataset](https://fever.ai/dataset/feverous.html)
- 2021
- Dataset of claims, verified against Wikipedia pages
- 87,026 examples
- Human annotation

**Problem it is solving:**
- Few datasets rely on structured information, primarily tables

**Claims:**
- Supported, refuted, or not enough information via evidence
- Manually constructed and verified
- Claims are human-generated from a sample
- Samples are from wikipedia pages, either four consecutive sentences or a table
- Three claims were generated for each sample:
    1. Claims using highlight information only
    2. Claims based on the highlight, but using external information as well
    3. Mutated Claim: can involve multi-hop reasoning

**Evidence:**
- Can be table cell, single sentence, or combination of multiple sentences and cells
- Sentence: just some wikipedia sentence
- Table: wikipedia infoboxes and tables

**Baseline:**
- Determine veracity of a claim by:
    - Retrieve evidence $E$, can be a sentence or table cell
    - Assign label (support, refute, not enough info) to the claim
