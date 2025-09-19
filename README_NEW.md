# 📝 My Blog - Full-Featured Blogging Platform

A modern, full-featured blogging platform built with Flask, featuring categories, tags, search, view tracking, and live preview editor.

## ✨ Features

### 🏷️ **Content Organization**
- **Categories**: Organize posts into topics
- **Tags**: Flexible tagging system  
- **Search**: Full-text search across posts
- **Excerpts**: "Read More" functionality

### 👀 **Analytics**
- **View Counter**: Track post popularity
- **Popular Posts**: Sidebar widget
- **Admin Dashboard**: Content statistics

### ✍️ **Writing Experience** 
- **Live Preview**: Real-time Markdown preview
- **Admin Interface**: Easy content management
- **Dark/Light Mode**: Theme switching

### 🔒 **Production Ready**
- **Security Headers**: XSS protection, CSRF prevention
- **Environment Config**: Secure configuration management
- **Multiple Deployment Options**: Railway, Vercel, Heroku, Docker

## 🚀 Quick Start

### Local Development

1. **Clone & Setup**
   ```bash
   git clone <your-repo>
   cd blogquantstat
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   # source .venv/bin/activate  # macOS/Linux
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Setup**
   ```bash
   copy .env.example .env  # Windows
   # cp .env.example .env   # macOS/Linux
   ```
   Edit `.env` file with your settings.

4. **Run Application**
   ```bash
   python app.py
   ```
   Visit: `http://localhost:5000`

### Admin Access
- URL: `/admin/login`
- Default Password: `changeme` (change in `.env`)

## 🌐 Deployment Options

### 1. 🚂 **Railway** (Recommended - Free Tier)
1. Fork this repository
2. Connect to [Railway](https://railway.app)
3. Set environment variables:
   - `SECRET_KEY`: Random string
   - `ADMIN_PASSWORD`: Your admin password
   - `FLASK_ENV`: production
4. Deploy automatically!

### 2. ▲ **Vercel** (Serverless)
1. Install Vercel CLI: `npm i -g vercel`
2. Run: `vercel`
3. Set environment variables in Vercel dashboard
4. Deploy: `vercel --prod`

### 3. 🐳 **Docker**
```bash
# Build image
docker build -t my-blog .

# Run container
docker run -p 5000:5000 \
  -e SECRET_KEY=your-secret-key \
  -e ADMIN_PASSWORD=your-password \
  -e FLASK_ENV=production \
  my-blog
```

### 4. ☁️ **Google Cloud Platform**
```bash
gcloud app deploy app.yaml
```

### 5. 🟣 **Heroku**
```bash
# Install Heroku CLI, then:
heroku create your-blog-name
heroku config:set SECRET_KEY=your-secret-key
heroku config:set ADMIN_PASSWORD=your-password
heroku config:set FLASK_ENV=production
git push heroku main
```

## 🔧 Configuration

### Environment Variables
```bash
SECRET_KEY=your-super-secret-key-here
ADMIN_PASSWORD=your-strong-admin-password
DATABASE_URL=sqlite:///blog.db  # or PostgreSQL URL
FLASK_ENV=production
PORT=5000
```

### Database Options
- **Development**: SQLite (default)
- **Production**: PostgreSQL recommended
  ```
  DATABASE_URL=postgresql://user:password@host:port/database
  ```

## 📖 Usage Guide

### Creating Content
1. Login to admin: `/admin/login`
2. Create categories: "📁 Manage Categories"
3. Write posts: "+ New Post"
4. Use live preview while writing
5. Add tags and excerpts

### Features Guide
- **Search**: Click 🔍 in header
- **Categories**: Click category names to filter
- **Tags**: Click tags to see related posts
- **Theme**: Click 🌙/☀️ to toggle dark/light mode

## 🛠️ Development

### Project Structure
```
blogquantstat/
├── app.py              # Main application
├── config.py           # Configuration classes
├── wsgi.py            # Production WSGI entry point
├── init_db.py         # Database initialization
├── requirements.txt   # Python dependencies
├── templates/         # Jinja2 templates
├── static/           # CSS, JS, images
├── .env.example      # Environment template
└── deployment files/ # Docker, Railway, Vercel configs
```

### Adding Features
1. Models: Add to `app.py` database section
2. Routes: Add to `app.py` routes section  
3. Templates: Create in `templates/`
4. Styles: Update `static/style.css`

## 🔐 Security

- ✅ CSRF protection
- ✅ XSS prevention
- ✅ Secure session management
- ✅ Input sanitization
- ✅ Environment-based secrets

## 📊 Tech Stack

- **Backend**: Flask, SQLAlchemy
- **Database**: SQLite (dev) / PostgreSQL (prod)
- **Frontend**: HTML5, CSS3, Vanilla JS
- **Markdown**: markdown2 + bleach
- **Security**: Flask built-ins + custom headers
- **Deployment**: Gunicorn + various platforms

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -am 'Add feature'`
4. Push to branch: `git push origin feature-name`
5. Create Pull Request

## 📝 License

MIT License - feel free to use for personal or commercial projects!

## 🆘 Support

- Check the [deployment guide](#-deployment-options)
- Review [environment variables](#environment-variables)
- Ensure database is properly initialized

---

**Happy Blogging! 🎉**