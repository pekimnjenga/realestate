from flask import Blueprint, render_template, request, redirect, url_for, abort, flash, current_app
from flask_login import login_required, current_user, login_user, logout_user
from app.models import Blog, Listing, User
from werkzeug.security import check_password_hash
from app.utils.r2_upload import upload_to_r2, delete_from_r2
from datetime import datetime
from app.extensions import db
import smtplib
from email.message import EmailMessage
import re
import os

main = Blueprint('main', __name__)

# --- USER INTERFACE ---
@main.route('/')
def home():
    featured_listings = Listing.query.filter_by(is_sold=False).limit(4).all()
    return render_template('user/home.html', featured_listings=featured_listings)


@main.route('/listings')
def listings():
    featured = Listing.query.filter_by(is_sold=False).order_by(Listing.id.desc()).all()
    sold = Listing.query.filter_by(is_sold=True).order_by(Listing.sold_at.desc()).all()
    return render_template('user/listings.html', featured=featured, sold=sold)

@main.route('/blog')
def blog():
    posts = Blog.query.order_by(Blog.date_posted.desc()).all()
    return render_template('user/blogs.html', posts=posts, no_background=True)

@main.route('/blog/<int:id>')
def blog_detail(id):
    post = Blog.query.get_or_404(id)
    return render_template('user/blog_detail.html', post=post)

@main.route('/listing/<int:listing_id>')
def listing_detail(listing_id):
    listing = Listing.query.get_or_404(listing_id)
    return render_template('user/listing_detail.html', listing=listing)

@main.route('/about')
def about():
    return render_template('user/about.html')

#Contact page with email functionality
def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

def log_submission(name, email, subject, message):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"[{timestamp}] {name} <{email}> | Subject: {subject} | Message: {message}\n"
    with open('contact_audit.log', 'a') as log_file:
        log_file.write(log_entry)

@main.route('/contact', methods=['POST'])
def contact():
    name = request.form.get('name')
    email = request.form.get('email')
    subject = request.form.get('subject')
    message = request.form.get('message')

    if not all([name, email, subject, message]) or not is_valid_email(email):
        flash("Please fill all fields correctly.", "danger")
        return redirect(url_for('main.contact_page'))

    try:
        # Log the submission
        log_submission(name, email, subject, message)

        # Compose message to site admin
        admin_msg = EmailMessage()
        admin_msg['Subject'] = f"New Inquiry: {subject}"
        admin_msg['From'] = 'info@ilikeitproperties.co.ke'
        admin_msg['To'] = 'info@ilikeitproperties.co.ke'
        admin_msg.set_content(
            f"Hello,\n\n"
            f"{name} ({email}) submitted a message via the contact form.\n\n"
            f"Subject: {subject}\n"
            f"Message:\n{message}\n\n"
            f"Best,\nI Like It Properties"
        )

        # Compose auto-reply to sender
        reply_msg = EmailMessage()
        reply_msg['Subject'] = "We've received your message!"
        reply_msg['From'] = 'I Like It Properties <info@ilikeitproperties.co.ke>'
        reply_msg['To'] = email
        reply_msg.set_content(
            f"Hi {name},\n\n"
            f"Thanks for reaching out to I Like It Properties. We’ve received your message and will get back to you shortly.\n\n"
            f"Subject: {subject}\n"
            f"Message:\n{message}\n\n"
            f"Warm regards,\n"
            f"I Like It Properties"
            )
        reply_msg.add_alternative(f"""\
                                  <html>
                                  <body style="font-family: Arial, sans-serif; color: #333;">
                                    <p>Hi {name},</p>
                                    <p>Thanks for reaching out to <strong>I Like It Properties</strong>. We've received your message and will get back to you shortly.</p>
                                    <p><strong>Subject:</strong> {subject}<br>
                                    <strong>Message:</strong><br>{message}</p>
                                    <p>Warm regards,<br>
                                    <strong>I Like It Properties</strong></p>
                                    <img src="https://pub-950077afaafe4cfc92639111581ed1ac.r2.dev/ilikeitproperties/logo.jpg" alt="I Like It Properties Logo" style="margin-top:20px; height:80px;">
                                  </body>
                                  </html>
                                  """, subtype='html')

        with smtplib.SMTP_SSL('mail.ilikeitproperties.co.ke', 465) as smtp:
            smtp.login('info@ilikeitproperties.co.ke', os.environ.get('EMAIL_PASSWORD'))
            smtp.send_message(admin_msg, from_addr='info@ilikeitproperties.co.ke', to_addrs=['info@ilikeitproperties.co.ke'])
            smtp.send_message(reply_msg, from_addr='info@ilikeitproperties.co.ke', to_addrs=[email])

        flash("Thank you for reaching out! Your message has been received and our team will respond shortly.", "success")

    except Exception as e:
        flash("Oops — we couldn't send your message due to a technical issue. Please try again or contact us directly at info@ilikeitproperties.co.ke.", "danger")

    return redirect(url_for('main.contact_page'))



