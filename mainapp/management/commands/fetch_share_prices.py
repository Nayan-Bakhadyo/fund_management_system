from decimal import Decimal, InvalidOperation

import requests
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand
from django.db import transaction

from mainapp.models import SharePrice


class Command(BaseCommand):
    help = 'Fetch latest share prices from sharesansar.com and update the SharePrice table'

    def add_arguments(self, parser):
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Enable verbose output',
        )

    def handle(self, *args, **options):
        URL = "https://www.sharesansar.com/today-share-price"
        
        try:
            if options['verbose']:
                self.stdout.write('Fetching share prices from sharesansar.com...')
            
            response = requests.get(URL)
            response.raise_for_status()  # Raise an exception for bad status codes
            
            soup = BeautifulSoup(response.text, "html.parser")

            # Find the table
            table = soup.find("table", {"id": "headFixed"})
            if not table:
                self.stdout.write(
                    self.style.ERROR('Could not find share price table on the website')
                )
                return

            rows = table.find("tbody").find_all("tr")

            # Get headers from the table
            headers = []
            header_row = table.find("thead").find_all("th")
            headers = [th.text.strip() for th in header_row]

            data = []
            for row in rows:
                cols = row.find_all("td")
                if len(cols) > 0:
                    data.append([col.text.strip() for col in cols])

            if not data:
                self.stdout.write(
                    self.style.ERROR('No share price data found')
                )
                return

            symbol_idx = headers.index('Symbol')
            ltp_idx = headers.index('LTP')

            updated = 0
            with transaction.atomic():
                for cols in data:
                    symbol = cols[symbol_idx].strip().upper()
                    ltp_str = cols[ltp_idx].replace(',', '').strip()
                    if not symbol:
                        continue
                    try:
                        ltp = Decimal(ltp_str)
                    except (InvalidOperation, ValueError):
                        continue
                    SharePrice.objects.update_or_create(
                        symbol=symbol, defaults={'ltp': ltp}
                    )
                    updated += 1

            if options['verbose']:
                self.stdout.write(f'Successfully fetched {updated} share prices')

            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully updated share prices - {updated} records'
                )
            )
            
        except requests.RequestException as e:
            self.stdout.write(
                self.style.ERROR(f'Network error while fetching share prices: {str(e)}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error fetching share prices: {str(e)}')
            )
