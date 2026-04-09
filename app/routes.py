import os
import re
import threading
import urllib.parse
from datetime import datetime
from typing import Any, cast

import bleach
from better_profanity import profanity
from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    send_from_directory,
    url_for,
)
from flask_login import current_user, login_required, login_user, logout_user
from flask_mail import Message
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from sqlalchemy.orm import joinedload
from werkzeug.security import check_password_hash

from app.extensions import cache, db, limiter, mail
from app.models import (
    Blog,
    Category,
    Comment,
    Feature,
    Listing,
    RequestSubmission,
    Subscriber,
    User,
)
from app.utils.r2_upload import delete_from_r2, upload_to_r2


# Custom Pagination class for lists, mimicking Flask-SQLAlchemy's Pagination
# This allows the same template logic to be used for list-based pagination.
class ListPagination:
    def __init__(self, items, page, per_page, total):
        self.items = items  # The actual items for the current page
        self.page = page
        self.per_page = per_page
        self.total = total
        self.pages = (total + per_page - 1) // per_page if per_page > 0 else 0
        self.has_prev = self.page > 1
        self.has_next = self.page < self.pages
        self.prev_num = self.page - 1 if self.has_prev else None
        self.next_num = self.page + 1 if self.has_next else None

    def iter_pages(self, left_edge=2, right_edge=2, left_current=2, right_current=2):
        last_page = self.pages
        if last_page == 0:
            return []
        for num in range(1, last_page + 1):
            if num <= left_edge or (self.page - left_current - 1 < num < self.page + right_current + 1) or num > last_page - right_edge:
                yield num
            elif num == left_edge + 1 or num == last_page - right_edge:
                yield None


main = Blueprint("main", __name__)
# Load default profanity word list once at import time
try:
    profanity.load_censor_words()
except Exception:
    pass


def notify_subscribers(subject, template_name, **kwargs):
    """Render individualized email HTML for active subscribers in the current
    request context, then send the pre-rendered messages from a background
    thread to avoid blocking the request.
    """
    active_subs = Subscriber.query.filter_by(is_active=True).all()
    if not active_subs:
        return

    messages = []
    # Determine an appropriate sender for outgoing messages. Accept either:
    # - a full email address in MAIL_DEFAULT_SENDER, or
    # - a display name in MAIL_DEFAULT_SENDER combined with MAIL_USERNAME,
    # - or fall back to MAIL_USERNAME.
    raw_sender = current_app.config.get("MAIL_DEFAULT_SENDER")
    mail_username = current_app.config.get("MAIL_USERNAME")

    def _effective_sender(raw, username):
        if not raw and username:
            return username
        if not raw:
            return None
        s = raw.strip()
        # Strip surrounding quotes if present
        if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
            s = s[1:-1]
        # If the configured default already looks like an email, use it.
        if "@" in s:
            return s
        # Otherwise, combine display name with the configured username if available.
        if username:
            return (s, username)
        return s

    effective_sender = _effective_sender(raw_sender, mail_username)
    for sub in active_subs:
        try:
            # Determine a host base to build absolute links that respect the
            # current request host (development) or fall back to a configured
            # public base (production). Prefer the request host when available
            # so links in dev point to localhost.
            try:
                host_base = request.host_url.rstrip("/")
            except Exception:
                host_base = current_app.config.get("BASE_URL") or (
                    f"{current_app.config.get('PREFERRED_URL_SCHEME', 'http')}://{current_app.config.get('SERVER_NAME', '')}"
                )

            # Build optional absolute URLs and pass into template context so
            # templates can prefer these values over url_for(..., _external=True).
            render_kwargs = dict(kwargs)
            render_kwargs["sub_email"] = sub.email
            try:
                quoted = urllib.parse.quote(sub.email, safe="")
                render_kwargs["unsubscribe_url"] = host_base + url_for("main.unsubscribe", email=quoted, _external=False)
            except Exception:
                pass

            # If a listing or blog object was passed, add their detail URLs.
            listing_obj = kwargs.get("listing")
            if listing_obj:
                try:
                    render_kwargs["listing_url"] = host_base + url_for(
                        "main.listing_detail",
                        listing_id=listing_obj.id,
                        _external=False,
                    )
                except Exception:
                    pass

            blog_obj = kwargs.get("blog")
            if blog_obj:
                try:
                    render_kwargs["blog_url"] = host_base + url_for("main.blog_detail", id=blog_obj.id, _external=False)
                except Exception:
                    pass

            html_body = render_template(template_name, **render_kwargs)
            msg = Message(
                subject=subject,
                sender=effective_sender,
                recipients=[cast(str, sub.email)],
                html=html_body,
            )
            messages.append(msg)
        except Exception as e:
            try:
                current_app.logger.error(f"Failed to render email for {sub.email}: {e}")
            except Exception:
                pass

    if not messages:
        return

    app = cast(Any, current_app)._get_current_object()

    def send_messages(msgs):
        with app.app_context():
            for m in msgs:
                try:
                    mail.send(m)
                except Exception as e:
                    try:
                        app.logger.error(f"Failed to send to {m.recipients}: {e}")
                    except Exception:
                        pass

    thread = threading.Thread(target=send_messages, args=(messages,))
    thread.daemon = True
    thread.start()


