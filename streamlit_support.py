import base64

def df_to_csv_download(df, link_text):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
    return f'<a href="data:file/csv;base64,{b64}">{link_text}</a> (right-click and save as &lt;some_name&gt;.csv)'
    