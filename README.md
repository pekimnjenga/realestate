### NAME OF THE WEBSITE 
ilikeitproperties

### BRANCH 
master(Staging)

### BRIEF DESCRIPTION
A dynamic, mobile-responsive real estate website built with Flask, HTML, Bootstrap 5, and CSS, designed to showcase property listings and blog posts, while enabling users to make inquiries directly via WhatsApp or a contact form.

Upon submitting an inquiry through the contact form, users automatically receive a confirmation email — ensuring a seamless and professional communication experience.

#### Site Architecture
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


### Tech Stack
- Backend: Flask — lightweight Python framework powering the core logic and routing
- Frontend: HTML, CSS, and Bootstrap 5 — responsive layout and UI styling
- Email Service: SMTP integration using Python's smtplib and email libraries — for automated inquiry responses
- Cloud Storage:
  - Cloudflare R2 — hosting public assets like images and static files
  - Neon — managed PostgreSQL database for listings, blogs, and admin data
- Deployment: Render — staging environment with auto-deploy from GitHub
- Version Control: GitHub — source code management and CI/CD integration


### PROJECT'S STRUCTURE
real-estate-website/
├── config.py
├── confirm_images.py
├── README.md
├── requirements.txt
├── run.py
├── render.yml
├── Dockerfile
├── set_admin.py
├── app/
│   ├── __init__.py
│   ├── extensions.py
│   ├── models.py
│   ├── routes.py
│   ├── static/
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


### INSTALLATION AND RUN INSTRUCTIONS
#### (a) If you are running the project locally, follow the instructions below;
##### 1. Clone the repo
'''bash
git clone https://github.com/pekimnjenga/realestate.git
cd realestate
git checkout master
'''

##### 2. Create and activate the virtual environment
# Linux/macOS
'''bash
python3 -m venv venv
source venv/bin/activate
'''

# Windows(Powershell or CMD)
'''bash
python -m venv venv
source venv\Scripts\activate
'''

##### 3. Install dependencies
'''bash
pip install -r requirements.txt
'''

##### 4. Create a .env file at the root directory
Note : Make sure .env is listed in .gitignore and .dockerignore to avoid exposing secrets.
'''env
DATABASE_URL=your-local-db-url
SECRET_KEY=your-secret-key
R2_ACCESS_KEY=your-access-key
R2_SECRET_KEY=your-secret-key
R2_ENDPOINT=https://your-r2-endpoint
R2_BUCKET=your-bucket-name
PUBLIC_BASE_URL=https://your-public-r2-url
EMAIL_PASSWORD=your-email-password #For SMTP email sending
'''

##### 5. Run the application
# Linux/macOS
'''bash
python3 run.py
'''

# Windows (PowerShell or CMD)
'''bash
python run.py
'''

#### (b) Docker-based setup
##### 1. Clone the Repository
'''bash
git clone https://github.com/pekimnjenga/realestate.git
cd realestate
'''

##### 2. Create a .env File at the Project Root
'''env
DATABASE_URL=your-local-db-url
SECRET_KEY=your-secret-key
R2_ACCESS_KEY=your-access-key
R2_SECRET_KEY=your-secret-key
R2_ENDPOINT=https://your-r2-endpoint
R2_BUCKET=your-bucket-name
PUBLIC_BASE_URL=https://your-public-r2-url
EMAIL_PASSWORD=your-email-password  # For SMTP email sending
'''

Ensure .env is listed in .gitignore and .dockerignore to avoid leaking secrets.

##### 3. Build the Docker Image
'''bash
docker build -t app .
'''

##### 5. Run the Docker Container
'''bash
docker run -p 8080:8080 --env-file .env app
'''


### DEPLOYMENT STRATEGY
This staging branch uses Render’s auto-deploy feature to automatically build and deploy the website whenever code is pushed to GitHub.

### Setup Steps
1. Create a Web project on Render and name the branch.
2. Create a web service in that project.
3. Connect your GitHub repo.
4. Configure your web service:
  - Name your service
  - Select the runtime environment (Docker, Python 3, etc.)
  - If using Python 3:
    Build Command: pip install -r requirements.txt
    Start Command: gunicorn run:app
  - Choose the branch to deploy from (main or master)
  - Select your region
  - Choose your plan
  - Add required environment variables
  - Deploy the service

#### Note: If you choose Docker as your runtime environment
- Create a render.yaml file 
'''yaml
services:
  - type: web
    name: app
    env: docker
    plan: free
    autoDeploy: true
'''
5. Push Code to GitHub
  - Code is pushed to your branch
  - Render detects the change and automatically:
    - Installs dependencies by running the build command
    - Runs the start command
    - Deploys the app


###  Developer Contact
Developed and maintained by Pekim
 Email: njengapekim@gmail.com 
 Phone: +254 797933409
 GitHub: [github.com/pekimnjenga](https://github.com/pekimnjenga)