@main.route("/subscribe", methods=["POST"])
def subscribe():
    email = request.form.get("email")

    if not email:
        flash("Please provide a valid email address.", "warning")
        return redirect(request.referrer or url_for("main.home"), code=303)

    # Check if they are already in the database
    existing_sub = Subscriber.query.filter_by(email=email).first()

    if existing_sub:
        if not existing_sub.is_active:
            # Welcome them back if they previously unsubscribed
            existing_sub.is_active = True
            db.session.commit()
            flash(
                "Welcome back! We've successfully reactivated your subscription.",
                "success",
            )
        else:
            # They are already active
            flash("You're already subscribed to our newsletter!", "info")
    else:
        # Create a brand new subscriber
        new_sub = Subscriber(email=email)
        db.session.add(new_sub)
        db.session.commit()
        flash(
            "Subscription successful! Stay tuned for the latest updates in your inbox.",
            "success",
        )

    return redirect(request.referrer or url_for("main.home"), code=303)


@main.route("/unsubscribe/")  # Fallback if no email is provided
@main.route("/unsubscribe/<string:email>")
def unsubscribe(email=None):
    if not email:
        # Maybe redirect them to a general contact page or show a generic message
        return render_template("unsubscribe_manual.html"), 400

    # Decode percent-encoded emails (Flask often decodes but be defensive)
    try:
        decoded = urllib.parse.unquote(email)
    except Exception:
        decoded = email

    subscriber = Subscriber.query.filter_by(email=decoded).first_or_404()
    subscriber.is_active = False
    db.session.commit()
    # Template lives under emails/ in this project
    return render_template("emails/unsubscribed_success.html", email=decoded)


# --- USER INTERFACE ---
@main.route("/")
# Cache the rendered home page for anonymous users to improve load times on mobile and desktop.
# We skip caching for authenticated users so admins see live data.
@cache.cached(timeout=300, unless=lambda: current_user.is_authenticated)
def home():
    # Fetch all listings for the grid in Section 2
    # Optimization: Use joinedload to fetch features in the same query to avoid N+1 issues
    all_listings = Listing.query.options(joinedload(cast(Any, Listing.features))).filter_by(is_sold=False).order_by(Listing.created_at.desc()).all()

    # We define the slide data here or directly in the HTML
    slides = [
        {
            "image": "https://pub-950077afaafe4cfc92639111581ed1ac.r2.dev/hero_1.jpg",
            "title": "I Like It Properties",
            "sub": "At I Like It Properties, we believe deeply in People, Purpose and Properties",
        },
        {
            "image": "https://pub-950077afaafe4cfc92639111581ed1ac.r2.dev/hero_2.jpg",
            "title": "Real Estate solutions",
            "sub": "Your trusted partner for seamless real estate solutions",
        },
        {
            "image": "https://pub-950077afaafe4cfc92639111581ed1ac.r2.dev/hero_3.jpg",
            "title": "Trusted Agency",
            "sub": "Partner with a team that champions informed choices, lasting relationships and property that truly delivers.",
        },
    ]

    return render_template("user/home.html", listings=all_listings, slides=slides)


@main.route("/listings")
# Added 'unless' to skip caching for logged-in users.
# This ensures admins always see the latest notification counts
# and the correct navbar items.
@cache.cached(timeout=300, query_string=True, unless=lambda: current_user.is_authenticated)
def listings():
    # 1. Start with the base query
    query = Listing.query.options(joinedload(cast(Any, Listing.features)))

    # 2. Capture user inputs from the URL
    location_filter = request.args.get("location")
    status_filter = request.args.get("status")
    type_filter = request.args.get("property_type")
    price_range = request.args.get("price_range")  # Returns "min-max" e.g., "0-15000"
    selected_features = request.args.getlist("features")

    # 3. Apply Case-Insensitive Location Filter (e.g., kiamunyi matches Kiamunyi)
    if location_filter:
        # .ilike() is case-insensitive and the % wildcards allow partial matches
        query = query.filter(Listing.location.ilike(f"%{location_filter}%"))

    # 4. Apply Status and Property Type Filters
    if status_filter:
        query = query.filter(Listing.listing_status == status_filter)

    if type_filter:
        query = query.filter(Listing.property_type == type_filter)

    # 5. Handle Amenities (Many-to-Many)
    if selected_features:
        for feature_name in selected_features:
            query = query.filter(Listing.features.any(Feature.name == feature_name))

    # Execute query for base results
    filtered_listings = query.all()

    # 6. Apply Dynamic Price Range Filtering (Python-side)
    if price_range and "-" in price_range:
        try:
            min_str, max_str = price_range.split("-")
            min_price_val = int(min_str)
            max_price_val = int(max_str)

            valid_listings = []
            for listing in filtered_listings:
                # Clean price string (e.g., "Ksh 5,000,000" -> 5000000)
                clean_price_str = re.sub(r"[^\d]", "", listing.price)

                if clean_price_str.isdigit():
                    price_int = int(clean_price_str)
                    # Check if property falls within the selected dropdown range
                    if min_price_val <= price_int <= max_price_val:
                        valid_listings.append(listing)

            filtered_listings = valid_listings
        except ValueError:
            # If split or int conversion fails, we return the unfiltered list
            pass

    # 7. Split and Sort (Available vs Sold)
    featured = [listing for listing in filtered_listings if not listing.is_sold]
    sold = [listing for listing in filtered_listings if listing.is_sold]

    # Sort Available newest first, Sold by most recently sold
    featured.sort(key=lambda x: x.id, reverse=True)
    sold.sort(key=lambda x: getattr(x, "sold_at", None) or x.created_at or x.id, reverse=True)

    # 8. Pagination Logic (Matching Blogs style)
    page = request.args.get("page", 1, type=int)
    per_page = 4
    total = len(featured)
    start = (page - 1) * per_page
    end = start + per_page
    paginated_featured = featured[start:end]
    pagination = ListPagination(paginated_featured, page, per_page, total)

    # 9. Extract UI Data for Sidebar Amenities
    active_features = Feature.query.filter(Feature.listings.any()).all()
    unique_features = sorted([f.name for f in active_features if f.name])
    show_features_filter = len(unique_features) >= 10

    # 10. Render the template
    return render_template(
        "user/listings.html",
        featured=paginated_featured,
        pagination=pagination,
        sold=sold,
        unique_features=unique_features,
        show_features_filter=show_features_filter,
        selected_features=selected_features,
    )


