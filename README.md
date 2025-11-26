# SnowRunner Save Sync

Automatically sync SnowRunner game progress between two players (`ftovaro` and `svanegasg`) while preserving individual truck customizations.

## ⚡ Quick Start

### Before Opening the Game
```bash
# Pull latest changes, prefer remote if conflicts
git pull -X theirs origin YOUR_BRANCH
```

### After Playing - Share Progress
```bash
# Sync with other player
git add .
git commit -m "Completed missions [trigger]"
git push
```

### After Opening Game - No Changes to Share
```bash
# Game auto-saves even if you do nothing
# Discard these changes if not playing
git stash
```

## 🎮 How It Works

### Three Branches System
- **`ftovaro`** - Player 1's save with personal truck customizations
- **`svanegasg`** - Player 2's save with personal truck customizations  
- **`main`** - Shared reference save with default truck configurations

### What Gets Synced

When you commit with `[trigger]` in the message:

✅ **Synced to Everyone**:
- New trucks discovered/purchased
- Money (automatically set to minimum $200k)
- Mission progress & achievements
- Map discoveries & upgrades
- Game progression

🎨 **Kept Personal** (per branch):
- Truck paint colors & skins
- Engine, gearbox, suspension upgrades
- Addons (snorkels, bumpers, stickers)
- Truck damage levels
- Wheel configurations

## 🚀 Daily Usage

### Initial Setup (in your SnowRunner save folder)

```bash
# Clone the repository
git clone https://github.com/ftovaro/snowrunner_save_sync.git
cd snowrunner_save_sync

# Checkout your branch
git checkout YOUR_BRANCH  # ftovaro or svanegasg
```

### Before Playing

```bash
git pull origin YOUR_BRANCH
```

Copy the `remote/` folder contents to your SnowRunner save location:
- **Windows**: `C:\Program Files (x86)\Steam\userdata\109587900\1465360\remote\`

### After Playing - Regular Save

Copy your SnowRunner `remote/` folder back to the repository, then:

```bash
git add remote/
git commit -m "Playing session"
git push
```

This **only updates money** to $200k minimum in your branch.

### After Playing - Sync with Others

When you want to share progress with the other player:

```bash
git add remote/
git commit -m "Completed Alaska region [trigger]"
git push
```

The `[trigger]` keyword activates the full sync:
1. ✅ Your progress synced to `main` (preserving main's default truck colors)
2. ✅ `main` synced to other player's branch (preserving their truck customizations)
3. ✅ Everyone gets new trucks, money, and progression
4. ✅ Everyone keeps their personal truck styles

## 🔧 Technical Details

### Scripts

- **`simple_money_update.py`** - Ensures minimum $200k money using string replacement (no JSON parsing)
- **`sync_to_main.py`** - Syncs saves between branches preserving truck customizations
- **`truck_customization_paths.py`** - Documents truck data structure and displays inventory

### GitHub Actions Workflow

**Trigger**: Any push to `ftovaro` or `svanegasg` branches

**Jobs**:
1. **update-money** - Always runs, ensures minimum $200k
2. **sync-to-main** - Only with `[trigger]`, syncs to main preserving customizations
3. **sync-to-other-branch** - Only with `[trigger]`, syncs main to other player

### Truck Customization Keys (Preserved Per Branch)

```python
# Performance
'engine', 'gearbox', 'suspension', 'winchUpgrade'
'wheelsType', 'tires', 'rims', 'wheelsScale'

# Visual
'customizationPreset'  # Colors, paint, skins
'addons'  # Snorkels, bumpers, stickers

# State
'engineDamage', 'gearboxDamage', 'suspensionDamage'
'fuel', 'water', 'repairs'
```

## 📁 Repository Structure

```
.
├── .github/workflows/
│   └── sync-saves.yml          # GitHub Actions workflow
├── remote/                      # Current save files
│   ├── CompleteSave.cfg        # Main game progress
│   └── CommonSslSave.cfg       # Achievements
├── scripts/
│   ├── simple_money_update.py  # Money updater
│   ├── sync_to_main.py         # Save sync with customization preservation
│   └── truck_customization_paths.py  # Truck data documentation
└── README.md
```
- **Test locally**: `./scripts/test_merge.sh`
- **Workflow**: `.github/workflows/sync-saves.yml` - Auto-triggers on push

**Happy trucking! 🚛**
