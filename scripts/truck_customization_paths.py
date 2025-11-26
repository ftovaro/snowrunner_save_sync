"""
SnowRunner Save File Structure Reference
=========================================

This script documents the JSON paths where truck customization data is stored
in the CompleteSave.cfg file. It doesn't perform any operations, just serves
as a reference for understanding the save file structure.

File: CompleteSave.cfg
Format: JSON with null byte terminator (\x00)
"""

# Main save structure
SAVE_STRUCTURE = {
    "CompleteSave": {
        "SslValue": {
            # Player money (what simple_money_update.py modifies)
            "persistentProfileData": {
                "money": "int - Player's current money",
                "experience": "int - Player XP",
                "rank": "int - Player level",
                "ownedTrucks": "dict - Truck IDs and count",
                
                # TRUCK CUSTOMIZATION DATA - Individual truck instances
                "trucksInWarehouse": [
                    {
                        "type": "string - Truck model ID (e.g., 'international_fleetstar_f2070a')",
                        "id": "string - Unique instance ID",
                        "globalId": "string - Global identifier",
                        "retainedMapId": "string - Which map the truck is on (e.g., 'level_us_01_02')",
                        
                        # Performance upgrades
                        "engine": {"name": "string - Engine upgrade ID"},
                        "gearbox": {"name": "string - Gearbox upgrade ID"},
                        "suspension": "string - Suspension upgrade ID",
                        "winchUpgrade": {"name": "string - Winch upgrade ID"},
                        "wheelsType": "string - Wheel type ID",
                        "wheelsSuspHeight": "array - Suspension height per wheel",
                        "wheelsScale": "float - Wheel size scale",
                        "tires": "string - Tire type ID",
                        "rims": "string - Rim style ID",
                        
                        # Visual customization
                        "customizationPreset": {
                            "id": "int - Color preset ID",
                            "overrideMaterialName": "string - Skin/paint ID",
                            "tintsColors": "array - RGB color values for paint",
                            "materialColorType": "int - Paint type",
                            "isSpecialSkin": "bool - Special edition skin"
                        },
                        
                        # Addons (cosmetic and functional)
                        "addons": [
                            {
                                "name": "string - Addon ID (snorkels, bumpers, stickers, etc.)",
                                "parentFrame": "string - Where it's attached on truck",
                                "position": {"x": 0, "y": 0, "z": 0},
                                "eulerAngles": {"x": 0, "y": 0, "z": 0},
                                "overrideMaterial": "string - Custom material/color",
                                "isInCockpit": "bool - Interior addon",
                                "repairs": "float - Addon damage level",
                                "water": "float - Water damage",
                                "fuel": "float - Fuel level if addon has fuel",
                            }
                        ],
                        
                        # Damage state
                        "engineDamage": "float - Engine damage (0-1)",
                        "gearboxDamage": "float - Gearbox damage (0-1)",
                        "suspensionDamage": "float - Suspension damage (0-1)",
                        "fuelTankDamage": "float - Fuel tank damage (0-1)",
                        "wheelRepairs": "int - Wheel repair count",
                        "damageDecals": "array - Visual damage markers",
                        
                        # State
                        "fuel": "float - Current fuel level",
                        "water": "float - Water damage level",
                        "isUnlocked": "bool - Is truck unlocked",
                        "isPacked": "bool - Is truck packed on trailer",
                        "phantomMode": "int - Ghost mode state",
                        "trailerGlobalId": "string - Attached trailer ID",
                        "isFreezedByObjective": "bool - Locked by mission"
                    }
                ],
                
                # Other profile data
                "addons": "dict - Owned addon IDs",
                "damagableAddons": "dict - Addon damage states",
                "customColors": "dict - Custom color definitions",
                "discoveredUpgrades": "dict - Found upgrade locations",
                "discoveredTrucks": "dict - Found truck locations",
                "unlockedItemNames": "dict - Unlocked items",
                "newTrucks": "array - Recently acquired trucks",
                "distance": "dict - Distance traveled per region"
            }
        }
    }
}

# Path references for programmatic access
class TruckPaths:
    """JSON path constants for truck customization data"""
    
    # Root path to all trucks
    TRUCKS_WAREHOUSE = "CompleteSave.SslValue.persistentProfileData.trucksInWarehouse"
    
    # Individual truck properties (use with array index)
    TRUCK_TYPE = "type"
    TRUCK_ID = "id"
    TRUCK_LOCATION = "retainedMapId"
    
    # Performance
    TRUCK_ENGINE = "engine.name"
    TRUCK_GEARBOX = "gearbox.name"
    TRUCK_SUSPENSION = "suspension"
    TRUCK_WINCH = "winchUpgrade.name"
    TRUCK_WHEELS = "wheelsType"
    TRUCK_TIRES = "tires"
    TRUCK_RIMS = "rims"
    
    # Customization
    TRUCK_CUSTOMIZATION = "customizationPreset"
    TRUCK_SKIN = "customizationPreset.overrideMaterialName"
    TRUCK_COLORS = "customizationPreset.tintsColors"
    TRUCK_ADDONS = "addons"
    
    # Damage
    TRUCK_ENGINE_DAMAGE = "engineDamage"
    TRUCK_GEARBOX_DAMAGE = "gearboxDamage"
    TRUCK_SUSPENSION_DAMAGE = "suspensionDamage"
    TRUCK_FUEL_TANK_DAMAGE = "fuelTankDamage"
    
    # State
    TRUCK_FUEL = "fuel"
    TRUCK_WATER = "water"
    TRUCK_UNLOCKED = "isUnlocked"


