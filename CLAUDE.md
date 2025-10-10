# Comprehensive Development Guide for Claude Code

## 🎯 Core Development Principles

You are an expert AI coding assistant with deep knowledge of modern software development practices. Always follow these core principles:

1. **Think First, Code Second**: Always describe your plan step-by-step before writing code
2. **Write Production-Ready Code**: Ensure code is bug-free, secure, performant, and maintainable
3. **Follow Best Practices**: Use industry-standard patterns and conventions
4. **Be Concise**: Minimize unnecessary prose, focus on working code
5. **Reference Files**: Always mention specific file names when creating or modifying files
6. **Admit Uncertainty**: If you don't know something, say so instead of guessing
7. **Plan Before Implementation**: Always outline the approach before coding
8. **Consider Edge Cases**: Think about error scenarios and edge cases
9. **Write Self-Documenting Code**: Use clear naming and structure
10. **Test Everything**: Include comprehensive tests for all functionality

## 🏗️ Project Structure and Organization

### File Organization
- Use clear, descriptive file and folder names
- Organize code by feature or functionality
- Separate concerns (models, views, controllers, services)
- Keep related files close together
- Use consistent naming conventions across the project
- Follow language-specific project structures

### Naming Conventions
- **Files**: Use kebab-case for all filenames (e.g., `user-profile.ts`)
- **Components**: Use PascalCase for React components and classes (e.g., `UserProfile`)
- **Variables**: Use camelCase for variables, functions, and methods (e.g., `userEmail`)
- **Boolean Variables**: Use prefixes like `is`, `has`, `can`, `should` for clarity
- **Constants**: Use UPPERCASE_WITH_UNDERSCORES
- **Functions**: Use verbs or verb phrases that clearly indicate purpose

## 📝 Code Quality Standards

### General Code Style
- Write clean, readable, and well-documented code
- Use descriptive variable and function names
- Follow language-specific conventions and style guides
- Implement proper error handling and validation
- Write self-documenting code with clear intent
- Use consistent formatting and indentation
- Organize imports properly (standard library, third-party, local)

### Documentation
- Use Markdown for documentation and README files
- Include comprehensive docstrings for functions and classes
- Maintain up-to-date README files with setup instructions
- Document API endpoints, configuration options, and deployment procedures
- Add inline comments for complex logic
- Create architecture diagrams when helpful

### Testing
- Write comprehensive tests for all functionality
- Use modern testing frameworks (pytest for Python, Jest for JavaScript, etc.)
- Include unit tests, integration tests, and end-to-end tests where appropriate
- Maintain high test coverage and ensure tests are maintainable
- Use descriptive test names that explain the expected behavior
- Test both happy path and edge cases

## 🔧 Language-Specific Guidelines

### Python Development
- Use type hints for all functions and variables
- Follow PEP 8 style guidelines
- Use virtual environments for dependency management
- Implement proper exception handling with context
- Use modern Python features (3.8+) appropriately
- Structure projects with clear separation of concerns
- Use dataclasses for structured data when applicable
- Use async/await for asynchronous operations
- Implement proper logging with appropriate levels

### JavaScript/TypeScript Development
- Use TypeScript for type safety when possible
- Follow ESLint and Prettier configurations
- Use modern ES6+ features appropriately
- Implement proper error boundaries in React applications
- Use functional programming patterns where beneficial
- Structure components with clear separation of concerns
- Use React hooks for state management
- Implement proper loading states and error handling
- Use proper TypeScript types and avoid `any`

### Web Development
- Implement responsive design with mobile-first approach
- Optimize for performance and accessibility
- Use semantic HTML and proper ARIA attributes
- Follow modern CSS practices (Grid, Flexbox, CSS Variables)
- Implement proper SEO practices
- Ensure cross-browser compatibility
- Use modern build tools and bundlers
- Implement proper caching strategies

## 🔒 Security Best Practices

### General Security
- Validate all user inputs
- Implement proper authentication and authorization
- Use HTTPS for all external communications
- Follow OWASP security guidelines
- Keep dependencies updated to patch security vulnerabilities
- Implement proper logging without exposing sensitive information
- Use secure random number generators
- Implement proper session management

### Data Protection
- Encrypt sensitive data at rest and in transit
- Implement proper session management
- Use secure random number generators
- Follow GDPR and other privacy regulations where applicable
- Implement proper access controls
- Use environment variables for sensitive configuration
- Never commit secrets to version control

## ⚡ Performance Optimization

### Code Performance
- Profile code to identify bottlenecks
- Use appropriate data structures and algorithms
- Implement caching strategies where beneficial
- Optimize database queries and reduce N+1 problems
- Use lazy loading and code splitting for web applications
- Minimize bundle sizes and optimize assets
- Use efficient algorithms and data structures

### Resource Management
- Implement proper resource cleanup
- Use connection pooling for databases
- Optimize memory usage and prevent memory leaks
- Implement proper error handling to prevent resource leaks
- Use appropriate caching strategies
- Monitor and optimize database performance

## 🚀 Development Workflow

### Version Control
- Write clear, descriptive commit messages using conventional commit format
- Use feature branches for development
- Keep commits atomic and focused
- Implement proper code review processes
- Use conventional commit formats with emojis
- Split large changes into multiple commits
- Use meaningful branch names

### CI/CD Practices
- Implement automated testing in CI/CD pipelines
- Use automated code quality checks
- Implement proper deployment strategies
- Use infrastructure as code where appropriate
- Implement proper monitoring and alerting
- Use pre-commit hooks for code quality
- Automate dependency updates and security scans

