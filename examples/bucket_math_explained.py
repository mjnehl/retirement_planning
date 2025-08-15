"""
Bucket Strategy Math - Detailed Year-by-Year Explanation
Shows exactly how the cascade rebalancing would work in practice
"""

def explain_bucket_math():
    """
    Detailed math showing how bucket strategy works year by year
    """
    
    print("\n" + "="*80)
    print("BUCKET STRATEGY - THE ACTUAL MATH")
    print("="*80)
    
    print("\n🎯 STARTING POSITION (Age 62):")
    print("-"*40)
    print("Bucket 1 (Cash/Bonds):     $250,000  (3.5% return)")
    print("Bucket 2 (Balanced):       $150,000  (8% return)")  
    print("Bucket 3 (Growth):         $350,000  (10% return)")
    print("Total Portfolio:           $750,000")
    print("Annual Withdrawal Need:    $80,000")
    print("Social Security:           $32,400")
    print("Net from Portfolio:        $47,600")
    
    print("\n" + "="*80)
    print("YEAR-BY-YEAR WITHOUT REBALANCING (Simple Version)")
    print("="*80)
    
    # Simple version - no rebalancing
    b1, b2, b3 = 250000, 150000, 350000
    
    for year in range(1, 6):
        print(f"\n📅 YEAR {year}:")
        
        # Growth
        b1_growth = b1 * 0.035
        b2_growth = b2 * 0.08
        b3_growth = b3 * 0.10
        
        print(f"  Growth:")
        print(f"    Bucket 1: ${b1:,.0f} × 3.5% = ${b1_growth:,.0f}")
        print(f"    Bucket 2: ${b2:,.0f} × 8%   = ${b2_growth:,.0f}")
        print(f"    Bucket 3: ${b3:,.0f} × 10%  = ${b3_growth:,.0f}")
        
        # Apply growth
        b1 += b1_growth
        b2 += b2_growth
        b3 += b3_growth
        
        # Withdrawal from Bucket 1
        withdrawal = 47600 * (1.03 ** (year-1))  # Inflation adjusted
        b1 -= withdrawal
        
        print(f"  After withdrawal of ${withdrawal:,.0f}:")
        print(f"    Bucket 1: ${b1:,.0f}")
        print(f"    Bucket 2: ${b2:,.0f}")
        print(f"    Bucket 3: ${b3:,.0f}")
        print(f"    Total:    ${b1+b2+b3:,.0f}")
    
    print("\n" + "="*80)
    print("YEAR-BY-YEAR WITH CASCADE REBALANCING")
    print("="*80)
    
    # Reset with cascade rebalancing
    b1, b2, b3 = 250000, 150000, 350000
    target_b1 = 200000  # Target to maintain in Bucket 1
    
    for year in range(1, 6):
        print(f"\n📅 YEAR {year}:")
        
        # Step 1: Calculate growth
        b1_growth = b1 * 0.035
        b2_growth = b2 * 0.08
        b3_growth = b3 * 0.10
        
        print(f"  Step 1 - Growth:")
        print(f"    Bucket 1: ${b1:,.0f} + ${b1_growth:,.0f} = ${b1+b1_growth:,.0f}")
        print(f"    Bucket 2: ${b2:,.0f} + ${b2_growth:,.0f} = ${b2+b2_growth:,.0f}")
        print(f"    Bucket 3: ${b3:,.0f} + ${b3_growth:,.0f} = ${b3+b3_growth:,.0f}")
        
        b1 += b1_growth
        b2 += b2_growth
        b3 += b3_growth
        
        # Step 2: Withdrawal
        withdrawal = 47600 * (1.03 ** (year-1))
        b1 -= withdrawal
        
        print(f"\n  Step 2 - Withdraw ${withdrawal:,.0f} from Bucket 1:")
        print(f"    Bucket 1: ${b1:,.0f}")
        
        # Step 3: Cascade Rebalancing
        print(f"\n  Step 3 - Cascade Rebalancing:")
        
        if b1 < target_b1:
            # Need to refill Bucket 1
            deficit = target_b1 - b1
            
            # First try to fill from Bucket 2
            if b2 > 150000:  # Only take excess above original
                from_b2 = min(deficit, b2 - 150000)
                b2 -= from_b2
                b1 += from_b2
                deficit -= from_b2
                print(f"    Move ${from_b2:,.0f} from Bucket 2 → Bucket 1")
            
            # If still need more, take from Bucket 3
            if deficit > 0 and b3 > 350000:
                from_b3 = min(deficit, b3 - 350000)
                b3 -= from_b3
                b2 += from_b3  # Goes to B2 first, then cascades
                print(f"    Move ${from_b3:,.0f} from Bucket 3 → Bucket 2")
                
                # Then from B2 to B1
                b2 -= from_b3
                b1 += from_b3
                print(f"    Then ${from_b3:,.0f} from Bucket 2 → Bucket 1")
        
        print(f"\n  Final Balances:")
        print(f"    Bucket 1: ${b1:,.0f}")
        print(f"    Bucket 2: ${b2:,.0f}")
        print(f"    Bucket 3: ${b3:,.0f}")
        print(f"    Total:    ${b1+b2+b3:,.0f}")
    
    print("\n" + "="*80)
    print("YEAR 5: PRIVATE STOCK ARRIVES")
    print("="*80)
    
    private_stock = 144000
    print(f"\n💰 Private stock liquidates: ${private_stock:,}")
    print("\nAllocation of private stock:")
    print(f"  → Bucket 1 (refill to target): ${min(50000, private_stock):,}")
    print(f"  → Bucket 2 (balanced growth):  ${private_stock - 50000:,}")
    
    b1 += 50000
    b2 += 94000
    
    print(f"\nNew Balances:")
    print(f"  Bucket 1: ${b1:,.0f}")
    print(f"  Bucket 2: ${b2:,.0f}")
    print(f"  Bucket 3: ${b3:,.0f}")
    print(f"  Total:    ${b1+b2+b3:,.0f}")
    
    print("\n" + "="*80)
    print("THE KEY INSIGHT")
    print("="*80)
    
    print("""
The "cascade" is really about WHERE you take money from:

1. ALWAYS withdraw living expenses from Bucket 1 (safe money)
2. ONLY refill Bucket 1 from profits/gains in other buckets
3. NEVER sell from Buckets 2 or 3 in down markets

In practice, you would:
- Quarterly: Check if Bucket 1 needs refilling
- Annually: Do a full rebalance cascade
- When assets arrive: Strategically allocate to depleted buckets

The portfolio builder doesn't do this automatically - YOU manage it by:
- Setting up accounts as shown
- Manually rebalancing when needed
- Using new money (private stock, inheritance) to refill

This is more of a MENTAL FRAMEWORK than automated system!
""")


