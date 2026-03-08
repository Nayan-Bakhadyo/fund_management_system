# BE Investment Firm - Fund Management System

## Project Overview
- **Stack**: Django 4.2, SQLite, Gunicorn on Ubuntu (AWS)
- **Local env**: conda `be_inv` | **Production env**: venv at `~/fund_management_system/venv`
- **Production**: `ubuntu@ip-172-31-14-207`, service: `fund_management_system.service`
- **Domain**: beinvestmentfirm.com
- **Branch**: `server`

## Key Commands
- **Local**: `conda run -n be_inv python manage.py <cmd>`
- **Production**: `source venv/bin/activate && python manage.py <cmd>` (use `python3` if venv not activated)
- **Deploy**: SSH into server → `cd ~/fund_management_system && ./deploy.sh`
- **deploy.sh** stashes share_price.csv before `git pull` (CSV is auto-updated by cron)
- **Static files**: `collectstatic` in deploy.sh handles it

## NAV System
- **Formula**: `NAV = (available_capital + current_investment_value) / total_circulating_units`
- **Single calculator**: `python manage.py calculate_nav` (the ONLY source of truth)
- `calculate_nav.sh` is a thin wrapper that calls the management command
- **Precision**: 6 decimal places (model + calculation), stored in `NAVRecord.unit_cost`
- **Dedup logic**: Only creates a new NAVRecord if value differs from latest record
- **7.5% CGT**: Applied on unrealized share market gains (when capital_gain > 0)
- **Closed investments**: NOT included in NAV calc (P&L already reflected in available_capital)

## Cron Jobs (Production)
- **Every 5 min**: `fetch_share_prices.sh` → scrapes sharesansar.com → updates `mainapp/utilities/share_price.csv`
- **Every 5 min**: `calculate_nav.sh` → recalculates NAV from CSV prices
- **Daily**: `daily_transaction_email` management command

## Portfolio (as of March 8, 2026)
- **Total Capital**: 252,304.06 | **Available**: 15,752.63 | **Invested**: 236,551.43
- **Circulating Units**: 28,111 | **NAV**: ~8.674612
- **Open investments**: IGI (106 shares), Eco Group (100k), 2 Loans (32k + 50k)
- **Closed**: AHPC (loss -1,602.84), Samling (profit +924.90) — already settled in capital

## Models
- `NAVRecord`: date_time (auto), unit_cost (DecimalField, max_digits=10, decimal_places=6)
- `UserTransaction`: unit_cost (12,6), purchase_unit (12,6), purchase_initiated_amount (12,2)
- `UserNAV`: available_unit (12,2), available_credit_amount (12,2)
- `TotalCapitalRecord`: total_capital, available_capital, invested_capital, total_circulating_unit
- `FirmInvestment`: investment details with status (open/closed), share_symbol for market investments

## Key Files
- `mainapp/management/commands/calculate_nav.py` — NAV calculation logic
- `mainapp/management/commands/fetch_share_prices.py` — scrapes share prices
- `mainapp/views.py` — dashboards (user, fund manager, firm status)
- `mainapp/utilities/share_price.csv` — live share prices (auto-updated, gitignore-worthy)
- `cleanup_nav_spikes.py` — one-time script to remove historical spike records + duplicates

## Past Issues & Fixes (March 2026)
1. **Stale CSV price**: IGI showed profit when actually at loss → manually updated CSV
2. **Dual NAV calculators**: `calculate_nav.sh` had inline Python with different logic (7.5% CGT + double-counted closed losses) causing spikes → replaced .sh with wrapper calling management command
3. **NAV chart spikes**: Views sent all raw records → added dedup + 40-point sampling
4. **Closed loss double-counting**: Old code subtracted AHPC loss again → fixed: only open investments in calc
5. **NAV rounding gap**: 2 decimals caused 105.13 gap across 28,111 units → increased to 6 decimals
6. **deploy.sh CSV conflict**: share_price.csv local changes blocked git pull → added git stash/pop
7. **Duplicate NAV records**: ~288 identical records/day from 5-min cron → added skip-if-unchanged logic
8. **indian_number_format**: Was stripping negative signs → fixed
