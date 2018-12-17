
# Calculator for long-term savings.
# WARNING: validity of calculations assumptions is probably RESTRICTED TO ISRAEL.
#
# Main functions are:
#   pension_payment()    - estimate the monthly pension payment at retirement.
#   mortgage_vs_rent()   - estimate the time required to buy a house
#                          (both with and without mortgage).
#
# More generic tools:
#   deposit_and_invest() - estimate future savings by initial sum, depositions and returns.
#   time_to_target()     - estimate time required to reach certain amount of savings.
#
# Written by Ido Greenberg, 2017.

import math
import warnings

def deposit_and_invest(x0, monthly_deposit, annual_return, T, verbose=False):
    '''
    Solve the differential problem (thanks to WolframAlpha):
      x(t+1) = x(t) + deposit + return*x(t)
      x(0) = x0
    '''
    annual_deposit = 12 * monthly_deposit
    A = x0 + annual_deposit/annual_return
    x = A * math.exp(annual_return*T) - annual_deposit/annual_return
    if verbose:
        print('Deposits: {:.0f}\nTotal return: {:.0f}'.format(
              annual_deposit*T, (x-x0)-annual_deposit*T))
    return x

def time_to_target(target, x0, monthly_deposit,
                   annual_return=0.04, target_annual_return=0., Tmax=1000):
    # Invert deposit_and_invest(): how much time it takes to reach financial goal
    annual_deposit = 12 * monthly_deposit
    A = x0 + annual_deposit / annual_return

    if target_annual_return == 0:
        # solve analytically
        T = math.log((target+annual_deposit/annual_return)/A)/annual_return
    else:
        # solve numerically
        x = x0
        y = target
        for t in range(Tmax):
            if x >= y:
                T = t
                break
            x = deposit_and_invest(x, monthly_deposit, annual_return, 1)
            y = deposit_and_invest(y, 0, target_annual_return, 1)
        if t == Tmax-1:
            T = math.inf

    return T

def pension_payment(initial_sum, ages, salaries, death_factor=85,
                    worker_deposit=6, company_deposit=6.5, compensation=6,
                    deposit_cost=1.5, annual_cost=0.01, annual_return=4,
                    verbose=True, ImSureIKnowWhatIDo=False):
    '''
    Estimate monthly payment after retirement.

    BEWARE!
    1. The result may be very sensitive to the input parameters.
    2. Actuarial risks are not taken into account.
    3. The result is "bruto" (doesn't take post-retirement taxes into account).
    4. The simulation is nominal (ignores inflation). To cancel it, the user
       may set the annual return in realistic terms.

    Arguments:
    ages = list of ages in which salary changes are simulated,
           from initial time to retirement.
    salaries = list (shorter than ages by 1) of salaries by ages.
    initial_sum = sum at t=ages[0]
    death_factor = either months factor for payment calculation,
                   or expected death age.
    Default costs correspond to the newly founded (2017) "default pensia".
    Default returns correspond to the (arguably controversial) standard.
    '''

    # Disclaimers
    if not ImSureIKnowWhatIDo:
        warning = '''
        BEWARE!
        1. The result may be very sensitive to the input parameters.
        2. Actuarial risks are not taken into account.
        3. The result is "bruto" (doesn't take post-retirement taxes into account).
        4. The simulation is nominal (ignores inflation). To cancel it, the user
           may set the annual return in realistic terms.'''
        warnings.warn(warning)
        print('')

    # Input validation and pre-processing
    if ages[-1] not in [62,67]:
        warnings.warn('Retirement age was set to {:d} rather than 62 or 67.'
                      .format(ages[-1]))
    if type(salaries) is not list: salaries=[salaries]
    if len(salaries) != len(ages)-1:
        raise IOError('For {:d} ages there must be exactly {:d} salaries, not {:d}.'
            .format(len(ages), len(ages)-1, len(salaries) ) )

    if death_factor < 120:
        expected_death_age = death_factor
        months_factor = 12 * (expected_death_age-ages[-1])
        if verbose:
            print('Months factor calculated for payments: {:d}\n'.format(
                months_factor))
    else:
        months_factor = death_factor

    # Simulate pension savings
    s = initial_sum
    annual_return = (annual_return-annual_cost)/100
    for ti, tf, salary in zip(ages[:-1], ages[1:], salaries):
        if verbose:
            print('Ages {:d}-{:d} salary: {:.0f}'.format(ti,tf,salary))
        monthly_deposit = salary*(worker_deposit+company_deposit+compensation)/100
        monthly_deposit *= (1-deposit_cost/100)
        s = deposit_and_invest(s, monthly_deposit, annual_return, tf-ti)

    payment = s / months_factor
    if verbose:
        print('\nEstimated monthly payment at retirement: {:.0f}'.format(payment))

    return payment


def mortgage_vs_rent(price, initial_sum, monthly_saving, rent_cost,
                     annual_return=5, mortgage_cost=3, price_increase=3,
                     TAX=25, verbose=True, ImSureIKnowWhatIDo=False):
    '''
    Estimate the time required to have a house without financial debts,
    for both mortgage case and rent-and-invest case.

    "Middle case" (mortgage for part of the cost) is not considered.
    Mortgage feasibility () is not checked.

    Input notes:
    monthly_saving: after paying rent (i.e. saving in the rent-and-invest case).
    annual_return: annual profit [percents], before taxation.
    Taxation is simulated as immediate, i.e. no tax delay.
    '''

    # Disclaimers
    if not ImSureIKnowWhatIDo:
        warning = '''
        BEWARE!
        1. Results are extremely sensitive to input values.
        2. Mortgage feasibility (e.g. minimum own-equity criterion) is not checked.'''
        warnings.warn(warning)
        print('')

    # Input validation
    if any([0<x and x<1 for x in (annual_return,mortgage_cost,price_increase,TAX)]):
        warnings.warn('Some of the numeric parameters satisfy 0%<x<1% - '
                      'note the units are percent.')

    t_rent = time_to_target(price, initial_sum, monthly_saving,
                            (1-TAX/100)*annual_return/100, price_increase/100)

    t_mortgage = time_to_target(0, initial_sum-price, monthly_saving+rent_cost,
                                mortgage_cost/100, price_increase/100)

    if verbose:
        print(f'Time required to have a {price/1e6:.2f}M-house without debts:')
        print(f'Rent-and-invest: {t_rent:.0f} years')
        print(f'Mortgage: {t_mortgage:.0f} years')

    return (t_rent, t_mortgage)


if __name__ == '__main__':

    warnings.warn('Use at your own risk, and never assume anything I say to be true.')

    print('\n_________________________\nPension payment simulation:\n')
    pension_payment(initial_sum=30e3, ages=[25,30,35,67], salaries=[7e3,8e3,10e3])

    print('\n_________________________\nMortgage vs. Renting comparison:\n')
    mortgage_vs_rent(price=1e6, initial_sum=100e3, monthly_saving=3e3, rent_cost=2e3)

    input()