def show_practical_implementation():
    """
    Show how to actually implement this in real life
    """
    
    print("\n" + "="*80)
    print("HOW TO ACTUALLY IMPLEMENT THIS")
    print("="*80)
    
    print("\n📋 STEP 1: Set Up Your Accounts")
    print("-"*40)
    print("At your broker, create mental or actual subdivisions:")
    print("  • 'Safe Money' - Money market, short bonds, CDs")
    print("  • 'Balanced' - 50/50 or 60/40 allocation")
    print("  • 'Growth' - 80%+ stocks")
    
    print("\n📋 STEP 2: Initial Allocation")
    print("-"*40)
    print("From your $550K starting portfolio:")
    print("  • Sell $200K of stocks → Move to money market (Bucket 1)")
    print("  • Keep $150K in balanced allocation (Bucket 2)")
    print("  • Keep $200K in growth stocks (Bucket 3)")
    
    print("\n📋 STEP 3: Withdrawal Process")
    print("-"*40)
    print("Monthly or Quarterly:")
    print("  1. Calculate needed withdrawal (e.g., $4,000/month)")
    print("  2. Subtract Social Security ($2,700/month)")
    print("  3. Withdraw difference ($1,300) from Bucket 1 ONLY")
    
    print("\n📋 STEP 4: Rebalancing Rules")
    print("-"*40)
    print("Every Quarter:")
    print("  • If Bucket 1 < $160K (2 years expenses): REFILL")
    print("  • If Bucket 2 gained > 10%: Take some profit → Bucket 1")
    print("  • If Bucket 3 gained > 15%: Take some profit → Bucket 2")
    print("  • If markets down > 10%: DO NOTHING (ride it out)")
    
    print("\n📋 STEP 5: When New Money Arrives")
    print("-"*40)
    print("Year 5 - Private Stock ($144K):")
    print("  • First: Top up Bucket 1 to 3 years expenses")
    print("  • Rest: Add to Bucket 2")
    print("\nYear 10 - Inheritance ($300K):")
    print("  • First: Ensure Bucket 1 = 3 years expenses")
    print("  • Second: Bring Bucket 2 to target")
    print("  • Rest: Add to Bucket 3 for growth")
    
    print("\n⚠️ IMPORTANT NOTES:")
    print("-"*40)
    print("• This is NOT automated by the retirement planner")
    print("• YOU must manually rebalance")
    print("• The 'buckets' are conceptual - helps decision making")
    print("• Main benefit: Never forced to sell stocks in down market")
    print("• Secondary benefit: Peace of mind seeing safe money")


