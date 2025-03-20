# StudyHub Frontend

## Overview

React-based frontend application for the StudyHub platform, providing the user interface for course management, assignments, and study materials.

## Prerequisites

- Node.js
- npm (Node Package Manager)
- Windows PowerShell (for setup scripts)

## Project Structure

```plaintext
frontend/
├── public/          # Static files
├── src/             # Source code
│   ├── components/  # React components
│   ├── pages/       # Page components
│   ├── services/    # API services
│   └── utils/       # Utility functions
├── setup.ps1        # Setup script
└── package.json     # Project configuration
```

## Setup Instructions

1. Run the setup script:
   ```powershell
   .\setup.ps1
   ```
   This will:
   - Create required directories
   - Install dependencies
   - Start the development server

2. Access the application:
   - Local: http://localhost:3000
   - Network: http://172.20.16.1:3000

## Available Scripts

- `npm start`: Start development server
- `npm test`: Run tests
- `npm run build`: Create production build
- `npm run eject`: Eject from Create React App

## Development

### Development Mode
The development server includes:
- Hot reloading
- Error reporting
- Development tools
- Unoptimized build for faster development

### Production Build
To create an optimized production build:
```bash
npm run build
```

## Environment Configuration

Create a `.env` file in the root directory:
```
REACT_APP_API_URL=http://localhost:5000
REACT_APP_ENV=development
```

## Connecting with Backend

The frontend connects to the backend API at:
- Development: http://localhost:5000
- Configure API URL in `.env` file

## Troubleshooting

1. **Port Conflicts**
   - Default port is 3000
   - Can be changed by setting PORT environment variable
   - Or by modifying package.json

2. **Build Issues**
   - Clear npm cache: `npm cache clean --force`
   - Delete node_modules: `rm -rf node_modules`
   - Reinstall dependencies: `npm install`

3. **API Connection Issues**
   - Verify backend is running
   - Check CORS configuration
   - Verify API URL in .env file

## Browser Support

Supports modern browsers:
- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request 