@main.route("/blogs")
def blog():
    # 1. Pagination Logic: 5 posts per page as seen in the images
    page = request.args.get("page", 1, type=int)
    pagination = Blog.query.order_by(Blog.date_posted.desc()).paginate(page=page, per_page=4)
    posts = pagination.items

    # 2. Sidebar Data: Fetch categories to generate the count grid
    categories = Category.query.all()

    return render_template(
        "user/blogs.html",
        posts=posts,
        pagination=pagination,
        categories=categories,
        no_background=True,
    )


@main.route("/blog/<int:id>", methods=["GET", "POST"])
@limiter.limit("10 per hour")
def blog_detail(id):
    post = Blog.query.get_or_404(id)
    admin = os.environ.get("ADMIN_USERNAME", "admin")

    if request.method == "POST":
        # --- LAYER 1: THE HONEYPOT ---
        if request.form.get("confirm_email_address"):
            return redirect(url_for("main.blog_detail", id=id), code=303)

        # --- LAYER 2: SANITIZATION ---
        raw_name = request.form.get("name")
        raw_email = request.form.get("email")
        raw_message = request.form.get("message")

        clean_name = bleach.clean(raw_name or "", tags=[], strip=True)
        clean_email = bleach.clean(raw_email or "", tags=[], strip=True)
        clean_message = bleach.clean(raw_message or "", tags=[], strip=True)

        if not clean_message or not clean_name:
            flash("Please enter a valid name and message.", "warning")
            return redirect(url_for("main.blog_detail", id=id), code=303)

        # --- LAYER 3: PROFANITY CHECK & MANUAL APPROVAL ---
        try:
            profane = profanity.contains_profanity(clean_message)
        except Exception:
            profane = False

        # Server-side: require Gmail addresses only (basic domain check)
        email_domain = clean_email.split("@")[-1].lower() if "@" in clean_email else ""
        allowed_domains = ("gmail.com", "googlemail.com")
        if email_domain not in allowed_domains:
            flash("Please provide a valid Gmail address (example@gmail.com).", "warning")
            return redirect(url_for("main.blog_detail", id=id), code=303)

        # Always require manual approval; mark flagged if profanity detected.
        new_comment = Comment(
            author_name=clean_name,
            author_email=clean_email,
            content=clean_message,
            blog_id=post.id,
            is_approved=False,
            is_seen=False,
            is_flagged=bool(profane),
            email_verified=False,
        )

        db.session.add(new_comment)
        db.session.commit()
        # Invalidate caches so the public site shows the up-to-date moderation state
        try:
            cache.clear()
        except Exception:
            current_app.logger.exception("Failed to clear cache after new comment")

        # Send admin notification (comment awaiting moderation)
        try:
            admin_sender = current_app.config.get("MAIL_USERNAME") or current_app.config.get("MAIL_DEFAULT_SENDER") or "info@ilikeitproperties.co.ke"
            admin_msg = Message(
                subject=f"New Comment Awaiting Approval: {post.title}",
                sender=admin_sender,
                recipients=[admin_sender],
            )
            admin_msg.body = (
                f"Hello Admin,\n\nA new comment has been posted on '{post.title}' by {clean_name}.\n\n"
                f"Message: {clean_message}\n\nFlagged for profanity: {profane}\n\n"
                "Please log in to the dashboard to approve or decline it."
            )
            mail.send(admin_msg)
        except Exception as e:
            print(f"Mail failed: {e}")

        # Send verification email to commenter to confirm ownership
        try:
            secret = current_app.config.get("SECRET_KEY") or ""
            s = URLSafeTimedSerializer(str(secret))
            token = s.dumps(
                {"comment_id": new_comment.id, "email": new_comment.author_email},
                salt="comment-verify",
            )
            verify_url = url_for("main.verify_comment", token=token, _external=True)
            user_sender = current_app.config.get("MAIL_USERNAME") or current_app.config.get("MAIL_DEFAULT_SENDER") or "info@ilikeitproperties.co.ke"
            user_msg = Message(
                subject="Verify your email for comment on I Like It Properties",
                sender=user_sender,
                recipients=[cast(str, new_comment.author_email)],
            )
            user_msg.body = (
                f"Hi {new_comment.author_name},\n\nPlease verify your email address by clicking the link below:\n\n{verify_url}\n\n"
                "This helps us confirm that you own this Gmail address. After verification, an admin will review your comment."
            )
            mail.send(user_msg)
        except Exception as e:
            print(f"Verification email failed: {e}")

        flash(
            "Thank you! Please verify your email (check your inbox). Your comment is awaiting moderation.",
            "success",
        )
        return redirect(url_for("main.blog_detail", id=id), code=303)

    # Optimization: Filter approved comments at the database level instead of a list comprehension
    comments = Comment.query.filter_by(blog_id=id, is_approved=True).order_by(Comment.timestamp.desc()).all()
    categories = Category.query.all()

    return render_template(
        "user/blog_detail.html",
        post=post,
        admin=admin,
        comments=comments,
        categories=categories,
    )


