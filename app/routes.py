from flask import Blueprint, render_template, request, redirect, url_for, abort,flash,current_app,session
from flask_login import login_required, current_user,login_user,logout_user
from app.models import Blog,db,User,Listing
from werkzeug.security import check_password_hash
import os
from werkzeug.utils import secure_filename


UPLOAD_FOLDER = 'static/uploads'


main = Blueprint('main', __name__)

@main.route('/')
def home():
    return render_template('user/home.html')

@main.route('/about')
def about():
    return render_template('user/about.html')

@main.route('/listings')
def listings():
    all_listings = Listing.query.order_by(Listing.id.desc()).all()
    return render_template('user/listings.html', listings=all_listings)

@main.route('/blog')
def blog():
    posts = Blog.query.order_by(Blog.date_posted.desc()).all()
    return render_template('user/blogs.html', posts=posts,no_background=True)

@main.route('/blog/<int:id>')
def blog_detail(id):
    post = Blog.query.get_or_404(id)
    return render_template('user/blog_detail.html', post=post)

@main.route('/contact')
def contact():
    return render_template('user/contact.html')


@main.route('/admin/blog/new', methods=['GET', 'POST'])
@login_required
def new_blog():
    if not current_user.is_admin:
        abort(403)

    if request.method == 'POST':
        title = request.form['title']
        summary = request.form['summary']
        content = request.form['content']

        # Handle image upload
        image_file = request.files['image']
        if image_file:
            filename = secure_filename(image_file.filename)
            image_path = os.path.join(current_app.root_path, 'static/images', filename)
            image_file.save(image_path)
        else:
            filename = 'default.jpg'  # fallback

        new_post = Blog(
            title=title,
            image=filename,
            author=current_user.username,
            summary=summary,
            content=content
        )
        db.session.add(new_post)
        db.session.commit()
        flash('Blog post published!', 'success')
        return redirect(url_for('main.blog'))

    return render_template('admin/new_blog.html')


@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Logged in successfully.', 'success')
            return redirect(url_for('main.admin_dashboard'))
        else:
            flash('Invalid credentials.', 'danger')

    return render_template('admin/login.html')
@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.home'))


@main.route('/admin/listing/new', methods=['GET', 'POST'])
@login_required
def new_listing():
    if not current_user.is_admin:
        abort(403)

    if request.method == 'POST':
        UPLOAD_FOLDER = current_app.config['UPLOAD_FOLDER']

        name = request.form['name']
        location = request.form['location']
        description = request.form.get('description')
        size = request.form['size']
        price = request.form['price']
        files = request.files.getlist('images')

        image_filenames = []
        for file in files:
            if file.filename:
                filename = secure_filename(file.filename)
                os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                file.save(os.path.join(UPLOAD_FOLDER, filename))
                image_filenames.append(filename)

        new_listing = Listing(
            name=name,
            location=location,
            description = description,
            size=size,
            price=price,
            images=','.join(image_filenames)
        )
        db.session.add(new_listing)
        db.session.commit()

        flash("Listing added successfully!", "success")
        return redirect(url_for('main.listings'))

    return render_template('admin/new_listing.html')


@main.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        abort(403)
    return render_template('admin/admin_dashboard.html')

@main.route('/admin/blogs')
@login_required
def admin_blogs():
    if not current_user.is_admin:
        abort(403)
    posts = Blog.query.order_by(Blog.date_posted.desc()).all()
    return render_template('admin/admin_blogs.html', posts=posts)

@main.route('/admin/listings')
@login_required
def admin_listings():
    if not current_user.is_admin:
        abort(403)
    listings = Listing.query.order_by(Listing.id.desc()).all()
    return render_template('admin/admin_listings.html', listings=listings)
@main.route('/admin/blog/delete/<int:id>', methods=['POST'])
@login_required
def delete_blog(id):
    if not current_user.is_admin:
        abort(403)
    post = Blog.query.get_or_404(id)
    db.session.delete(post)
    db.session.commit()
    flash('Blog post deleted.', 'info')
    return redirect(url_for('main.admin_blogs'))

@main.route('/admin/listing/delete/<int:id>', methods=['POST'])
@login_required
def delete_listing(id):
    if not current_user.is_admin:
        abort(403)
    listing = Listing.query.get_or_404(id)
    db.session.delete(listing)
    db.session.commit()
    flash('Listing deleted.', 'info')
    return redirect(url_for('main.admin_listings'))
@main.route('/admin/blog/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_blog(id):
    if not current_user.is_admin:
        abort(403)

    post = Blog.query.get_or_404(id)

    if request.method == 'POST':
        post.title = request.form['title']
        post.summary = request.form['summary']
        post.content = request.form['content']

        image_file = request.files['image']
        if image_file and image_file.filename:
            filename = secure_filename(image_file.filename)
            image_path = os.path.join(current_app.root_path, 'static/images', filename)
            image_file.save(image_path)
            post.image = filename  # Replace old image

        db.session.commit()
        flash('Blog post updated successfully!', 'success')
        return redirect(url_for('main.admin_blogs'))

    return render_template('admin/edit_blog.html', post=post)

@main.route('/admin/listing/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_listing(id):
    if not current_user.is_admin:
        abort(403)

    listing = Listing.query.get_or_404(id)

    if request.method == 'POST':
        UPLOAD_FOLDER = current_app.config['UPLOAD_FOLDER']

        listing.name = request.form['name']
        listing.location = request.form['location']
        listing.size = request.form['size']
        listing.price = request.form['price']
        listing.description = request.form['description']

        files = request.files.getlist('images')
        new_images = []
        for file in files:
            if file and file.filename:
                filename = secure_filename(file.filename)
                os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                file.save(os.path.join(UPLOAD_FOLDER, filename))
                new_images.append(filename)

        if new_images:
            # Append new images to existing ones
            existing = listing.get_image_list()
            listing.images = ','.join(existing + new_images)

        db.session.commit()
        flash('Listing updated successfully!', 'success')
        return redirect(url_for('main.admin_listings'))

    return render_template('admin/edit_listing.html', listing=listing)

@main.route('/listing/<int:listing_id>')
def listing_detail(listing_id):
    listing = Listing.query.get_or_404(listing_id)
    return render_template('user/listing_detail.html', listing=listing)

