import sqlite3

import streamlit as st

from sample import sample, generate


db = sqlite3.connect('knowledge_graph.db')
cursor = db.cursor()

with st.form('request'):
    st.write('Sample:')
    n_hops = st.number_input('Num hops:', min_value=1, value=3)
    c = st.number_input('Constant weight', value=0.3)
    bad_props = st.text_input('Properties to avoid', value='P31 P1343 P279')
    bad_items = st.text_input('Items to avoid', value='')
    n_samples = st.number_input('Number samples', min_value=1, value=3)
    submit = st.form_submit_button('Sample!')

if submit:
    it = 0
    while it < int(n_samples):
        ct = st.container(border=True)
        log = []
        path, props = sample(
            cursor,
            int(n_hops),
            c,
            bad_prop_ids=set(bad_props.split(' ')),
            bad_item_ids=set(bad_items.split(' ')),
            log=log,
        )
        if 'no possible' in log[-1]:
            print('no possible')
            continue

        ct.write('log:')
        ct.write(log)

        for i, (item, prop) in enumerate(zip(path[:-1], props)):
            ct.write(f'**Item {i+1}:** {item[0]}, {item[1][:80]}')
            ct.write(f'**Prop:** {prop[0]}, {prop[1][:80]}')
        ct.write(f'**Item {len(path)+1}:** {path[-1][0]}, {path[-1][1][:80]}')
        
        ct.markdown(f'**Generated Question:** *{generate(path, props)}*')
        it += 1
