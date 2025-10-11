**This branch mirrors the master branch in functionality, with two key differences: it uses a different deployment method and includes SEO enhancements. In this branch, the website and database are hosted on Truehost for production.**

### NAME OF THE WEBSITE 
ilikeitproperties

### BRANCH 
main(Production)

### PROJECT'S BRIEF DESCRIPTION
A dynamic, SEO-optimized real estate website built with Flask, HTML, Bootstrap 5 classes and CSS, designed to showcase property listings and blog posts and also for users to make inquiries about the listings, while enabling users to make inquiries directly via WhatsApp or a contact form.

Upon submitting an inquiry through the contact form, users automatically receive a confirmation email — ensuring a seamless and professional communication experience.


#### Site Architecture(same as the master branch)
##### User Interface
Public-facing pages for:
  - Browsing property listings
  - Reading blog posts
  - Learning about the company
  - Making inquiries via WhatsApp or contact form

##### Admin Interface
Secure backend for:
  - Managing property listings and blogs
  - Streamlining content workflows


### Tech stack
- Backend: Flask — lightweight Python framework powering routing, logic, and server-side rendering
- Frontend: HTML, CSS, and Bootstrap 5 — responsive layout, UI components, and styling
- Email Service: SMTP integration using Python’s smtplib and email libraries — handles automated inquiry responses via the contact form
- Cloud Storage: Cloudflare R2 — hosts public assets including images and static files
- Database: PostgreSQL hosted on Truehost — stores listings, blog content, and admin data
- Deployment: Truehost Server — production hosting environment for the live website
- CI/CD Automation: GitHub Actions — automates testing, deployment, and workflow tasks
- Version Control: GitHub — source code management and collaboration

### INSTALLATION AND RUN INSTRUCTIONS
#### (a) If you are running the project locally, follow the instructions below;
##### 1. Clone the repo
```bash
git clone https://github.com/pekimnjenga/realestate.git
cd realestate
git checkout main
```

##### 2. Create and activate the virtual environment
##### Linux/macOS
```bash
python3 -m venv venv
source venv/bin/activate
```

##### Windows(Powershell or CMD)
```bash
python -m venv venv
source venv\Scripts\activate
```

##### 3. Install dependencies
```bash
pip install -r requirements.txt
```

##### 4. Create a .env file at the root directory
Note : Make sure .env is listed in .gitignore and .dockerignore to avoid exposing secrets.
```env
DATABASE_URL=your-local-db-url
SECRET_KEY=your-secret-key
R2_ACCESS_KEY=your-access-key
R2_SECRET_KEY=your-secret-key
R2_ENDPOINT=https://your-r2-endpoint
R2_BUCKET=your-bucket-name
PUBLIC_BASE_URL=https://your-public-r2-url
EMAIL_PASSWORD=your-email-password #For SMTP email sending
```

##### 5. Run the application
```bash
gunicorn run:app
```



#### (b) Docker-based setup(same as the master branch)
##### 1. Clone the Repository
```bash
git clone https://github.com/pekimnjenga/realestate.git
cd realestate
```

##### 2. Create a .env File at the Project Root
```env
DATABASE_URL=your-local-db-url
SECRET_KEY=your-secret-key
R2_ACCESS_KEY=your-access-key
R2_SECRET_KEY=your-secret-key
R2_ENDPOINT=https://your-r2-endpoint
R2_BUCKET=your-bucket-name
PUBLIC_BASE_URL=https://your-public-r2-url
EMAIL_PASSWORD=your-email-password  # For SMTP email sending
```

Ensure .env is listed in .gitignore and .dockerignore to avoid leaking secrets.

##### 3. Build the Docker Image
```bash
docker build -t app .
```

##### 5. Run the Docker Container
```bash
docker run -p 8080:8080 --env-file .env app
```


### PROJECT'S STRUCTURE
real-estate-website/
├── config.py
├── confirm_images.py
├── README.md
├── requirements.txt
├── run.py
├── set_admin.py
├── .github/
│   └── workflows/
│       └── deploy.yml
├── app/
│   ├── __init__.py
│   ├── extensions.py
│   ├── models.py
│   ├── routes.py
│   ├── static/
│   │   ├── sitemap.xml
│   │   ├── css/
│   │   │   └── styles.css
│   │   └── images/
│   │       ├── corevalues.png
│   │       ├── growth.png
│   │       ├── handshake.png
│   │       ├── IMG-20250831-WA0012.jpg
│   │       ├── Jacob.jpg
│   │       ├── logo.jpg
│   │       ├── mission.png
│   │       ├── realestateimage.jpeg
│   │       └── vision.png
│   ├── templates/
│   │   ├── base.html
│   │   ├── admin/
│   │   │   ├── admin_blogs.html
│   │   │   ├── admin_dashboard.html
│   │   │   ├── admin_listings.html
│   │   │   ├── edit_blog.html
│   │   │   ├── edit_listing.html
│   │   │   ├── login.html
│   │   │   ├── new_blog.html
│   │   │   └── new_listing.html
│   │   └── user/
│   │       ├── about.html
│   │       ├── blog_detail.html
│   │       ├── blogs.html
│   │       ├── contact.html
│   │       ├── home.html
│   │       ├── listing_detail.html
│   │       └── listings.html
│   └── utils/
│       └── r2_upload.py
├── migrations/
│   ├── alembic.ini
│   ├── env.py
│   ├── README
│   ├── script.py.mako
│   └── versions/
│       └── 6e2a4d3fde84_adding_new_columns_to_my_models_and_.py


### DEPLOYMENT STRATEGY
Unlike the staging branch (which uses Render’s auto-deploy), I manually configured the production branch to deploy to Truehost using GitHub Actions each time a push is made.

## Production Deployment via GitHub Actions
### Setup
- Create a `.github/workflows/deploy.yml`
- Log in to cPanel and create an FTP account
- Add FTP credentials to GitHub Secrets i.e FTP_HOST, FTP_USER , FTP_PASS
- Define the branch to be deployed from, local/server directories and exclusions in the deploy.yml file

### Python App Configuration on Truehost
- Create a Python application in cPanel
- Set:
  - Application Root
  - Application URL
  - Startup File eg `run.py`
  - Entry Point for eg `app`
- Added environment variables (e.g. `DATABASE_URL`, `R2_ACCESS_KEY`, etc.)

### Deployment Flow
- Push to `main` triggers GitHub Actions
- Code is deployed to Truehost via FTP
- Install the dependencies on cPanel's terminal
- Restart the application
- The app now runs live on production domain


### Search Engine Optimization (SEO)
The site is strategically optimized for search engine visibility and brand authority, with a focus on indexing only the homepage for clean, branded search results.

### Strategy Overview
- Selective Indexing – Only the homepage is indexed; all other routes (/about, /listings, /blogs, /contact) are crawlable but excluded from search results using noindex, follow directives
- Canonical Tag Logic – Each route declares its own canonical URL to prevent duplicate content and reinforce page identity
- Structured Data (Schema Markup) – JSON-LD schema for RealEstateAgent includes logo, address, contact info, and business description for rich search previews
- Open Graph & Twitter Cards – Social media previews are enhanced with custom titles, descriptions, and branded imagery
- Favicon & Apple Touch Icon – Branded tab icon and mobile bookmark visibility for consistent identity across platforms
- Sitemap Management – A clean sitemap.xml submitted to Google Search Console includes only the homepage, reinforcing the selective indexing strategy


## Developer Contact
Developed and maintained by PEKIM
 Email: njengapekim@gmail.com 
 Phone: +254 797933409
 GitHub: [github.com/pekimnjenga](https://github.com/pekimnjenga)
