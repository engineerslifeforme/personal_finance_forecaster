import streamlit as st
import yaml
import streamlit.components.v1 as components

import SessionState
from forecast_designer import load_forecast_designer
from forecast_compare import load_forecast_compare

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

HtmlFile = open('test.html', 'r', encoding='utf-8')
source_code = HtmlFile.read()
components.html(source_code, height=600)