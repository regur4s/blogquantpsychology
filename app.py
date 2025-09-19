import os
from datetime import datetime
from functools import wraps

from flask import Flask, render_template, request, redirect, url_for, session, flash, abort
from flask_sqlalchemy import SQLAlchemy
from slugify import slugify
import markdown2
import bleach
from config import config


def create_app():
    app = Flask(__name__)

    # Load configuration
    config_name = os.environ.get('FLASK_ENV', 'development')
    app.config.from_object(config[config_name])

    # For Vercel serverless, use in-memory SQLite
    if config_name == 'production' and 'vercel' in os.environ.get('VERCEL_URL', ''):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

    # Init DB
    db.init_app(app)

    with app.app_context():
        db.create_all()
        seed_if_empty()

    # Security headers
    @app.after_request
    def security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        return response

    # Routes
    @app.route('/')
    def index():
        posts = (Post.query
                 .filter_by(published=True)
                 .order_by(Post.created_at.desc())
                 .all())
        categories = Category.query.all()
        popular_posts = (Post.query
                        .filter_by(published=True)
                        .order_by(Post.view_count.desc())
                        .limit(5)
                        .all())
        return render_template('index.html', posts=posts, categories=categories, popular_posts=popular_posts)

    @app.route('/post/<slug>')
    def post_detail(slug):
        post = Post.query.filter_by(slug=slug, published=True).first_or_404()
        # Increment view count
        post.view_count += 1
        db.session.commit()
        html = render_markdown(post.content_md)
        return render_template('post.html', post=post, html=html)

    @app.route('/category/<slug>')
    def category_posts(slug):
        category = Category.query.filter_by(slug=slug).first_or_404()
        posts = (Post.query
                 .filter_by(category_id=category.id, published=True)
                 .order_by(Post.created_at.desc())
                 .all())
        return render_template('category.html', category=category, posts=posts)

    @app.route('/tag/<slug>')
    def tag_posts(slug):
        tag = Tag.query.filter_by(slug=slug).first_or_404()
        posts = (Post.query
                 .filter(Post.tags.contains(tag))
                 .filter_by(published=True)
                 .order_by(Post.created_at.desc())
                 .all())
        return render_template('tag.html', tag=tag, posts=posts)

    @app.route('/search')
    def search():
        query = request.args.get('q', '').strip()
        posts = []
        if query:
            posts = (Post.query
                     .filter(Post.published == True)
                     .filter(
                         db.or_(
                             Post.title.contains(query),
                             Post.content_md.contains(query),
                             Post.excerpt.contains(query)
                         )
                     )
                     .order_by(Post.created_at.desc())
                     .all())
        return render_template('search.html', posts=posts, query=query)

    # Admin auth
    @app.route('/admin/login', methods=['GET', 'POST'])
    def admin_login():
        if request.method == 'POST':
            password = request.form.get('password', '')
            expected = app.config.get('ADMIN_PASSWORD', 'changeme')
            if password == expected:
                session['is_admin'] = True
                flash('Logged in as admin', 'success')
                return redirect(url_for('admin_dashboard'))
            else:
                flash('Invalid password', 'error')
        return render_template('admin_login.html')

    @app.route('/admin/logout')
    def admin_logout():
        session.pop('is_admin', None)
        flash('Logged out', 'info')
        return redirect(url_for('index'))

    # Admin CRUD
    @app.route('/admin')
    @login_required
    def admin_dashboard():
        posts = Post.query.order_by(Post.created_at.desc()).all()
        categories = Category.query.all()
        tags = Tag.query.all()
        return render_template('admin_dashboard.html', posts=posts, categories=categories, tags=tags)

    @app.route('/admin/new', methods=['GET', 'POST'])
    @login_required
    def admin_new():
        if request.method == 'POST':
            title = request.form.get('title', '').strip()
            content_md = request.form.get('content_md', '')
            excerpt = request.form.get('excerpt', '').strip()
            published = bool(request.form.get('published'))
            category_id = request.form.get('category_id')
            tag_names = request.form.get('tags', '').strip()
            
            if not title:
                flash('Title is required', 'error')
                return render_template('admin_edit.html', mode='new', 
                                     categories=Category.query.all())
            
            slug = ensure_unique_slug(slugify(title))
            post = Post(title=title, slug=slug, content_md=content_md, 
                       excerpt=excerpt, published=published)
            
            # Set category
            if category_id and category_id.isdigit():
                post.category_id = int(category_id)
            
            db.session.add(post)
            db.session.flush()  # Get post ID before adding tags
            
            # Handle tags
            if tag_names:
                tag_list = [name.strip() for name in tag_names.split(',') if name.strip()]
                for tag_name in tag_list:
                    tag = Tag.query.filter_by(name=tag_name).first()
                    if not tag:
                        tag = Tag(name=tag_name, slug=slugify(tag_name))
                        db.session.add(tag)
                    post.tags.append(tag)
            
            db.session.commit()
            flash('Post created', 'success')
            return redirect(url_for('admin_dashboard'))
        
        return render_template('admin_edit.html', mode='new', 
                             categories=Category.query.all())

    @app.route('/admin/edit/<int:post_id>', methods=['GET', 'POST'])
    @login_required
    def admin_edit(post_id):
        post = Post.query.get_or_404(post_id)
        if request.method == 'POST':
            title = request.form.get('title', '').strip()
            content_md = request.form.get('content_md', '')
            excerpt = request.form.get('excerpt', '').strip()
            published = bool(request.form.get('published'))
            category_id = request.form.get('category_id')
            tag_names = request.form.get('tags', '').strip()
            
            if not title:
                flash('Title is required', 'error')
                return render_template('admin_edit.html', mode='edit', post=post,
                                     categories=Category.query.all())
            
            if title != post.title:
                post.slug = ensure_unique_slug(slugify(title))
            
            post.title = title
            post.content_md = content_md
            post.excerpt = excerpt
            post.published = published
            post.updated_at = datetime.utcnow()
            
            # Set category
            if category_id and category_id.isdigit():
                post.category_id = int(category_id)
            else:
                post.category_id = None
            
            # Clear existing tags
            post.tags.clear()
            
            # Handle tags
            if tag_names:
                tag_list = [name.strip() for name in tag_names.split(',') if name.strip()]
                for tag_name in tag_list:
                    tag = Tag.query.filter_by(name=tag_name).first()
                    if not tag:
                        tag = Tag(name=tag_name, slug=slugify(tag_name))
                        db.session.add(tag)
                    post.tags.append(tag)
            
            db.session.commit()
            flash('Post updated', 'success')
            return redirect(url_for('admin_dashboard'))
        
        return render_template('admin_edit.html', mode='edit', post=post,
                             categories=Category.query.all())

    # Admin category management
    @app.route('/admin/categories', methods=['GET', 'POST'])
    @login_required
    def admin_categories():
        if request.method == 'POST':
            name = request.form.get('name', '').strip()
            description = request.form.get('description', '').strip()
            if name:
                slug = ensure_unique_category_slug(slugify(name))
                category = Category(name=name, slug=slug, description=description)
                db.session.add(category)
                db.session.commit()
                flash('Category created', 'success')
            else:
                flash('Category name is required', 'error')
        
        categories = Category.query.all()
        return render_template('admin_categories.html', categories=categories)

    @app.route('/admin/category/delete/<int:category_id>', methods=['POST'])
    @login_required
    def admin_delete_category(category_id):
        category = Category.query.get_or_404(category_id)
        # Remove category from posts
        Post.query.filter_by(category_id=category_id).update({Post.category_id: None})
        db.session.delete(category)
        db.session.commit()
        flash('Category deleted', 'info')
        return redirect(url_for('admin_categories'))

    @app.route('/admin/delete/<int:post_id>', methods=['POST'])
    @login_required
    def admin_delete(post_id):
        post = Post.query.get_or_404(post_id)
        db.session.delete(post)
        db.session.commit()
        flash('Post deleted', 'info')
        return redirect(url_for('admin_dashboard'))

    return app


