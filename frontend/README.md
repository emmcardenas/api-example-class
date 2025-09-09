# Items Management System - Frontend

A modern, responsive web application for managing product items through a REST API. This frontend provides a clean interface to perform CRUD operations on items with ASIN, name, and price fields.

## Features

### 🔧 API Configuration
- Configure API base URL dynamically
- Test API connection with ping endpoint
- Visual connection status indicator
- Persistent URL storage in browser

### 📦 Items Management
- **View All Items**: Display all items in a responsive grid layout
- **Add New Items**: Create items with ASIN, name, and price
- **Edit Items**: Update existing item details
- **Delete Items**: Remove items with confirmation dialog
- **Search & Filter**: Real-time search by ASIN, name, or price

### 🎨 User Interface
- Modern, responsive design that works on all devices
- Clean card-based layout with hover effects
- Loading indicators and status messages
- Toast notifications for user feedback
- Modal dialogs for editing items

### 🚀 Technical Features
- Pure HTML, CSS, and JavaScript (no frameworks required)
- Responsive design (mobile-first approach)
- Error handling and user feedback
- Local storage for API configuration
- Accessible design with proper ARIA labels

## Getting Started

### Prerequisites
- A web server to serve the static files (or simply open `index.html` in a browser)
- Access to the Items Management API

### Installation

1. **Clone or download the frontend files**:
   ```
   frontend/
   ├── index.html
   ├── styles.css
   ├── script.js
   └── README.md
   ```

2. **Serve the files**:
   
   **Option 1: Simple HTTP Server (Python)**
   ```bash
   cd frontend
   python -m http.server 8080
   ```
   Then open http://localhost:8080

   **Option 2: Node.js HTTP Server**
   ```bash
   cd frontend
   npx http-server -p 8080
   ```

   **Option 3: Open directly in browser**
   Simply open `index.html` in your web browser (some features may be limited due to CORS)

### Configuration

1. **Open the application** in your web browser
2. **Configure API URL**:
   - Enter your API Gateway URL in the "API Configuration" section
   - Example: `https://your-api-id.execute-api.region.amazonaws.com/stage`
   - Click "Save" to store the configuration
3. **Test Connection**: Click "Test Connection" to verify API connectivity
4. **Start Managing Items**: Once connected, you can begin adding and managing items

## Usage Guide

### Adding Items
1. Fill in the "Add New Item" form:
   - **ASIN**: Product identifier (e.g., B08N5WRWNW)
   - **Product Name**: Descriptive name
   - **Price**: Price with or without currency symbol
2. Click "Add Item" to create the item

### Managing Items
- **View Items**: All items are displayed in the items list section
- **Search**: Use the search bar to filter items by any field
- **Edit**: Click the "Edit" button on any item card
- **Delete**: Click the "Delete" button and confirm the action
- **Refresh**: Click the "Refresh" button to reload items from the API

### API Endpoints Used
The frontend interacts with these API endpoints:

- `GET /ping` - Test API connectivity
- `GET /items` - Retrieve all items
- `GET /items/{asin}` - Get specific item (used for validation)
- `POST /items` - Create new item
- `PUT /items` - Update existing item
- `DELETE /items/{asin}` - Delete item

## Deployment Options

### 1. Static Web Hosting
Deploy to any static hosting service:
- **AWS S3 + CloudFront**
- **Netlify**
- **Vercel**
- **GitHub Pages**
- **Azure Static Web Apps**

### 2. Web Server
Deploy to any web server:
- Apache HTTP Server
- Nginx
- IIS

### 3. CDN Deployment
For production use, consider:
- Minifying CSS and JavaScript files
- Optimizing images
- Setting up proper caching headers
- Enabling GZIP compression

## Browser Compatibility

- **Modern Browsers**: Chrome 60+, Firefox 55+, Safari 12+, Edge 79+
- **Mobile Browsers**: iOS Safari 12+, Chrome Mobile 60+
- **Features Used**:
  - CSS Grid and Flexbox
  - Fetch API
  - ES6+ JavaScript features
  - CSS Custom Properties

## Customization

### Styling
- Modify `styles.css` to change colors, fonts, and layout
- CSS custom properties are used for easy theming
- Responsive breakpoints can be adjusted

### Functionality
- Add new features by extending `script.js`
- API endpoints can be modified in the JavaScript functions
- Form validation can be enhanced

### Configuration
- Default API URL can be set in the JavaScript
- Toast notification timing can be adjusted
- Search functionality can be enhanced

## Security Considerations

- **CORS**: Ensure your API has proper CORS configuration
- **HTTPS**: Use HTTPS for production deployments
- **Input Validation**: Client-side validation is implemented, but server-side validation is crucial
- **Error Handling**: Sensitive error information is not exposed to users

## Troubleshooting

### Common Issues

1. **Connection Failed**
   - Verify API URL is correct
   - Check CORS configuration on API
   - Ensure API is running and accessible

2. **Items Not Loading**
   - Check browser console for errors
   - Verify API endpoints are working
   - Test API connection first

3. **CORS Errors**
   - Configure API Gateway to allow your domain
   - Add proper CORS headers to Lambda responses

4. **Mobile Display Issues**
   - Clear browser cache
   - Check viewport meta tag
   - Test on different devices

### Debug Mode
Open browser developer tools (F12) to:
- View console logs for detailed error information
- Monitor network requests to the API
- Inspect element styles and layout

## Contributing

To contribute to this frontend:

1. Follow the existing code style and structure
2. Test on multiple browsers and devices
3. Ensure responsive design principles
4. Add appropriate error handling
5. Update documentation for new features

## License

This frontend application is provided as-is for educational and development purposes.