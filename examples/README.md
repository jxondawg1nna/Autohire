# Examples

This directory contains examples of how to use the `.cursorrules` file in different project types.

## Project Examples

### 1. Python FastAPI Project

Create a new Python FastAPI project with the following structure:

```
my-fastapi-project/
├── .cursorrules          # Copy the main .cursorrules file here
├── README.md
├── requirements.txt
├── .env.example
├── .gitignore
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── models/
│   ├── routes/
│   ├── services/
│   └── utils/
├── tests/
│   ├── __init__.py
│   ├── test_main.py
│   └── conftest.py
└── docs/
    └── api.md
```

### 2. React TypeScript Project

Create a new React TypeScript project with the following structure:

```
my-react-project/
├── .cursorrules          # Copy the main .cursorrules file here
├── README.md
├── package.json
├── tsconfig.json
├── .env.example
├── .gitignore
├── src/
│   ├── components/
│   ├── hooks/
│   ├── pages/
│   ├── services/
│   ├── types/
│   └── utils/
├── public/
└── tests/
```

### 3. Node.js Express Project

Create a new Node.js Express project with the following structure:

```
my-express-project/
├── .cursorrules          # Copy the main .cursorrules file here
├── README.md
├── package.json
├── .env.example
├── .gitignore
├── src/
│   ├── controllers/
│   ├── middleware/
│   ├── models/
│   ├── routes/
│   ├── services/
│   └── utils/
├── tests/
└── docs/
```

## Customizing Rules for Your Project

### Step 1: Copy the Base Rules

Copy the main `.cursorrules` file to your project root:

```bash
cp .cursorrules /path/to/your/project/
```

### Step 2: Add Project-Specific Rules

Add a section to your `.cursorrules` file with project-specific guidelines:

```markdown
## Project-Specific Rules

### My FastAPI Project
- Use Pydantic models for data validation
- Implement JWT authentication with python-jose
- Use SQLAlchemy with async support
- Follow FastAPI best practices for dependency injection
- Use Alembic for database migrations

### My React Project
- Use React Query for server state management
- Implement proper error boundaries
- Use React Hook Form for form handling
- Follow atomic design principles for components
- Use Tailwind CSS for styling
```

### Step 3: Test Your Rules

Create a simple test to verify your rules are working:

1. Open your project in Cursor
2. Ask Cursor to create a new component or function
3. Verify that the generated code follows your rules
4. Adjust rules as needed

## Common Customizations

### For API Projects

```markdown
### API Development Rules
- Use OpenAPI/Swagger for documentation
- Implement proper HTTP status codes
- Use consistent error response formats
- Implement rate limiting
- Add request/response logging
```

### For Frontend Projects

```markdown
### Frontend Development Rules
- Use TypeScript for all components
- Implement proper loading states
- Use React.memo for performance optimization
- Follow accessibility guidelines
- Implement proper error handling
```

### For Full-Stack Projects

```markdown
### Full-Stack Development Rules
- Use consistent naming conventions across frontend and backend
- Implement proper CORS configuration
- Use environment variables for configuration
- Implement proper authentication flow
- Use consistent data validation
```

## Best Practices

1. **Start Simple**: Begin with the base rules and add project-specific rules gradually
2. **Test Regularly**: Verify that your rules produce the expected code quality
3. **Update as Needed**: Modify rules as your project evolves
4. **Team Collaboration**: Share rules with your team and get feedback
5. **Document Changes**: Keep track of rule changes and their rationale

## Troubleshooting

### Rules Not Working

1. Ensure the `.cursorrules` file is in your project root
2. Restart Cursor after making changes
3. Check that the file syntax is correct
4. Verify that Cursor is reading the file (check Cursor settings)

### Generated Code Doesn't Match Rules

1. Review your rules for clarity and specificity
2. Test with simple requests first
3. Provide more context in your prompts
4. Consider adding more specific examples to your rules

### Performance Issues

1. Keep rules concise and focused
2. Avoid overly complex or contradictory rules
3. Test rules with actual code generation
4. Remove unused or outdated rules

## Resources

- [Cursor AI Documentation](https://cursor.sh/docs)
- [Awesome CursorRules Repository](https://github.com/PatrickJS/awesome-cursorrules)
- [Cursor Community](https://community.cursor.sh/)
