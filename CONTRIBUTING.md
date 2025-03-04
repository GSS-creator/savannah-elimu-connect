# Contributing to Savannah Elimu Connect

Thank you for your interest in contributing to Savannah Elimu Connect! This document provides guidelines and instructions for contributing to the project.

## Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct:
- Be respectful and inclusive
- Use welcoming and inclusive language
- Be collaborative
- Focus on what is best for the community
- Show empathy towards other community members

## How to Contribute

### Setting Up Development Environment

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/your-username/-savannah-elimu-connect.git
   cd -savannah-elimu-connect
   ```

3. Set up virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configurations
   ```

### Development Workflow

1. Create a new branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes following our coding standards:
   - Use clear, descriptive variable and function names
   - Follow PEP 8 style guide
   - Add comments for complex logic
   - Write tests for new features

3. Run tests locally:
   ```bash
   pytest
   ```

4. Format your code:
   ```bash
   black .
   isort .
   flake8 .
   ```

5. Commit your changes:
   ```bash
   git add .
   git commit -m "Description of changes"
   ```

6. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

7. Create a Pull Request

### Pull Request Guidelines

1. PR Title Format:
   - feat: Add new feature
   - fix: Fix bug
   - docs: Update documentation
   - style: Code style changes
   - refactor: Code refactoring
   - test: Add tests
   - chore: Maintenance tasks

2. PR Description should include:
   - Purpose of the PR
   - Changes made
   - How to test the changes
   - Screenshots (if applicable)
   - Related issues

3. Checks that must pass:
   - Code formatting
   - Tests
   - Security checks
   - Coverage requirements (80% minimum)

### Adding New Features

1. Language Support:
   - Follow existing language implementation patterns
   - Include language metadata
   - Add translation files
   - Update language selection UI

2. Educational Content:
   - Follow content guidelines
   - Include metadata
   - Add appropriate tags
   - Ensure mobile responsiveness

3. AI Features:
   - Document model requirements
   - Include performance metrics
   - Add error handling
   - Provide fallback options

### Documentation

1. Code Documentation:
   - Add docstrings to functions and classes
   - Include type hints
   - Document complex algorithms
   - Add inline comments for clarity

2. User Documentation:
   - Update README.md
   - Add usage examples
   - Include screenshots
   - Document configuration options

### Testing

1. Write tests for:
   - New features
   - Bug fixes
   - Edge cases
   - API endpoints

2. Test categories:
   - Unit tests
   - Integration tests
   - UI tests
   - Performance tests

### Reporting Issues

1. Include:
   - Clear description
   - Steps to reproduce
   - Expected vs actual behavior
   - Screenshots/logs
   - Environment details

2. Label issues appropriately:
   - bug
   - enhancement
   - documentation
   - help wanted

## Contact

For questions or support:
- Email: gastonsoftwaresolutions234@gmail.com
- Support: support@savannahelimu.com

## Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Credited in documentation

Thank you for contributing to making education more accessible across Africa! 