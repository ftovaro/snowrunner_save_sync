#!/usr/bin/env python3
"""
Sync CompleteSave.cfg to main branch preserving truck customizations.

This script:
1. Takes the entire CompleteSave.cfg from the player branch
2. Preserves truck customizations (colors, addons, damage, etc.) from main
3. Syncs everything else: new trucks, money, progress, discovered items, etc.
4. Uses string manipulation to avoid JSON reordering issues
"""

import json
import os
import sys
import re


def read_save_file(filepath):
    """Read save file and return the data."""
    with open(filepath, 'rb') as f:
        data = f.read()
        has_null = data.endswith(b'\x00')
        if has_null:
            data = data[:-1]
        text = data.decode('utf-8')
        save_data = json.loads(text)
        return save_data, has_null


def write_save_file(filepath, save_data, add_null):
    """Write save file preserving null terminator if needed."""
    text = json.dumps(save_data, separators=(',', ':'), ensure_ascii=False)
    data = text.encode('utf-8')
    if add_null:
        data += b'\x00'
    with open(filepath, 'wb') as f:
        f.write(data)


def get_truck_customization_keys():
    """Return list of keys that represent truck customization (not new trucks)."""
    return [
        'engine',
        'gearbox', 
        'suspension',
        'winchUpgrade',
        'wheelsType',
        'wheelsSuspHeight',
        'wheelsScale',
        'tires',
        'rims',
        'customizationPreset',  # Colors, paint, skin
        'addons',  # Snorkels, bumpers, stickers, etc.
        'engineDamage',
        'gearboxDamage',
        'suspensionDamage',
        'fuelTankDamage',
        'wheelRepairs',
        'damageDecals',
        'fuel',
        'water',
        'repairs',
        'controlConstrPosition'
    ]


def sync_trucks(branch_trucks, main_trucks):
    """
    Sync trucks from branch to main:
    - New trucks from branch are added to main
    - Existing trucks keep main's customizations but update type/location if changed
    - Removed trucks from branch are removed from main
    
    Returns: Updated truck list
    """
    customization_keys = get_truck_customization_keys()
    
    # Create a map of trucks by type for easy lookup
    main_trucks_by_type = {truck.get('type'): truck for truck in main_trucks}
    branch_trucks_by_type = {truck.get('type'): truck for truck in branch_trucks}
    
    synced_trucks = []
    
    # Process all trucks from branch
    for branch_truck in branch_trucks:
        truck_type = branch_truck.get('type')
        
        if truck_type in main_trucks_by_type:
            # Truck exists in main - preserve customizations
            main_truck = main_trucks_by_type[truck_type]
            synced_truck = branch_truck.copy()
            
            # Restore customizations from main
            for key in customization_keys:
                if key in main_truck:
                    synced_truck[key] = main_truck[key]
            
            synced_trucks.append(synced_truck)
            print(f"  ✓ Preserved customizations for: {truck_type}")
        else:
            # New truck from branch - add as-is
            synced_trucks.append(branch_truck)
            print(f"  + New truck added: {truck_type}")
    
    # Report removed trucks
    for truck_type in main_trucks_by_type:
        if truck_type not in branch_trucks_by_type:
            print(f"  - Truck removed: {truck_type}")
    
    return synced_trucks


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(script_dir)
    
    # Paths
    branch_save = os.path.join(repo_root, 'remote', 'CompleteSave.cfg')
    main_save = os.path.join(repo_root, 'main_CompleteSave.cfg')  # Will be provided by CI
    output_save = os.path.join(repo_root, 'synced_CompleteSave.cfg')
    
    # Check if we're in CI and main save was provided
    if len(sys.argv) > 1:
        main_save = sys.argv[1]
    if len(sys.argv) > 2:
        output_save = sys.argv[2]
    
    print("="*50)
    print("SYNCING TO MAIN - PRESERVING TRUCK CUSTOMIZATIONS")
    print("="*50)
    
    # Read both saves
    print(f"\n📂 Reading branch save: {branch_save}")
    if not os.path.exists(branch_save):
        print(f"❌ Branch save not found!")
        sys.exit(1)
    
    branch_data, branch_has_null = read_save_file(branch_save)
    
    print(f"📂 Reading main save: {main_save}")
    if not os.path.exists(main_save):
        print(f"⚠️  Main save not found - using branch save as-is")
        main_data = None
        main_has_null = branch_has_null
    else:
        main_data, main_has_null = read_save_file(main_save)
    
    # Start with branch data
    synced_data = branch_data
    
    if main_data:
        # Get truck lists
        branch_trucks = branch_data['CompleteSave']['SslValue']['persistentProfileData']['trucksInWarehouse']
        main_trucks = main_data['CompleteSave']['SslValue']['persistentProfileData']['trucksInWarehouse']
        
        print(f"\n🚛 Branch trucks: {len(branch_trucks)}")
        print(f"🚛 Main trucks: {len(main_trucks)}")
        print("\nSyncing trucks...")
        
        # Sync trucks preserving customizations
        synced_trucks = sync_trucks(branch_trucks, main_trucks)
        
        # Update the synced data with merged trucks
        synced_data['CompleteSave']['SslValue']['persistentProfileData']['trucksInWarehouse'] = synced_trucks
        
        print(f"\n✅ Final truck count: {len(synced_trucks)}")
    else:
        print("\n⚠️  No main save to compare - keeping all branch data")
    
    # Write output
    print(f"\n💾 Writing synced save: {output_save}")
    write_save_file(output_save, synced_data, branch_has_null or main_has_null)
    
    # Show summary
    branch_money = branch_data['CompleteSave']['SslValue']['persistentProfileData']['money']
    synced_money = synced_data['CompleteSave']['SslValue']['persistentProfileData']['money']
    
    print("\n" + "="*50)
    print("SYNC SUMMARY")
    print("="*50)
    print(f"Money: ${synced_money:,}")
    print(f"Trucks: {len(synced_data['CompleteSave']['SslValue']['persistentProfileData']['trucksInWarehouse'])}")
    print("\n✅ Sync complete!")


if __name__ == "__main__":
    main()
