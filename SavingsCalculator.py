
# Written by Ido Greenberg, 2017.


import math
import warnings


def deposit_and_invest(x0, monthly_deposit, annual_return, T, verbose=False):
    # Solve the differential problem:
    #   x(t+1) = x(t) + deposit + return*x(t)
    #   x(0) = x0
    annual_deposit = 12 * monthly_deposit
    A = x0 + annual_deposit/annual_return
    x = A * math.exp(annual_return*T) - annual_deposit/annual_return
    if verbose:
        print('Deposits: {:.0f}\nTotal return: {:.0f}'.format(
              annual_deposit*T, (x-x0)-annual_deposit*T))
    return x


def time_to_target(target, x0, monthly_deposit,
                   annual_return=0.04, target_annual_return=0):
    # Invert deposit_and_invest: how much time it takes to reach financial goal
    annual_deposit = 12 * monthly_deposit
    A = x0 + annual_deposit / annual_return

    if target_annual_return == 0:
        # solve analytically
        T = math.log((target+annual_deposit/annual_return)/A)/annual_return
    else:
        # solve numerically
        Tmax = 1000
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
                    deposit_cost=1.31, annual_cost=0.01, annual_return=4,
                    verbose=True):
    # Estimate the monthly payment after retirement.
    # The model may be very sensitive to the parameters.
    # In addition, it does not take into account relevant factors such as
    # insurance risks, pension mutual support, taxes after retirement, etc.
    #
    # ages = list of ages in which salary changes are simulated,
    #        from initial time to retirement.
    # salaries = list (shorter than ages by 1) of salaries by ages.
    # initial_sum = sum at t=ages[0]
    # death_factor = either months factor for payment calculation,
    #                or average death age.
    # costs are defaulted by one of the default pensias.
    # returns are defaulted according to treasury instructions.

    # Disclaimers
    print('Note: the simulation is "BRUTO", '
          'i.e. does not refer to post-retirement taxation.')
    print('Note: the simulation does not refer to INFLATION. The user may choose '
          'to set the input in either realistic or nominal terms.')
    print('Note: the simulation is sensitive to its input '
          'and does not refer to UNCERTAINTIES (e.g. actuarial deficit).')
    print('Note: the simulation probably misses additional important factors, '
          'and contains bugs as well.\n')

    # Input check
    if ages[-1] != 67:
        warnings.warn('Retirement age was set to {:d} rather than 67.'
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

    s = initial_sum
    annual_return = (annual_return-annual_cost)/100
    for ti, tf, salary in zip(ages[:-1], ages[1:], salaries):
        print('Ages {:d}-{:d} salary: {:.0f}'.format(ti,tf,salary))
        monthly_deposit = salary*(worker_deposit+company_deposit+compensation)/100
        monthly_deposit *= (1-deposit_cost/100)
        s = deposit_and_invest(s, monthly_deposit, annual_return, tf-ti)

    payment = s / months_factor
    if verbose:
        print('\nEstimated monthly payment at retirement: {:.0f}'.format(payment))

    return payment


def mortgage_vs_rent(price, initial_sum, monthly_saving, rent_cost,
                     annual_return=6, mortgage_cost=3, price_increase=3,
                     verbose=True):
    # Estimate the time required to have a house without financial debts,
    # for both mortgage case and rent-and-invest case.
    #
    # monthly_saving: after paying rent (i.e. saving in the rent-and-invest case).
    # annual_return: annual profit [percents], before taxation.
    #                note: taxation is simulated as immediate, i.e. no tax delay.

    TAX = 0.25

    t_rent = time_to_target(price, initial_sum, monthly_saving,
                            (1-TAX)*annual_return/100, price_increase/100)

    t_mortgage = time_to_target(0, initial_sum-price, monthly_saving+rent_cost,
                                mortgage_cost/100, price_increase/100)

    if verbose:
        print('Time required to have a {:.2f}M-house without debts:'
              .format(price/1e6))
        print('Rent-and-invest: {:.0f} years'.format(t_rent))
        print('Mortgage: {:.0f} years'.format(t_mortgage))

    return (t_rent, t_mortgage)



if __name__ == '__main__':

    print('This module is foolish and mistakeful and only dumb people use it.'
          'On their own responsibility, of course.')

    print('\n_________________________\nPension payment simulation:\n')
    pension_payment(initial_sum=160e3,
                    ages=[27, 29, 35, 67], salaries=[0, 20e3, 25e3])

    print('\n_________________________\nMortgage vs. Renting comparison:\n')
    mortgage_vs_rent(price=2e6, initial_sum=200e3,
                     monthly_saving=7e3, rent_cost=3e3)