@main.route("/listing/<int:listing_id>", methods=["GET", "POST"])
def listing_detail(listing_id):
    listing = Listing.query.get_or_404(listing_id)

    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        message = request.form.get("message")

        if not all([name, email, message]):
            flash("Please complete all inquiry fields.", "warning")
            return redirect(url_for("main.listing_detail", listing_id=listing_id), code=303)

        try:
            # Log the inquiry
            new_submission = RequestSubmission(
                name=name,
                email=email,
                subject=f"Inquiry: {listing.name}",
                message=message,
            )
            db.session.add(new_submission)
            db.session.commit()
            # Invalidate listing/listings caches so users see the new inquiry state if relevant
            try:
                cache.clear()
            except Exception:
                current_app.logger.exception("Failed to clear cache after listing inquiry")

            raw_sender = current_app.config.get("MAIL_DEFAULT_SENDER")
            mail_username = current_app.config.get("MAIL_USERNAME")

            def _format_sender(raw, username):
                if raw:
                    s = raw.strip()
                    if "@" in s:
                        return s
                    if username:
                        return f"{s} <{username}>"
                    return s
                return username

            admin_sender = _format_sender(raw_sender, mail_username) or mail_username or "info@ilikeitproperties.co.ke"
            admin_recipient = mail_username or "info@ilikeitproperties.co.ke"

            admin_msg = Message(
                subject=f"Listing Inquiry: {listing.name}",
                sender=admin_sender,
                recipients=[admin_recipient],
            )
            admin_msg.body = f"{name} <{email}> is interested in {listing.name} (ID: {listing.id}).\n\nMessage:\n{message}"
            mail.send(admin_msg)

            flash(
                "Inquiry sent! Our team will review your message and contact you shortly.",
                "success",
            )
        except Exception:
            current_app.logger.exception("Failed to send listing inquiry")
            flash("Unable to send inquiry right now — please try again later.", "danger")

        return redirect(url_for("main.listing_detail", listing_id=listing_id), code=303)

    return render_template("user/listing_detail.html", listing=listing)


@main.route("/about")
@cache.cached(timeout=3600)
def about():
    return render_template("user/about.html")


# Contact page with email functionality
def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)


