#!/bin/bash

# NAV Calculation Script for BE Investment Firm
# Calculates NAV based on stock market performance and investment data
# Usage: ./calculate_nav.sh

# Set script directory and Django project path
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR"
SHARE_PRICE_CSV="$PROJECT_DIR/mainapp/utilities/share_price.csv"

# Check if share_price.csv exists
if [ ! -f "$SHARE_PRICE_CSV" ]; then
    echo "Error: Share price CSV file not found at $SHARE_PRICE_CSV"
    exit 1
fi

# Activate virtual environment if it exists
if [ -f "$PROJECT_DIR/venv/bin/activate" ]; then
    source "$PROJECT_DIR/venv/bin/activate"
    echo "Virtual environment activated"
elif [ -f "$HOME/anaconda3/envs/BE_inv/bin/activate" ]; then
    source "$HOME/anaconda3/envs/BE_inv/bin/activate"
    echo "Conda environment activated"
fi

# Change to Django project directory
cd "$PROJECT_DIR"

# Export Django settings
export DJANGO_SETTINGS_MODULE=be_inv_project.settings

# Create Python script for NAV calculation
cat << 'EOF' > temp_nav_calculator.py
#!/usr/bin/env python
import os
import sys
import django
from decimal import Decimal, ROUND_HALF_UP
import csv
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'be_inv_project.settings')
django.setup()

from mainapp.models import (
    TotalCapitalRecord, FirmInvestment, InvestmentTransaction, 
    NAVRecord, InvestmentCategory
)