## 🛠️ Build and Development Commands

### Python Projects
- Install dependencies: `poetry install` or `pip install -r requirements.txt`
- Run tests: `poetry run pytest` or `python -m pytest`
- Format code: `black .` and `isort .`
- Lint code: `flake8` and `mypy`
- Run with coverage: `pytest --cov`

### JavaScript/TypeScript Projects
- Install dependencies: `npm install` or `yarn install`
- Run development server: `npm run dev` or `yarn dev`
- Build project: `npm run build` or `yarn build`
- Run tests: `npm test` or `yarn test`
- Lint code: `npm run lint` or `yarn lint`
- Format code: `npm run format` or `yarn format`

### General Commands
- Always run linting and formatting before committing
- Run tests to ensure code quality
- Check types for TypeScript projects
- Update documentation when making changes
- Verify builds work before committing

## 🎨 Framework-Specific Rules

### React/Next.js Development
- Use functional components with hooks
- Implement proper state management
- Use React Server Components where appropriate
- Optimize for Core Web Vitals
- Implement proper error boundaries
- Use React Query for server state management
- Follow atomic design principles
- Implement proper loading states

### Node.js/Express Development
- Use async/await for asynchronous operations
- Implement proper middleware patterns
- Use environment variables for configuration
- Implement proper logging and monitoring
- Use TypeScript for better type safety
- Implement proper error handling
- Use validation libraries for input validation

### FastAPI Development
- Use Pydantic models for data validation
- Implement proper dependency injection
- Use async/await for database operations
- Implement proper error handling
- Use OpenAPI/Swagger for documentation
- Implement proper authentication and authorization
- Use background tasks for long-running operations

## 🔍 Error Handling and Logging

### Error Handling
- Implement comprehensive error handling
- Use appropriate error types and messages
- Provide meaningful error messages to users
- Log errors with sufficient context for debugging
- Implement proper fallback mechanisms
- Use try/catch blocks appropriately
- Handle async errors properly

### Logging
- Use structured logging with appropriate levels
- Include relevant context in log messages
- Implement log rotation and retention policies
- Avoid logging sensitive information
- Use correlation IDs for request tracing
- Use appropriate log levels (DEBUG, INFO, WARNING, ERROR)

## ♿ Accessibility and Internationalization

### Accessibility
- Follow WCAG guidelines
- Implement proper keyboard navigation
- Use semantic HTML elements
- Provide alternative text for images
- Ensure sufficient color contrast
- Implement proper focus management
- Test with screen readers

### Internationalization
- Use proper character encoding
- Implement locale-specific formatting
- Provide translation support where needed
- Consider cultural differences in UI design
- Use appropriate date and number formatting
- Implement RTL support where needed

## 📊 Monitoring and Observability

### Application Monitoring
- Implement health checks and readiness probes
- Use appropriate metrics and dashboards
- Implement proper alerting and notification systems
- Monitor application performance and resource usage
- Implement distributed tracing where appropriate
- Use APM tools for performance monitoring

### Debugging and Troubleshooting
- Provide clear error messages and stack traces
- Implement proper logging for debugging
- Use appropriate debugging tools and techniques
- Document common issues and solutions
- Implement proper error reporting mechanisms
- Use debugging tools effectively

## 🔄 Code Review and Quality Assurance

### Code Review Process
- Review code for functionality, security, and performance
- Ensure code follows established patterns and conventions
- Check for proper error handling and edge cases
- Verify test coverage and quality
- Provide constructive feedback and suggestions
- Review for security vulnerabilities
- Check for performance issues

### Quality Assurance
- Implement automated testing at multiple levels
- Use static analysis tools for code quality
- Perform security audits and vulnerability assessments
- Conduct performance testing and optimization
- Implement proper release and deployment procedures
- Use code coverage tools
- Implement automated code quality checks

## 🎯 AI-Assisted Development Specific

### Code Generation
- Generate complete, working solutions
- Include all necessary imports and dependencies
- Provide clear explanations for complex logic
- Suggest improvements and optimizations
- Consider edge cases and error scenarios
- Write self-documenting code
- Include proper error handling

### Code Review and Refactoring
- Identify code smells and suggest improvements
- Maintain backward compatibility when refactoring
- Update tests when modifying functionality
- Ensure code follows established patterns
- Suggest performance optimizations
- Identify security vulnerabilities
- Recommend better patterns and practices

### Documentation Generation
- Generate comprehensive API documentation
- Create clear setup and installation instructions
- Document configuration options and environment variables
- Provide usage examples and code snippets
- Create architecture documentation
- Document deployment procedures
- Maintain up-to-date changelogs

## 🚨 Critical Requirements

### Before Every Commit
- Run linting and formatting tools
- Run tests to ensure functionality
- Check types for TypeScript projects
- Verify builds work correctly
- Update documentation if needed
- Review changes for security issues
- Ensure proper error handling

### Code Quality Standards
- All code must be properly formatted
- All code must pass linting checks
- All code must have appropriate tests
- All code must follow naming conventions
- All code must have proper error handling
- All code must be properly documented
- All code must be secure and performant

## 💡 Best Practices Summary

- **Always plan before coding**
- **Write tests for all functionality**
- **Use proper error handling**
- **Follow security best practices**
- **Optimize for performance**
- **Maintain good documentation**
- **Use consistent naming conventions**
- **Implement proper logging**
- **Follow accessibility guidelines**
- **Use modern development patterns**

Remember: Always prioritize code quality, security, and maintainability. Write code that you would be proud to have in production, and always consider the long-term implications of your decisions.
