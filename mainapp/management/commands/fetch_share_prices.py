import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Fetch latest share prices from sharesansar.com and update CSV file'

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

            df = pd.DataFrame(data, columns=headers)
            
            # Define the CSV file path
            csv_path = os.path.join(settings.BASE_DIR, 'mainapp', 'utilities', 'share_price.csv')
            
            # Ensure the utilities directory exists
            utilities_dir = os.path.dirname(csv_path)
            os.makedirs(utilities_dir, exist_ok=True)
            
            # Export to CSV
            df.to_csv(csv_path, index=False)
            
            if options['verbose']:
                self.stdout.write(f'Successfully fetched {df.shape[0]} share prices')
                self.stdout.write(f'Data saved to: {csv_path}')
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully updated share prices - {df.shape[0]} records'
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
