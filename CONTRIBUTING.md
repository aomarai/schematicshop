# Contributing to SchematicShop

**Private Repository** - Internal development guidelines for team members.

## Getting Started

1. Clone the repository (requires access): `git clone https://github.com/aomarai/schematicshop.git`
2. Create a branch: `git checkout -b feature/your-feature-name`
3. Make your changes
4. Test your changes thoroughly
5. Commit: `git commit -m "Add your feature"`
6. Push: `git push origin feature/your-feature-name`
7. Open a Pull Request for review

## Development Setup

Follow the instructions in the [README.md](README.md) to set up your development environment.

Quick start:
```bash
./setup-dev.sh
```

## Code Style

### Python (Backend)
- Follow PEP 8 style guide
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Keep functions focused and small
- Write type hints where appropriate

### JavaScript/TypeScript (Frontend)
- Use TypeScript for new files
- Follow the Airbnb JavaScript Style Guide
- Use functional components with hooks
- Keep components small and focused
- Use meaningful prop names

## Testing

### Backend Tests
```bash
cd backend
pytest
pytest --cov=apps  # With coverage
```

### Frontend Tests
```bash
cd frontend
npm test
npm run test:coverage
```

## Commit Messages

Follow the Conventional Commits specification:

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes (formatting, etc.)
- `refactor:` Code refactoring
- `test:` Adding or updating tests
- `chore:` Maintenance tasks

Examples:
```
feat: add 3D schematic preview
fix: resolve upload progress tracking issue
docs: update API documentation
```

## Pull Request Process

1. Update documentation if needed
2. Add tests for new features
3. Ensure all tests pass
4. Update the README.md if necessary
5. Reference any related issues in the PR description
6. Wait for code review and address feedback

## Code Review

All submissions require review. We use GitHub pull requests for this purpose.

Reviewers will check:
- Code quality and style
- Test coverage
- Documentation
- Performance implications
- Security considerations

## Areas for Contribution

### High Priority
- 3D schematic preview in browser
- Advanced search filters
- Performance optimizations
- Mobile responsiveness improvements

### Good First Issues
- UI/UX improvements
- Documentation enhancements
- Test coverage improvements
- Bug fixes

### Feature Requests
- Collections and playlists
- User follow system
- Community forums
- In-browser schematic editor

## Questions?

Feel free to open an issue for:
- Bug reports
- Feature requests
- Documentation improvements
- General questions

## Code of Conduct

Be respectful and constructive in all interactions. We are committed to providing a welcoming and inclusive environment for all contributors.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
