# Contributing to Scentinel

Thank you for your interest in contributing to Scentinel! This guide will help you get started with contributing to our fragrance management system.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Documentation](#documentation)
- [Pull Request Process](#pull-request-process)
- [Issue Guidelines](#issue-guidelines)
- [Feature Requests](#feature-requests)

## Code of Conduct

This project follows a simple code of conduct: be respectful, constructive, and helpful. We welcome contributors of all skill levels and backgrounds.

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- Basic understanding of Python, SQLAlchemy, and web development
- Familiarity with fragrance terminology is helpful but not required

### First Contribution Ideas

Good first contributions include:
- Fixing typos or improving documentation
- Adding new fragrance notes or classifications
- Improving error messages
- Adding unit tests
- Small UI improvements
- Bug fixes

## Development Setup

### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then clone your fork
git clone https://github.com/yourusername/Scentinel.git
cd Scentinel
```

### 2. Set Up Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
# Install all dependencies
pip install -r requirements.txt

# For development with hot reload
# Edit scentinel/main.py and change ui.run(reload=False) to ui.run(reload=True)
```

### 4. Run the Application

```bash
python run.py
```

The application will start on `http://localhost:8080`

### 5. Set Up Git Hooks (Optional)

```bash
# Set up pre-commit hooks for code formatting
pip install pre-commit
pre-commit install
```

## Project Structure

```
Scentinel/
├── scentinel/
│   ├── main.py              # Main NiceGUI application
│   ├── database.py          # SQLAlchemy models and analytics
│   ├── recommender.py       # ML recommendation algorithms
│   ├── tabs/               # UI tab components
│   │   ├── collection.py
│   │   ├── analytics.py
│   │   ├── recommendations.py
│   │   └── settings.py
│   └── utils/              # Utility functions
├── scripts/                # Helper scripts
├── quick_start/           # Templates and examples
├── requirements.txt       # Python dependencies
├── run.py                # Application launcher
└── TODO.md               # Development roadmap
```

## Development Workflow

### Creating a Feature Branch

```bash
# Create and switch to a new feature branch
git checkout -b feature/your-feature-name

# Or for bug fixes
git checkout -b bugfix/issue-description
```

### Making Changes

1. **Small Commits**: Make small, focused commits with clear messages
2. **Test Locally**: Always test your changes locally before pushing
3. **Check TODO.md**: Align your work with current development priorities
4. **Update Documentation**: Update relevant documentation for your changes

### Commit Message Guidelines

Use clear, descriptive commit messages:

```bash
# Good examples
git commit -m "Add support for vintage fragrance classifications"
git commit -m "Fix analytics crash when no wear data exists"
git commit -m "Improve responsive design for mobile devices"

# Avoid
git commit -m "fix bug"
git commit -m "update stuff"
```

## Coding Standards

### Python Style

- Follow PEP 8 guidelines
- Use meaningful variable and function names
- Add docstrings for new functions and classes
- Keep functions focused and concise
- Use type hints where appropriate

### Code Organization

- **Models**: Database models go in `database.py`
- **UI Components**: New tabs go in `scentinel/tabs/`
- **Algorithms**: Recommendation logic goes in `recommender.py`
- **Utilities**: Helper functions go in `scentinel/utils/`

### NiceGUI Best Practices

- Use consistent styling with existing components
- Implement responsive design considerations
- Follow the existing tab structure for new features
- Use appropriate NiceGUI components for the task

## Testing

### Manual Testing

Before submitting changes:

1. **Basic Functionality**: Test core features (add cologne, log wear, view analytics)
2. **Edge Cases**: Test with empty databases, large collections, invalid inputs
3. **UI Testing**: Test on different screen sizes and both light/dark modes
4. **Import/Export**: Test CSV and JSON import/export functionality

### Adding Tests

While we don't have a comprehensive test suite yet, contributions of tests are welcome:

- Unit tests for database functions
- Integration tests for recommendation algorithms
- UI component tests

## Documentation

### Code Documentation

- Add docstrings for new functions and classes
- Include type hints for function parameters and returns
- Comment complex algorithms or business logic

### User Documentation

- Update README.md for new features
- Add examples to quick_start/ for complex features
- Update TODO.md when completing planned features

## Pull Request Process

### Before Submitting

1. **Rebase**: Rebase your branch on the latest main branch
2. **Test**: Ensure all functionality works as expected
3. **Clean Up**: Remove debug code, temporary files, and unnecessary comments
4. **Documentation**: Update relevant documentation

### PR Description

Include in your pull request:

- **Description**: Clear description of what your PR does
- **Changes**: List of specific changes made
- **Testing**: How you tested your changes
- **Screenshots**: For UI changes, include before/after screenshots
- **Related Issues**: Reference any related GitHub issues

### Example PR Template

```markdown
## Description
Brief description of the changes

## Changes Made
- Added new feature X
- Fixed bug in Y
- Updated documentation for Z

## Testing
- Tested with small collection (5 colognes)
- Tested with large collection (100+ colognes)
- Verified analytics calculations
- Tested import/export functionality

## Screenshots (if applicable)
[Include screenshots for UI changes]

## Related Issues
Closes #123
```

## Issue Guidelines

### Bug Reports

When reporting bugs, include:

- **Steps to Reproduce**: Clear steps to reproduce the issue
- **Expected Behavior**: What you expected to happen
- **Actual Behavior**: What actually happened
- **Environment**: OS, Python version, installation method
- **Collection Size**: Approximate number of colognes and wear logs
- **Screenshots/Logs**: If applicable

### Feature Requests

For feature requests:

- **Use Case**: Describe the problem you're trying to solve
- **Proposed Solution**: Your suggested approach
- **Alternatives**: Other solutions you've considered
- **Priority**: How important this is to your workflow

## Feature Requests

We welcome feature requests! Check TODO.md for current priorities, but don't let that stop you from suggesting new ideas.

### Current Focus Areas

- Performance optimization for large collections
- Advanced analytics and visualizations
- Mobile experience improvements
- Additional recommendation algorithms
- Import/export format support

### Implementation Guidelines

- **Start Small**: Break large features into smaller, manageable pieces
- **Discuss First**: Open an issue to discuss major features before implementing
- **User-Centric**: Focus on features that improve the user experience
- **Performance**: Consider impact on users with large collections

## Getting Help

- **GitHub Issues**: For bug reports and feature requests
- **Discussions**: For questions about development or usage
- **Code Review**: Don't hesitate to ask for feedback on your approach

## Recognition

All contributors will be recognized in the project. We value all types of contributions:

- Code contributions
- Bug reports
- Feature suggestions
- Documentation improvements
- User testing and feedback

Thank you for contributing to Scentinel! Your efforts help make fragrance management better for everyone.