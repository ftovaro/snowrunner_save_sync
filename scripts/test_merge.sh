#!/bin/bash
# Test merge script locally before pushing to GitHub

set -e

echo "🧪 Testing SnowRunner Save Merge Script"
echo "======================================="
echo ""

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Create temp directories
TEST_DIR="/tmp/snowrunner_merge_test"
rm -rf "$TEST_DIR"
mkdir -p "$TEST_DIR"

echo "📁 Creating test directories..."
CURRENT_DIR="$(pwd)"

# Test 1: Merge with ftovaro customizations
echo ""
echo "Test 1: Merging with ftovaro customizations preserved"
python3 scripts/merge_saves.py \
    "$CURRENT_DIR" \
    "$CURRENT_DIR" \
    "$TEST_DIR/output_ftovaro" \
    --preserve ftovaro

# Test 2: Merge with svanegasg customizations
echo ""
echo "Test 2: Merging with svanegasg customizations preserved"
python3 scripts/merge_saves.py \
    "$CURRENT_DIR" \
    "$CURRENT_DIR" \
    "$TEST_DIR/output_svanegasg" \
    --preserve svanegasg

# Verify outputs
echo ""
echo "🔍 Verifying merged saves..."
python3 << 'EOF'
import json

def check_save(path, player):
    try:
        with open(f"{path}/remote/CompleteSave.cfg", 'rb') as f:
            data = json.loads(f.read().rstrip(b'\x00').decode('utf-8'))
            ppd = data['CompleteSave']['SslValue']['persistentProfileData']
            money = ppd.get('money', 0)
            trucks = len(ppd.get('trucksInWarehouse', []))
            
            print(f"\n✅ {player} merge successful:")
            print(f"   💰 Money: ${money:,}")
            print(f"   🚚 Trucks: {trucks}")
            
            if money < 200000:
                print(f"   ⚠️  Warning: Money is below $200,000")
                return False
            return True
    except Exception as e:
        print(f"\n❌ {player} merge failed: {e}")
        return False

success = True
success &= check_save("/tmp/snowrunner_merge_test/output_ftovaro", "ftovaro")
success &= check_save("/tmp/snowrunner_merge_test/output_svanegasg", "svanegasg")

if success:
    print("\n✅ All tests passed! Script is ready for GitHub Actions.")
else:
    print("\n❌ Some tests failed. Please check the script.")
    exit(1)
EOF

# Cleanup
echo ""
echo "🧹 Cleaning up test files..."
rm -rf "$TEST_DIR"

echo ""
echo "✅ Testing complete! You can now push to GitHub."
