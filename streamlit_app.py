import pathlib

import streamlit as st
import yaml
import streamlit.components.v1 as components
from bs4 import BeautifulSoup

import SessionState
from forecast_designer import load_forecast_designer
from forecast_compare import load_forecast_compare

GA_JS = """<script data-ad-client="ca-pub-1479523501051314" async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js"></script>"""

# Insert the script in the head tag of the static template inside your virtual environement
index_path = pathlib.Path(st.__file__).parent / "static" / "index.html"
soup = BeautifulSoup(index_path.read_text(), features="lxml")
if not soup.find(id='custom-js'):
    script_tag = soup.new_tag("script", id='custom-js')
    script_tag.string = GA_JS
    soup.head.append(script_tag)
    index_path.write_text(str(soup))

session_state = SessionState.get(expenses=None)

if session_state.expenses is None:
    with open('default.yaml', 'r') as fh:
        configuration_content = fh.read()
        config = yaml.load(configuration_content, Loader=yaml.SafeLoader)
        session_state.expenses = config
else:
    config = session_state.expenses
    configuration_content = yaml.safe_dump(config)


st.set_page_config(layout='wide')

analysis_modes = [
    'Forecast Designer', 
    'Forecast Comparison',
]

analysis_type = st.sidebar.radio(
    'Analysis Type',
    analysis_modes,
)

if analysis_type == analysis_modes[0]: # Designer
    st.markdown('# Forecast Designer')
    load_forecast_designer(st, session_state, config, configuration_content)
elif analysis_type == analysis_modes[1]: # Compare
    st.markdown('# Forecast Comparison')
    load_forecast_compare(st)
else:
    st.write('Unknown Analysis Mode!')

""" Version 0.3 """