# Example usage (for documentation purposes)
EXAMPLE_USAGE = """
To access truck customization in Python:

import json

# Read save file
with open('CompleteSave.cfg', 'rb') as f:
    data = f.read()
    # Remove null terminator if present
    if data.endswith(b'\\x00'):
        data = data[:-1]
    save_data = json.loads(data.decode('utf-8'))

# Access trucks
trucks = save_data['CompleteSave']['SslValue']['persistentProfileData']['trucksInWarehouse']

# Iterate through trucks
for truck in trucks:
    print(f"Truck: {truck['type']}")
    print(f"  Engine: {truck['engine']['name']}")
    print(f"  Skin: {truck['customizationPreset']['overrideMaterialName']}")
    print(f"  Addons: {[addon['name'] for addon in truck['addons']]}")
    print()
"""


if __name__ == "__main__":
    import json
    import os
    import sys
    
    # Check if trigger was activated
    trigger_activated = sys.argv[1] if len(sys.argv) > 1 else "false"
    
    if trigger_activated == "true":
        print("\n" + "="*50)
        print("🚨 TRIGGER ACTIVATED")
        print("="*50)
        print("\n⚠️  Special truck operation requested")
        print("Future functionality will be added here")
        print("(Detected [trigger] in commit message)")
    
    print("\n" + "="*50)
    print("TRUCK CUSTOMIZATION PATHS")
    print("="*50)
    print(f"\nMain path: {TruckPaths.TRUCKS_WAREHOUSE}")
    print("\nEach truck contains:")
    print(f"  - Type: {TruckPaths.TRUCK_TYPE}")
    print(f"  - Engine: {TruckPaths.TRUCK_ENGINE}")
    print(f"  - Suspension: {TruckPaths.TRUCK_SUSPENSION}")
    print(f"  - Skin: {TruckPaths.TRUCK_SKIN}")
    print(f"  - Addons: {TruckPaths.TRUCK_ADDONS}")
    print(f"  - Damage: {TruckPaths.TRUCK_ENGINE_DAMAGE}, etc.")
    
    # Try to read and display current trucks
    save_file = os.path.join(os.path.dirname(__file__), '..', 'remote', 'CompleteSave.cfg')
    if os.path.exists(save_file):
        print("\n" + "="*50)
        print("CURRENT TRUCKS IN SAVE FILE")
        print("="*50)
        
        try:
            with open(save_file, 'rb') as f:
                data = f.read()
                # Remove null terminator if present
                if data.endswith(b'\x00'):
                    data = data[:-1]
                save_data = json.loads(data.decode('utf-8'))
            
            trucks = save_data['CompleteSave']['SslValue']['persistentProfileData']['trucksInWarehouse']
            
            if not trucks:
                print("\n⚠️  No trucks in warehouse")
            else:
                print(f"\n📦 Total trucks: {len(trucks)}\n")
                
                for i, truck in enumerate(trucks, 1):
                    truck_type = truck.get('type', 'Unknown')
                    location = truck.get('retainedMapId', 'Unknown')
                    engine = truck.get('engine', {}).get('name', 'default')
                    skin = truck.get('customizationPreset', {}).get('overrideMaterialName', 'default')
                    addon_count = len(truck.get('addons', []))
                    
                    # Calculate damage percentage
                    engine_dmg = truck.get('engineDamage', 0) * 100
                    gearbox_dmg = truck.get('gearboxDamage', 0) * 100
                    suspension_dmg = truck.get('suspensionDamage', 0) * 100
                    avg_dmg = (engine_dmg + gearbox_dmg + suspension_dmg) / 3
                    
                    print(f"🚛 Truck #{i}: {truck_type}")
                    print(f"   Location: {location}")
                    print(f"   Engine: {engine}")
                    print(f"   Paint: {skin}")
                    print(f"   Addons: {addon_count}")
                    print(f"   Damage: {avg_dmg:.1f}% avg (E:{engine_dmg:.0f}% G:{gearbox_dmg:.0f}% S:{suspension_dmg:.0f}%)")
                    print()
                    
        except Exception as e:
            print(f"\n❌ Error reading save file: {e}")
    else:
        print(f"\n⚠️  Save file not found at: {save_file}")
    
    print("\n" + "="*50)
    print(EXAMPLE_USAGE)
