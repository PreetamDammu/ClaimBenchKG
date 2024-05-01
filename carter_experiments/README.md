# Wikidata5m sampling experiments

## Structure:

Code for interacting with and sampling from Wikidata5m is in the `wikidata5m` folder. Some basic experiments are in this current folder. You can import code via `from wikidata5m ... import ...`. The db is contained in the `db` folder, likewise data is within the `data` folder.

The Wikidata5m data is available both in the repo, but also [here](https://deepgraphlearning.github.io/project/wikidata5m), [this](https://arxiv.org/pdf/1911.06136.pdf) is the paper. The local db uses the `transductive_train` portion of the dataset.

I left documentation within the helper code. You can use `pdoc` (steps below) to view it in the browser.

## Setup:

For Linux/Mac, IDK about Windows:

1. Setup virtual environment: `python3 -m venv .venv`
    - To activate: `source .venv/bin/activate`
2. Install dependencies: `pip install -m requirements.txt`
3. (Optional) add OpenAI API key
4. Open documentation via `pdoc wikidata5m`. This will generate a window with documentation for the code.

**If you are having import issues:** append the following line to the `.venv/bin/activate` file: `export PYTHONPATH="<CURRENT_WORKING_DIRECTORY>:$PYTHONPATH"`. This will let python recognize `wikidata5m` as a package.

## General notes:

I structured the code as a package (`wikidata5m`) so that it is easier to modularlly change experiment code (e.g. filters, sampling techniques). I also want our work to be reproducible and understandable. If this is "over-engineered" or excessively complex, I'm happy to do something different.

I used Wikidata5m for a couple reasons:
- Smaller DS is easier to work with (locally)
- There's some filtering already applied, which removes some "bad" items

I'm not tied to using the 5m subset.

## Experiments:

- `test_random_walk.py`: uses a random walk to sample from the graph, feeds the path to the model, then gets an example question.

## TODOs:

- Some GUI to view experimental generations:
    - I've used streamlit in the past, it's pretty easy for things like this
- Code to setup the DB is in the `setup_db.ipynb` notebook, but quite messy. I'd like to convert that to an actual script if we decide to use Wikidata5m.
