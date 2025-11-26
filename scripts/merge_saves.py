#!/usr/bin/env python3
"""
SnowRunner Save Merger
Merges two player saves to share progress while preserving individual customizations.
"""

import json
import sys
import os
import shutil
import copy
from pathlib import Path
from typing import Dict, Any, List, Set
from collections import OrderedDict
import argparse


def update_dict_preserve_order(target: Dict, updates: Dict) -> None:
    """
    Update target dict with values from updates dict while preserving key order.
    CRITICAL: SnowRunner requires exact field order - this function ensures we don't reorder.
    """
    for key, value in updates.items():
        if key in target:
            if isinstance(value, dict) and isinstance(target[key], dict):
                # Recursively update nested dicts
                update_dict_preserve_order(target[key], value)
            else:
                # Update the value in place
                target[key] = value
        else:
            # New key - add at end (shouldn't happen in merge, but safe)
            target[key] = value


class SnowRunnerSaveMerger:
    """Merges SnowRunner save files with smart conflict resolution."""
    
    MINIMUM_MONEY = 200000
    
    def __init__(self, player1_dir: Path, player2_dir: Path, output_dir: Path):
        self.player1_dir = Path(player1_dir)
        self.player2_dir = Path(player2_dir)
        self.output_dir = Path(output_dir)
        
    def merge(self, preserve_customizations_from: str):
        """
        Merge saves, preserving customizations from specified player.
        
        Args:
            preserve_customizations_from: "ftovaro" or "svanegasg" - whose truck customizations to keep
        """
        print(f"🔄 Merging saves (preserving {preserve_customizations_from} customizations)...")
        
        # Load saves
        player1_complete = self._load_json(self.player1_dir / "remote" / "CompleteSave.cfg")
        player2_complete = self._load_json(self.player2_dir / "remote" / "CompleteSave.cfg")
        player1_common = self._load_json(self.player1_dir / "remote" / "CommonSslSave.cfg")
        player2_common = self._load_json(self.player2_dir / "remote" / "CommonSslSave.cfg")
        
        # Merge CommonSslSave (achievements, progress, discoveries)
        merged_common = self._merge_common_save(player1_common, player2_common)
        
        # Merge CompleteSave (trucks, money, map state)
        if preserve_customizations_from == "ftovaro":
            merged_complete = self._merge_complete_save(player1_complete, player2_complete, player1_complete)
        else:
            merged_complete = self._merge_complete_save(player1_complete, player2_complete, player2_complete)
        
        # Ensure minimum money
        self._ensure_minimum_money(merged_complete)
        
        # Create output directory
        output_remote = self.output_dir / "remote"
        output_remote.mkdir(parents=True, exist_ok=True)
        
        # Write merged saves
        self._save_json(output_remote / "CompleteSave.cfg", merged_complete)
        self._save_json(output_remote / "CommonSslSave.cfg", merged_common)
        
        # Validate field order (critical for SnowRunner)
        print("  🔍 Validating field order...")
        common_order = ['objVersion', 'finishedTrials', 'birthVersion', 'achievementStates', 
                       'givenProsEntitlements', 'saveSlotsTransaction', 'lastGeneratedId', 
                       'platformStatsInfo', 'freezedTrailers']
        if self._validate_field_order(output_remote / "CommonSslSave.cfg", common_order):
            print("    ✓ CommonSslSave.cfg field order is correct")
        else:
            print("    ⚠️  WARNING: CommonSslSave.cfg field order may be incorrect!")
        
        # Handle binary files (fog, sts, mudmaps) - use larger file (more progress)
        self._merge_binary_files()
        
        # Copy other config files from player with customizations
        source_dir = self.player1_dir if preserve_customizations_from == "ftovaro" else self.player2_dir
        self._copy_other_files(source_dir, self.output_dir)
        
        print(f"✅ Merge complete! Output in: {self.output_dir}")
    
    def _load_json(self, filepath: Path) -> Dict[str, Any]:
        """Load and parse JSON save file."""
        with open(filepath, 'rb') as f:
            # Read as binary and strip null bytes that might be at the end
            content = f.read().rstrip(b'\x00').decode('utf-8')
            # CRITICAL: Preserve key order - SnowRunner expects specific order
            # Python 3.7+ dicts maintain insertion order by default
            return json.loads(content)
    
    def _save_json(self, filepath: Path, data: Dict[str, Any]):
        """
        Save JSON data to file with null terminator (required by SnowRunner).
        
        CRITICAL FIELD ORDER REQUIREMENTS:
        CommonSslSave.SslValue must have fields in this order:
        1. objVersion, 2. finishedTrials, 3. birthVersion, 4. achievementStates,
        5. givenProsEntitlements, 6. saveSlotsTransaction, 7. lastGeneratedId,
        8. platformStatsInfo, 9. freezedTrailers
        
        CompleteSave has similar requirements - never reorder fields!
        """
        with open(filepath, 'wb') as f:
            # CRITICAL: Don't use sort_keys - SnowRunner expects specific key order!
            # Python 3.7+ dicts maintain insertion order, so this preserves original order
            json_str = json.dumps(data, separators=(',', ':'), ensure_ascii=False)
            f.write(json_str.encode('utf-8'))
            f.write(b'\x00')  # Add null terminator - critical for SnowRunner!
    
    def _merge_common_save(self, p1: Dict, p2: Dict) -> Dict:
        """Merge CommonSslSave - take maximum progress from both players."""
        print("  📊 Merging achievements and progress...")
        
        # CRITICAL: Use proper deep copy that preserves key order
        # Start with p1 as template to maintain exact field ordering
        merged = copy.deepcopy(p1)
        
        p1_data = p1['CommonSslSave']['SslValue']
        p2_data = p2['CommonSslSave']['SslValue']
        merged_data = merged['CommonSslSave']['SslValue']
        
        # Merge achievement states - take the maximum progress
        # IMPORTANT: Only update values in-place, don't reassign the whole dict
        for achievement, p2_state in p2_data.get('achievementStates', {}).items():
            p1_state = p1_data.get('achievementStates', {}).get(achievement, {})
            
            # Handle different achievement types
            if '$type' in p2_state:
                achievement_type = p2_state['$type']
                
                if 'IntWithStringArrayAchievementState' in achievement_type:
                    # For array-based achievements, take union
                    p1_values = set(p1_state.get('valuesArray', []))
                    p2_values = set(p2_state.get('valuesArray', []))
                    merged_values = list(p1_values | p2_values)
                    
                    # Update in place to preserve field order
                    if achievement in merged_data['achievementStates']:
                        merged_data['achievementStates'][achievement]['valuesArray'] = merged_values
                        merged_data['achievementStates'][achievement]['currentValue'] = len(merged_values)
                        merged_data['achievementStates'][achievement]['isUnlocked'] = (
                            p1_state.get('isUnlocked', False) or p2_state.get('isUnlocked', False)
                        )
                    else:
                        merged_data['achievementStates'][achievement] = p2_state.copy()
                        merged_data['achievementStates'][achievement]['valuesArray'] = merged_values
                        merged_data['achievementStates'][achievement]['currentValue'] = len(merged_values)
                        merged_data['achievementStates'][achievement]['isUnlocked'] = (
                            p1_state.get('isUnlocked', False) or p2_state.get('isUnlocked', False)
                        )
                    
                elif 'PlatformIntWithStringArrayAchievementState' in achievement_type:
                    # Similar for platform-specific array achievements
                    p1_common = set(p1_state.get('commonValuesArray', []))
                    p2_common = set(p2_state.get('commonValuesArray', []))
                    merged_common = list(p1_common | p2_common)
                    
                    # Update in place to preserve field order
                    if achievement in merged_data['achievementStates']:
                        merged_data['achievementStates'][achievement]['commonValuesArray'] = merged_common
                        merged_data['achievementStates'][achievement]['commonValue'] = len(merged_common)
                        merged_data['achievementStates'][achievement]['isUnlocked'] = (
                            p1_state.get('isUnlocked', False) or p2_state.get('isUnlocked', False)
                        )
                    else:
                        merged_data['achievementStates'][achievement] = p2_state.copy()
                        merged_data['achievementStates'][achievement]['commonValuesArray'] = merged_common
                        merged_data['achievementStates'][achievement]['commonValue'] = len(merged_common)
                        merged_data['achievementStates'][achievement]['isUnlocked'] = (
                            p1_state.get('isUnlocked', False) or p2_state.get('isUnlocked', False)
                        )
                    
                elif 'IntAchievementState' in achievement_type or 'PlatformtIntAchievementState' in achievement_type:
                    # For numeric achievements, take maximum
                    p1_val = p1_state.get('currentValue', 0) or p1_state.get('commonValue', 0)
                    p2_val = p2_state.get('currentValue', 0) or p2_state.get('commonValue', 0)
                    max_val = max(p1_val, p2_val)
                    
                    # Update in place to preserve field order
                    if achievement in merged_data['achievementStates']:
                        if 'currentValue' in merged_data['achievementStates'][achievement]:
                            merged_data['achievementStates'][achievement]['currentValue'] = max_val
                        if 'commonValue' in merged_data['achievementStates'][achievement]:
                            merged_data['achievementStates'][achievement]['commonValue'] = max_val
                        merged_data['achievementStates'][achievement]['isUnlocked'] = (
                            p1_state.get('isUnlocked', False) or p2_state.get('isUnlocked', False)
                        )
                    else:
                        merged_data['achievementStates'][achievement] = p2_state.copy()
                        if 'currentValue' in p2_state:
                            merged_data['achievementStates'][achievement]['currentValue'] = max_val
                        if 'commonValue' in p2_state:
                            merged_data['achievementStates'][achievement]['commonValue'] = max_val
                        merged_data['achievementStates'][achievement]['isUnlocked'] = (
                            p1_state.get('isUnlocked', False) or p2_state.get('isUnlocked', False)
                        )
        
        # Merge platform stats - take maximum
        # CRITICAL: Update in place to preserve field order
        p1_stats = p1_data.get('platformStatsInfo', {})
        p2_stats = p2_data.get('platformStatsInfo', {})
        if 'platformStatsInfo' in merged_data:
            merged_data['platformStatsInfo']['totalDistanceMeters'] = max(
                p1_stats.get('totalDistanceMeters', 0),
                p2_stats.get('totalDistanceMeters', 0)
            )
            merged_data['platformStatsInfo']['totalCoopSessions'] = max(
                p1_stats.get('totalCoopSessions', 0),
                p2_stats.get('totalCoopSessions', 0)
            )
            merged_data['platformStatsInfo']['totalMoneyEarned'] = max(
                p1_stats.get('totalMoneyEarned', 0),
                p2_stats.get('totalMoneyEarned', 0)
            )
        
        print(f"    ✓ Merged achievements and discoveries")
        return merged
    
    def _merge_complete_save(self, p1: Dict, p2: Dict, customization_source: Dict) -> Dict:
        """Merge CompleteSave - share progress, preserve customizations."""
        print("  🚚 Merging trucks and game state...")
        
        # CRITICAL: Use proper deep copy that preserves key order
        merged = copy.deepcopy(p1)
        
        p1_data = p1['CompleteSave']['SslValue']
        p2_data = p2['CompleteSave']['SslValue']
        customization_data = customization_source['CompleteSave']['SslValue']
        merged_data = merged['CompleteSave']['SslValue']
        
        # Get persistent profile data
        p1_ppd = p1_data.get('persistentProfileData', {})
        p2_ppd = p2_data.get('persistentProfileData', {})
        custom_ppd = customization_data.get('persistentProfileData', {})
        
        # Ensure merged has persistentProfileData
        if 'persistentProfileData' not in merged_data:
            merged_data['persistentProfileData'] = {}
        merged_ppd = merged_data['persistentProfileData']
        
        # Merge money - take maximum
        p1_money = p1_ppd.get('money', 0)
        p2_money = p2_ppd.get('money', 0)
        merged_ppd['money'] = max(p1_money, p2_money)
        
        # Merge experience and rank - take maximum
        merged_ppd['experience'] = max(p1_ppd.get('experience', 0), p2_ppd.get('experience', 0))
        merged_ppd['rank'] = max(p1_ppd.get('rank', 0), p2_ppd.get('rank', 0))
        
        # Merge discovered trucks
        p1_discovered = set(p1_ppd.get('discoveredTrucks', []))
        p2_discovered = set(p2_ppd.get('discoveredTrucks', []))
        merged_ppd['discoveredTrucks'] = list(p1_discovered | p2_discovered)
        
        # Merge discovered upgrades
        p1_upgrades = set(p1_ppd.get('discoveredUpgrades', []))
        p2_upgrades = set(p2_ppd.get('discoveredUpgrades', []))
        merged_ppd['discoveredUpgrades'] = list(p1_upgrades | p2_upgrades)
        
        # Merge unlocked items
        p1_unlocked = set(p1_ppd.get('unlockedItemNames', []))
        p2_unlocked = set(p2_ppd.get('unlockedItemNames', []))
        merged_ppd['unlockedItemNames'] = list(p1_unlocked | p2_unlocked)
        
        # Merge known regions
        p1_regions = set(p1_ppd.get('knownRegions', []))
        p2_regions = set(p2_ppd.get('knownRegions', []))
        merged_ppd['knownRegions'] = list(p1_regions | p2_regions)
        
        # Merge trucks in warehouse - preserve customizations from specified player
        p1_warehouse = p1_ppd.get('trucksInWarehouse', [])
        p2_warehouse = p2_ppd.get('trucksInWarehouse', [])
        custom_warehouse = custom_ppd.get('trucksInWarehouse', [])
        
        # Create a map of truck IDs to truck data for easy lookup
        warehouse_map = {}
        for truck in p1_warehouse + p2_warehouse:
            truck_type = truck.get('type', '')
            if truck_type:
                warehouse_map[truck_type] = truck
        
        # Use customizations from specified player if available
        final_warehouse = []
        for truck in custom_warehouse:
            truck_type = truck.get('type', '')
            if truck_type in warehouse_map:
                # Use custom player's version (has their colors/mods)
                final_warehouse.append(truck)
                del warehouse_map[truck_type]
        
        # Add any trucks that custom player doesn't have yet
        final_warehouse.extend(warehouse_map.values())
        merged_ppd['trucksInWarehouse'] = final_warehouse
        
        # Merge discovered objectives at root level
        p1_objectives = set(p1_data.get('discoveredObjectives', []))
        p2_objectives = set(p2_data.get('discoveredObjectives', []))
        merged_data['discoveredObjectives'] = list(p1_objectives | p2_objectives)
        
        # Merge objective states - take union
        p1_obj_states = p1_data.get('objectiveStates', {})
        p2_obj_states = p2_data.get('objectiveStates', {})
        merged_obj_states = {}
        
        # Combine all objectives
        all_objectives = set(list(p1_obj_states.keys()) + list(p2_obj_states.keys()))
        for obj_id in all_objectives:
            p1_state = p1_obj_states.get(obj_id, {})
            p2_state = p2_obj_states.get(obj_id, {})
            
            # If either player completed it, mark as completed
            if p1_state or p2_state:
                # Take whichever has more data (likely more complete)
                merged_obj_states[obj_id] = p1_state if len(str(p1_state)) > len(str(p2_state)) else p2_state
        
        merged_data['objectiveStates'] = merged_obj_states
        
        truck_count = len(final_warehouse)
        print(f"    ✓ Merged {truck_count} trucks, money: ${merged_ppd['money']:,}")
        return merged
    
    def _ensure_minimum_money(self, complete_save: Dict):
        """Ensure money is at least MINIMUM_MONEY."""
        data = complete_save['CompleteSave']['SslValue']
        ppd = data.get('persistentProfileData', {})
        current_money = ppd.get('money', 0)
        
        if current_money < self.MINIMUM_MONEY:
            ppd['money'] = self.MINIMUM_MONEY
            print(f"    💰 Increased money from ${current_money:,} to ${self.MINIMUM_MONEY:,}")
        else:
            print(f"    💰 Money is ${current_money:,} (above minimum)")
    
    def _merge_binary_files(self):
        """Merge binary fog/sts/mudmaps files by selecting larger file (more progress)."""
        print("  🗺️  Merging map discovery files...")
        
        output_remote = self.output_dir / "remote"
        p1_remote = self.player1_dir / "remote"
        p2_remote = self.player2_dir / "remote"
        
        # Find all binary files
        binary_patterns = ['fog_*.cfg', 'sts_*.cfg', 'sts_mudmaps_*.cfg']
        
        merged_count = 0
        for pattern in binary_patterns:
            for p1_file in p1_remote.glob(pattern):
                filename = p1_file.name
                p2_file = p2_remote / filename
                output_file = output_remote / filename
                
                if not p2_file.exists():
                    # Only player1 has this file
                    shutil.copy2(p1_file, output_file)
                    merged_count += 1
                else:
                    # Both have it - use larger file (more progress)
                    p1_size = p1_file.stat().st_size
                    p2_size = p2_file.stat().st_size
                    
                    if p1_size >= p2_size:
                        shutil.copy2(p1_file, output_file)
                    else:
                        shutil.copy2(p2_file, output_file)
                    merged_count += 1
            
            # Check for files only player2 has
            for p2_file in p2_remote.glob(pattern):
                filename = p2_file.name
                p1_file = p1_remote / filename
                output_file = output_remote / filename
                
                if not p1_file.exists() and not output_file.exists():
                    shutil.copy2(p2_file, output_file)
                    merged_count += 1
        
        print(f"    ✓ Merged {merged_count} map files")
    
    def _copy_other_files(self, source_dir: Path, output_dir: Path):
        """Copy other configuration files from source player."""
        print("  📄 Copying other config files...")
        
        files_to_copy = [
            'remotecache.vdf',
            'remote/user_settings.cfg',
            'remote/user_profile.cfg',
            'remote/GameVersionSave.cfg',
            'remote/user_social_data.cfg',
            'remote/video.cfg'
        ]
        
        for filepath in files_to_copy:
            src = source_dir / filepath
            dst = output_dir / filepath
            
            if src.exists():
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
        
        print(f"    ✓ Copied config files")
    
    def _validate_field_order(self, filepath: Path, expected_order: List[str]) -> bool:
        """
        Validate that JSON fields are in expected order.
        Returns True if order is correct, False otherwise.
        """
        with open(filepath, 'rb') as f:
            content = f.read().rstrip(b'\x00').decode('utf-8')
            
        # Find positions of each field
        positions = {}
        for field in expected_order:
            pos = content.find(f'"{field}":')
            if pos != -1:
                positions[field] = pos
        
        # Check if positions are in ascending order
        last_pos = -1
        for field in expected_order:
            if field in positions:
                if positions[field] < last_pos:
                    return False
                last_pos = positions[field]
        
        return True


def main():
    parser = argparse.ArgumentParser(description='Merge SnowRunner save files')
    parser.add_argument('player1_dir', help='ftovaro save directory')
    parser.add_argument('player2_dir', help='svanegasg save directory')
    parser.add_argument('output_dir', help='Output directory for merged save')
    parser.add_argument('--preserve', choices=['ftovaro', 'svanegasg'], required=True,
                        help='Which player\'s customizations to preserve')
    
    args = parser.parse_args()
    
    try:
        merger = SnowRunnerSaveMerger(args.player1_dir, args.player2_dir, args.output_dir)
        merger.merge(args.preserve)
        return 0
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
