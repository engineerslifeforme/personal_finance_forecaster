# Design

This page is intended to document why PFF works the way
it does.

## Balance Calculation

The starting balance (`start_balance`) is increased by
`income` and decreased by `expenses`.  By default both
income and expenses are increased according to `inflation`.
Simiarly each period the balance increases by `returns`.

## Balance

A person or family's net worth is likely distributed across
more than a single account.  For simplicity, PFF assumes
a single account.

A non-conversative (but hopefully) result of the single account
assumption is that the `returns` appreciation is applied
to the full balance.  It is likely a portion of the funds
have a much lower appreciation than others.

A conservative `returns` value is encouraged.

## Age

Many of the configuration values and plot axes are related
to age.  Doing the plots by age as opposed to pure date
makes the plots a little more intuitively interprettable.
Similarly, this can sometimes be helpful in configuring
expenses and income, e.g. "What if income stops at 55?".