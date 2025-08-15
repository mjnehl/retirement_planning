"""Monte Carlo simulator for multi-account portfolios"""

from dataclasses import dataclass, field
from decimal import Decimal
from typing import List, Dict, Optional
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor
import copy

from .money import Money
from .multi_account_portfolio import MultiAccountPortfolio
from .multi_account_withdrawal import MultiAccountWithdrawalStrategy
from .accounts import AccountType


@dataclass
class MultiAccountSimulationRun:
    """Single simulation run for multi-account portfolio"""
    run_id: int
    yearly_snapshots: List[Dict[str, Money]]  # Account balances by year
    withdrawals: List[Money]
    taxes_paid: List[Money]
    mortgage_payments: List[Money]
    net_worth_trajectory: List[Money]
    final_net_worth: Money
    depleted: bool
    depletion_year: Optional[int]
    mortgage_paid_off_year: Optional[int]


@dataclass
class MultiAccountSimulationParameters:
    """Parameters for multi-account simulation"""
    portfolio: MultiAccountPortfolio
    years: int
    num_simulations: int
    withdrawal_strategy: MultiAccountWithdrawalStrategy
    pay_mortgage: bool = True
    parallel_execution: bool = True
    max_workers: int = 4


@dataclass
class MultiAccountSimulationResults:
    """Results from multi-account simulation"""
    runs: List[MultiAccountSimulationRun]
    success_rate: Decimal
    median_final_net_worth: Money
    total_taxes_paid: Money
    parameters: MultiAccountSimulationParameters
    
    def get_successful_runs(self) -> List[MultiAccountSimulationRun]:
        return [r for r in self.runs if not r.depleted]
    
    def get_account_depletion_stats(self) -> Dict[str, Dict]:
        """Get statistics on when each account type depletes"""
        stats = {}
        
        for account_type in AccountType:
            if account_type == AccountType.MORTGAGE:
                continue
            
            depletion_years = []
            for run in self.runs:
                for year_idx, snapshot in enumerate(run.yearly_snapshots):
                    # Check if any account of this type is depleted
                    for account_name, balance in snapshot.items():
                        if account_type.value in account_name.lower():
                            if not balance.is_positive():
                                depletion_years.append(year_idx)
                                break
            
            if depletion_years:
                import numpy as np
                stats[account_type.value] = {
                    'median_depletion': int(np.median(depletion_years)),
                    'earliest_depletion': min(depletion_years),
                    'latest_depletion': max(depletion_years),
                    'depletion_rate': len(depletion_years) / len(self.runs)
                }
        
        return stats