def log_message(message):
    """Log messages with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def load_share_prices():
    """Load share prices from CSV file"""
    share_prices = {}
    csv_path = 'mainapp/utilities/share_price.csv'
    
    try:
        with open(csv_path, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                symbol = row['Symbol'].strip()
                # Remove commas and convert LTP to decimal
                ltp_str = row['LTP'].replace(',', '')
                try:
                    ltp = Decimal(ltp_str)
                    share_prices[symbol] = ltp
                    log_message(f"Loaded price for {symbol}: {ltp}")
                except (ValueError, decimal.InvalidOperation):
                    log_message(f"Warning: Invalid LTP for {symbol}: {row['LTP']}")
                    continue
        
        log_message(f"Loaded {len(share_prices)} share prices from CSV")
        return share_prices
    
    except FileNotFoundError:
        log_message(f"Error: Share price CSV file not found at {csv_path}")
        return {}
    except Exception as e:
        log_message(f"Error loading share prices: {str(e)}")
        return {}

def is_share_market_investment(investment):
    """Determine if an investment is share market type"""
    # Check if share_symbol exists and is not empty
    if investment.share_symbol and investment.share_symbol.strip():
        return True
    
    # Check category name for share market keywords
    category_name = investment.investment_category.category_name.lower()
    share_keywords = ['share', 'stock', 'equity', 'securities']
    
    return any(keyword in category_name for keyword in share_keywords)

def calculate_investment_value(investment, share_prices):
    """Calculate current value of an investment"""
    log_message(f"Calculating value for investment: {investment.investment_name}")
    
    # Get all transactions for this investment
    transactions = InvestmentTransaction.objects.filter(investment=investment)
    
    if is_share_market_investment(investment):
        return calculate_share_market_value(investment, transactions, share_prices)
    else:
        return calculate_other_investment_value(investment, transactions)

def calculate_share_market_value(investment, transactions, share_prices):
    """Calculate value for share market investments using LTP"""
    symbol = investment.share_symbol.strip().upper()
    
    if symbol not in share_prices:
        log_message(f"Warning: No price data for symbol {symbol}, using net invested amount")
        return calculate_other_investment_value(investment, transactions)
    
    # Calculate net stock units
    total_units = Decimal('0')
    net_invested = Decimal('0')
    
    for transaction in transactions:
        if transaction.amount_type == 'investment':
            if transaction.stock_units_purchased:
                total_units += transaction.stock_units_purchased
            net_invested += transaction.amount
        elif transaction.amount_type == 'return':
            if transaction.stock_units_purchased:
                total_units -= transaction.stock_units_purchased
            net_invested -= transaction.amount
    
    # Calculate current market value
    current_ltp = share_prices[symbol]
    market_value = total_units * current_ltp
    
    log_message(f"  Share Market Investment: {investment.investment_name}")
    log_message(f"    Symbol: {symbol}")
    log_message(f"    Total Units: {total_units}")
    log_message(f"    Current LTP: {current_ltp}")
    log_message(f"    Market Value: {market_value}")
    log_message(f"    Net Invested: {net_invested}")
    log_message(f"    Gain/Loss: {market_value - net_invested}")
    
    return market_value

def calculate_other_investment_value(investment, transactions):
    """Calculate value for non-share market investments using net invested amount"""
    net_value = Decimal('0')
    
    for transaction in transactions:
        if transaction.amount_type == 'investment':
            net_value += transaction.amount
        elif transaction.amount_type == 'return':
            net_value -= transaction.amount
    
    log_message(f"  Other Investment: {investment.investment_name}")
    log_message(f"    Net Value: {net_value}")
    
    return max(net_value, Decimal('0'))  # Don't allow negative values

def calculate_total_investment_value(share_prices):
    """Calculate total value of all firm investments"""
    total_value = Decimal('0')
    investment_details = []
    
    # Get all investments
    investments = FirmInvestment.objects.all()
    
    log_message(f"Found {investments.count()} total investments")
    
    for investment in investments:
        try:
            investment_value = calculate_investment_value(investment, share_prices)
            total_value += investment_value
            
            investment_details.append({
                'name': investment.investment_name,
                'type': 'Share Market' if is_share_market_investment(investment) else 'Other',
                'symbol': investment.share_symbol or 'N/A',
                'value': investment_value
            })
            
        except Exception as e:
            log_message(f"Error calculating value for {investment.investment_name}: {str(e)}")
            continue
    
    # Log investment summary
    log_message("\n=== INVESTMENT PORTFOLIO SUMMARY ===")
    for detail in investment_details:
        log_message(f"{detail['name']} ({detail['type']}): NRs. {detail['value']:,.2f}")
    
    log_message(f"\nTotal Investment Portfolio Value: NRs. {total_value:,.2f}")
    
    return total_value

def calculate_nav():
    """Main NAV calculation function"""
    log_message("Starting NAV calculation...")
    
    # Load share prices
    share_prices = load_share_prices()
    if not share_prices:
        log_message("No share prices loaded, proceeding with net invested amounts only")
    
    # Get latest capital record
    try:
        latest_capital = TotalCapitalRecord.objects.latest('date_time')
        log_message(f"Latest Capital Record: {latest_capital.date_time}")
        log_message(f"  Total Capital: NRs. {latest_capital.total_capital:,.2f}")
        log_message(f"  Available Capital: NRs. {latest_capital.available_capital:,.2f}")
        log_message(f"  Invested Capital: NRs. {latest_capital.invested_capital:,.2f}")
        log_message(f"  Total Circulating Units: {latest_capital.total_circulating_unit:,}")
    except TotalCapitalRecord.DoesNotExist:
        log_message("Error: No capital records found")
        return None
    
    # Check for zero circulating units
    if latest_capital.total_circulating_unit == 0:
        log_message("Error: Total circulating units is zero, cannot calculate NAV")
        return None
    
    # Calculate total investment value
    total_investment_value = calculate_total_investment_value(share_prices)
    
    # Calculate NAV
    # NAV = (Available Capital + Current Investment Value) / Total Circulating Units
    total_portfolio_value = latest_capital.available_capital + total_investment_value
    nav_value = total_portfolio_value / latest_capital.total_circulating_unit
    
    # Round to 2 decimal places
    nav_value = nav_value.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    log_message("\n=== NAV CALCULATION DETAILS ===")
    log_message(f"Available Capital: NRs. {latest_capital.available_capital:,.2f}")
    log_message(f"Current Investment Value: NRs. {total_investment_value:,.2f}")
    log_message(f"Total Portfolio Value: NRs. {total_portfolio_value:,.2f}")
    log_message(f"Total Circulating Units: {latest_capital.total_circulating_unit:,}")
    log_message(f"Calculated NAV: NRs. {nav_value}")
    
    # Create new NAV record
    try:
        nav_record = NAVRecord.objects.create(unit_cost=nav_value)
        log_message(f"✅ New NAV record created with ID: {nav_record.id}")
        log_message(f"✅ NAV successfully updated to: NRs. {nav_value}")
        
        return nav_record
    
    except Exception as e:
        log_message(f"Error creating NAV record: {str(e)}")
        return None

def main():
    """Main execution function"""
    log_message("=" * 60)
    log_message("BE INVESTMENT FIRM - NAV CALCULATION SCRIPT")
    log_message("=" * 60)
    
    try:
        nav_record = calculate_nav()
        
        if nav_record:
            log_message(f"\n🎉 NAV calculation completed successfully!")
            log_message(f"📊 New NAV: NRs. {nav_record.unit_cost}")
            log_message(f"🕒 Timestamp: {nav_record.date_time}")
            exit_code = 0
        else:
            log_message(f"\n❌ NAV calculation failed!")
            exit_code = 1
            
    except Exception as e:
        log_message(f"\n💥 Unexpected error: {str(e)}")
        import traceback
        log_message(traceback.format_exc())
        exit_code = 1
    
    log_message("=" * 60)
    return exit_code

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
EOF

# Run the NAV calculation
echo "Starting NAV calculation..."
python temp_nav_calculator.py

# Store exit code
exit_code=$?

# Clean up temporary file
rm -f temp_nav_calculator.py

# Exit with the same code as the Python script
if [ $exit_code -eq 0 ]; then
    echo "✅ NAV calculation completed successfully!"
else
    echo "❌ NAV calculation failed! Check the logs above."
fi

exit $exit_code
