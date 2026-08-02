import requests
from bs4 import BeautifulSoup
import pandas as pd

URL = "https://www.sharesansar.com/today-share-price"


def fetch_today_share_price_df():
    response = requests.get(URL)
    soup = BeautifulSoup(response.text, "html.parser")

    # Find the table
    table = soup.find("table", {"id": "headFixed"})
    rows = table.find("tbody").find_all("tr") if table else []

    # Get headers from the table
    headers = []
    if table:
        header_row = table.find("thead").find_all("th")
        headers = [th.text.strip() for th in header_row]

    data = []
    for row in rows:
        cols = row.find_all("td")
        if len(cols) > 0:
            data.append([col.text.strip() for col in cols])

    df = pd.DataFrame(data, columns=headers)
    #number of rows in df
    print(df.shape[0])
    print(df.head())  # Show first 5 rows
    # Export to CSV
    df.to_csv("mainapp/utilities/share_price.csv", index=False)
    print("Exported to mainapp/utilities/share_price.csv")
    return df


if __name__ == "__main__":
    fetch_today_share_price_df()