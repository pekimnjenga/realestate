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
  - [Email Service](#email-service)
  - [Text Editor](#text-editor)
  - [Cloud Storage](#cloud-storage)
  - [Database](#database)
  - [Deployment](#deployment)
  - [CI/CD Automation](#cicd-automation)
  - [Version Control](#version-control)
- [SETUP AND INSTALLATION INSTRUCTIONS](#setup-and-installation-instructions)
- [DEPLOYMENT STRATEGY](#deployment-strategy)
  - [Production Deployment via GitHub Actions](#production-deployment-via-github-actions)
    - [Setup](#setup)
    - [Python App Configuration on Truehost](#python-app-configuration-on-truehost)
    - [Deployment Flow](#deployment-flow)
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

### Tech Stack
![Python Version](https://img.shields.io/badge/Python-3.9%2B-blue)
![Flask Framework](https://img.shields.io/badge/framework-Flask-blue)
![Bootstrap 5](https://img.shields.io/badge/UI-Bootstrap_5-purple)
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
A dynamic, SEO-optimized real estate website built with Flask, HTML, Bootstrap 5 classes and CSS, designed to showcase property listings and blog posts and also for users to make inquiries about the listings, while enabling users to make inquiries directly via WhatsApp or a contact form.

Upon submitting an inquiry through the contact form, users automatically receive a confirmation email — ensuring a seamless and professional communication experience.

### Live website
[I Like It Properties](https://ilikeitproperties.co.ke)

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
#### Backend
- Flask — lightweight Python framework powering routing, logic, and server-side rendering

#### Frontend
- HTML, CSS, and Bootstrap 5 — responsive layout, UI components, and styling

#### Email Service
- SMTP integration using Python’s smtplib and email libraries — handles automated inquiry responses via the contact form

#### Text Editor
- Quill.js — rich text editor for blog post creation, supporting headings, formatting, lists, and embedded HTML content

#### Cloud Storage
- Cloudflare R2 — hosts public assets including images and static files

#### Database
- PostgreSQL hosted on Truehost — stores listings, blog content, and admin data

#### Deployment
- Truehost Server — production hosting environment for the live website

#### CI/CD Automation
- **CI Automation**: GitHub Actions for automated tests and code quality checks. On every push or pull request, the following checks run automatically via `.github/workflows/ci.yml`:
  - `black` — ensures consistent code formatting
  - `isort` — enforces import order
  - `flake8` — flags style and syntax issues
  - `pytest` — runs automated tests to verify the functionality of routes, models, utility functions (like upload_to_r2 function), and the contact form.
- **CD Automation**: The project gets automatically deployed to Truehost after passing all testing and quality checks through Github actions.

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
- [Bootstrap 5](https://getbootstrap.com/)
- [Truehost](https://truehost.co.ke)
- [pre-commit](https://pre-commit.com/)
- [Github](https://github.com)
- [Quill.js](https://quilljs.com)

### Developer Contact
Developed and maintained by Pekim
 - Email: njengapekim@gmail.com 
 - Phone: +254 797933409
 - GitHub: [github.com/pekimnjenga](https://github.com/pekimnjenga)


