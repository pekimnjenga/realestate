### Table of Contents
- [NAME OF THE WEBSITE](#name-of-the-website)
- [BRANCH](#branch)
- [BRIEF DESCRIPTION](#brief-description)
  - [Site Architecture](#site-architecture)
    - [User Interface](#user-interface)
    - [Admin Interface](#admin-interface)
- [Tech Stack](#tech-stack)
  - [Backend](#backend)
  - [Frontend](#frontend)
  - [Text Editor](#text-editor)
  - [Email Service](#email-service)
  - [Cloud Storage](#cloud-storage)
  - [Deployment](#deployment)
  - [CI/CD integration](#cicd-integration)
  - [Version Control](#version-control)
- [SETUP AND INSTALLATION INSTRUCTIONS](#setup-and-installation-instructions)
  - [(a) Local Setup](#a-local-setup)
  - [(b) Docker-based setup](#b-docker-based-setup)
- [Quill.js Integration](#quilljs-integration)
- [Pre-commit Hooks & automated tests](#pre-commit-hooks--automated-tests)
- [Test Coverage](#test-coverage)
- [DEPLOYMENT STRATEGY](#deployment-strategy)
  - [Setup Steps](#setup-steps)
- [Future improvements](#future-improvements)
- [Contributing](#contributing)
- [Acknowledgements](#acknowledgements)
- [Developer Contact](#developer-contact)


### NAME OF THE WEBSITE 
ilikeitproperties

### Project Status
![Staging Status](https://img.shields.io/badge/Status-Staging-yellow)
[![CI Status](https://img.shields.io/github/actions/workflow/status/pekimnjenga/realestate/ci.yml?branch=master)](https://github.com/pekimnjenga/realestate/actions)
![Pre-commit Hooks](https://img.shields.io/badge/Pre--commit-Hooks-brightgreen)
![CI/CD Pipeline](https://img.shields.io/badge/CI/CD-GitHub_Actions-blue)

### Tech Stack
![Python Version](https://img.shields.io/badge/Python-3.9%2B-blue)
![Flask Framework](https://img.shields.io/badge/Framework-Flask-lightgrey)
![Bootstrap UI](https://img.shields.io/badge/UI-Bootstrap%205-purple)
![Quill.js Editor](https://img.shields.io/badge/Editor-Quill.js-1f8f2f?logo=quill)
![Docker Ready](https://img.shields.io/badge/Docker-Ready-blue)

### Infrastructure
![Neon PostgreSQL](https://img.shields.io/badge/Database-Neon%20PostgreSQL-lightgrey)
![Cloudflare R2 Storage](https://img.shields.io/badge/Storage-Cloudflare%20R2-orange)
![Email Service](https://img.shields.io/badge/Email-SMTP%20Enabled-green)
![Deployed to Render](https://img.shields.io/badge/Deployed%20to-Render-blue)

### License
![License](https://img.shields.io/github/license/pekimnjenga/realestate)



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
#### Backend
- **Framework** - Flask — lightweight Python framework powering the core logic and routing
- **Database** — Neon — managed PostgreSQL database for listings, blogs, and admin data

#### Frontend
- HTML, CSS, and Bootstrap 5 — responsive layout and UI styling

#### Text Editor
- Quill.js — rich text editor for blog post creation, supporting headings, formatting, lists, and embedded HTML content. For integration, here are the [steps](#quilljs-integration)

#### Email Service
- SMTP integration using Python's smtplib and email libraries — for automated inquiry responses

#### Cloud Storage
- Cloudflare R2 — hosting public assets like images and static files
  
#### Deployment
- Render — staging environment with auto-deploy from GitHub

#### CI/CD integration
- **CI Automation**: GitHub Actions for automated tests and code quality checks. On every push or pull request, the following checks run automatically via `.github/workflows/ci.yml`:
  - `black` — ensures consistent code formatting
  - `isort` — enforces import order
  - `flake8` — flags style and syntax issues
  - `pytest` — runs automated tests to verify the functionality of routes, models, utility functions (like upload_to_r2 function), and the contact form.
- **CD Automation**: The project gets automatically deployed to Render after passing all testing and quality checks.

#### Version Control
- **GitHub**: Source code management and collaboration


### SETUP AND INSTALLATION INSTRUCTIONS
#### (a) Local Setup
##### 1. Clone the repo
```bash
git clone https://github.com/pekimnjenga/realestate.git
cd realestate
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

##### 5.Run migrations
```bash
flask db migrate -m "Describe your change"  #Only if you have modified the models
flask db upgrade
```
##### 6. Run the application
##### Linux/macOS
```bash
python3 run.py
```

##### Windows (PowerShell or CMD)
```bash
python run.py
```

#### (b) Docker-based setup
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

##### 4. Running migrations
```bash
docker run --env-file .env app flask db migrate -m "Describe your change"  #If you have modified the models
docker run --env-file .env app flask db upgrade
```

##### 5. Run the Docker Container
```bash
docker run -p 8080:8080 --env-file .env app
```

### Quill.js Integration
- This project uses [Quill.js](https://quilljs.com) to provide a rich text editing experience for blog post creation.

#### Setup steps
1. Include Quill in your base template
```bash
<!-- Quill Styles -->
<link href="https://cdn.quilljs.com/1.3.6/quill.snow.css" rel="stylesheet">

<!-- Quill Scripts -->
<script src="https://cdn.quilljs.com/1.3.6/quill.min.js"></script>
```
2. Add the editor container in your form
```bash
<div id="editor" style="height: 300px;"></div>
<input type="hidden" name="content" id="content">
```
3. Initialize Quill in the body tag of your base template
```bash
<script>
  var quill = new Quill('#editor', {
    theme: 'snow',
    modules: {
      toolbar: [
        [{ header: [1, 2, 3, false] }],
        ['bold', 'italic', 'underline'],
        ['link', 'blockquote', 'code-block'],
        [{ list: 'ordered' }, { list: 'bullet' }],
        ['clean']
      ]
    }
  });

  // Copy HTML content to hidden input on form submit
  document.querySelector('form').addEventListener('submit', function () {
    document.querySelector('#content').value = quill.root.innerHTML;
  });
</script>
```

### Pre-commit Hooks & automated tests
This project uses [pre-commit](https://pre-commit.com/) to enforce code quality and security checks before each commit.
1. Install Pre-commit
```bash
pip install pre-commit
```
2. Install the Git Hooks
```bash
pre-commit install
```
3. Configure .pre-commit-config.yml
```bash
repos:
  - repo: https://github.com/psf/black
    rev: 25.9.0
    hooks:
      - id: black
        args: [--check]

  - repo: https://github.com/PyCQA/flake8
    rev: 7.3.0
    hooks:
      - id: flake8

  - repo: https://github.com/pre-commit/mirrors-isort
    rev: v5.10.1
    hooks:
      - id: isort
        args: [--check-only]
```
4. Run the pre-commit hook and tests
```bash
pre-commit run --all-files
PYTHONPATH=. pytest #Runs tests from the root directory
```

### Test Coverage
This project includes automated tests written with `pytest` to ensure correctness across:

- Contact form validation and email logic
- Model integrity for Listings and Blogs
- Route accessibility and dynamic content rendering
- Utility functions like `upload_to_r2`

Tests run automatically via GitHub Actions and can be triggered locally with:

```bash
PYTHONPATH=. pytest
```

### DEPLOYMENT STRATEGY
This staging branch uses Render’s auto-deploy feature to automatically build and deploy the website whenever code is pushed to GitHub.

#### Setup Steps
1. Create a Web project on Render and name the branch.
2. Create a web service in that project.
3. Connect your GitHub repo.
4. Configure your web service:
  - Name your service
  - Select the runtime environment (Docker, Python 3, etc.)
  - If using Python 3:
    Build Command: pip install -r requirements.txt
    Start Command: flask db upgrade && gunicorn run:app
  - Choose the branch to deploy from (main or master)
  - Select your region
  - Choose your plan
  - Add required environment variables
  - Deploy the service

**Note**: If you choose Docker as your runtime environment
- Create a render.yaml file
```yaml
services:
  - type: web
    name: app
    env: docker
    plan: free
    autoDeploy: true
```
5. Push Code to GitHub
   Code is pushed to your branch
   Render detects the change and automatically:
   - Installs dependencies by running the build command
   - Runs the start command
   - Deploys the app


### Future improvements
- **AI Chatbot Integration**: Implement a conversational AI assistant to handle customer inquiries, guide users through listings, and provide instant support.
- **Enhanced UI/UX Design**: Refine layout, typography, and responsiveness to deliver a more intuitive and visually appealing user experience across devices.
- **Search & Filter Improvements**: Add advanced filters for price, location, property type, and availability.


### Contributing
Contributions are welcome. To contribute:
1. Fork the Repository
2. Clone Your Fork Locally
```bash
git clone https://github.com/yourusername/realestate.git
cd realestate
```
3. Create a Feature Branch
```bash
git checkout -b feature/your-feature-name
```
4. Make Your Changes
   Write clean, well-documented code
   Follow PEP 8 style guide
   Run pre-commit hooks and tests before committing
   ```bash
   pre-commit run --all-files && pytest
   ```

5. Commit your changes
```bash
git commit -m "Add: Brief description of your changes"
```
6. Push to your fork
```bash
git push origin feature/your-feature-name
```
7. Open a Pull Request targeting my master branch, i.e base branch should be **pekimnjenga/realestate:master** , submit and wait for review


### Acknowledgements
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Bootstrap 5](https://getbootstrap.com/)
- [Neon](https://neon.com/)
- [Render](https://render.com/)
- [pre-commit](https://pre-commit.com/)
- [Github](https://github.com)
- [Quill.js](https://quilljs.com)

###  Developer Contact
Developed and maintained by Pekim
 - Email: njengapekim@gmail.com 
 - Phone: +254 797933409
 - GitHub: [github.com/pekimnjenga](https://github.com/pekimnjenga)