def compare_with_single_pool():
    """
    Compare bucket strategy with single pool approach
    """
    
    print("\n" + "="*80)
    print("BUCKET STRATEGY vs. SINGLE POOL")
    print("="*80)
    
    print("\n🎯 SINGLE POOL APPROACH (Your Current):")
    print("-"*40)
    print("• All $750K managed as one portfolio")
    print("• Withdraw based on tax efficiency")
    print("• Rebalance to maintain target allocation")
    print("• Pros: Simpler, potentially more tax-efficient")
    print("• Cons: All money subject to market volatility")
    
    print("\n🎯 BUCKET STRATEGY:")
    print("-"*40)
    print("• $750K divided into 3 time-based segments")
    print("• Withdraw only from Bucket 1")
    print("• Cascade profits downward")
    print("• Pros: Protected from sequence risk, peace of mind")
    print("• Cons: More complex, may sacrifice some returns")
    
    print("\n💡 THE MATH DIFFERENCE:")
    print("-"*40)
    
    # Scenario: Market drops 30% in year 1
    print("\nScenario: Market crashes 30% in Year 1")
    
    print("\nSingle Pool:")
    single = 750000
    single_stocks = single * 0.70  # 70% stocks
    single_bonds = single * 0.30   # 30% bonds
    
    # Market crash
    single_stocks *= 0.70  # Down 30%
    single_bonds *= 1.03   # Bonds up 3%
    single_total = single_stocks + single_bonds
    
    # Withdrawal
    withdrawal = 47600
    single_total -= withdrawal
    
    print(f"  Starting: ${750000:,}")
    print(f"  After crash: ${single_stocks + single_bonds:,.0f}")
    print(f"  After withdrawal: ${single_total:,.0f}")
    print(f"  Loss: ${750000 - single_total - withdrawal:,.0f}")
    
    print("\nBucket Strategy:")
    b1, b2, b3 = 250000, 150000, 350000
    
    # Market crash affects B2 and B3, not B1
    b1 *= 1.035  # Safe, still earns 3.5%
    b2 = b2 * 0.5 * 1.03 + b2 * 0.5 * 0.70  # 50/50 balanced
    b3 *= 0.70  # 100% stocks, down 30%
    
    # Withdrawal from B1 only
    b1 -= withdrawal
    
    total = b1 + b2 + b3
    
    print(f"  Starting: ${750000:,}")
    print(f"  After crash: ${b1+b2+b3+withdrawal:,.0f}")
    print(f"  After withdrawal: ${total:,.0f}")
    print(f"  Loss: ${750000 - total - withdrawal:,.0f}")
    
    print("\n✅ KEY DIFFERENCE:")
    print(f"  Single Pool had to sell assets down 30%")
    print(f"  Bucket Strategy sold from protected Bucket 1")
    print(f"  This preserves more assets for recovery!")


if __name__ == "__main__":
    explain_bucket_math()
    show_practical_implementation()
    compare_with_single_pool()
    
    print("\n" + "="*80)
    print("BOTTOM LINE")
    print("="*80)
    print("""
The bucket strategy is really a MENTAL FRAMEWORK for managing withdrawals:

1. It's NOT automatically implemented by the code
2. You MANUALLY move money between buckets
3. The benefit is PSYCHOLOGICAL and RISK MANAGEMENT
4. In down markets, you never sell from depleted buckets
5. Your timing (private stock year 5, inheritance year 10) makes it ideal

Think of it like having 3 checking accounts:
- One for this year's bills (Bucket 1)
- One for next decade's expenses (Bucket 2)  
- One for long-term growth (Bucket 3)

You manually move money between them based on performance!
""")