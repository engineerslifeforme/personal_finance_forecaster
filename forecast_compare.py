""" Forecast Comparison Page """

from io import StringIO
from pathlib import Path

import yaml
import pandas

from business import (
    assess,
)
from comparison_plots import (
    balance_comparison_plot,
    income_comparison_plot,
    expense_comparison_plot,
)

def load_forecast_compare(st):
    st.markdown('**NOTE:** The filename will be used to label the data, so name the files descriptively')

    uploaded_files = st.file_uploader(
        'Configurations to Compare Upload', 
        type=['yaml', 'yml', 'txt'],
        help='Upload saved configurations (.yaml, .yml, and .txt allowed)',
        accept_multiple_files=True,
    )

    configurations = []
    for uploaded_file in uploaded_files:
        stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
        configuration_content = stringio.read()
        configurations.append((
            Path(uploaded_file.name).stem,
            yaml.safe_load(configuration_content)
        ))

    balances = []
    transactions = []
    for label, forecast in configurations:
        balance, transaction, _ = assess(forecast)
        
        balance['source'] = label
        transaction['source'] = label
        balances.append(balance)
        transactions.append(transaction)

    if len(balances) > 0:
        all_balance = pandas.concat(balances)
        all_transaction = pandas.concat(transactions)
        st.plotly_chart(
            balance_comparison_plot(all_balance),
            use_container_width=True
        )
        st.plotly_chart(
            income_comparison_plot(all_transaction),
            use_container_width=True,
        )
        st.plotly_chart(
            expense_comparison_plot(all_transaction),
            use_container_width=True,
        )
    else:
        st.write('Upload some more forecasts!')