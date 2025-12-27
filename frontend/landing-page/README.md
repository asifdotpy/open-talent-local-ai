# OpenTalent Product Showcase

This directory contains the source code for the OpenTalent product showcase landing page, a modern web application built to market the platform to recruiters and hiring managers.

## 🚀 Features
- **High-Impact Branding**: Professional aesthetic designed for the SelectUSA Tech 2026 pitch.
- **Download Center**: Direct links for Windows, macOS, and Linux installers.
- **Privacy First**: Static landing page with no tracking or cloud calls.
- **SEO Optimized**: Fully configured meta tags for social sharing and search visibility.

## 🛠️ Technology Stack
- **Framework**: React 18 + Vite
- **Styling**: TailwindCSS 3
- **Deployment**: Vercel

## 📦 Local Development

```bash
# Navigate to the directory
cd frontend/landing-page

# Install dependencies
npm install

# Start the dev server
npm run dev
```

## 🚢 Deployment (Vercel)

The site is configured for automatic deployment via Vercel.

### Deployment via REST API
For environments where the Vercel CLI is not available, we use a custom Python script:

```bash
export VERCEL_TOKEN="your_token_here"
python3 deploy_api.py
```

### Build Progress
To monitor the build status:
```bash
export VERCEL_TOKEN="your_token_here"
python3 check_status.py
```

## 📄 License
This project is licensed under the MIT License - see the root [LICENSE](../../LICENSE) file for details.