# Database setup
db = SQLAlchemy()

# Association tables for many-to-many relationships
post_tags = db.Table('post_tags',
    db.Column('post_id', db.Integer, db.ForeignKey('post.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True)
)


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    slug = db.Column(db.String(120), unique=True, nullable=False, index=True)
    description = db.Column(db.Text, default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    posts = db.relationship('Post', backref='category', lazy=True)
    
    def __repr__(self):
        return f'<Category {self.name}>'


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    slug = db.Column(db.String(70), unique=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Tag {self.name}>'


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(220), unique=True, nullable=False, index=True)
    content_md = db.Column(db.Text, default='')
    excerpt = db.Column(db.Text, default='')  # For read more functionality
    published = db.Column(db.Boolean, default=False)
    view_count = db.Column(db.Integer, default=0)  # For popularity tracking
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign keys
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True)
    
    # Many-to-many relationship with tags
    tags = db.relationship('Tag', secondary=post_tags, lazy='subquery',
                          backref=db.backref('posts', lazy=True))


# Helpers
def login_required(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if not session.get('is_admin'):
            return redirect(url_for('admin_login'))
        return view_func(*args, **kwargs)
    return wrapper


ALLOWED_TAGS = set(bleach.sanitizer.ALLOWED_TAGS).union({'p', 'pre', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'img', 'table', 'thead', 'tbody', 'tr', 'th', 'td', 'code'})
ALLOWED_ATTRS = {
    **bleach.sanitizer.ALLOWED_ATTRIBUTES,
    'img': ['src', 'alt', 'title'],
    'a': ['href', 'title', 'rel', 'target'],
}


def render_markdown(md_text: str) -> str:
    html = markdown2.markdown(md_text or '', extras=[
        'fenced-code-blocks', 'tables', 'strike', 'break-on-newline', 'task_list'
    ])
    # sanitize
    cleaned = bleach.clean(html, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRS)
    # linkify urls
    return bleach.linkify(cleaned)


def ensure_unique_slug(base_slug: str) -> str:
    candidate = base_slug or 'post'
    i = 1
    while Post.query.filter_by(slug=candidate).first() is not None:
        i += 1
        candidate = f"{base_slug}-{i}"
    return candidate


def ensure_unique_category_slug(base_slug: str) -> str:
    candidate = base_slug or 'category'
    i = 1
    while Category.query.filter_by(slug=candidate).first() is not None:
        i += 1
        candidate = f"{base_slug}-{i}"
    return candidate


def seed_if_empty():
    if Post.query.count() == 0:
        # Create sample categories
        tech_cat = Category(name='Technology', slug='technology', description='Tech related posts')
        general_cat = Category(name='General', slug='general', description='General posts')
        db.session.add(tech_cat)
        db.session.add(general_cat)
        db.session.flush()
        
        # Create sample tags
        blog_tag = Tag(name='Blog', slug='blog')
        welcome_tag = Tag(name='Welcome', slug='welcome')
        db.session.add(blog_tag)
        db.session.add(welcome_tag)
        db.session.flush()
        
        sample = Post(
            title='Welcome to your blog',
            slug='welcome',
            content_md='''# Hello!

This is your new blog. Edit or delete this post in the Admin area.

- Toggle the theme with the moon/sun button.
- Write posts in Markdown.
- Use categories and tags to organize your content.
''',
            excerpt='Welcome to your new blog! Learn how to use the features.',
            published=True,
            category_id=general_cat.id
        )
        sample.tags.append(blog_tag)
        sample.tags.append(welcome_tag)
        
        db.session.add(sample)
        db.session.commit()


if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='127.0.0.1', port=port, debug=True)

