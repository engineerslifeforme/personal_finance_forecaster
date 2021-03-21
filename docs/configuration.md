# Configuration Instructions

A PFF forecast is built according to the YAML configuration details.  The
web app initalizes with an example YAML.  It is recommended to copy the contents
of the configuration and save locally for use later.

Instuctions for populating the configuration fields are provided below.

## Example

```{code-block} yaml
inflation: 0.02
returns: 0.07
start_age: 25
start_year: 2021
start_month: 3
start_balance:  100000.00
stop_age: 100
income:
    - name: An Income
      amount: 5000.00 # monthly
      stop_age: 40
      tax: 0.25
expenses:
    - name: mortgage
      amount: 1500.00
      stop_age: 50
      inflate: False
```

## Configuration Values

All of these top level configuration values are required.

```{list-table} Configuration Values
:header-rows: 1

* - Key
  - Value Type
  - Description
* - inflation
  - decimal
  - Yearly inflation to be applied where noted (0.02 = 2%)
* - returns
  - decimal
  - Yearly appreciation to be applied where noted (0.07 = 7%)
* - start_age
  - integer
  - Age at the begining of the forecast.  For simplicity, birthdays are assumed on 1 Jan.
* - start_year
  - integer
  - Year to start forecast
* - start_month
  - integer
  - Month to start forecast (1 = January)
* - start_balance
  - decimal
  - Starting balance to which income will be added and expenses will be removed
* - stop_age
  - integer
  - Age to end the forecast
* - income
  - list of dictionaries (key + values)
  - Monthly income to be added to balance. More details below.
* - expenses
  - list of dictionaries (key + values)
  - Monthly expenses to be subtracted from balance.  More details below.
```

## Income

Multiple sources of income can be defined as a list
in the configuration file.  Optional fields do not
need to be included.

```{note} Income increases according to inflation.
```

```{code-block} yaml
income:
    - name: An Income
      amount: 5000.00 # monthly
      stop_age: 40
      tax: 0.25
    - name: Another Income
      amount: 10.00
      stop_age: 30
      tax: 0.20
```

```{list-table} Income Configuration
:header-rows: 1

* - Key
  - Optional
  - Value Type
  - Description
* - name
  - 
  - string
  - A name for the income source
* - amount
  - 
  - decimal
  - Monthly income amount
* - stop_age
  - X
  - integer
  - Age at which income will stop. Default end_age.
* - tax
  - X
  - decimal
  - Removed from income prior to addition (0.25 = 25%).  Default 0.00.
```

## Expenses

Multiple sources of expense can be defined as a list
in the configuration file.  Optional fields do not
need to be included.

```{note} Expenses increase according to inflation unless configured otherwise.
```

```{code-block} yaml
expenses:
    - name: mortgage
      amount: 1500.00
      stop_age: 50
      inflate: False
    - name: car payment
      amount: 500.00
      stop_age: 50
      inflate: False
```

```{list-table} Income Configuration
:header-rows: 1

* - Key
  - Optional
  - Value Type
  - Description
* - name
  - 
  - string
  - A name for the expense source
* - amount
  - 
  - decimal
  - Monthly expense amount
* - stop_age
  - X
  - integer
  - Age at which expense will stop. Default end_age.
* - inflate
  - X
  - boolean
  - Whether or not to apply inflation.  False = do not apply.  Default True.
* - start_age
  - X
  - integer
  - Age at which expense will start.  Default global start_age.
* - one_time
  - X
  - int/float
  - A one time expense of amount at this age, e.g. 35
```

### Expense Examples

**Forever Expense**

A $50.00 per month expense for forever.

```{code-block} yaml
- name: Internet Service
  amount: 50.00
```

**Ending Expense**

A $1,000.00 per month expense that ends at age 40.

```{code-block} yaml
- name: Day Care
  amount: 1000.00
  stop_age: 40 # When my child is 5
```

**Later Expense**

A $500.00 per month expense that starts at age 60.

```{code-block} yaml
- name: Retirement Health Insurance
  amount: 500.00
  start_age: 60
```

**Later Starting and Ending**

$1,000.00 per month expense starting at age 35 and ending at age 40.

```{code-block} yaml
- name: Day Care
  amount: 1000.00
  start_age: 35
  stop_age: 40
```

**One Time Expense**

One time expense of $20,000.00 at age 40.

```{code-block} yaml
- name: New Car
  amount: 20000.00
  one_time: 40
```