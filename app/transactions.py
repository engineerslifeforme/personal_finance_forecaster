""" Transaction classes """

from enum import Enum

import streamlit as stl

class TransactionEnum(Enum):
    INCOME = 0
    EXPENSE = 1

def future_value(investment, rate, periods):
    """ Compute future value

    :param investment: base amount
    :type investment: decimal
    :param rate: rate of change per period
    :type rate: decimal
    :param periods: number of periods into future
    :type periods: int
    :return: new future value
    :rtype: decimal

    https://www.investopedia.com/terms/f/futurevalue.asp#:~:text=Future%20value%20(FV)%20is%20the,be%20worth%20in%20the%20future.
    """
    return investment * (1 + (rate * periods))

class Transaction(object):
    transaction_type = 'Transaction'
    transaction_enum = None
    dict_label = None
    
    def __init__(self, index: int, appreciation_rate: float, age_range:list):
        self.index = index
        self.name = f'New {self.transaction_type} {self.index}'
        self.amount = 0.00
        self.stop_age = age_range[1]
        if self.transaction_enum == TransactionEnum.INCOME:
            self.tax_rate = 0.15
        elif self.transaction_enum == TransactionEnum.EXPENSE:
            self.tax_rate = None
        self.start_age = age_range[0]
        self.inflate = False
        self.appreciation_rate = appreciation_rate

    def ingest_dict(self, dict_data: dict, age_range:list):
        self.name = dict_data['name']
        self.amount = float(dict_data['amount'])
        self.tax_rate = dict_data.get('tax', 0.0)
        self.start_age = dict_data.get('start_age', age_range[0])
        self.stop_age = dict_data.get('stop_age', age_range[1])
        self.inflate = dict_data.get('inflate', True)
    
    def create_input(self, st:stl, age_range:list):
        st.title(f'{self.transaction_type} #{self.index}')
        self.name = st.text_input(
            f'{self.transaction_type} #{self.index} Name',
            value=self.name,
            help=f'Name of this {self.transaction_type} stream'
        )
        left, middle, right = st.beta_columns(3)
        self.amount = left.number_input(
            f'{self.transaction_type} #{self.index} Amount ($)',
            value=self.amount,
            min_value=0.0,
            help=f'Monthly {self.transaction_type} Amount'
        )
        self.stop_age = middle.number_input(
            f'{self.transaction_type} #{self.index} Stop Age',
            value=self.stop_age,
            min_value=age_range[0],
            max_value=age_range[1],
            help=f'Age at which {self.transaction_type} will end'
        )
        if self.transaction_enum == TransactionEnum.INCOME:
            self.tax_rate = right.number_input(
                f'{self.transaction_type} #{self.index} Tax Rate (%)',
                value=self.tax_rate*100.0,
                min_value=0.0,
                max_value=100.0,
                help=f'Tax rate of {self.transaction_type}'
            )/100.0
        self.start_age = left.number_input(
            f'{self.transaction_type} #{self.index} Start Age',
            min_value=age_range[0],
            max_value=age_range[1],
            value=self.start_age,
            help=f'Age at which {self.transaction_type} will start'
        )
        self.inflate = middle.checkbox(
            f'{self.transaction_type} #{self.index} Inflate?',
            value=self.inflate
        )

    def get_value(self, month_periods: int, age_year: int):
        if age_year >= self.start_age and age_year <= self.stop_age:
            value = self.amount
            if self.inflate:
                value = future_value(self.amount, self.appreciation_rate/12.0, month_periods)
            if self.tax_rate is not None:
                value -= self.tax_rate*value
        else:
            value = 0.0
        return value

    def output_as_dict(self):
        data_dict = {
            'name': self.name,
            'amount': self.amount,
            'stop_age': self.stop_age,
            'start_age': self.start_age,
            'inflate': self.inflate,
        }
        if self.transaction_enum == TransactionEnum.INCOME:
            data_dict['tax'] = self.tax_rate
        return data_dict

class Income(Transaction):
    transaction_type = 'Income'
    transaction_enum = TransactionEnum.INCOME
    dict_label = 'income'


class Expense(Transaction):
    transaction_type = 'Expense'
    transaction_enum = TransactionEnum.EXPENSE
    dict_label = 'expenses'

    def get_value(self, *args):
        return -1 * (super().get_value(*args))