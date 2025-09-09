# API Example Class - Items Management System

A complete full-stack application for managing product items with ASIN, name, and price fields. This project includes both a serverless backend API and a modern web frontend.

## Project Structure

```
├── api/                    # Backend API (AWS Lambda + DynamoDB)
│   ├── items.py           # Items CRUD operations
│   ├── ping.py            # Health check endpoints
│   ├── serverless.yml     # Serverless framework configuration
│   ├── requirements.txt   # Python dependencies
│   └── package.json       # Node.js dependencies for deployment
├── frontend/              # Web frontend application
│   ├── index.html         # Main HTML file
│   ├── styles.css         # CSS styling
│   ├── script.js          # JavaScript functionality
│   ├── package.json       # Frontend dependencies
│   ├── netlify.toml       # Netlify deployment configuration
│   └── README.md          # Frontend documentation
├── infra/                 # Infrastructure as Code
│   ├── dynamodb.yml       # DynamoDB table configuration
│   ├── ec2.yml            # EC2 configuration
│   └── serverless.yml     # Infrastructure serverless config
└── buildspec.yml          # AWS CodeBuild specification

```

## Features

### Backend API
- **RESTful API** built with AWS Lambda and Python
- **DynamoDB** for data persistence
- **CRUD operations** for items management
- **Health check endpoints** for monitoring
- **Serverless architecture** for scalability and cost-effectiveness

### Frontend Web Application
- **Modern responsive design** that works on all devices
- **Real-time API integration** with connection testing
- **Complete CRUD interface** for managing items
- **Search and filtering** capabilities
- **Toast notifications** and error handling
- **No framework dependencies** - pure HTML, CSS, and JavaScript

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/ping` | Health check |
| GET | `/ping2` | Secondary health check |
| GET | `/ping3` | Tertiary health check |
| GET | `/items` | Get all items |
| GET | `/items/{asin}` | Get specific item by ASIN |
| POST | `/items` | Create new item |
| PUT | `/items` | Update existing item |
| DELETE | `/items/{asin}` | Delete item by ASIN |

## Quick Start

### Backend Deployment
1. Install dependencies:
   ```bash
   cd api
   npm install
   pip install -r requirements.txt
   ```

2. Deploy with Serverless Framework:
   ```bash
   serverless deploy --env stg
   ```

### Frontend Setup
1. Navigate to frontend directory:
   ```bash
   cd frontend
   ```

2. Start local development server:
   ```bash
   # Using Node.js
   npm install
   npm start
   
   # Or using Python
   python -m http.server 8080
   ```

3. Open http://localhost:8080 in your browser

4. Configure the API URL in the frontend interface

## Data Model

Items have the following structure:
```json
{
  "asin": "B08N5WRWNW",
  "name": "Wireless Bluetooth Headphones",
  "price": "$29.99"
}
```

## Deployment Options

### Backend
- **AWS Lambda** with Serverless Framework
- **DynamoDB** for data storage
- **API Gateway** for HTTP endpoints

### Frontend
- **Static hosting**: AWS S3, Netlify, Vercel, GitHub Pages
- **Web servers**: Apache, Nginx, IIS
- **CDN**: CloudFront, Cloudflare

## Development

### Backend Development
- Python 3.8+ runtime
- AWS SDK (boto3) for DynamoDB operations
- Serverless Framework for deployment

### Frontend Development
- Modern JavaScript (ES6+)
- CSS Grid and Flexbox for layout
- Fetch API for HTTP requests
- No build process required

## Security Notes

⚠️ **Important**: The backend includes a vulnerable function (`vulnerable_function`) that demonstrates OS command injection. This is for educational purposes only and should never be used in production.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is provided for educational and development purposes.