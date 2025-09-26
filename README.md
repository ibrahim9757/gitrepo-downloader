# GitHub Repository File Browser

A modern web application that allows you to browse, preview, and download files from any GitHub repository with a beautiful, responsive interface.

## 🚀 Features

- **Browser any GitHub repository** - Enter any GitHub repo URL to browse its files
- **File download** - Download individual files directly
- **Bulk download** - Download all files at once as a ZIP archive
- **Modern UI** - Beautiful, responsive design with animations
- **Real-time feedback** - Toast notifications and loading states
- **CORS enabled** - Frontend and backend communication setup

## 📁 Project Structure

```
hello-api-project/
├── backend/
│   ├── main.py              # FastAPI backend (primary)
│   ├── app.py                # Flask backend (alternative)
│   └── requirements.txt      # Python dependencies
├── frontend/
│   ├── index.html            # Main HTML file
│   ├── styles.css           # Custom CSS styles
│   ├── package.json         # Node.js dependencies
│   └── package-lock.json     # Dependency lock file
├── venv/                    # Python virtual environment
└── README.md                # This file
```

## 🛠️ Installation & Setup

### Prerequisites

- Python 3.7+ installed
- Node.js (for frontend dependencies)
- Git (to clone the repository)

### Backend Setup

1. **Navigate to the backend directory:**
   ```bash
   cd backend
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the FastAPI backend:**
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

   Or alternatively, run the Flask backend:
   ```bash
   python app.py
   ```

The backend will be available at:
- FastAPI: `http://localhost:8000`
- Flask: `http://localhost:5000`

### Frontend Setup

1. **Navigate to the frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Open the application:**
   Simply open `index.html` in your browser, or serve it with a local server:
   ```bash
   # Using Python HTTP server
   python -m http.server 8080
   
   # Or using Node.js http-server
   npx http-server -p 8080
   ```

## 🎯 Usage

1. **Start the backend server** (FastAPI or Flask)
2. **Open the frontend** in your browser
3. **Enter a GitHub repository URL** in the input field
   - Example: `https://github.com/microsoft/vscode`
   - Example: `https://github.com/facebook/react`
4. **Click "Load Repository"** to browse files
5. **Download individual files** using the download buttons
6. **Download all files as ZIP** using the "Download All Files" button

## 🔧 API Endpoints

### FastAPI Backend (main.py)

| Endpoint | Method | Description | Parameters |
|----------|--------|-------------|------------|
| `/` | GET | Health check endpoint | None |
| `/api/files` | GET | List files in repository | `repo_url` (query param) |
| `/api/download` | GET | Download individual file | `url` (query param) |
| `/api/download_all` | GET | Download all files as ZIP | `repo_url` (query param) |

### Flask Backend (app.py)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Basic health check |
| `/api/message` | GET | Test endpoint returning JSON message |

## 🎨 Technologies Used

### Backend
- **FastAPI** - Modern, fast web framework for building APIs
- **Flask** - Lightweight web framework (alternative)
- **Requests** - HTTP library for making API calls
- **Uvicorn** - ASGI server for running FastAPI
- **Python** - Backend programming language

### Frontend
- **HTML5** - Structure and content
- **CSS3** - Styling with gradients and animations
- **JavaScript** - Interactive functionality
- **Tailwind CSS** - Utility-first CSS framework
- **Toastify.js** - Beautiful toast notifications

## 📦 Dependencies

### Backend (requirements.txt)
```
fastapi
uvicorn
requests
python-dotenv
aiofiles
zipfile36
```

### Frontend (package.json)
```json
{
  "dependencies": {
    "axios": "^1.12.2",
    "react": "^19.1.1",
    "react-dom": "^19.1.1",
    "react-router-dom": "^7.9.2",
    "sonner": "^2.0.7"
  }
}
```

## 🚦 Development Workflow

1. **Clone the repository**
2. **Start the backend server** (`uvicorn main:app --reload`)
3. **Open the frontend** in your browser
4. **Test the API endpoints** using the frontend interface
5. **Check browser console** for any error messages

## 🔒 Security Notes

- The current setup allows CORS from all origins (`*`) for development purposes
- In production, restrict CORS to specific domains
- The application relies on public GitHub repos - no authentication required
- File downloads are proxied through the backend for security

## 🌟 Features in Detail

### File Browser
- Displays files in an elegant card-based layout
- Shows file types with color-coded badges
- Responsive design that works on mobile and desktop
- Hover effects and animations for enhanced UX

### Download System
- Individual file downloads with proper MIME type handling
- Bulk ZIP downloads for entire repositories
- Proper filename handling and error management
- Progress indication during bulk operations

### Error Handling
- Comprehensive error messages for invalid URLs
- Network error handling with user-friendly notifications
- Graceful fallbacks for API failures

## 🐛 Troubleshooting

### Common Issues

1. **Backend not starting**
   - Check if Python is installed
   - Verify virtual environment is activated
   - Install missing dependencies with `pip install -r requirements.txt`

2. **CORS errors in browser**
   - Ensure backend is running on the correct port
   - Check CORS configuration in the backend code
   - Verify frontend is accessing the correct backend URL

3. **File downloads not working**
   - Check if GitHub repository URL is valid and public
   - Verify backend is running and accessible
   - Check browser console for JavaScript errors

### Performance Tips

- For large repositories, consider implementing pagination
- Limit the number of files rendered at once
- Implement caching for frequently accessed repositories

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

## 🙋 Support

If you encounter any issues or have questions:
1. Check the troubleshooting section above
2. Review the browser console for any JavaScript errors
3. Verify that all dependencies are correctly installed
4. Ensure the backend server is running and accessible

---

**Enjoy browsing GitHub repositories with style!** 🎉
