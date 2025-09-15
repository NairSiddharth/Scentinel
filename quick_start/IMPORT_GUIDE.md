# 🚀 Scentinel Quick Start Guide

This folder contains everything you need to get started with Scentinel quickly! Choose between JSON (full-featured) or CSV (basic data) import methods.

## 📂 Available Files

### JSON Import (Recommended - Full Features)

- **`cologne_example_template.json`**: Example template with 5 filled examples + 5 empty slots
- **`cologne_template_50.json`**: Empty template with 50 cologne slots

### CSV Import (Basic Data Only)

- **`template.csv`**: Empty CSV template with proper headers
- **`sample_collection.csv`**: Example CSV with 6 popular fragrances

## 🎯 Import Methods Comparison

| Feature | JSON Import | CSV Import |
|---------|-------------|------------|
| **Cologne Data** | ✅ Full details | ✅ Basic info only |
| **Wear History** | ✅ Complete tracking | ❌ Not supported |
| **Ratings** | ✅ Individual wear ratings | ❌ Not supported |
| **Seasons/Occasions** | ✅ Detailed tracking | ❌ Not supported |
| **Duplicate Resolution** | ✅ Smart handling | ❌ Basic only |
| **Best For** | Complete collections | Quick bulk additions |

## 📋 JSON Templates

## 📝 How to Fill Out Templates

### Required Fields (Must be filled)

- `"name"`: The fragrance name (e.g., "Bleu de Chanel")
- `"brand"`: The brand name (e.g., "Chanel")

### Optional Fields

- `"notes"`: Array of fragrance notes (e.g., `["bergamot", "cedar", "vanilla"]`)
- `"classifications"`: Array of categories (e.g., `["fresh", "woody", "aromatic"]`)
- `"wear_history"`: Array of wear records (see format below)

### Wear History Format

```json
{
  "date": "2024-09-14T08:00:00",
  "season": "fall",
  "occasion": "work",
  "rating": 4.5
}
```

**Valid Seasons**: `spring`, `summer`, `fall`, `winter`
**Valid Occasions**: `casual`, `work`, `date`, `formal`, `exercise`, `special`
**Rating Range**: 1.0 - 5.0 (decimals allowed like 4.5)

## 🚀 Quick Start Guide

1. **Choose Your Template**:
   - New user? Start with `cologne_example_template.json`
   - Large collection? Use `cologne_template_50.json`

2. **Fill in Your Data**:

   ```json
   {
     "id": 1,
     "name": "Your Fragrance Name",
     "brand": "Brand Name",
     "notes": ["note1", "note2", "note3"],
     "classifications": ["fresh", "woody"],
     "wear_history": []
   }
   ```

3. **Import to Scentinel**:
   - Open Scentinel app
   - Go to Settings tab
   - Click "Import Collection"
   - Upload your filled JSON file

## 📊 CSV Import Guide

### Quick CSV Import

1. **Start with Template**:
   - Use `template.csv` for headers: `name,brand,notes,classifications`
   - Or modify `sample_collection.csv` with your own fragrances

2. **CSV Format Rules**:
   ```csv
   name,brand,notes,classifications
   Sauvage,Dior,bergamot;pepper;ambroxan,fresh;masculine;designer
   ```
   - **Semicolons** separate multiple notes/classifications
   - **No spaces** around semicolons
   - **Required**: name and brand columns
   - **Optional**: notes and classifications columns

3. **Import to Scentinel**:
   - Open Scentinel app
   - Go to Settings tab
   - Drag and drop your CSV file to the CSV Import area

### CSV Limitations
- ❌ No wear history import
- ❌ No ratings
- ❌ Limited duplicate handling
- ✅ Quick way to add basic cologne info

## 💡 Pro Tips

### Common Fragrance Notes

**Citrus**: bergamot, lemon, lime, orange, grapefruit, mandarin
**Floral**: jasmine, rose, lavender, orange blossom, neroli, ylang ylang
**Woody**: cedar, sandalwood, vetiver, oud, birch, oakmoss
**Spicy**: pepper, cardamom, cinnamon, nutmeg, ginger, cloves
**Sweet**: vanilla, amber, tonka bean, honey, caramel
**Fresh**: mint, eucalyptus, sea breeze, ozone, cucumber

### Common Classifications

**Freshies**: fresh, citrus, aquatic, marine, green
**Woody**: woody, cedar, sandalwood, vetiver
**Orientals**: oriental, amber, spicy, exotic
**Gourmands**: gourmand, sweet, vanilla, foodie
**Special**: luxury, niche, designer, vintage, seasonal

### Date Format Notes

- Use ISO 8601 format: `"2024-09-14T08:00:00"`
- Time represents when you applied the fragrance
- No timezone needed (assumes local time)

## ⚠️ Common Mistakes to Avoid

1. **Empty Required Fields**: Both `name` and `brand` must have values
2. **Invalid JSON**: Use a JSON validator to check syntax
3. **Wrong Date Format**: Must be ISO 8601 (`YYYY-MM-DDTHH:MM:SS`)
4. **Invalid Seasons/Occasions**: Must match the valid values listed above
5. **Rating Out of Range**: Must be between 1.0 and 5.0

## 🔍 Validation Checklist

Before importing, verify:

- [ ] All fragrance names and brands are filled in
- [ ] JSON syntax is valid (use a JSON validator)
- [ ] Dates are in correct format
- [ ] Seasons are: spring/summer/fall/winter
- [ ] Occasions are: casual/work/date/formal/exercise/special
- [ ] Ratings are between 1.0 and 5.0
- [ ] Notes and classifications are meaningful strings

## 🛠️ Troubleshooting

**Import Failed?**

1. Check JSON syntax with online validator
2. Verify required fields are not empty
3. Check date formats match ISO 8601
4. Ensure seasons/occasions use valid values

**Duplicates Detected?**

- Scentinel skips colognes with same name + brand
- Check for exact name/brand matches in your collection

**Missing Data?**

- Empty arrays `[]` are perfectly fine for notes/classifications
- You can always add data later through the app

## 📊 Example Data Scenarios

### Minimal Entry (Just Basics)

```json
{
  "id": 1,
  "name": "Sauvage",
  "brand": "Dior",
  "notes": [],
  "classifications": [],
  "wear_history": []
}
```

### Full Entry (Complete Data)

```json
{
  "id": 2,
  "name": "Bleu de Chanel",
  "brand": "Chanel",
  "notes": ["bergamot", "cedar", "ginger", "sandalwood"],
  "classifications": ["fresh", "woody", "versatile"],
  "wear_history": [
    {
      "date": "2024-09-14T08:00:00",
      "season": "fall",
      "occasion": "work",
      "rating": 4.5
    }
  ]
}
```

---

**Need Help?** Check the main README.md or create an issue on GitHub!
