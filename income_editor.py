""" Income Editor """

from constants import AGE_RANGE

def income_editor_dialog(st, index, item_key, item, start_age, i_or_e='Income', new=False, tax=True, inflate=False):
    visible_index = index + 1
    income_label, left, right = st.beta_columns((1, 2, 2))
    income_label.markdown(f"{i_or_e} Source #{visible_index}")
    next_available_option = 0
    text_label = 'Name'
    if new:
        text_label = text_label + ' (MUST CHANGE)'
    name = left.text_input(
        text_label, 
        value = item_key,
        key=f'{i_or_e}_name_{index}'
    )
    amount = right.number_input(
        f'Amount',
        value=item['amount'],
        key=f'{i_or_e}_amount_{index}'
    )
    new_item = {
        'amount': amount,
    }
    
    options = st.beta_columns(4)
    if tax:
        include_tax = options[next_available_option].checkbox(
            f'Tax?',
            value=('tax' in item),
            key=f'{i_or_e}_include_tax_{index}'
        )
        next_available_option+=1
        if include_tax:
            if 'tax' in item:
                default_tax = item['tax']*100.0
            else:
                default_tax = 25.0
            new_item['tax'] = (st.slider(
                f'Tax Rate',
                value=default_tax,
                min_value=0.0,
                max_value=100.0,
                step=1.0,
                key=f'{i_or_e}_tax_rate_{index}'
            )/100.0)
    use_end_age = options[next_available_option].checkbox(
        f'End Age?',
        value=('stop_age' in item),
        key=f'{i_or_e}_end_age_{index}'
    )
    next_available_option += 1
    if use_end_age:
        if 'stop_age' in item:
            default_end_age = item['stop_age']
        else:
            default_end_age = AGE_RANGE[1]
        new_item['stop_age'] = st.slider(
            f'Income Ends at Age',
            value = default_end_age,
            min_value=AGE_RANGE[0],
            max_value=AGE_RANGE[1],
            step=1,
            key=f'{i_or_e}_end_age_{index}'
        )
    if inflate:
        if 'inflate' in item:
            default_inflate = item['inflate']
        else:
            default_inflate = True
        new_item['inflate'] = options[next_available_option].checkbox(
            f'Inflate?',
            value=default_inflate,
            key=f'{i_or_e}_inflate_{index}'
        )
        next_available_option += 1
    if 'start_age' in item:
        default_start_age = item['start_age']
    else:
        default_start_age = start_age
    use_start_age = options[next_available_option].checkbox(
        'Start Age?',
        value=('start_age' in item),
        key=f"{i_or_e}_start_age_{index}"
    )
    next_available_option += 1
    if use_start_age:
        new_start_age = st.slider(
            'Income Starts at Age',
            value=default_start_age,
            min_value=AGE_RANGE[0],
            max_value=AGE_RANGE[1],
            key=f"{i_or_e}_start_age_{index}"
        )
        new_item['start_age'] = new_start_age
    if 'one_time' in item:
        default_one_time = item['one_time']
    else:
        default_one_time = start_age
    is_one_time = options[next_available_option].checkbox(
        'One Time?',
        value=('one_time' in item),
        key=f"{i_or_e}_one_time_{index}"
    )
    if is_one_time:
        new_one_time = st.slider(
            'Occurs Once at Age:',
            value = default_one_time,
            min_value=AGE_RANGE[0],
            max_value=AGE_RANGE[1],
            key=f"{i_or_e}_one_time_{index}"
        )
        new_item['one_time'] = new_one_time


    return True, name, new_item