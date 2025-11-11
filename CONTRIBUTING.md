# Contributing to WhatsApp Sales Bot

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## 🤝 How to Contribute

### Reporting Bugs

Before creating bug reports, please check existing issues. When creating a bug report, include:

- **Clear title** - Descriptive and specific
- **Steps to reproduce** - Detailed steps to reproduce the issue
- **Expected behavior** - What you expected to happen
- **Actual behavior** - What actually happened
- **Environment** - OS, Python version, Chrome version
- **Logs** - Relevant log excerpts (remove sensitive data)
- **Screenshots** - If applicable

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion:

- **Use a clear title** - Describe the enhancement
- **Provide detailed description** - Explain why this enhancement would be useful
- **Include examples** - Show how it would work
- **Consider alternatives** - List any alternative solutions

### Pull Requests

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```

3. **Make your changes**
   - Follow the coding standards below
   - Add tests if applicable
   - Update documentation

4. **Commit your changes**
   ```bash
   git commit -m "Add amazing feature"
   ```

5. **Push to your fork**
   ```bash
   git push origin feature/amazing-feature
   ```

6. **Open a Pull Request**
   - Provide clear description
   - Reference related issues
   - Wait for review

## 💻 Development Setup

### Local Development

```bash
# Clone your fork
git clone https://github.com/yourusername/whatsapp-sales-bot.git
cd whatsapp-sales-bot

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install pytest black flake8 mypy
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=helpers tests/

# Run specific test
pytest tests/test_message_helper.py
```

## 📝 Coding Standards

### Python Style Guide

We follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) with some modifications:

```python
# Good
def send_message(driver, name, program):
    """
    Send a WhatsApp message.
    
    Args:
        driver: Selenium WebDriver instance
        name (str): Recipient name
        program (str): Program name
        
    Returns:
        bool: True if successful
    """
    message = format_message(name, program)
    return whatsapp_helper.send(driver, message)

# Bad
def send_msg(d,n,p):
    msg = format_msg(n,p)
    return wh.send(d,msg)
```

### Code Formatting

Use **Black** for consistent formatting:
```bash
black helpers/ main.py
```

### Linting

Use **Flake8** to check code quality:
```bash
flake8 helpers/ main.py --max-line-length=100
```

### Type Hints

Use type hints where appropriate:
```python
def clean_phone(phone: str) -> str | None:
    """Clean and validate phone number."""
    ...
```

### Docstrings

All functions should have docstrings:
```python
def fetch_leads(campuses: list, batch_size: int = 5) -> list:
    """
    Fetch leads from database.
    
    Args:
        campuses (list): List of campus names
        batch_size (int, optional): Number of leads to fetch
        
    Returns:
        list: List of lead records
        
    Raises:
        DatabaseError: If connection fails
    """
```

## 🗂️ Project Structure

```
whatsapp-sales-bot/
├── helpers/
│   ├── __init__.py           # Package initialization
│   ├── db_helper.py          # Database operations
│   ├── whatsapp_helper.py    # WhatsApp automation
│   ├── message_helper.py     # Message templates
│   └── email_helper.py       # Email notifications
├── tests/
│   ├── test_db_helper.py
│   ├── test_message_helper.py
│   └── test_email_helper.py
├── main.py                   # Main application
├── config.json               # Configuration
├── messages.json             # Message templates
├── requirements.txt
└── README.md
```

## 🧪 Testing Guidelines

### Writing Tests

```python
import pytest
from helpers.message_helper import MessageHelper

def test_normalize_program():
    """Test program name normalization."""
    helper = MessageHelper("messages.json")
    
    assert helper.normalize_program("Ph.D.") == "phd"
    assert helper.normalize_program("MBA Online") == "mba"
    assert helper.normalize_program("  Multiple   Spaces  ") == "multiple spaces"

def test_format_message():
    """Test message formatting with template."""
    helper = MessageHelper("test_messages.json")
    
    message = helper.format_message(
        name="John Doe",
        program="MBA",
        phone="+1234567890"
    )
    
    assert "John Doe" in message
    assert "MBA" in message
```

### Test Coverage

Aim for at least 80% code coverage:
```bash
pytest --cov=helpers --cov-report=html
```

## 📚 Documentation

### Code Comments

```python
# Good - Explains WHY
# Use clipboard to preserve emojis and formatting
pyperclip.copy(message)

# Bad - Explains WHAT (obvious from code)
# Copy message to clipboard
pyperclip.copy(message)
```

### README Updates

When adding features, update:
- Features list
- Configuration section
- Usage examples
- Troubleshooting if needed

## 🔒 Security

### Reporting Vulnerabilities

**Do NOT** create public issues for security vulnerabilities.

Instead:
1. Email security@example.com
2. Include detailed description
3. Provide reproduction steps
4. Wait for acknowledgment

### Security Considerations

- Never commit `.env` files
- Don't log sensitive data (passwords, API keys)
- Validate all user inputs
- Use parameterized SQL queries
- Keep dependencies updated

## 📋 Checklist Before Submitting PR

- [ ] Code follows style guidelines
- [ ] All tests pass
- [ ] New tests added for new features
- [ ] Documentation updated
- [ ] No sensitive data in commits
- [ ] Commit messages are clear
- [ ] Branch is up to date with main

## 🎯 Priority Areas for Contribution

We especially welcome contributions in these areas:

1. **Additional Message Templates** - More program-specific templates
2. **Error Handling** - Better error recovery mechanisms
3. **Testing** - Increase test coverage
4. **Documentation** - Improve setup guides and examples
5. **Performance** - Optimization for high-volume scenarios
6. **Features** - See open issues tagged "enhancement"

## 💬 Getting Help

- **Questions?** Open a GitHub Discussion
- **Chat?** Join our Discord (if available)
- **Email?** contact@example.com

## 📜 Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inspiring community for all.

### Our Standards

**Positive behaviors:**
- Using welcoming and inclusive language
- Being respectful of differing viewpoints
- Gracefully accepting constructive criticism
- Focusing on what is best for the community

**Unacceptable behaviors:**
- Harassment or discriminatory language
- Trolling or insulting comments
- Publishing others' private information
- Other unprofessional conduct

### Enforcement

Violations may be reported to project maintainers who will review and investigate.

## 🙏 Thank You!

Your contributions make this project better. Whether it's:
- Fixing a typo
- Adding a feature
- Reporting a bug
- Improving documentation

Every contribution is valuable and appreciated! ❤️

---

**Questions?** Feel free to ask in issues or discussions!
