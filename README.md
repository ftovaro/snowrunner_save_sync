# SnowRunner Save Sync

Automatically sync SnowRunner progress between two players while preserving individual truck customizations.

## 🎮 What Gets Synced

✅ **Shared**: Missions, achievements, discoveries, trucks, money (min $200k)  
🎨 **Individual**: Truck colors, modifications, parts

## 🚀 Setup

### SnowRunner Save Locations
- **Windows**: `C:\Program Files (x86)\Steam\userdata\109587900\1465360\remote\`

### Initial Setup (in your SnowRunner save folder)

```bash
git init
git add .
git commit -m "Initial saves"
git remote add origin https://github.com/ftovaro/snowrunner_save.git
git branch -M main
git push -u origin main

# Create branches
git checkout -b ftovaro
git push -u origin ftovaro
git checkout -b svanegasg
git push -u origin svanegasg
```

### Daily Usage

**Before playing:**
```bash
git pull origin YOUR_BRANCH
```

**After playing:**
```bash
git add .
git commit -m "Completed [mission/area]"
git push origin YOUR_BRANCH
```

GitHub Actions automatically merges progress to both branches. Just pull to get updates!

## 🔧 Technical Details

- **Merge script**: `scripts/merge_saves.py` - Merges JSON saves and binary map files
- **Test locally**: `./scripts/test_merge.sh`
- **Workflow**: `.github/workflows/sync-saves.yml` - Auto-triggers on push

**Happy trucking! 🚛**
