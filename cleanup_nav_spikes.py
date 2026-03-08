#!/usr/bin/env python
"""
NAV Spike Cleanup Script
========================
Identifies and removes anomalous NAV records (spikes) caused by the old
buggy calculate_nav.sh script that had conflicting CGT logic.

Strategy:
- For each day, determine the "correct" NAV as the median value for that day
- Records that deviate significantly from the daily median are considered spikes
- Also removes duplicate records, keeping only one record per distinct NAV value per day

Usage:
    python cleanup_nav_spikes.py              # Dry run (default) - shows what would be deleted
    python cleanup_nav_spikes.py --apply      # Actually delete spike records
    python cleanup_nav_spikes.py --threshold 0.02  # Custom spike threshold (default: 3%)
"""

import os
import sys
import django
from collections import defaultdict
from statistics import median

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'be_inv_project.settings')
django.setup()

from mainapp.models import NAVRecord


def detect_and_clean_spikes(apply=False, spike_threshold=0.03):
    """
    Detect and optionally remove NAV spike records.
    
    Spike detection strategy:
    1. Group all NAV records by date
    2. For days with multiple distinct values, compute the median
    3. Values deviating more than spike_threshold from median are spikes
    4. Also deduplicate: keep only one record per distinct value per day
    """
    
    records = list(
        NAVRecord.objects.order_by('date_time')
        .values_list('id', 'date_time', 'unit_cost')
    )
    
    total_records = len(records)
    print(f"Total NAV records: {total_records}")
    print(f"Date range: {records[0][1].strftime('%Y-%m-%d %H:%M')} to {records[-1][1].strftime('%Y-%m-%d %H:%M')}")
    print(f"Spike threshold: {spike_threshold*100:.1f}%")
    print(f"Mode: {'APPLY (will delete)' if apply else 'DRY RUN (preview only)'}")
    print("=" * 70)
    
    # Group by date
    daily = defaultdict(list)
    for rec_id, dt, unit_cost in records:
        day = dt.strftime('%Y-%m-%d')
        daily[day].append((rec_id, dt, float(unit_cost)))
    
    ids_to_delete = set()
    spike_days = []
    duplicate_count = 0
    spike_count = 0
    
    for day in sorted(daily.keys()):
        day_records = daily[day]
        values = [r[2] for r in day_records]
        distinct_values = set(round(v, 6) for v in values)
        
        if len(distinct_values) <= 1:
            # Single value all day - only remove exact timestamp duplicates
            # Keep one record per distinct value
            seen_values = {}
            for rec_id, dt, val in day_records:
                rounded = round(val, 6)
                if rounded not in seen_values:
                    seen_values[rounded] = rec_id  # Keep first occurrence
                else:
                    ids_to_delete.add(rec_id)
                    duplicate_count += 1
            continue
        
        # Multiple distinct values in one day - detect spikes
        med = median(values)
        
        # Separate spikes from normal values
        day_spikes = []
        day_normal = []
        for rec_id, dt, val in day_records:
            deviation = abs(val - med) / med if med > 0 else 0
            if deviation > spike_threshold:
                day_spikes.append((rec_id, dt, val, deviation))
                ids_to_delete.add(rec_id)
                spike_count += 1
            else:
                day_normal.append((rec_id, dt, val))
        
        # Deduplicate normal records: keep one per distinct value
        seen_values = {}
        for rec_id, dt, val in day_normal:
            rounded = round(val, 6)
            if rounded not in seen_values:
                seen_values[rounded] = rec_id
            else:
                ids_to_delete.add(rec_id)
                duplicate_count += 1
        
        if day_spikes:
            spike_days.append(day)
            normal_vals = sorted(set(round(r[2], 2) for r in day_normal)) if day_normal else []
            spike_vals = sorted(set(round(s[2], 2) for s in day_spikes))
            print(f"  {day}: median={med:.2f}, normal={normal_vals}, SPIKES={spike_vals} ({len(day_spikes)} records)")
    
    print("=" * 70)
    print(f"\nSummary:")
    print(f"  Days with spikes: {len(spike_days)}")
    print(f"  Spike records to remove: {spike_count}")
    print(f"  Duplicate records to remove: {duplicate_count}")
    print(f"  Total records to remove: {len(ids_to_delete)}")
    print(f"  Records remaining: {total_records - len(ids_to_delete)}")
    
    if not ids_to_delete:
        print("\nNo spikes or duplicates found. Database is clean!")
        return
    
    if apply:
        print(f"\nDeleting {len(ids_to_delete)} records...")
        # Delete in batches to avoid memory issues
        ids_list = list(ids_to_delete)
        batch_size = 500
        deleted_total = 0
        for i in range(0, len(ids_list), batch_size):
            batch = ids_list[i:i + batch_size]
            count, _ = NAVRecord.objects.filter(id__in=batch).delete()
            deleted_total += count
        print(f"Deleted {deleted_total} records.")
        
        # Show final state
        remaining = NAVRecord.objects.count()
        latest = NAVRecord.objects.order_by('-date_time').first()
        print(f"\nFinal state:")
        print(f"  Remaining records: {remaining}")
        if latest:
            print(f"  Latest NAV: {latest.unit_cost} ({latest.date_time.strftime('%Y-%m-%d %H:%M')})")
    else:
        print(f"\nThis is a DRY RUN. To apply changes, run:")
        print(f"  python cleanup_nav_spikes.py --apply")


if __name__ == '__main__':
    apply = '--apply' in sys.argv
    
    threshold = 0.03  # 3% default
    for i, arg in enumerate(sys.argv):
        if arg == '--threshold' and i + 1 < len(sys.argv):
            threshold = float(sys.argv[i + 1])
    
    detect_and_clean_spikes(apply=apply, spike_threshold=threshold)
