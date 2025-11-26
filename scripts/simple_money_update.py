#!/usr/bin/env python3
"""
Simple money updater - only touches the money value, nothing else.
No JSON parsing, no field reordering, just direct string replacement.
"""

import sys
import re
from pathlib import Path

MINIMUM_MONEY = 200000

def update_money_in_file(filepath: Path) -> bool:
    """Update money value if below minimum. Returns True if changed."""
    
    # Read file as bytes to preserve everything
    with open(filepath, 'rb') as f:
        content = f.read()
    
    # Convert to string but keep null terminator separate
    has_null = content[-1] == 0
    text = content.rstrip(b'\x00').decode('utf-8')
    
    # Navigate to the correct money location:
    # CompleteSave.SslValue.persistentProfileData.money
    # Pattern: "persistentProfileData":{...lots of stuff..."money":12345
    
    # Find persistentProfileData section
    ppd_start = text.find('"persistentProfileData":{')
    if ppd_start == -1:
        print(f"  ⚠️  Could not find persistentProfileData in {filepath.name}")
        return False
    
    # Now find "money": after persistentProfileData (within that section)
    # Look for the pattern starting from persistentProfileData
    search_section = text[ppd_start:]
    money_pattern = r'"money":(\d+)'
    match = re.search(money_pattern, search_section)
    
    if not match:
        print(f"  ⚠️  Could not find money in persistentProfileData")
        return False
    
    current_money = int(match.group(1))
    print(f"  Current money (in persistentProfileData): ${current_money:,}")
    
    if current_money >= MINIMUM_MONEY:
        print(f"  ✓ Money is above minimum (${MINIMUM_MONEY:,})")
        return False
    
    # Replace the money value we found
    # Calculate absolute position in the full text
    money_pos_in_section = match.start()
    money_pos_absolute = ppd_start + money_pos_in_section
    
    old_pattern = f'"money":{current_money}'
    new_pattern = f'"money":{MINIMUM_MONEY}'
    
    # Replace at the specific position
    new_text = text[:money_pos_absolute] + new_pattern + text[money_pos_absolute + len(old_pattern):]
    
    # Write back preserving null terminator
    with open(filepath, 'wb') as f:
        f.write(new_text.encode('utf-8'))
        if has_null:
            f.write(b'\x00')
    
    print(f"  ✓ Updated money from ${current_money:,} to ${MINIMUM_MONEY:,}")
    return True


def main():
    if len(sys.argv) > 1:
        save_dir = Path(sys.argv[1])
    else:
        save_dir = Path(__file__).parent.parent / "remote"
    
    complete_save = save_dir / "CompleteSave.cfg"
    
    print("=== Simple Money Update ===")
    print(f"Target: {complete_save}")
    
    if not complete_save.exists():
        print(f"❌ File not found: {complete_save}")
        return 1
    
    print()
    changed = update_money_in_file(complete_save)
    
    if changed:
        print("\n✓ Money updated successfully")
    else:
        print("\n✓ No changes needed")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
