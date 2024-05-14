- What is it/summary?
We are creating a dataset for complex question-answering using a reference knowledge graph (KG). The questions are a sentence and require multiple conceptual (as well as KG) hops to answer it. The answer is a simple noun (TODO: rephrase), an item in the knowledge graph. More specifically, given a sampled path of items in a knowledge graph, the question will ask what the final item is given the initial item and all properties (edges) in the path. (TODO: include example)

- Why is this important? How is this different from other work? (TODO: related work)
(TODO: need to read some more)

- What is the KG?
A knowledge graph (KG) is a way to store relationships in a graph format. A claim is represented as two nodes and a directed and labeled edge relating them. For example, "UW", "located in", and "Seattle" would be a claim, called a triple. Many claims can be stored, creating a graph with relational knowledge. A popular KG is Wikidata, a community-run KG made with volunteer efforts. It has over 100 million items (nodes) and 10 thousand types of properties (edges). We use a subset of Wikidata, Wikidata5m, containing 5 million items, 825 types of properties, and over 20 million claims. The items are the subset of Wikidata items which have a corresponding Wikipedia page, the claims are the subset which is between those valid items. We are using Wikidata5m for a few reasons. First, many items in Wikidata are quite niche, for instance specific academic articles with little recognition. The Wikipedia-page requirement filters out many niche items while leaving enough items with notoriety. Second, the sheer size of Wikidata is difficult to work with. Wikidata5m is much easier in this respect.

- Pipeline
Examples are created in the following manner. First, a path of nodes is sampled from the KG. This is done using a random walk from a random initial item, augmented with filters and weighting (discussed later). Along with a prompt, the initial item and all properties are passed to an LLM (currently GPT-4) to generate a natural-sounding (TODO?) question. These questions will be filtered by humans on MTurk for various concerns. The final example consists of the generated question, the answer (TODO: specify), and the sampled path.

- Filters:
Filters are used during sampling via random walk to prevent "bad" paths, and therefore examples, from being generated. Some "bad" properties/cases for the example includes:
  - Not all hops being required. We'd like all hops in a question to be necessary to come to the answer. If a question has two hops which could be bypassed by just one, our dataset is less effective. (TODO: example)
    - To address this, we exclude all nodes from being chosen as a next hop if they previously could have been chosen. (TODO: example)
    - Similarly, we exclude all nodes and properties which are already in the path from appearing a second time.
  - Nonsensical questions: all the questions should "make sense" (TODO: elaborate).
  - Vague/ambigious questions: questions should have one, and only one (TODO: is this true?) right answer.
    - Some properties, such as "different from" (P1889) lead to vague questions which are too ambiguous to answer. Manually excluding certain properties can alleviate this problem.
    - Additionally, there are sometimes multiple items which are true for a relationship. For instance, there are multiple claims UW "has subsidiary" "Information School" and "Paul G. Allen School of Computer Science & Engineering". To avoid ambigious questions, at each sampling step we exclude all claims for which other claims from the item have the same property.

- Weighting:
Random walks will tend to converge on more popular items. While we want more popular items to be more represented in the dataset, random walks will overrepresent those examples. To combat this, we use a custom weighting for hops instead of uniform random weights. Weighting by the inverse of the in-degree of nodes prevents popular nodes from being overrepresented. The probability of hopping from some node $x$ to a connected node $y$, given a weight $c$, is: $$P_{x,y} = \frac{\text{in-degree}_y^{-c}}{\sum_{z \sim x} \text{in-degree}_z^{-c}}$$
$c=1$ corresponds to weighting exactly by inverse in-degree, $c=0$ is uniform weights. $c=0.5$ has generally worked well to have a good representation of popular items.

- Existing questions:
  - How big should the dataset be?
  - Could an LLM be used to do some pre-filtering? Is that necessary?
  - What should the answer look like? A specific node? Some text?
  - How can a model be evaluated on this dataset?
