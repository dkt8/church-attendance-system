# Contributing to QR Code Attendance System

Thank you for your interest in contributing to the QR Code Attendance System! This document provides guidelines for contributing to the project.

## 🤝 How to Contribute

### Reporting Bugs

1. **Check existing issues** first to avoid duplicates
2. **Use the bug report template** when creating new issues
3. **Provide detailed information**:
   - Operating system and version
   - Python version
   - Browser (for web interface issues)
   - Steps to reproduce the issue
   - Expected vs actual behavior
   - Screenshots if applicable

### Suggesting Features

1. **Check existing feature requests** to avoid duplicates
2. **Use the feature request template**
3. **Provide clear use cases** and benefits
4. **Consider implementation complexity**

### Code Contributions

#### Setup Development Environment

```bash
# Fork and clone the repository
git clone https://github.com/yourusername/qr-attendance-system.git
cd qr-attendance-system

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install black flake8 pytest
```

#### Development Workflow

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**:
   - Follow existing code style
   - Add comments for complex logic
   - Update documentation if needed

3. **Test your changes**:
   ```bash
   # Run basic tests
   python scripts/generate_qr_codes.py data/templates/students_template.csv
   
   # Format code
   black src/ scripts/
   
   # Check code style
   flake8 src/ scripts/
   ```

4. **Commit your changes**:
   ```bash
   git add .
   git commit -m "Add: Brief description of your changes"
   ```

5. **Push and create Pull Request**:
   ```bash
   git push origin feature/your-feature-name
   ```

#### Code Style Guidelines

- **Python**: Follow PEP 8 style guide
- **JavaScript**: Use consistent indentation and naming
- **Comments**: Write clear, concise comments
- **Documentation**: Update README.md for user-facing changes

#### Commit Message Convention

```
Type: Brief description

Detailed description if needed

Types:
- Add: New features
- Fix: Bug fixes
- Update: Improvements to existing features
- Docs: Documentation changes
- Style: Code formatting changes
- Refactor: Code refactoring
- Test: Adding or updating tests
```

## 📋 Development Guidelines

### Python Code

- Use type hints where appropriate
- Follow existing error handling patterns
- Add docstrings to functions and classes
- Keep functions focused and small

### Google Apps Script

- Use consistent naming conventions
- Add error handling for all external calls
- Comment complex logic
- Test with different data scenarios

### Configuration

- Don't hardcode values
- Use configuration files appropriately
- Provide sensible defaults
- Document configuration options

## 🧪 Testing

### Manual Testing

1. **QR Generation**:
   - Test with various CSV formats
   - Verify QR codes scan correctly
   - Check ID card generation

2. **Web Interface**:
   - Test camera functionality
   - Verify QR scanning accuracy
   - Check error handling

3. **Google Sheets Integration**:
   - Test attendance recording
   - Verify time-based logic
   - Check data accuracy

### Automated Testing

We welcome contributions to improve our testing infrastructure:
- Unit tests for Python modules
- Integration tests for the full workflow
- Browser automation for web interface testing

## 📚 Documentation

### Code Documentation

- Add docstrings to all public functions
- Include parameter types and return values
- Provide usage examples

### User Documentation

- Update README.md for new features
- Add examples and use cases
- Keep installation instructions current

## 🎯 Priority Areas

We especially welcome contributions in these areas:

1. **Testing Infrastructure**: Automated testing setup
2. **Error Handling**: Improved error messages and recovery
3. **Performance**: Optimization for large datasets
4. **Documentation**: Examples and tutorials
5. **Mobile Support**: Better mobile web interface
6. **Internationalization**: Multi-language support

## ❓ Questions?

- **General questions**: Create a discussion or issue
- **Implementation questions**: Comment on relevant issues
- **Security concerns**: Email maintainers directly

## 🙏 Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes for significant contributions
- GitHub contributor graphs

Thank you for helping make the QR Code Attendance System better for everyone!
