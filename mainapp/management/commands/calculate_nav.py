from django.core.management.base import BaseCommand
from django.utils import timezone
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
import csv
import os
from mainapp.models import (
    TotalCapitalRecord, FirmInvestment, InvestmentTransaction, 
    NAVRecord, InvestmentCategory, UserNAV
)


class Command(BaseCommand):
    help = 'Calculate NAV based on stock market performance and investment data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Calculate NAV but do not save to database',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed calculation logs',
        )

    def handle(self, *args, **options):
        self.dry_run = options['dry_run']
        self.verbose = options['verbose']
        
        if self.dry_run:
            self.stdout.write(
                self.style.WARNING('DRY RUN MODE - No changes will be saved to database')
            )
        
        self.stdout.write("=" * 60)
        self.stdout.write("BE INVESTMENT FIRM - NAV CALCULATION")
        self.stdout.write("=" * 60)
        
        try:
            nav_record = self.calculate_nav()
            
            if nav_record:
                if self.dry_run:
                    self.stdout.write(
                        self.style.SUCCESS(f"✅ NAV calculated: NRs. {nav_record} (DRY RUN)")
                    )
                else:
                    self.stdout.write(
                        self.style.SUCCESS(f"✅ NAV updated successfully: NRs. {nav_record.unit_cost}")
                    )
            else:
                self.stdout.write(
                    self.style.ERROR("❌ NAV calculation failed!")
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"💥 Error: {str(e)}")
            )
            if self.verbose:
                import traceback
                self.stdout.write(traceback.format_exc())

    def log(self, message, level='INFO'):
        """Log messages with timestamp"""
        timestamp = timezone.now().strftime("%Y-%m-%d %H:%M:%S")
        if level == 'ERROR':
            self.stdout.write(self.style.ERROR(f"[{timestamp}] {message}"))
        elif level == 'WARNING':
            self.stdout.write(self.style.WARNING(f"[{timestamp}] {message}"))
        elif level == 'SUCCESS':
            self.stdout.write(self.style.SUCCESS(f"[{timestamp}] {message}"))
        else:
            self.stdout.write(f"[{timestamp}] {message}")

    def load_share_prices(self):
        """Load share prices from CSV file"""
        share_prices = {}
        csv_path = os.path.join('mainapp', 'utilities', 'share_price.csv')
        
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
                        if self.verbose:
                            self.log(f"Loaded price for {symbol}: {ltp}")
                    except (ValueError, InvalidOperation):
                        self.log(f"Warning: Invalid LTP for {symbol}: {row['LTP']}", 'WARNING')
                        continue
            
            self.log(f"Loaded {len(share_prices)} share prices from CSV")
            return share_prices
        
        except FileNotFoundError:
            self.log(f"Error: Share price CSV file not found at {csv_path}", 'ERROR')
            return {}
        except Exception as e:
            self.log(f"Error loading share prices: {str(e)}", 'ERROR')
            return {}

    def is_share_market_investment(self, investment):
        """Determine if an investment is share market type"""
        # Check if share_symbol exists and is not empty
        if investment.share_symbol and investment.share_symbol.strip():
            return True
        
        # Check category name for share market keywords
        category_name = investment.investment_category.category_name.lower()
        share_keywords = ['share', 'stock', 'equity', 'securities']
        
        return any(keyword in category_name for keyword in share_keywords)

    def calculate_investment_value(self, investment, share_prices):
        """Calculate current value of an investment"""
        if self.verbose:
            self.log(f"Calculating value for investment: {investment.investment_name}")
        
        # Get all transactions for this investment
        transactions = InvestmentTransaction.objects.filter(investment=investment)
        
        if self.is_share_market_investment(investment):
            return self.calculate_share_market_value(investment, transactions, share_prices)
        else:
            return self.calculate_other_investment_value(investment, transactions)

    def calculate_share_market_value(self, investment, transactions, share_prices):
        """Calculate value for share market investments using LTP"""
        # Check if share_symbol exists and is not empty
        if not investment.share_symbol or not investment.share_symbol.strip():
            self.log(f"Warning: No share symbol for {investment.investment_name}, using net invested amount", 'WARNING')
            return self.calculate_other_investment_value(investment, transactions)
        
        symbol = investment.share_symbol.strip().upper()
        
        if symbol not in share_prices:
            self.log(f"Warning: No price data for symbol {symbol}, using net invested amount", 'WARNING')
            return self.calculate_other_investment_value(investment, transactions)
        
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
        gross_market_value = total_units * current_ltp
        
        # Apply 7.5% capital gains tax provision on unrealized profits
        capital_gain = gross_market_value - net_invested
        capital_gains_tax = Decimal('0')
        if capital_gain > 0:
            capital_gains_tax = capital_gain * Decimal('0.075')
        
        market_value = gross_market_value - capital_gains_tax
        
        if self.verbose:
            self.log(f"  Share Market Investment: {investment.investment_name}")
            self.log(f"    Symbol: {symbol}")
            self.log(f"    Total Units: {total_units}")
            self.log(f"    Current LTP: {current_ltp}")
            self.log(f"    Gross Market Value: {gross_market_value}")
            self.log(f"    Net Invested: {net_invested}")
            self.log(f"    Capital Gain: {capital_gain}")
            self.log(f"    Capital Gains Tax (7.5%): {capital_gains_tax}")
            self.log(f"    Net Market Value: {market_value}")
        
        return market_value

    def calculate_other_investment_value(self, investment, transactions):
        """Calculate value for non-share market investments using net invested amount"""
        net_value = Decimal('0')
        
        for transaction in transactions:
            if transaction.amount_type == 'investment':
                net_value += transaction.amount
            elif transaction.amount_type == 'return':
                net_value -= transaction.amount
        
        if self.verbose:
            self.log(f"  Other Investment: {investment.investment_name}")
            self.log(f"    Net Value: {net_value}")
        
        return max(net_value, Decimal('0'))  # Don't allow negative values

    def calculate_total_investment_value(self, share_prices):
        """Calculate total value of all firm investments"""
        total_value = Decimal('0')
        investment_details = []
        
        # Get only open investments (closed investments' P&L is already in available_capital)
        investments = FirmInvestment.objects.filter(status='open')
        
        self.log(f"Found {investments.count()} open investments")
        
        for investment in investments:
            try:
                investment_value = self.calculate_investment_value(investment, share_prices)
                total_value += investment_value
                
                investment_details.append({
                    'name': investment.investment_name,
                    'type': 'Share Market' if self.is_share_market_investment(investment) else 'Other',
                    'symbol': investment.share_symbol or 'N/A',
                    'value': investment_value
                })
                
            except Exception as e:
                self.log(f"Error calculating value for {investment.investment_name}: {str(e)}", 'ERROR')
                continue
        
        # Log investment summary
        self.log("\n=== INVESTMENT PORTFOLIO SUMMARY ===")
        for detail in investment_details:
            self.log(f"{detail['name']} ({detail['type']}): NRs. {detail['value']:,.2f}")
        
        self.log(f"\nTotal Investment Portfolio Value: NRs. {total_value:,.2f}")
        
        return total_value

    def calculate_nav(self):
        """Main NAV calculation function"""
        self.log("Starting NAV calculation...")
        
        # Load share prices
        share_prices = self.load_share_prices()
        if not share_prices:
            self.log("No share prices loaded, proceeding with net invested amounts only", 'WARNING')
        
        # Get latest capital record
        try:
            latest_capital = TotalCapitalRecord.objects.latest('date_time')
            self.log(f"Latest Capital Record: {latest_capital.date_time}")
            self.log(f"  Total Capital: NRs. {latest_capital.total_capital:,.2f}")
            self.log(f"  Available Capital: NRs. {latest_capital.available_capital:,.2f}")
            self.log(f"  Invested Capital: NRs. {latest_capital.invested_capital:,.2f}")
            self.log(f"  Total Circulating Units: {latest_capital.total_circulating_unit:,}")
        except TotalCapitalRecord.DoesNotExist:
            self.log("Error: No capital records found", 'ERROR')
            return None
        
        # Check for zero circulating units
        if latest_capital.total_circulating_unit == 0:
            self.log("Error: Total circulating units is zero, cannot calculate NAV", 'ERROR')
            return None
        
        # Calculate total investment value
        total_investment_value = self.calculate_total_investment_value(share_prices)
        
        # Subtract total user credits from available_capital.
        # Credits are small leftover amounts from deposits that couldn't buy a whole unit.
        # They are already included in available_capital (the full deposit amount was added),
        # but each user's total is computed as (units × NAV) + credit. To avoid
        # double-counting credits (once in NAV via available_capital, once explicitly),
        # we exclude them from the NAV numerator.
        from django.db.models import Sum
        total_user_credits = UserNAV.objects.aggregate(
            total=Sum('available_credit_amount')
        )['total'] or Decimal('0')
        
        # Calculate NAV
        # NAV = (Available Capital - Total Credits + Current Investment Value) / Total Circulating Units
        adjusted_available = latest_capital.available_capital - total_user_credits
        total_portfolio_value = adjusted_available + total_investment_value
        nav_value = total_portfolio_value / latest_capital.total_circulating_unit
        
        # Round to 6 decimal places
        nav_value = nav_value.quantize(Decimal('0.000001'), rounding=ROUND_HALF_UP)
        
        self.log("\n=== NAV CALCULATION DETAILS ===")
        self.log(f"Available Capital: NRs. {latest_capital.available_capital:,.2f}")
        self.log(f"Total User Credits (excluded): NRs. {total_user_credits:,.2f}")
        self.log(f"Adjusted Available Capital: NRs. {adjusted_available:,.2f}")
        self.log(f"Current Investment Value: NRs. {total_investment_value:,.2f}")
        self.log(f"Total Portfolio Value: NRs. {total_portfolio_value:,.2f}")
        self.log(f"Total Circulating Units: {latest_capital.total_circulating_unit:,}")
        self.log(f"Calculated NAV: NRs. {nav_value}")
        
        # Create new NAV record (unless dry run)
        if self.dry_run:
            self.log("DRY RUN: NAV record NOT saved to database", 'WARNING')
            return nav_value
        
        # Skip if NAV hasn't changed from the latest record
        latest_nav = NAVRecord.objects.order_by('-date_time').first()
        if latest_nav and latest_nav.unit_cost == nav_value:
            self.log(f"NAV unchanged at {nav_value} — skipping record creation")
            return latest_nav
        
        try:
            nav_record = NAVRecord.objects.create(unit_cost=nav_value)
            self.log(f"New NAV record created with ID: {nav_record.id}", 'SUCCESS')
            self.log(f"NAV successfully updated to: NRs. {nav_value}", 'SUCCESS')
            
            return nav_record
        
        except Exception as e:
            self.log(f"Error creating NAV record: {str(e)}", 'ERROR')
            return None