def log_submission(name, email, subject, message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {name} <{email}> | Subject: {subject} | Message: {message}\n"

    try:
        # Use absolute path for robustness
        base_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
        log_path = os.path.join(base_dir, "contact_audit.log")
        with open(log_path, "a", encoding="utf-8") as log_file:
            log_file.write(log_entry)
    except OSError as e:
        try:
            current_app.logger.warning(f"Failed to write to contact_audit.log: {e}")
        except OSError:
            pass  # If console logging also fails, satisfy the request silently


@main.route("/contact", methods=["POST"])
def contact():
    name = request.form.get("name")
    email = request.form.get("email")
    subject = request.form.get("subject")
    message = request.form.get("message")

    if not all([name, email, subject, message]) or not is_valid_email(email):
        flash("Please fill all fields correctly.", "danger")
        return redirect(url_for("main.contact_page"), code=303)

    try:
        # Log the submission
        log_submission(name, email, subject, message)
        new_submission = RequestSubmission(name=name, email=email, subject=subject, message=message)
        db.session.add(new_submission)
        db.session.commit()

        # Compose message to site admin using Flask-Mail for consistent config
        raw_sender = current_app.config.get("MAIL_DEFAULT_SENDER")
        mail_username = current_app.config.get("MAIL_USERNAME")

        def _format_sender(raw, username):
            if raw:
                s = raw.strip()
                if "@" in s:
                    return s
                if username:
                    return f"{s} <{username}>"
                return s
            return username

        admin_sender = _format_sender(raw_sender, mail_username) or mail_username or "info@ilikeitproperties.co.ke"
        admin_recipient = mail_username or "info@ilikeitproperties.co.ke"

        admin_msg = Message(
            subject=f"New Inquiry: {subject}",
            sender=admin_sender,
            recipients=[admin_recipient],
        )
        admin_msg.body = (
            f"Hello,\n\n{name} ({email}) submitted a message via the contact form.\n\nSubject: {subject}\nMessage:\n{message}\n\nBest,\nI Like It Properties"
        )

        # Compose auto-reply to sender
        reply_msg = Message(
            subject="We've received your message!",
            sender=admin_sender,
            recipients=[cast(str, email)],
        )
        reply_msg.body = (
            f"Hi {name},\n\n"
            f"Thanks for reaching out to I Like It Properties. We’ve received your message and will get back to you shortly.\n\n"
            f"Subject: {subject}\n"
            f"Message:\n{message}\n\n"
            f"Warm regards,\n"
            f"I Like It Properties"
        )
        reply_msg.html = (
            f'<html><body style="font-family: Arial, sans-serif; color: #333;">'
            f"<p>Hi {name},</p>"
            f"<p>Thanks for reaching out to <strong>I Like It Properties</strong>. We've received your message and will get back to you shortly.</p>"
            f"<p><strong>Subject:</strong> {subject}<br><strong>Message:</strong><br>{message}</p>"
            f"<p>Warm regards,<br><strong>I Like It Properties</strong></p>"
            f'<img src="https://pub-950077afaafe4cfc92639111581ed1ac.r2.dev/ilikeitproperties/logo.jpg" alt="Logo" style="margin-top:20px; height:80px;">'
            f"</body></html>"
        )

        # Send via Flask-Mail (uses app-configured SMTP settings). Log errors for visibility.
        current_app.logger.debug("Sending contact emails: admin=%s user=%s", admin_recipient, email)
        try:
            mail.send(admin_msg)
            mail.send(reply_msg)
        except Exception:
            current_app.logger.exception("Failed to send contact emails")
            raise

        flash(
            "Thank you for reaching out! Your message has been received and our team will respond shortly.",
            "success",
        )

    except Exception:
        current_app.logger.exception("Contact handler failed")
        flash(
            "Oops — we couldn't send your message due to a technical issue. Please try again or contact us directly at info@ilikeitproperties.co.ke.",
            "danger",
        )

    return redirect(url_for("main.contact_page"), code=303)


@main.route("/contact")
def contact_page():
    return render_template("user/contact.html")


# --- ADMIN INTERFACE ---
# AUTHENTICATION FOR THE ADMIN PAGE
@main.route("/login", methods=["GET", "POST"])
def login():
    # If already logged in, don't show the login page
    if current_user.is_authenticated:
        return redirect(url_for("main.admin_dashboard"))

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password") or ""
        remember = True if request.form.get("remember") else False

        user = User.query.filter_by(username=username).first()

        if user and password and check_password_hash(user.password, password):
            login_user(user, remember=remember)

            # Handle the 'next' parameter for better UX
            next_page = request.args.get("next")
            flash("Welcome back, Admin!", "success")
            if next_page:
                return redirect(next_page, code=303)
            return redirect(url_for("main.admin_dashboard"), code=303)
        else:
            flash("Access Denied: Invalid credentials.", "danger")

    return render_template("admin/admin_login.html")


@main.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been securely logged out.", "info")
    return redirect(url_for("main.home"))


# ADMIN DASHBOARD
@main.route("/admin/dashboard")
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        abort(403)

    # Fetch counts for the dashboard stats
    # Assuming your models are named Listing and Blog
    active_count = Listing.query.filter_by(is_sold=False).count()
    sold_count = Listing.query.filter_by(is_sold=True).count()
    blog_count = Blog.query.count()

    return render_template(
        "admin/admin_dashboard.html",
        active_count=active_count,
        sold_count=sold_count,
        blog_count=blog_count,
    )


@main.route("/admin/blogs")
@login_required
def admin_blogs():
    if not current_user.is_admin:
        abort(403)
    posts = Blog.query.order_by(Blog.date_posted.desc()).all()
    return render_template("admin/admin_blogs.html", posts=posts)


@main.route("/admin/listings")
@login_required
def admin_listings():
    if not current_user.is_admin:
        abort(403)
    listings = Listing.query.order_by(Listing.is_sold.asc(), Listing.id.desc()).all()

    return render_template("admin/admin_listings.html", listings=listings)


# BLOGS
@main.route("/admin/blog/new", methods=["GET", "POST"])
@login_required
def new_blog():
    if not current_user.is_admin:
        abort(403)

    if request.method == "POST":
        title = request.form.get("title")
        content = request.form.get("content")
        category_name = (request.form.get("category", "General") or "General").strip()
        image_file = request.files.get("image")

        # Basic validation: require title and content
        if not title or not content:
            flash("Please provide both title and content for the blog post.", "warning")
            return redirect(url_for("main.new_blog"), code=303)

        # --- CATEGORY LOGIC ---
        # Find existing or create new category on the fly
        category = Category.query.filter_by(name=category_name).first()
        if not category:
            category = Category(name=category_name)
            db.session.add(category)
            db.session.flush()  # Gets us the ID immediately

        # --- AUTOMATIC SUMMARY LOGIC ---
        # Strip HTML tags first, then take the first 155 characters
        clean_text = bleach.clean(content, tags=[], strip=True)
        auto_summary = (clean_text[:152] + "...") if len(clean_text) > 155 else clean_text

        image_url = upload_to_r2(image_file) if image_file and getattr(image_file, "filename", None) else None

        new_post = Blog(
            title=title,
            image_url=image_url,
            author=current_user.username,
            summary=auto_summary,  # Now automated
            content=content,
            category_id=category.id,  # Linking via ID
        )
        db.session.add(new_post)
        db.session.commit()
        # Invalidate caches so new posts appear immediately on the public site
        try:
            cache.clear()
        except Exception:
            current_app.logger.exception("Failed to clear cache after new blog")

        # --- NOTIFICATION LOGIC ---
        # Pass the arguments directly; DO NOT render_template here!
        notify_subscribers(
            subject=f"New Post: {new_post.title}",
            template_name="emails/blog_notification.html",
            blog=new_post,
        )

        flash("Blog post published and subscribers notified!", "success")
        return redirect(url_for("main.admin_blogs"), code=303)

    return render_template("admin/new_blog.html")


@main.route("/admin/blog/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_blog(id):
    if not current_user.is_admin:
        abort(403)

    post = Blog.query.get_or_404(id)

    if request.method == "POST":
        # Use .get to avoid KeyError/400 when tests omit optional fields
        post.title = request.form.get("title") or post.title
        post.content = request.form.get("content") or post.content

        # Update Category
        category_name = request.form.get("category", "General").strip()
        category = Category.query.filter_by(name=category_name).first()
        if not category:
            category = Category(name=category_name)
            db.session.add(category)
            db.session.flush()
        post.category_id = category.id

        # Update Summary based on new content
        clean_text = bleach.clean(post.content, tags=[], strip=True)
        post.summary = (clean_text[:152] + "...") if len(clean_text) > 155 else clean_text

        image_file = request.files.get("image")
        if image_file and getattr(image_file, "filename", None):
            if post.image_url:
                delete_from_r2(post.image_url)
            post.image_url = upload_to_r2(image_file)

        db.session.commit()
        # Invalidate caches so updated blog content is shown
        try:
            cache.clear()
        except Exception:
            current_app.logger.exception("Failed to clear cache after edit blog")
        flash("Blog post updated successfully!", "success")
        return redirect(url_for("main.admin_blogs"), code=303)

    return render_template("admin/edit_blog.html", post=post)


@main.route("/admin/blog/delete/<int:id>", methods=["POST"])
@login_required
def delete_blog(id):
    if not current_user.is_admin:
        abort(403)

    post = Blog.query.get_or_404(id)

    if post.image_url:
        delete_from_r2(post.image_url)

    db.session.delete(post)
    db.session.commit()
    # Clear caches so deleted content disappears from listings/pages
    try:
        cache.clear()
    except Exception:
        current_app.logger.exception("Failed to clear cache after delete blog")
    flash("Blog post deleted.", "info")
    return redirect(url_for("main.admin_blogs"), code=303)


# --- HELPER FUNCTION ---
def safe_int(value):
    """Safely converts empty form strings to None for the database."""
    try:
        return int(value) if value and value.strip() else None
    except ValueError:
        return None


# --- NEW LISTING ROUTE ---
@main.route("/admin/listing/new", methods=["GET", "POST"])
@login_required
def new_listing():
    if not current_user.is_admin:
        abort(403)

    if request.method == "POST":
        # Required Core Fields
        name = request.form["name"]
        location = request.form["location"]
        description = request.form.get("description", "")
        size = request.form["size"]
        price = request.form["price"]

        # Dropdowns (With safe defaults)
        property_type = request.form.get("property_type", "Residential")
        listing_status = request.form.get("listing_status", "For Sale")

        # Optional Specs
        bedrooms = safe_int(request.form.get("bedrooms"))
        bathrooms = safe_int(request.form.get("bathrooms"))
        floors = safe_int(request.form.get("floors"))
        parking_spaces = safe_int(request.form.get("parking_spaces"))
        year_built = safe_int(request.form.get("year_built"))

        # Image Handling: accept zero or more images; allow listings without images
        files = request.files.getlist("images") or []
        image_urls = []
        for file in files:
            if file and getattr(file, "filename", None):
                url = upload_to_r2(file)
                if url:
                    image_urls.append(url)

        # Create Property Object
        new_property = Listing(
            name=name,
            location=location,
            description=description,
            size=size,
            price=price,
            image_urls=",".join(image_urls) if image_urls else "",
            property_type=property_type,
            listing_status=listing_status,
            bedrooms=bedrooms,
            bathrooms=bathrooms,
            floors=floors,
            parking_spaces=parking_spaces,
            year_built=year_built,
        )

        # --- TAG INPUT FEATURES LOGIC ---
        features_raw = request.form.get("features_list")  # e.g. "Borehole, CCTV"
        if features_raw:
            names = [n.strip() for n in features_raw.split(",") if n.strip()]
            for f_name in names:
                feat = Feature.query.filter_by(name=f_name).first()
                if not feat:
                    feat = Feature(name=f_name)  # Auto-create missing features
                    db.session.add(feat)
                    db.session.flush()
                new_property.features.append(feat)

        db.session.add(new_property)
        db.session.commit()
        # Clear caches so the new listing is visible immediately
        try:
            cache.clear()
        except Exception:
            current_app.logger.exception("Failed to clear cache after new listing")

        # --- NOTIFICATION AUTOMATION ---
        hero_image = image_urls[0] if image_urls else None

        # Pass the arguments directly; DO NOT render_template here!
        notify_subscribers(
            subject=f"New Property Alert: {new_property.name}",
            template_name="emails/listing_notification.html",
            listing=new_property,
            image=hero_image,
        )

        flash("Listing added and subscribers notified!", "success")
        return redirect(url_for("main.admin_listings"), code=303)

    return render_template("admin/new_listing.html")


# --- EDIT LISTING ROUTE ---
@main.route("/admin/listing/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_listing(id):
    if not current_user.is_admin:
        abort(403)

    listing = Listing.query.get_or_404(id)

    if request.method == "POST":
        # Update Core & Dropdowns
        listing.name = request.form["name"]
        listing.location = request.form["location"]
        listing.size = request.form["size"]
        listing.price = request.form["price"]
        listing.description = request.form.get("description", "")
        listing.property_type = request.form.get("property_type", "Residential")
        listing.listing_status = request.form.get("listing_status", "For Sale")

        # Update Optional Specs
        listing.bedrooms = safe_int(request.form.get("bedrooms"))
        listing.bathrooms = safe_int(request.form.get("bathrooms"))
        listing.floors = safe_int(request.form.get("floors"))
        listing.parking_spaces = safe_int(request.form.get("parking_spaces"))
        listing.year_built = safe_int(request.form.get("year_built"))

        # Update Features (Clear old ones, add current ones)
        listing.features = []
        features_raw = request.form.get("features_list")
        if features_raw:
            names = [n.strip() for n in features_raw.split(",") if n.strip()]
            for f_name in names:
                feat = Feature.query.filter_by(name=f_name).first()
                if not feat:
                    feat = Feature(name=f_name)
                    db.session.add(feat)
                    db.session.flush()
                listing.features.append(feat)

        # Image Handling (Only replace if new ones are uploaded)
        files = request.files.getlist("images")
        if files and any(f.filename for f in files):
            for url in listing.image_urls.split(","):
                if url.strip():
                    delete_from_r2(url.strip())
            new_images = [upload_to_r2(file) for file in files if file and file.filename]
            listing.image_urls = ",".join(new_images)

        db.session.commit()
        # Clear caches so the updated listing is reflected publicly
        try:
            cache.clear()
        except Exception:
            current_app.logger.exception("Failed to clear cache after edit listing")
        flash("Listing updated successfully!", "success")
        return redirect(url_for("main.admin_listings"), code=303)

    return render_template("admin/edit_listing.html", listing=listing)


# --- DELETE LISTING ROUTE ---
@main.route("/admin/listing/delete/<int:id>", methods=["POST"])
@login_required
def delete_listing(id):
    if not current_user.is_admin:
        abort(403)

    listing = Listing.query.get_or_404(id)

    if listing.image_urls:
        for url in listing.image_urls.split(","):
            if url.strip():
                delete_from_r2(url.strip())

    db.session.delete(listing)
    db.session.commit()
    try:
        cache.clear()
    except Exception:
        current_app.logger.exception("Failed to clear cache after delete listing")
    flash("Listing deleted.", "info")
    return redirect(url_for("main.admin_listings"), code=303)


# --- TOGGLE SOLD STATUS ROUTE ---
@main.route("/admin/listing/<int:id>/toggle_sold", methods=["POST"])
@login_required
def toggle_listing_sold(id):
    if not current_user.is_admin:
        abort(403)

    listing = Listing.query.get_or_404(id)

    # Toggle logic
    if listing.is_sold:
        listing.is_sold = False
        listing.sold_at = None
        flash(f'"{listing.name}" is back on the market!', "success")
    else:
        listing.is_sold = True
        listing.sold_at = datetime.utcnow()
        flash(f'"{listing.name}" marked as sold! Congratulations!', "success")

    db.session.commit()
    try:
        cache.clear()
    except Exception:
        current_app.logger.exception("Failed to clear cache after toggling sold status")
    return redirect(url_for("main.admin_listings"), code=303)


@main.route("/admin/comments")
@login_required
def pending_comments():
    if not current_user.is_admin:
        flash("Unauthorized access.", "danger")
        return redirect(url_for("main.home"))

    # Fetch all comments that haven't been approved yet
    comments = Comment.query.filter_by(is_approved=False).order_by(Comment.timestamp.desc()).all()

    # Logic: Mark all currently visible pending comments as 'seen'
    # This ensures that when the page reloads, the navbar bell becomes neutral
    unseen_comments = [c for c in comments if not c.is_seen]
    if unseen_comments:
        for comment in unseen_comments:
            comment.is_seen = True
        db.session.commit()  # Save the 'seen' status to your database

    return render_template("admin/pending_comments.html", comments=comments)


@main.app_context_processor
def inject_admin_stats():
    # Avoid directly accessing current_user attributes in contexts where a request
    # context may not be available (e.g., background email threads).
    try:
        is_auth = getattr(current_user, "is_authenticated", False)
        is_admin = getattr(current_user, "is_admin", False)
        if is_auth and is_admin:
            # The bell only shows the count of NEW (unseen) pending comments
            count = Comment.query.filter_by(is_approved=False, is_seen=False).count()
        else:
            count = 0
    except Exception:
        count = 0

    # This makes 'pending_comments_count' available in every HTML template automatically
    return {"pending_comments_count": count}


@main.route("/admin/comment/approve/<int:comment_id>")
@login_required
def approve_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    comment.is_approved = True
    db.session.commit()
    flash("Comment approved and is now live!", "success")
    # Redirect back to referring page (admin list or edit page) when possible
    ref = request.referrer
    # Clear caches so approved comments appear immediately
    try:
        cache.clear()
    except Exception:
        current_app.logger.exception("Failed to clear cache after approving comment")
    if ref:
        return redirect(ref)
    return redirect(url_for("main.pending_comments"))


@main.route("/admin/comment/delete/<int:comment_id>")
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    blog_id = comment.blog_id
    # Delete the comment and its replies. The `Comment.replies` relationship
    # is configured with `cascade="all, delete-orphan"` in the model,
    # so removing the parent will remove its child replies recursively.
    db.session.delete(comment)
    db.session.commit()
    flash("Selected comment removed.", "info")
    # Clear caches so removed comments disappear immediately
    try:
        cache.clear()
    except Exception:
        current_app.logger.exception("Failed to clear cache after deleting comment")
    # Redirect back to referring page if available, otherwise go to edit page for the blog
    ref = request.referrer
    if ref:
        return redirect(ref)
    return redirect(url_for("main.edit_blog", id=blog_id))


@main.route("/admin/comment/reply/<int:comment_id>", methods=["POST"])
@login_required
@limiter.limit("30 per hour")
def reply_comment(comment_id):
    if not current_user.is_admin:
        return redirect(url_for("main.home"))

    parent_comment = Comment.query.get_or_404(comment_id)
    reply_content = request.form.get("reply_content")

    if reply_content:
        admin_reply = Comment(
            author_name="I Like It Properties (Admin)",
            author_email=current_app.config.get("MAIL_USERNAME") or None,
            author_is_admin=True,
            content=reply_content,
            blog_id=parent_comment.blog_id,
            parent_id=parent_comment.id,
            is_approved=True,
            is_seen=True,
        )
        parent_comment.is_approved = True
        db.session.add(admin_reply)
        db.session.commit()
        # Clear caches so the admin reply and approved state are reflected
        try:
            cache.clear()
        except Exception:
            current_app.logger.exception("Failed to clear cache after admin reply")

    return redirect(request.referrer or url_for("main.home"), code=303)


@main.app_context_processor
def inject_pending_comments():
    # Avoid accessing `current_user` directly without a request context.
    try:
        is_auth = getattr(current_user, "is_authenticated", False)
        is_admin = getattr(current_user, "is_admin", False)
        if is_auth and is_admin:
            count = Comment.query.filter_by(is_approved=False).count()
        else:
            count = 0
    except Exception:
        count = 0

    return {"pending_comments_count": count}


@main.route("/comment/verify/<token>")
def verify_comment(token):
    secret = current_app.config.get("SECRET_KEY") or ""
    s = URLSafeTimedSerializer(str(secret))
    try:
        data = s.loads(token, salt="comment-verify", max_age=60 * 60 * 24)  # 24 hours
        comment_id = data.get("comment_id")
        email = data.get("email")
    except SignatureExpired:
        flash(
            "Verification link expired. Please request a new verification email.",
            "warning",
        )
        return redirect(url_for("main.home"))
    except (BadSignature, Exception):
        flash("Invalid verification link.", "danger")
        return redirect(url_for("main.home"))

    comment = Comment.query.get_or_404(comment_id)
    if comment.author_email != email:
        flash("Verification email does not match comment email.", "danger")
        return redirect(url_for("main.home"))

    comment.email_verified = True
    db.session.commit()
    try:
        cache.clear()
    except Exception:
        current_app.logger.exception("Failed to clear cache after verifying comment")
    flash("Email verified. Your comment is still pending admin approval.", "success")
    return redirect(url_for("main.blog_detail", id=comment.blog_id))


# SERVE SITEMAP
@main.route("/sitemap.xml")
def sitemap():
    return send_from_directory("static", "sitemap.xml")