class MultiAccountMonteCarloSimulator:
    """Monte Carlo simulator for multi-account retirement planning"""
    
    def __init__(self, parameters: MultiAccountSimulationParameters):
        self.params = parameters
    
    def run(self) -> MultiAccountSimulationResults:
        """Execute simulation"""
        if self.params.parallel_execution:
            runs = self._run_parallel()
        else:
            runs = self._run_sequential()
        
        return self._aggregate_results(runs)
    
    def _run_parallel(self) -> List[MultiAccountSimulationRun]:
        """Run simulations in parallel"""
        runs = []
        with ThreadPoolExecutor(max_workers=self.params.max_workers) as executor:
            futures = [
                executor.submit(self._run_single_simulation, i)
                for i in range(self.params.num_simulations)
            ]
            
            for future in concurrent.futures.as_completed(futures):
                runs.append(future.result())
        
        return runs
    
    def _run_sequential(self) -> List[MultiAccountSimulationRun]:
        """Run simulations sequentially"""
        return [
            self._run_single_simulation(i)
            for i in range(self.params.num_simulations)
        ]
    
    def _run_single_simulation(self, run_id: int) -> MultiAccountSimulationRun:
        """Execute single simulation"""
        # Deep copy portfolio for this simulation
        portfolio = self._copy_portfolio(self.params.portfolio)
        
        yearly_snapshots = []
        withdrawals = []
        taxes_paid = []
        mortgage_payments = []
        net_worth_trajectory = []
        mortgage_paid_off_year = None
        
        for year in range(self.params.years):
            # Record starting snapshot
            snapshot = portfolio.get_account_summary()
            yearly_snapshots.append(snapshot)
            net_worth_trajectory.append(portfolio.get_net_worth())
            
            # Check if depleted
            if portfolio.is_depleted():
                # Fill remaining years
                remaining = self.params.years - len(yearly_snapshots)
                for _ in range(remaining):
                    yearly_snapshots.append(snapshot)
                    withdrawals.append(Money(Decimal('0')))
                    taxes_paid.append(Money(Decimal('0')))
                    mortgage_payments.append(Money(Decimal('0')))
                    net_worth_trajectory.append(Money(Decimal('0')))
                break
            
            # Process income for this year (before expenses)
            gross_income, after_tax_income = portfolio.get_annual_income(year)
            if after_tax_income.is_positive():
                # Deposit income into portfolio (goes to cash or taxable accounts)
                portfolio.deposit_income(after_tax_income)
            
            # Pay mortgage if applicable
            if self.params.pay_mortgage:
                mortgage_payment, mortgage_tax = portfolio.pay_mortgage(year)
                mortgage_payments.append(mortgage_payment)
                
                # Check if mortgage paid off this year
                mortgages = portfolio.get_accounts_by_type(AccountType.MORTGAGE)
                if mortgages and mortgage_paid_off_year is None:
                    if all(m.is_paid_off() for m in mortgages):
                        mortgage_paid_off_year = year
            else:
                mortgage_payments.append(Money(Decimal('0')))
                mortgage_tax = Money(Decimal('0'))
            
            # Calculate withdrawal for living expenses
            withdrawal_amount = self.params.withdrawal_strategy.calculate_withdrawal(
                portfolio, year, 
                withdrawals[-1] if withdrawals else None
            )
            
            # Reduce withdrawal by after-tax income (income offsets expenses)
            if after_tax_income.is_positive():
                withdrawal_amount = withdrawal_amount.subtract(after_tax_income)
                if withdrawal_amount.amount < 0:
                    withdrawal_amount = Money(Decimal('0'))
            
            # Execute withdrawal (pass year for private stock accounts)
            actual_withdrawal, withdrawal_tax = portfolio.withdraw(withdrawal_amount, year)
            withdrawals.append(actual_withdrawal)
            
            # Total taxes
            total_tax = withdrawal_tax.add(mortgage_tax if self.params.pay_mortgage else Money(Decimal('0')))
            taxes_paid.append(total_tax)
            
            # Apply investment returns
            portfolio.apply_returns(year)
            
            # Age portfolio owner
            portfolio.increment_age()
        
        # Determine depletion
        final_net_worth = portfolio.get_net_worth()
        depleted = not portfolio.get_total_assets().is_positive()
        
        depletion_year = None
        if depleted:
            for i, nw in enumerate(net_worth_trajectory):
                if not nw.is_positive():
                    depletion_year = i
                    break
        
        return MultiAccountSimulationRun(
            run_id=run_id,
            yearly_snapshots=yearly_snapshots,
            withdrawals=withdrawals,
            taxes_paid=taxes_paid,
            mortgage_payments=mortgage_payments,
            net_worth_trajectory=net_worth_trajectory,
            final_net_worth=final_net_worth,
            depleted=depleted,
            depletion_year=depletion_year,
            mortgage_paid_off_year=mortgage_paid_off_year
        )
    
    def _copy_portfolio(self, portfolio: MultiAccountPortfolio) -> MultiAccountPortfolio:
        """Create deep copy of portfolio"""
        new_portfolio = MultiAccountPortfolio(
            portfolio_id=portfolio.portfolio_id,
            owner_id=portfolio.owner_id,
            withdrawal_order=portfolio.withdrawal_order,
            current_age=portfolio.current_age
        )
        
        # Deep copy each account
        for account_id, account in portfolio.accounts.items():
            new_account = copy.deepcopy(account)
            new_portfolio.accounts[account_id] = new_account
        
        return new_portfolio
    
    def _aggregate_results(self, runs: List[MultiAccountSimulationRun]) -> MultiAccountSimulationResults:
        """Aggregate simulation results"""
        # Calculate success rate
        successful = sum(1 for r in runs if not r.depleted)
        success_rate = (Decimal(successful) / Decimal(len(runs))) * Decimal('100')
        
        # Calculate median final net worth
        import numpy as np
        final_net_worths = [float(r.final_net_worth.amount) for r in runs]
        median_final = Money(Decimal(str(np.median(final_net_worths))))
        
        # Calculate total taxes
        total_taxes = Money(Decimal('0'))
        for run in runs:
            for tax in run.taxes_paid:
                total_taxes = total_taxes.add(tax)
        
        # Average taxes per simulation
        avg_taxes = total_taxes.divide(Decimal(len(runs)))
        
        return MultiAccountSimulationResults(
            runs=runs,
            success_rate=success_rate,
            median_final_net_worth=median_final,
            total_taxes_paid=avg_taxes,
            parameters=self.params
        )