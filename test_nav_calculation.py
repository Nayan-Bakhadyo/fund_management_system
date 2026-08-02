#!/usr/bin/env python3

"""
Test script for NAV calculation logic
Run this to verify the calculation approach before using the full Django command
"""

import csv
from decimal import Decimal, ROUND_HALF_UP

def test_share_price_loading():
    """Test loading share prices from CSV"""
    print("=== Testing Share Price Loading ===")
    
    share_prices = {}
    csv_path = 'mainapp/utilities/share_price.csv'
    
    try:
        with open(csv_path, 'r') as file:
            reader = csv.DictReader(file)
            count = 0
            for row in reader:
                if count >= 5:  # Just show first 5 for testing
                    break
                    
                symbol = row['Symbol'].strip()
                ltp_str = row['LTP'].replace(',', '')
                try:
                    ltp = Decimal(ltp_str)
                    share_prices[symbol] = ltp
                    print(f"✅ {symbol}: NRs. {ltp}")
                    count += 1
                except (ValueError, Exception) as e:
                    print(f"❌ Error with {symbol}: {e}")
                    continue
        
        print(f"\n📊 Successfully loaded sample prices for {len(share_prices)} symbols")
        return share_prices
        
    except FileNotFoundError:
        print(f"❌ Share price CSV file not found at {csv_path}")
        return {}
    except Exception as e:
        print(f"❌ Error loading share prices: {str(e)}")
        return {}

def test_nav_calculation():
    """Test NAV calculation logic with sample data"""
    print("\n=== Testing NAV Calculation Logic ===")
    
    # Sample data for testing
    available_capital = Decimal('500000.00')  # 5 lakh available
    total_circulating_units = 1000
    
    # Sample investment values
    share_investments = [
        {'name': 'NABIL Investment', 'units': 100, 'ltp': Decimal('1250.00')},
        {'name': 'NICA Investment', 'units': 200, 'ltp': Decimal('850.00')},
    ]
    
    other_investments = [
        {'name': 'Real Estate', 'net_value': Decimal('300000.00')},
        {'name': 'Fixed Deposit', 'net_value': Decimal('200000.00')},
    ]
    
    print(f"Available Capital: NRs. {available_capital:,.2f}")
    print(f"Total Circulating Units: {total_circulating_units:,}")
    
    # Calculate share market investments
    share_market_value = Decimal('0')
    print("\nShare Market Investments:")
    for inv in share_investments:
        value = inv['units'] * inv['ltp']
        share_market_value += value
        print(f"  {inv['name']}: {inv['units']} units × NRs. {inv['ltp']} = NRs. {value:,.2f}")
    
    # Calculate other investments
    other_investments_value = Decimal('0')
    print("\nOther Investments:")
    for inv in other_investments:
        other_investments_value += inv['net_value']
        print(f"  {inv['name']}: NRs. {inv['net_value']:,.2f}")
    
    # Total investment value
    total_investment_value = share_market_value + other_investments_value
    
    # Calculate NAV
    total_portfolio_value = available_capital + total_investment_value
    nav_value = total_portfolio_value / total_circulating_units
    nav_value = nav_value.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    print(f"\n=== CALCULATION SUMMARY ===")
    print(f"Available Capital: NRs. {available_capital:,.2f}")
    print(f"Share Market Value: NRs. {share_market_value:,.2f}")
    print(f"Other Investments Value: NRs. {other_investments_value:,.2f}")
    print(f"Total Investment Value: NRs. {total_investment_value:,.2f}")
    print(f"Total Portfolio Value: NRs. {total_portfolio_value:,.2f}")
    print(f"Total Circulating Units: {total_circulating_units:,}")
    print(f"🎯 Calculated NAV: NRs. {nav_value}")
    
    return nav_value

def main():
    print("🧮 NAV CALCULATION TEST SCRIPT")
    print("=" * 50)
    
    # Test share price loading
    share_prices = test_share_price_loading()
    
    # Test NAV calculation logic
    nav_value = test_nav_calculation()
    
    print(f"\n✅ Test completed successfully!")
    print(f"📈 Sample NAV calculated: NRs. {nav_value}")
    
    print("\n📋 NEXT STEPS:")
    print("1. Set up your Django environment properly")
    print("2. Install required dependencies (django, python-dotenv)")
    print("3. Run: python manage.py calculate_nav --dry-run --verbose")
    print("4. If successful, run: python manage.py calculate_nav")
    print("5. Set up cron job: ./calculate_nav.sh")

if __name__ == "__main__":
    main()
