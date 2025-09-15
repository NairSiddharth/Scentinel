# 🌸 Scentinel - Advanced Fragrance Tracking & Analytics

**Your intelligent fragrance companion for tracking, analyzing, and discovering your perfect scent rotation.**

**Note that this README.md was generated via Claude Code, it has been proofread but please report any errors spotted in the instructions and I will take a look!**

Scentinel transforms basic cologne tracking into a comprehensive fragrance management system with AI-powered recommendations, detailed analytics, and professional bottle imagery.

## ✨ Features

### 🎯 **Smart Tracking**

- **Collection Management**: Track colognes with notes, brands, and classifications
- **Wear Logging**: Record when, where, and how you rate each fragrance
- **Seasonal Context**: Automatic season detection with occasion-based logging
- **CSV Import/Export**: Bulk import your collection or backup your data

### 📊 **Advanced Analytics**

- **Wear Frequency Insights**: Identify neglected, overused, and well-rotated bottles
- **Seasonal Deep Dive**: Detailed analysis of your seasonal preferences and patterns
- **Usage Patterns**: Track diversity scores and monthly breakdowns
- **Visual Dashboard**: Interactive Plotly charts with hover details and insights

### 🔍 **Intelligent Recommendations**

- **Rotation Suggestions**: Smart recommendations based on usage patterns and ratings
- **Similar Fragrance Discovery**: Find new favorites based on shared notes and classifications
- **Seasonal Matching**: Context-aware suggestions for current weather
- **Neglected Bottle Alerts**: Rediscover forgotten gems in your collection

### 📸 **Professional Imagery** *(Coming Soon)*

- **Automatic Bottle Photos**: Scrapes high-quality images from fragrance databases
- **Image Compression**: Optimized storage with automatic resizing
- **Storage Management**: Size monitoring with cleanup utilities
- **Offline Caching**: Local image storage with metadata tracking

### 🎨 **Modern UI/UX**

- **Dark/Light Mode**: Beautiful themes with smooth transitions
- **Responsive Design**: Works perfectly on desktop and mobile
- **Tabbed Interface**: Clean organization with URL-based navigation
- **Professional Styling**: Gradient headers, glass-morphism cards, and hover effects

## 📝 TODO

1. **Center the navbar**
2. **Center the settings buttons**
3. **Make the footer stretch across the full app**
4. **Add a "floating menu" in the bottom right corner** (dark mode toggle + other similar features)
5. **Move Wear Frequency Insights to the top of its section in Analytics**
6. **Stretch empty table in collection container**
7. **Generate test data**
8. **Finish actual data**
9. **Create executable**
10. **Update README installation instructions** - Fix references to `app.py` (should be `src/scentinel/main.py`)
11. **Add error handling for missing image directory** - Graceful fallback when `data/images/cologne.png` is missing
12. **Configuration file support** - Add config file for port, database path, and other settings
13. **Input validation** - Sanitize and validate all user inputs for security
14. **Loading states/spinners** - Add loading indicators for analytics refresh and data operations
15. **Confirm dialogs for destructive actions** - Add confirmation for data import/export operations
16. **Bulk operations** - Allow selecting multiple colognes for batch actions
17. **Advanced search filters** - Add filters by rating, last worn date, notes, etc.
18. **Usage recommendations widget** - Show "You haven't worn X in Y days" notifications
19. **Performance optimization** - Optimize for large collections (1000+ fragrances)

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- pip package manager

### Installation

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

5. **Open your browser**

   Navigate to `http://localhost:8080`

## 📖 Usage Guide

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

- `data/cologne_example_template.json` - 5 real examples + 5 empty slots
- `data/cologne_template_50.json` - 50 empty cologne slots
- `data/TEMPLATE_GUIDE.md` - Complete usage documentation

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

- ✅ **Additive Imports**: Multiple imports add to your collection (50→100→150)
- ✅ **Duplicate Prevention**: Skips existing colognes (by name + brand)
- ✅ **Comprehensive Data**: Supports notes, classifications, and wear history
- ✅ **Flexible**: Empty templates or pre-filled examples

### Data Management

- **Export**: Download complete JSON backup from Settings tab
- **Import**: Restore from JSON backup with full data integrity
- **Search**: Find colognes by name, brand, notes, or classifications

## 🛠 Architecture

### Core Components

- **`src/scentinel/main.py`**: Main NiceGUI application with tabbed interface
- **`src/scentinel/database.py`**: SQLAlchemy models and analytics engine
- **`src/scentinel/recommender.py`**: ML-based recommendation algorithms
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

## 🎯 Advanced Features

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

## 🔧 Configuration

### Environment Variables

- `SCENTINEL_PORT`: Application port (default: 8080)
- `SCENTINEL_DB`: Database file path (default: scentinel.db)

### Settings

- **Dark Mode**: Toggle in header with system preference detection
- **Photo Storage**: Configurable image compression and cleanup
- **Analytics Refresh**: Real-time updates on data changes

## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines:

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/amazing-feature`
3. **Commit changes**: `git commit -m 'Add amazing feature'`
4. **Push to branch**: `git push origin feature/amazing-feature`
5. **Open Pull Request**

### Development Setup

```bash
# Install development dependencies
pip install -r requirements.txt

# Run with auto-reload for development
python run.py  # starts the application
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **NiceGUI**: Modern Python web framework
- **Plotly**: Interactive data visualization
- **Scikit-learn**: Machine learning recommendations
- **SQLAlchemy**: Robust database management
- **Tailwind CSS**: Beautiful, responsive styling

## 📊 Tech Stack

- **Backend**: Python, SQLAlchemy, Scikit-learn
- **Frontend**: NiceGUI, Tailwind CSS, Plotly
- **Database**: SQLite with advanced analytics
- **Images**: PIL/Pillow for compression
- **ML**: TF-IDF vectorization, cosine similarity

---

**Made with ❤️ for fragrance enthusiasts who want to optimize their scent journey.**
