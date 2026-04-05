### Table of Contents
- [NAME OF THE WEBSITE](#name-of-the-website)
- [BRANCH](#branch)
- [PROJECT'S BRIEF DESCRIPTION](#projects-brief-description)
- [Live website](#live-website)
- [Site Architecture(same as the master branch)](#site-architecturesame-as-the-master-branch)
  - [User Interface](#user-interface)
  - [Admin Interface](#admin-interface)
- [Tech stack](#tech-stack)
  - [Backend](#backend)
  - [Frontend](#frontend)
  - [JavaScript / Client libraries](#javascript-client-libraries)
  - [Email Service](#email-service)
  - [Text Editor](#text-editor)
  - [Cloud Storage](#cloud-storage)
  - [Database](#database)
  - [Deployment](#deployment)
  - [CI/CD Automation](#cicd-automation)
  - [Caching & Performance](#caching-performance)
  - [Security & Moderation](#security-moderation)
  - [Version Control](#version-control)
- [SETUP AND INSTALLATION INSTRUCTIONS](#setup-and-installation-instructions)
- [DEPLOYMENT STRATEGY](#deployment-strategy)
  - [Production Deployment via GitHub Actions](#production-deployment-via-github-actions)
    - [Setup](#setup)
    - [Python App Configuration on Truehost](#python-app-configuration-on-truehost)
    - [Deployment Flow](#deployment-flow)
- [Tailwind (binary) — build instructions](#tailwind-binary-build-instructions)
- [Search Engine Optimization (SEO)](#search-engine-optimization-seo)
  - [Strategy Overview](#strategy-overview)
- [Future improvements](#future-improvements)
- [Acknowledgements](#acknowledgements)
- [Developer Contact](#developer-contact)

**This branch mirrors the master branch in functionality, with two key differences: it uses a different deployment method and includes SEO enhancements. In this branch, the website and database are hosted on Truehost for production.**

### NAME OF THE WEBSITE 
ilikeitproperties

### Project Status
![Production Status](https://img.shields.io/badge/status-production-green)
[![CI Checks (main)](https://github.com/pekimnjenga/realestate/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/pekimnjenga/realestate/actions/workflows/ci.yml)
[![Deploy to Truehost (main)](https://github.com/pekimnjenga/realestate/actions/workflows/deploy.yml/badge.svg?branch=main)](https://github.com/pekimnjenga/realestate/actions/workflows/deploy.yml)
![Pre-commit Hook Enabled](https://img.shields.io/badge/pre--commit-enabled-brightgreen)

<!-- Tooling badges -->
![Tests](https://img.shields.io/badge/tests-pytest-5A43D6?logo=pytest)
![Type checking](https://img.shields.io/badge/type--check-mypy-4B8BBE)
![Linter](https://img.shields.io/badge/lint-ruff-black)

### Tech Stack
![Python Version](https://img.shields.io/badge/Python-3.9%2B-blue)
![Flask Framework](https://img.shields.io/badge/framework-Flask-blue)
![Tailwind CSS](https://img.shields.io/badge/CSS-Tailwind-06B6D4?logo=tailwindcss&logoColor=white)
![Quill.js Editor](https://img.shields.io/badge/editor-Quill.js-1f8f2f?logo=quill)
![Docker Ready](https://img.shields.io/badge/docker-ready-blue)

### Infrastructure & Automation
![Truehost Deployment](https://img.shields.io/badge/deployment-Truehost-red)
![PostgreSQL Database](https://img.shields.io/badge/database-PostgreSQL-blue)
![Cloudflare R2 Storage](https://img.shields.io/badge/storage-Cloudflare_R2-orange)
![GitHub Actions CI/CD](https://img.shields.io/badge/CI/CD-GitHub_Actions-blue)

### Optimization & Licensing
![SEO Optimized](https://img.shields.io/badge/SEO-optimized-brightgreen)
![MIT License](https://img.shields.io/github/license/pekimnjenga/realestate)


### BRANCH 
main(Production)

### PROJECT'S BRIEF DESCRIPTION
A dynamic, SEO-optimized real estate website built with Flask, Javascript, HTML, CSS, and Tailwind CSS, designed to showcase property listings and blog posts and also for users to make inquiries about the listings, while enabling users to make inquiries directly via WhatsApp or a contact form.

Upon submitting an inquiry through the contact form, users automatically receive a confirmation email — ensuring a seamless and professional communication experience.

### Live website
[I Like It Properties](https://ilikeitproperties.co.ke)

#### Site Architecture(same as the master branch)
##### User Interface
Public-facing pages for:
  - Browsing property listings
  - Reading blog posts and adding comments
  - Learning about the company
  - Making inquiries via WhatsApp or contact form

##### Admin Interface
Secure backend for:
  - Managing property listings and blogs
  - Streamlining content workflows


### Tech stack
#### Backend
- Flask — lightweight Python framework powering routing, logic, and server-side rendering

#### Frontend
- HTML and Tailwind CSS — responsive layout and utility-first styling

#### JavaScript / Client libraries
- Quill.js — rich-text editor used in admin for blog creation and editing
- Swiper — carousel/slider used on the homepage and listing previews
- AOS — scroll reveal animations used across the site
- Turbo (Hotwire) — fast navigation for in-page transitions
- instant.page — link prefetching on hover to speed up navigations

#### Email Service
- SMTP integration using Python’s smtplib and email libraries — handles automated inquiry responses via the contact form

#### Text Editor
- Quill.js — rich text editor for blog post creation, supporting headings, formatting, lists, and embedded HTML content

#### Cloud Storage
- Cloudflare R2 — hosts public assets including images and static files
  
- `boto3` is used in `app/utils/r2_upload.py` to upload and delete objects from R2.

#### Database
- PostgreSQL hosted on Truehost — stores listings, blog content, and admin data

#### Deployment
- Truehost Server — production hosting environment for the live website

#### CI/CD Automation
- **CI Automation**: GitHub Actions for automated tests and code quality checks. On every push or pull request, the following checks run automatically via `.github/workflows/ci.yml`:

  - `Ruff` — high-performance linter and formatter (replaces Black, Isort, and Flake8)
  - `Mypy` — static type checking for Python
  - `pytest` — runs automated tests to verify the functionality of routes, models, utility functions (like upload_to_r2 function), and the contact form.
- **CD Automation**: The project gets automatically deployed to Truehost after passing all testing and quality checks through Github actions.

### Caching & Performance
- Template fragment caching is used via Flask-Caching and the `@cache.cached` decorator for anonymous users to improve response times.
- Development uses `SimpleCache` (configured via `CACHE_TYPE=SimpleCache` in `config.py`) which is in-memory and suitable for single-process development only.
- For production, configure a shared cache backend (Redis or Memcached) and update `CACHE_TYPE` accordingly to ensure cache is shared across worker processes.
- Performance improvements implemented in the templates include preconnecting to Cloudflare R2, `rel="preload"` for hero images, `fetchpriority="high"`, and `decoding="async"` on critical images to improve LCP.

### Security & Moderation
- CSRF protection is enabled via Flask's CSRF extension (`csrf` in `app/extensions.py`).
- Rate limiting is enforced with `Flask-Limiter` to protect high-risk endpoints (e.g., comment submission) — limits are applied using decorator rules.
- Comment moderation uses `better_profanity` to filter disallowed words before saving or displaying comments.
- Server-side validation is performed on form inputs and emails; email verification tokens are implemented for comment verification endpoints.

#### Version Control
- GitHub — source code management and collaboration

### SETUP AND INSTALLATION INSTRUCTIONS
Setup and installation instructions are maintained in the [master branch README](https://github.com/pekimnjenga/realestate/blob/master/README.md#setup-and-installation-instructions).

Please refer to it for:

- Local and Docker-based setup steps  
- Environment configuration  
- Database migration commands  
- Quill.js integration  
- Automated tests and pre-commit hook setup


### DEPLOYMENT STRATEGY
Unlike the staging branch (which uses Render’s auto-deploy), I manually configured the production branch to deploy to Truehost using GitHub Actions each time a push is made.

### Production Deployment via GitHub Actions
#### Setup
- Create a .github/workflows/deploy.yml
- Log in to cPanel and create an FTP account
- Add FTP credentials to GitHub Secrets i.e FTP_HOST, FTP_USER , FTP_PASS
- Define the branch to be deployed from, local/server directories and exclusions in the deploy.yml file
#### Python App Configuration on Truehost
- Create a Python application in cPanel
- Set:
  Application Root
  Application URL
  Startup File eg run.py
  Entry Point for eg app
- Add environment variables (e.g. DATABASE_URL, R2_ACCESS_KEY, etc.)

#### Deployment Flow
- Push to main triggers GitHub Actions
- Code is deployed to Truehost via FTP
- Install the dependencies on cPanel's terminal
- Restart the application
- The app now runs live on production domain

## Tailwind (binary) — build instructions

This project uses the standalone `tailwindcss` CLI binary. Two common local workflows are supported:

- Windows PowerShell (when `tailwindcss.exe` is present in repo root):

```powershell
# from repo root
.\tailwindcss.exe -i .\app\static\css\input.css -o .\app\static\css\output.css --content "./app/templates/**/*.html" "./app/**/*.py" "./app/static/js/**/*.js" --minify
```

- macOS / Linux (when `tailwindcss` binary is available):

```bash
# from repo root
./tailwindcss -i ./app/static/css/input.css -o ./app/static/css/output.css --content "./app/templates/**/*.html" "./app/**/*.py" "./app/static/js/**/*.js" --minify
```

CI builds: The included `.github/workflows/build-tailwind.yml` will use a bundled `tailwindcss` binary if present in the repository root; otherwise it downloads the appropriate binary for the runner and builds `app/static/css/output.css`.

Notes:
- To avoid committing the binary, add `tailwindcss` / `tailwindcss.exe` to `.gitignore` and rely on CI downloads.
- If you need PostCSS plugins (autoprefixer, cssnano), switch to an npm/PostCSS workflow.

If you plan to commit the `tailwindcss` binary to this repository (recommended only if you want deterministic local builds):

- Add the binary to the repository root (e.g. `tailwindcss` or `tailwindcss.exe`).
- On macOS / Linux set the executable bit before committing:

```bash
chmod +x ./tailwindcss
git add ./tailwindcss
git commit -m "Add Tailwind CLI binary"
```

- CI will automatically use the bundled binary if present; no additional changes are required.

- To later stop committing the binary, add `tailwindcss` and `tailwindcss.exe` to `.gitignore` and remove the file from the repo (`git rm --cached tailwindcss`).

## Local dev & common commands

- Create and activate a virtual environment and install dependencies:

```bash
python -m venv .venv
# macOS / Linux
source .venv/bin/activate
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

- Run tests and static checks:

```bash
pytest -q
mypy .
ruff check . --fix
pre-commit run --all-files
```


### Search Engine Optimization (SEO)
The site is strategically optimized for search engine visibility and brand authority, with a focus on indexing only the homepage for clean, branded search results.

#### Strategy Overview
- Selective Indexing – Only the homepage is indexed; all other routes (/about, /listings, /blogs, /contact) are crawlable but excluded from search results using noindex, follow directives
- Canonical Tag Logic – Each route declares its own canonical URL to prevent duplicate content and reinforce page identity
- Structured Data (Schema Markup) – JSON-LD schema for RealEstateAgent includes logo, address, contact info, and business description for rich search previews
- Open Graph & Twitter Cards – Social media previews are enhanced with custom titles, descriptions, and branded imagery
- Favicon & Apple Touch Icon – Branded tab icon and mobile bookmark visibility for consistent identity across platforms
- Sitemap Management – A clean sitemap.xml submitted to Google Search Console includes only the homepage, reinforcing the selective indexing strategy

### Future improvements
- **Indexing dynamic routes**: Index the listings and blog routes
- **AI Chatbot Integration**: Implement a conversational AI assistant to handle customer inquiries, guide users through listings, and provide instant support.
- **Enhanced UI/UX Design**: Refine layout, typography, and responsiveness to deliver a more intuitive and visually appealing user experience across devices.
- **Search & Filter Improvements**: Add advanced filters for price, location, property type, and availability.

### Acknowledgements
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Tailwind CSS](https://tailwindcss.com/)
- [Truehost](https://truehost.co.ke)
- [pre-commit](https://pre-commit.com/)
- [Github](https://github.com)
- [Quill.js](https://quilljs.com)
 - [boto3 (Cloud SDK)](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
 - [Flask-Limiter](https://flask-limiter.readthedocs.io/)
 - [better_profanity](https://pypi.org/project/better-profanity/)
 - [Swiper](https://swiperjs.com/)
 - [AOS](https://michalsnik.github.io/aos/)
 - [Turbo (Hotwire)](https://turbo.hotwired.dev/)
 - [instant.page](https://instant.page/)

### Developer Contact
Developed and maintained by Pekim
 - Email: njengapekim@gmail.com 
 - Phone: +254 797933409
 - GitHub: [github.com/pekimnjenga](https://github.com/pekimnjenga)




