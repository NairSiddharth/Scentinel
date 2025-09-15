# 📊 Scentinel Data Formats Documentation

This document provides comprehensive specifications for all data formats supported by Scentinel.

## 📋 Table of Contents

- [JSON Format (Complete)](#json-format-complete)
- [CSV Format (Basic Import)](#csv-format-basic-import)
- [Data Validation Rules](#data-validation-rules)
- [Import/Export Behavior](#importexport-behavior)

---

## 🎯 JSON Format (Complete)

The JSON format supports all Scentinel features including wear history, ratings, and complete metadata.

### 📁 File Structure

```json
{
  "metadata": {
    "version": "1.0",
    "created_date": "2024-09-14T12:00:00Z",
    "total_colognes": 50,
    "total_wear_records": 156
  },
  "colognes": [
    {
      "name": "Fragrance Name",
      "brand": "Brand Name",
      "notes": ["note1", "note2", "note3"],
      "classifications": ["classification1", "classification2"],
      "wear_history": [
        {
          "date": "2024-09-14T08:00:00",
          "season": "fall",
          "occasion": "work",
          "rating": 4.5
        }
      ]
    }
  ]
}
```

### 🔧 Field Specifications

#### Required Fields
- **`name`** (string): Fragrance name
  - Must be non-empty
  - Maximum 200 characters
  - Example: `"Bleu de Chanel"`

- **`brand`** (string): Brand name
  - Must be non-empty
  - Maximum 100 characters
  - Example: `"Chanel"`

#### Optional Fields

- **`notes`** (array of strings): Fragrance notes
  - Each note: 1-50 characters
  - Common examples: `["bergamot", "cedar", "vanilla"]`
  - Can be empty array: `[]`

- **`classifications`** (array of strings): Fragrance categories
  - Each classification: 1-30 characters
  - Common examples: `["fresh", "woody", "designer"]`
  - Can be empty array: `[]`

- **`wear_history`** (array of objects): Wear records
  - Can be empty array: `[]`
  - See wear history format below

#### Wear History Format

```json
{
  "date": "2024-09-14T08:00:00",
  "season": "fall",
  "occasion": "work",
  "rating": 4.5
}
```

**Wear Record Fields:**
- **`date`** (string, required): ISO 8601 datetime
  - Format: `YYYY-MM-DDTHH:MM:SS`
  - Timezone optional (assumes local if not specified)

- **`season`** (string, required): Season worn
  - Valid values: `"spring"`, `"summer"`, `"fall"`, `"winter"`

- **`occasion`** (string, required): Occasion type
  - Valid values: `"casual"`, `"work"`, `"date"`, `"formal"`, `"exercise"`, `"special"`

- **`rating`** (number, required): User rating
  - Range: 1.0 to 5.0
  - Decimals allowed (e.g., 4.5)

---

## 📊 CSV Format (Basic Import)

The CSV format provides quick bulk import for basic cologne data only.

### 📁 File Structure

```csv
name,brand,notes,classifications
Sauvage,Dior,bergamot;pepper;ambroxan,fresh;masculine;designer
Bleu de Chanel,Chanel,citrus;incense;cedar,fresh;versatile;designer
```

### 🔧 Field Specifications

#### Required Columns
- **`name`**: Fragrance name (same rules as JSON)
- **`brand`**: Brand name (same rules as JSON)

#### Optional Columns
- **`notes`**: Semicolon-separated fragrance notes
  - Format: `note1;note2;note3`
  - No spaces around semicolons
  - Can be empty

- **`classifications`**: Semicolon-separated classifications
  - Format: `classification1;classification2;classification3`
  - No spaces around semicolons
  - Can be empty

### 📝 CSV Format Rules

1. **Headers Required**: First row must contain column names
2. **Comma Separation**: Standard CSV comma separation
3. **Semicolon Lists**: Multiple values separated by semicolons (no spaces)
4. **Quotes**: Use quotes around values containing commas
5. **Encoding**: UTF-8 encoding recommended

### ❌ CSV Limitations

- No wear history import
- No ratings support
- No date tracking
- Limited duplicate resolution
- No metadata support

---

## ✅ Data Validation Rules

### Global Rules
- All string fields trimmed of leading/trailing whitespace
- Empty strings converted to null values
- Case-sensitive matching for enums (seasons, occasions)

### Duplicate Detection
- Duplicates identified by: `name + brand` combination
- Case-insensitive matching
- Leading/trailing spaces ignored

### Import Behavior
- **JSON Import**: Full duplicate resolution workflow
- **CSV Import**: Basic duplicate checking, skips duplicates by default

---

## 🔄 Import/Export Behavior

### JSON Import Process
1. **File Validation**: Schema validation
2. **Duplicate Analysis**: Detect existing colognes
3. **Resolution Dialog**: User chooses how to handle duplicates
4. **Data Import**: Execute with chosen resolutions
5. **Transaction Logging**: Record import details

### CSV Import Process
1. **File Parsing**: Read CSV with error handling
2. **Row Validation**: Validate each row individually
3. **Duplicate Skipping**: Skip existing name+brand combinations
4. **Bulk Insert**: Add valid rows to database
5. **Error Reporting**: Report any problematic rows

### Export Process
1. **Data Collection**: Gather all cologne and wear data
2. **JSON Generation**: Create complete JSON structure
3. **Metadata Addition**: Add export timestamp and counts
4. **File Download**: Trigger browser download

---

## 📚 Examples

### Complete JSON Example
```json
{
  "metadata": {
    "version": "1.0",
    "created_date": "2024-09-14T12:00:00Z",
    "total_colognes": 2,
    "total_wear_records": 3
  },
  "colognes": [
    {
      "name": "Sauvage",
      "brand": "Dior",
      "notes": ["bergamot", "pepper", "ambroxan"],
      "classifications": ["fresh", "masculine", "designer"],
      "wear_history": [
        {
          "date": "2024-09-14T08:00:00",
          "season": "fall",
          "occasion": "work",
          "rating": 4.5
        },
        {
          "date": "2024-09-13T19:30:00",
          "season": "fall",
          "occasion": "date",
          "rating": 5.0
        }
      ]
    },
    {
      "name": "Aventus",
      "brand": "Creed",
      "notes": ["pineapple", "birch", "vanilla"],
      "classifications": ["fruity", "smoky", "niche"],
      "wear_history": [
        {
          "date": "2024-09-12T20:00:00",
          "season": "fall",
          "occasion": "special",
          "rating": 4.8
        }
      ]
    }
  ]
}
```

### Complete CSV Example
```csv
name,brand,notes,classifications
Sauvage,Dior,bergamot;pepper;ambroxan,fresh;masculine;designer
Aventus,Creed,pineapple;birch;vanilla,fruity;smoky;niche
Bleu de Chanel,Chanel,citrus;incense;cedar,fresh;versatile;designer
Tom Ford Oud Wood,Tom Ford,oud;sandalwood;vanilla,woody;oriental;luxury
Acqua di Gio,Giorgio Armani,marine;bergamot;white musk,aquatic;fresh;designer
La Nuit de L'Homme,Yves Saint Laurent,lavender;cedar;coumarin,seductive;evening;designer
```

---

## 🛠️ Technical Notes

### Database Schema Alignment
- JSON format maps directly to database schema
- CSV import creates minimal records (no wear history)
- All imports generate transaction logs for auditing

### Performance Considerations
- Large JSON files (>1000 colognes): ~5-10 seconds import time
- CSV files: Very fast import for basic data
- Export generation: Scales with wear history volume

### Error Handling
- JSON: Schema validation catches format errors early
- CSV: Row-by-row validation with detailed error reporting
- Both: Transaction rollback on critical errors