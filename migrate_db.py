#!/usr/bin/env python3
"""
Production Database Migration Script
"""
import os
import sys
from app import create_app, db, Category, Tag, Post

def migrate_to_postgresql():
    """Migrate data from SQLite to PostgreSQL"""
    print("🗄️ Starting database migration...")
    
    # Set environment to production
    os.environ['FLASK_ENV'] = 'production'
    
    app = create_app()
    with app.app_context():
        try:
            # Create all tables
            print("📋 Creating database tables...")
            db.create_all()
            print("✅ Database tables created successfully!")
            
            # Check if tables are empty
            if Post.query.count() == 0:
                print("📊 No existing data found. Creating sample data...")
                
                # Create sample categories
                tech_cat = Category(name='Technology', slug='technology', 
                                  description='Technology and programming posts')
                lifestyle_cat = Category(name='Lifestyle', slug='lifestyle', 
                                       description='Life, health, and productivity')
                business_cat = Category(name='Business', slug='business', 
                                      description='Business and entrepreneurship')
                
                db.session.add_all([tech_cat, lifestyle_cat, business_cat])
                db.session.flush()
                
                # Create sample tags
                tags_data = [
                    ('Python', 'python'), ('Flask', 'flask'), ('Web Development', 'web-development'),
                    ('Productivity', 'productivity'), ('Health', 'health'), ('Startup', 'startup'),
                    ('Tutorial', 'tutorial'), ('Tips', 'tips'), ('Review', 'review')
                ]
                
                tags = []
                for name, slug in tags_data:
                    tag = Tag(name=name, slug=slug)
                    tags.append(tag)
                    db.session.add(tag)
                
                db.session.flush()
                
                # Create sample posts
                posts_data = [
                    {
                        'title': 'Welcome to My Blog',
                        'slug': 'welcome-to-my-blog',
                        'content_md': '''# Welcome to My Blog!

Thank you for visiting my blog. This is a place where I share my thoughts, experiences, and knowledge about various topics.

## What You'll Find Here

- **Technology**: Programming tutorials, web development tips, and tech reviews
- **Lifestyle**: Productivity hacks, health tips, and personal growth
- **Business**: Entrepreneurship insights and startup experiences

## Features

This blog includes:
- 🏷️ Categories and tags for easy navigation
- 🔍 Search functionality to find specific content
- 👁️ View tracking to see popular posts
- 🌙 Dark/light mode toggle
- 📱 Mobile-friendly responsive design

Feel free to explore and don't hesitate to reach out if you have any questions!''',
                        'excerpt': 'Welcome to my blog! Discover technology tutorials, lifestyle tips, and business insights.',
                        'published': True,
                        'category': tech_cat,
                        'tags': [tags[0], tags[6]]  # Python, Tutorial
                    },
                    {
                        'title': 'Getting Started with Flask Web Development',
                        'slug': 'getting-started-flask-development',
                        'content_md': '''# Getting Started with Flask Web Development

Flask is a lightweight and flexible Python web framework that's perfect for beginners and experts alike.

## Why Choose Flask?

1. **Simple and Minimalist**: Flask follows the "micro" framework philosophy
2. **Flexible**: You can structure your application as you prefer
3. **Extensible**: Large ecosystem of extensions
4. **Well Documented**: Excellent documentation and community support

## Basic Flask Application

```python
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'

if __name__ == '__main__':
    app.run(debug=True)
```

## Next Steps

- Learn about routing and templates
- Understand database integration
- Explore Flask extensions
- Deploy your application

Happy coding! 🚀''',
                        'excerpt': 'Learn the basics of Flask web development and create your first Python web application.',
                        'published': True,
                        'category': tech_cat,
                        'tags': [tags[0], tags[1], tags[2], tags[6]]  # Python, Flask, Web Dev, Tutorial
                    },
                    {
                        'title': '10 Productivity Tips for Remote Workers',
                        'slug': 'productivity-tips-remote-workers',
                        'content_md': '''# 10 Productivity Tips for Remote Workers

Working from home can be challenging. Here are proven strategies to stay productive and maintain work-life balance.

## 1. Create a Dedicated Workspace
Set up a specific area for work only. This helps your brain switch into "work mode."

## 2. Establish a Routine
- Wake up at the same time
- Get dressed for work
- Take regular breaks
- End work at a specific time

## 3. Use Time Management Techniques
- **Pomodoro Technique**: 25 minutes work, 5 minutes break
- **Time blocking**: Schedule specific tasks for specific times
- **The 2-minute rule**: If it takes less than 2 minutes, do it now

## 4. Minimize Distractions
- Turn off notifications during focused work
- Use website blockers if needed
- Keep your phone in another room

## 5. Take Care of Your Health
- Stay hydrated
- Take walks during breaks
- Maintain good posture
- Get enough sleep

Remember: Productivity isn't about working more hours, it's about working smarter! 💪''',
                        'excerpt': 'Discover 10 proven strategies to boost your productivity while working from home.',
                        'published': True,
                        'category': lifestyle_cat,
                        'tags': [tags[3], tags[7], tags[4]]  # Productivity, Tips, Health
                    }
                ]
                
                for post_data in posts_data:
                    post = Post(
                        title=post_data['title'],
                        slug=post_data['slug'],
                        content_md=post_data['content_md'],
                        excerpt=post_data['excerpt'],
                        published=post_data['published'],
                        category_id=post_data['category'].id,
                        view_count=0
                    )
                    
                    # Add tags
                    for tag in post_data['tags']:
                        post.tags.append(tag)
                    
                    db.session.add(post)
                
                db.session.commit()
                print("✅ Sample data created successfully!")
                print(f"   - {Category.query.count()} categories")
                print(f"   - {Tag.query.count()} tags") 
                print(f"   - {Post.query.count()} posts")
            else:
                print(f"📊 Database already contains {Post.query.count()} posts")
            
            print("🎉 Database migration completed successfully!")
            
        except Exception as e:
            print(f"❌ Error during migration: {str(e)}")
            db.session.rollback()
            sys.exit(1)

def check_database_connection():
    """Check if database connection is working"""
    print("🔗 Testing database connection...")
    
    app = create_app()
    with app.app_context():
        try:
            # Try to connect to database
            db.engine.execute('SELECT 1')
            print("✅ Database connection successful!")
            return True
        except Exception as e:
            print(f"❌ Database connection failed: {str(e)}")
            return False

if __name__ == '__main__':
    print("🚀 Production Database Setup")
    print("=" * 40)
    
    if not os.environ.get('DATABASE_URL'):
        print("⚠️  DATABASE_URL environment variable not set!")
        print("   Please set your PostgreSQL connection string:")
        print("   export DATABASE_URL='postgresql://user:password@host:port/database'")
        sys.exit(1)
    
    if check_database_connection():
        migrate_to_postgresql()
    else:
        print("💡 Make sure your DATABASE_URL is correct and the database server is running.")
        sys.exit(1)