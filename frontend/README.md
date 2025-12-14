# Shope Frontend

React frontend for the Shope sweet shop management system.

## Tech Stack

- React 18
- React Router DOM v6
- JavaScript (no TypeScript)
- Fetch API
- Basic CSS (no UI libraries)

## Setup

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm start
```

The app will run on http://localhost:3000 and proxy API requests to http://localhost:8000.

## Features

### Authentication
- **Login** (`/login`) - User authentication with JWT
- **Register** (`/register`) - New user registration with role selection
- **Dashboard** (`/dashboard`) - Protected page (requires authentication)

### JWT Handling
- Token stored in localStorage
- Automatically included in API requests via `Authorization: Bearer <token>` header
- User data (username, role) stored in localStorage

## Project Structure

```
frontend/
├── public/
│   └── index.html
├── src/
│   ├── pages/
│   │   ├── Login.js
│   │   ├── Register.js
│   │   └── Dashboard.js
│   ├── api.js          # API utilities and auth functions
│   ├── App.js          # Main app with routing
│   ├── index.js        # Entry point
│   └── index.css       # Global styles
├── package.json
└── README.md
```

## API Integration

The frontend communicates with the FastAPI backend:

- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login (returns JWT token)

## Available Scripts

- `npm start` - Run development server
- `npm build` - Build for production
- `npm test` - Run tests