@main.route('/contact')
def contact_page():
    return render_template('user/contact.html')


# --- ADMIN INTERFACE ---
# AUTHENTICATION FOR THE ADMIN PAGE
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

# ADMIN DASHBOARD
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
    featured = Listing.query.filter_by(is_sold=False).order_by(Listing.id.desc()).all()
    sold = Listing.query.filter_by(is_sold=True).order_by(Listing.sold_at.desc()).all()
    return render_template('admin/admin_listings.html', featured=featured, sold=sold)


# CREATE BLOG 
@main.route('/admin/blog/new', methods=['GET', 'POST'])
@login_required
def new_blog():
    if not current_user.is_admin:
        abort(403)

    if request.method == 'POST':
        title = request.form['title']
        summary = request.form['summary']
        content = request.form['content']
        image_file = request.files['image']

        image_url = upload_to_r2(image_file) if image_file and image_file.filename else 'https://via.placeholder.com/600x400?text=No+Image'

        new_post = Blog(
            title=title,
            image_url=image_url,
            author=current_user.username,
            summary=summary,
            content=content
        )
        db.session.add(new_post)
        db.session.commit()
        flash('Blog post published!', 'success')
        return redirect(url_for('main.blog'))

    return render_template('admin/new_blog.html')

# CREATE LISTING
@main.route('/admin/listing/new', methods=['GET', 'POST'])
@login_required
def new_listing():
    if not current_user.is_admin:
        abort(403)

    if request.method == 'POST':
        name = request.form['name']
        location = request.form['location']
        description = request.form.get('description')
        size = request.form['size']
        price = request.form['price']
        files = request.files.getlist('images')

        image_urls = []
        for file in files:
            url = upload_to_r2(file)
            if url:
                image_urls.append(url)
            else:
                current_app.logger.error(f"R2 upload error for {file.filename}")


        if not image_urls:
            flash("Image upload failed. Please try again.", "danger")
            return redirect(url_for('main.new_listing'))

        new_listing = Listing(
            name=name,
            location=location,
            description=description,
            size=size,
            price=price,
            image_urls=','.join(image_urls)
        )
        db.session.add(new_listing)
        db.session.commit()
        flash("Listing added successfully!", "success")
        return redirect(url_for('main.listings'))

    return render_template('admin/new_listing.html')

# DELETE BLOG 
@main.route('/admin/blog/delete/<int:id>', methods=['POST'])
@login_required
def delete_blog(id):
    if not current_user.is_admin:
        abort(403)

    post = Blog.query.get_or_404(id)

    if post.image_url:
        delete_from_r2(post.image_url)

    db.session.delete(post)
    db.session.commit()
    flash('Blog post deleted.', 'info')
    return redirect(url_for('main.admin_blogs'))

# DELETE LISTING 
@main.route('/admin/listing/delete/<int:id>', methods=['POST'])
@login_required
def delete_listing(id):
    if not current_user.is_admin:
        abort(403)

    listing = Listing.query.get_or_404(id)

    if listing.image_urls:
        for url in listing.image_urls.split(','):
            delete_from_r2(url)

    db.session.delete(listing)
    db.session.commit()
    flash('Listing deleted.', 'info')
    return redirect(url_for('main.admin_listings'))

# EDIT BLOG 
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
            delete_from_r2(post.image)
            post.image_url = upload_to_r2(image_file)

        db.session.commit()
        flash('Blog post updated successfully!', 'success')
        return redirect(url_for('main.admin_blogs'))

    return render_template('admin/edit_blog.html', post=post)

# EDIT LISTING 
@main.route('/admin/listing/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_listing(id):
    if not current_user.is_admin:
        abort(403)

    listing = Listing.query.get_or_404(id)

    if request.method == 'POST':
        listing.name = request.form['name']
        listing.location = request.form['location']
        listing.size = request.form['size']
        listing.price = request.form['price']
        listing.description = request.form['description']

        files = request.files.getlist('images')
        if files and any(f.filename for f in files):
            for url in listing.image_urls.split(','):
                delete_from_r2(url)

            new_images = [upload_to_r2(file) for file in files if file and file.filename]
            listing.image_urls = ','.join(new_images)

        db.session.commit()
        flash('Listing updated successfully!', 'success')
        return redirect(url_for('main.admin_listings'))

    return render_template('admin/edit_listing.html', listing=listing)


# MARK LISTING AS SOLD 
@main.route('/admin/listing/<int:id>/mark_sold', methods=['POST'])
@login_required
def mark_listing_sold(id):
    if not current_user.is_admin:
        abort(403)

    listing = Listing.query.get_or_404(id)
    listing.is_sold = True
    listing.sold_at = datetime.utcnow()
    db.session.commit()

    flash('Listing marked as sold.', 'success')
    return redirect(url_for('main.admin_listings'))


#@main.route("/init-db")
#def init_db():
    try:
        db.create_all()
        return "✅ Tables created successfully on cPanel DB."
    except Exception as e:
        return f"❌ Migration failed: {e}"

