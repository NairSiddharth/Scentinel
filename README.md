# Scentinel - Advanced Fragrance Tracking & Analytics

**Your intelligent fragrance companion for tracking, analyzing, and discovering your perfect scent rotation.**

## Table of Contents

- [Features](#features)
  - [Smart Tracking](#smart-tracking)
  - [Advanced Analytics](#advanced-analytics)
  - [Intelligent Recommendations](#intelligent-recommendations)
  - [Modern UI/UX](#modern-uiux)
- [Development Status](#development-status)
- [Quick Start](#quick-start)
  - [Prerequisites](#prerequisites)
  - [Option 1: Executable (Recommended)](#option-1-executable-recommended)
  - [Option 2: From Source](#option-2-from-source)
- [Usage Guide](#usage-guide)
  - [Getting Started](#getting-started)
  - [CSV Import](#csv-import)
  - [JSON Templates & Bulk Import](#json-templates--bulk-import)
  - [Data Management](#data-management)
- [Architecture](#architecture)
  - [Core Components](#core-components)
  - [Database Schema](#database-schema)
  - [Analytics Engine](#analytics-engine)
- [Advanced Features](#advanced-features)
  - [Smart Recommendations](#smart-recommendations)
  - [Analytics Insights](#analytics-insights)
- [Configuration](#configuration)
  - [Settings](#settings)
- [Contributing](#contributing)
  - [Development Setup](#development-setup)
- [License](#license)
- [Acknowledgments](#acknowledgments)
- [Tech Stack](#tech-stack)

Scentinel transforms basic cologne tracking into a comprehensive fragrance management system with AI-powered recommendations, detailed analytics, and professional bottle imagery.

## Features

### **Smart Tracking**

- **Collection Management**: Track colognes with notes, brands, and classifications
- **Wear Logging**: Record when, where, and how you rate each fragrance
- **Seasonal Context**: Automatic season detection with occasion-based logging
- **CSV Import/Export**: Bulk import your collection or backup your data

### **Advanced Analytics**

- **Wear Frequency Insights**: Identify neglected, overused, and well-rotated bottles
- **Seasonal Deep Dive**: Detailed analysis of your seasonal preferences and patterns
- **Usage Patterns**: Track diversity scores and monthly breakdowns
- **Visual Dashboard**: Interactive Plotly charts with hover details and insights

### **Intelligent Recommendations**

- **Rotation Suggestions**: Smart recommendations based on usage patterns and ratings
- **Similar Fragrance Discovery**: Find new favorites based on shared notes and classifications
- **Seasonal Matching**: Context-aware suggestions for current weather
- **Neglected Bottle Alerts**: Rediscover forgotten gems in your collection

### **Modern UI/UX**

- **Dark/Light Mode**: Beautiful themes with smooth transitions
- **Responsive Design**: Works perfectly on desktop and mobile
- **Tabbed Interface**: Clean organization with URL-based navigation
- **Professional Styling**: Gradient headers, glass-morphism cards, and hover effects

## Development Status

This project is actively developed with most core features complete. See [TODO.md](TODO.md) for current development priorities and planned features.

**Current Status**: Production-ready with executable available. Primary focus now on performance optimization for large collections.

## Quick Start

### Prerequisites

- Python 3.8+
- pip package manager

### Option 1: Executable (Recommended)

1. **Download the executable** from the releases page
2. **Run Scentinel.exe** directly - no installation required!

### Option 2: From Source

1. **Clone the repository**

   ```bash
   git clone https://github.com/yourusername/Scentinel.git
   cd Scentinel
   ```

2. **Create virtual environment** *(recommended)*

   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**

   ```bash
   python run.py
   ```

## Usage Guide

### Getting Started

1. **Add Your First Cologne**: Click "Add Cologne" in the header
2. **Log Your Wears**: Use "Log Wear" to track usage with ratings
3. **Explore Analytics**: Visit the Analytics tab for insights
4. **Get Recommendations**: Check the sidebar for smart suggestions

### CSV Import

Upload a CSV file with columns:

- `name`: Cologne name
- `brand`: Brand name
- `notes`: Semicolon-separated fragrance notes
- `classifications`: Semicolon-separated categories

### JSON Templates & Bulk Import

For larger collections, use our JSON templates for efficient bulk import:

#### **Quick Start Templates**

- `quick_start/cologne_example_template.json` - 5 real examples + 5 empty slots
- `quick_start/cologne_template_50.json` - 50 empty cologne slots
- `quick_start/TEMPLATE_GUIDE.md` - Complete usage documentation

#### **Custom Template Generator**

Generate templates with any number of slots:

```bash
# Generate 100 empty cologne slots
python scripts/generate_template.py 100

# Generate 50 slots with 5 example colognes
python scripts/generate_template.py 50 --with-examples

# Custom filename
python scripts/generate_template.py 25 --output my_collection.json
```

**Template Features:**

- **Additive Imports**: Multiple imports add to your collection (50→100→150)
- **Duplicate Prevention**: Skips existing colognes (by name + brand)
- **Comprehensive Data**: Supports notes, classifications, and wear history
- **Flexible**: Empty templates or pre-filled examples

### Data Management

- **Export**: Download complete JSON backup from Settings tab
- **Import**: Restore from JSON backup with full data integrity
- **Search**: Find colognes by name, brand, notes, or classifications

## Architecture

### Core Components

- **`scentinel/main.py`**: Main NiceGUI application with tabbed interface
- **`scentinel/database.py`**: SQLAlchemy models and analytics engine
- **`scentinel/recommender.py`**: ML-based recommendation algorithms
- **`scentinel/tabs/`**: Modular tab components for UI organization
- **`run.py`**: Application launcher script

### Database Schema

- **Colognes**: Name, brand with many-to-many relationships
- **Fragrance Notes**: Reusable note library (bergamot, sandalwood, etc.)
- **Classifications**: Categories (fresh, woody, oriental, etc.)
- **Wear History**: Usage logs with ratings, seasons, and occasions

### Analytics Engine

- **Wear Frequency Analysis**: Usage pattern detection
- **Seasonal Modeling**: Preference trends over time
- **Similarity Matching**: Content-based filtering using Jaccard coefficients
- **Behavioral Analysis**: User preference learning

## Advanced Features

### Smart Recommendations

- **Content-Based**: Similarity matching using TF-IDF vectorization
- **Behavioral**: Usage pattern analysis with recency weighting
- **Hybrid**: Combined approach for optimal suggestions
- **Contextual**: Season and occasion-aware recommendations

### Analytics Insights

- **Neglected Bottles**: Haven't worn in 30+ days
- **Seasonal Favorites**: Top fragrances per season
- **Diversity Scores**: Variety measurement in your rotation
- **Usage Trends**: Monthly and yearly pattern analysis

## Configuration

### Settings

- **Dark Mode**: Toggle in header with system preference detection
- **Analytics Refresh**: Real-time updates on data changes

## Contributing

I welcome contributions! Please see my contributing guidelines:

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/amazing-feature`
3. **Commit changes**: `git commit -m 'Add amazing feature'`
4. **Push to branch**: `git push origin feature/amazing-feature`
5. **Open Pull Request**

### Development Setup

```bash
# Install development dependencies
pip install -r requirements.txt

# For development with hot reload, edit scentinel/main.py:
# Change ui.run(reload=False) to ui.run(reload=True) on line 391

# Run the application
python run.py  # starts the application
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **NiceGUI**: Modern Python web framework
- **Plotly**: Interactive data visualization
- **Scikit-learn**: Machine learning recommendations
- **SQLAlchemy**: Robust database management
- **Tailwind CSS**: Opinionated, responsive styling

## Tech Stack

- **Backend**: Python, SQLAlchemy, Scikit-learn
- **Frontend**: NiceGUI, Tailwind CSS, Plotly
- **Database**: SQLite with advanced analytics
- **ML**: TF-IDF vectorization, cosine similarity

---

**Made for fragrance enthusiasts who want to optimize their scent journey.**
