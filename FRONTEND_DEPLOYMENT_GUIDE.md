# Frontend Deployment Guide - Mifumo SMS Integration

## 📋 Table of Contents
1. [Pre-deployment Checklist](#pre-deployment-checklist)
2. [Environment Configuration](#environment-configuration)
3. [Build Process](#build-process)
4. [Deployment Strategies](#deployment-strategies)
5. [Production Optimization](#production-optimization)
6. [Monitoring & Analytics](#monitoring--analytics)
7. [Security Considerations](#security-considerations)
8. [Troubleshooting](#troubleshooting)

---

## ✅ Pre-deployment Checklist

### Code Quality
- [ ] All tests passing (unit, integration, e2e)
- [ ] Code coverage > 80%
- [ ] No linting errors
- [ ] No console errors or warnings
- [ ] Performance budget met
- [ ] Accessibility standards met

### API Integration
- [ ] All API endpoints tested
- [ ] Error handling implemented
- [ ] Loading states added
- [ ] Offline handling configured
- [ ] Token refresh working
- [ ] Rate limiting handled

### UI/UX
- [ ] Responsive design tested
- [ ] Cross-browser compatibility
- [ ] Mobile app functionality
- [ ] User flows completed
- [ ] Error messages user-friendly
- [ ] Loading indicators present

### Security
- [ ] Sensitive data not exposed
- [ ] API keys secured
- [ ] HTTPS enforced
- [ ] Content Security Policy configured
- [ ] Input validation implemented
- [ ] XSS protection enabled

---

## 🔧 Environment Configuration

### 1. Environment Variables

#### Development (.env.development)
```env
REACT_APP_API_URL=http://localhost:8000/api
REACT_APP_WS_URL=ws://localhost:8000/ws
REACT_APP_DEBUG=true
REACT_APP_LOG_LEVEL=debug
REACT_APP_SENTRY_DSN=
REACT_APP_GOOGLE_ANALYTICS_ID=
```

#### Staging (.env.staging)
```env
REACT_APP_API_URL=https://staging-api.mifumo.com/api
REACT_APP_WS_URL=wss://staging-api.mifumo.com/ws
REACT_APP_DEBUG=false
REACT_APP_LOG_LEVEL=info
REACT_APP_SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
REACT_APP_GOOGLE_ANALYTICS_ID=GA-XXXXXXXXX
```

#### Production (.env.production)
```env
REACT_APP_API_URL=https://api.mifumo.com/api
REACT_APP_WS_URL=wss://api.mifumo.com/ws
REACT_APP_DEBUG=false
REACT_APP_LOG_LEVEL=error
REACT_APP_SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
REACT_APP_GOOGLE_ANALYTICS_ID=GA-XXXXXXXXX
REACT_APP_CDN_URL=https://cdn.mifumo.com
```

### 2. Environment-specific Configuration

```javascript
// src/config/environment.js
const config = {
  development: {
    apiUrl: process.env.REACT_APP_API_URL,
    wsUrl: process.env.REACT_APP_WS_URL,
    debug: process.env.REACT_APP_DEBUG === 'true',
    logLevel: process.env.REACT_APP_LOG_LEVEL || 'debug',
    sentryDsn: process.env.REACT_APP_SENTRY_DSN,
    analyticsId: process.env.REACT_APP_GOOGLE_ANALYTICS_ID,
  },
  staging: {
    apiUrl: process.env.REACT_APP_API_URL,
    wsUrl: process.env.REACT_APP_WS_URL,
    debug: false,
    logLevel: 'info',
    sentryDsn: process.env.REACT_APP_SENTRY_DSN,
    analyticsId: process.env.REACT_APP_GOOGLE_ANALYTICS_ID,
  },
  production: {
    apiUrl: process.env.REACT_APP_API_URL,
    wsUrl: process.env.REACT_APP_WS_URL,
    debug: false,
    logLevel: 'error',
    sentryDsn: process.env.REACT_APP_SENTRY_DSN,
    analyticsId: process.env.REACT_APP_GOOGLE_ANALYTICS_ID,
    cdnUrl: process.env.REACT_APP_CDN_URL,
  }
};

export default config[process.env.NODE_ENV] || config.development;
```

---

## 🏗️ Build Process

### 1. Build Scripts

#### package.json
```json
{
  "scripts": {
    "build": "react-scripts build",
    "build:staging": "REACT_APP_ENV=staging npm run build",
    "build:production": "REACT_APP_ENV=production npm run build",
    "build:analyze": "npm run build && npx bundle-analyzer build/static/js/*.js",
    "build:test": "npm run test -- --coverage --watchAll=false && npm run build",
    "prebuild": "npm run test -- --coverage --watchAll=false",
    "postbuild": "npm run optimize-assets"
  }
}
```

### 2. Build Optimization

#### webpack.config.js (if using custom webpack)
```javascript
const path = require('path');
const TerserPlugin = require('terser-webpack-plugin');
const CompressionPlugin = require('compression-webpack-plugin');

module.exports = {
  mode: 'production',
  optimization: {
    minimize: true,
    minimizer: [
      new TerserPlugin({
        terserOptions: {
          compress: {
            drop_console: true, // Remove console.log in production
            drop_debugger: true,
          },
        },
      }),
    ],
    splitChunks: {
      chunks: 'all',
      cacheGroups: {
        vendor: {
          test: /[\\/]node_modules[\\/]/,
          name: 'vendors',
          chunks: 'all',
        },
        common: {
          name: 'common',
          minChunks: 2,
          chunks: 'all',
          enforce: true,
        },
      },
    },
  },
  plugins: [
    new CompressionPlugin({
      algorithm: 'gzip',
      test: /\.(js|css|html|svg)$/,
      threshold: 8192,
      minRatio: 0.8,
    }),
  ],
};
```

### 3. Asset Optimization

#### optimize-assets.js
```javascript
const imagemin = require('imagemin');
const imageminMozjpeg = require('imagemin-mozjpeg');
const imageminPngquant = require('imagemin-pngquant');
const imageminSvgo = require('imagemin-svgo');

async function optimizeAssets() {
  console.log('Optimizing assets...');
  
  await imagemin(['build/static/media/*.{jpg,jpeg,png,svg}'], {
    destination: 'build/static/media/',
    plugins: [
      imageminMozjpeg({ quality: 80 }),
      imageminPngquant({ quality: [0.6, 0.8] }),
      imageminSvgo(),
    ],
  });
  
  console.log('Assets optimized!');
}

optimizeAssets().catch(console.error);
```

---

## 🚀 Deployment Strategies

### 1. Static Hosting (Netlify/Vercel)

#### Netlify Configuration
```toml
# netlify.toml
[build]
  command = "npm run build:production"
  publish = "build"

[build.environment]
  NODE_VERSION = "18"
  NPM_VERSION = "9"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200

[[headers]]
  for = "/static/*"
  [headers.values]
    Cache-Control = "public, max-age=31536000, immutable"

[[headers]]
  for = "/*.js"
  [headers.values]
    Cache-Control = "public, max-age=31536000, immutable"

[[headers]]
  for = "/*.css"
  [headers.values]
    Cache-Control = "public, max-age=31536000, immutable"
```

#### Vercel Configuration
```json
{
  "version": 2,
  "builds": [
    {
      "src": "package.json",
      "use": "@vercel/static-build",
      "config": {
        "distDir": "build"
      }
    }
  ],
  "routes": [
    {
      "src": "/static/(.*)",
      "headers": {
        "cache-control": "public, max-age=31536000, immutable"
      }
    },
    {
      "src": "/(.*)",
      "dest": "/index.html"
    }
  ]
}
```

### 2. AWS S3 + CloudFront

#### AWS CLI Deployment
```bash
#!/bin/bash
# deploy.sh

# Build the application
npm run build:production

# Sync to S3
aws s3 sync build/ s3://your-bucket-name --delete

# Invalidate CloudFront cache
aws cloudfront create-invalidation --distribution-id YOUR_DISTRIBUTION_ID --paths "/*"

echo "Deployment completed!"
```

#### CloudFront Configuration
```json
{
  "Origins": [
    {
      "DomainName": "your-bucket-name.s3.amazonaws.com",
      "Id": "S3-Origin",
      "S3OriginConfig": {
        "OriginAccessIdentity": ""
      }
    }
  ],
  "DefaultCacheBehavior": {
    "TargetOriginId": "S3-Origin",
    "ViewerProtocolPolicy": "redirect-to-https",
    "CachePolicyId": "4135ea2d-6f57-4da3-9383-8a0a1c3c4b5c",
    "Compress": true
  },
  "CacheBehaviors": [
    {
      "PathPattern": "/static/*",
      "TargetOriginId": "S3-Origin",
      "ViewerProtocolPolicy": "redirect-to-https",
      "CachePolicyId": "4135ea2d-6f57-4da3-9383-8a0a1c3c4b5c",
      "Compress": true,
      "TTL": {
        "DefaultTTL": 31536000,
        "MaxTTL": 31536000
      }
    }
  ]
}
```

### 3. Docker Deployment

#### Dockerfile
```dockerfile
# Multi-stage build
FROM node:18-alpine as build

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build:production

# Production stage
FROM nginx:alpine

# Copy built app
COPY --from=build /app/build /usr/share/nginx/html

# Copy nginx config
COPY nginx.conf /etc/nginx/nginx.conf

# Copy SSL certificates
COPY ssl/ /etc/nginx/ssl/

EXPOSE 80 443

CMD ["nginx", "-g", "daemon off;"]
```

#### nginx.conf
```nginx
events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    server {
        listen 80;
        server_name your-domain.com;
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name your-domain.com;

        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;

        root /usr/share/nginx/html;
        index index.html;

        # Cache static assets
        location /static/ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }

        # Handle client-side routing
        location / {
            try_files $uri $uri/ /index.html;
        }

        # API proxy
        location /api/ {
            proxy_pass https://api.mifumo.com;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
```

---

## ⚡ Production Optimization

### 1. Performance Optimization

#### Code Splitting
```javascript
// Lazy load components
const SMSDashboard = lazy(() => import('./components/SMSDashboard'));
const PaymentFlow = lazy(() => import('./components/PaymentFlow'));
const SenderIDManagement = lazy(() => import('./components/SenderIDManagement'));

// Route-based code splitting
const App = () => (
  <Router>
    <Suspense fallback={<LoadingSpinner />}>
      <Routes>
        <Route path="/dashboard" element={<SMSDashboard />} />
        <Route path="/payment" element={<PaymentFlow />} />
        <Route path="/sender-ids" element={<SenderIDManagement />} />
      </Routes>
    </Suspense>
  </Router>
);
```

#### Service Worker
```javascript
// public/sw.js
const CACHE_NAME = 'mifumo-sms-v1';
const urlsToCache = [
  '/',
  '/static/js/bundle.js',
  '/static/css/main.css',
  '/manifest.json'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => cache.addAll(urlsToCache))
  );
});

self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request)
      .then((response) => {
        if (response) {
          return response;
        }
        return fetch(event.request);
      })
  );
});
```

### 2. Monitoring Setup

#### Sentry Integration
```javascript
// src/sentry.js
import * as Sentry from '@sentry/react';
import { Integrations } from '@sentry/tracing';

Sentry.init({
  dsn: process.env.REACT_APP_SENTRY_DSN,
  environment: process.env.NODE_ENV,
  integrations: [
    new Integrations.BrowserTracing(),
  ],
  tracesSampleRate: process.env.NODE_ENV === 'production' ? 0.1 : 1.0,
  beforeSend(event) {
    // Filter out development errors
    if (process.env.NODE_ENV === 'development') {
      return null;
    }
    return event;
  },
});

export default Sentry;
```

#### Google Analytics
```javascript
// src/analytics.js
import ReactGA from 'react-ga4';

const GA_TRACKING_ID = process.env.REACT_APP_GOOGLE_ANALYTICS_ID;

if (GA_TRACKING_ID) {
  ReactGA.initialize(GA_TRACKING_ID);
}

export const trackEvent = (action, category, label, value) => {
  if (GA_TRACKING_ID) {
    ReactGA.event({
      action,
      category,
      label,
      value,
    });
  }
};

export const trackPage = (page) => {
  if (GA_TRACKING_ID) {
    ReactGA.send({ hitType: 'pageview', page });
  }
};
```

### 3. Error Boundary

```javascript
// src/components/ErrorBoundary.js
import React from 'react';
import * as Sentry from '@sentry/react';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    Sentry.captureException(error, {
      contexts: {
        react: {
          componentStack: errorInfo.componentStack,
        },
      },
    });
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="error-boundary">
          <h2>Something went wrong</h2>
          <p>We're sorry, but something unexpected happened.</p>
          <button onClick={() => window.location.reload()}>
            Reload Page
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
```

---

## 🔒 Security Considerations

### 1. Content Security Policy

```html
<!-- public/index.html -->
<meta http-equiv="Content-Security-Policy" content="
  default-src 'self';
  script-src 'self' 'unsafe-inline' https://www.googletagmanager.com;
  style-src 'self' 'unsafe-inline' https://fonts.googleapis.com;
  font-src 'self' https://fonts.gstatic.com;
  img-src 'self' data: https:;
  connect-src 'self' https://api.mifumo.com wss://api.mifumo.com;
  frame-ancestors 'none';
  base-uri 'self';
  form-action 'self';
">
```

### 2. Environment Variable Security

```javascript
// src/utils/security.js
export const isSecureEnvironment = () => {
  return process.env.NODE_ENV === 'production' && 
         window.location.protocol === 'https:';
};

export const validateApiUrl = (url) => {
  const allowedDomains = [
    'api.mifumo.com',
    'staging-api.mifumo.com',
    'localhost:8000'
  ];
  
  try {
    const urlObj = new URL(url);
    return allowedDomains.includes(urlObj.hostname);
  } catch {
    return false;
  }
};
```

### 3. Input Sanitization

```javascript
// src/utils/sanitization.js
import DOMPurify from 'dompurify';

export const sanitizeInput = (input) => {
  if (typeof input === 'string') {
    return DOMPurify.sanitize(input);
  }
  return input;
};

export const validatePhoneNumber = (phone) => {
  const phoneRegex = /^(\+255|0)[0-9]{9}$/;
  return phoneRegex.test(phone);
};

export const validateEmail = (email) => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};
```

---

## 📊 Monitoring & Analytics

### 1. Performance Monitoring

```javascript
// src/utils/performance.js
export const measurePerformance = (name, fn) => {
  const start = performance.now();
  const result = fn();
  const end = performance.now();
  
  console.log(`${name} took ${end - start} milliseconds`);
  
  // Send to analytics
  if (window.gtag) {
    window.gtag('event', 'timing_complete', {
      name: name,
      value: Math.round(end - start)
    });
  }
  
  return result;
};

export const measureApiCall = async (apiCall, endpoint) => {
  const start = performance.now();
  try {
    const result = await apiCall();
    const end = performance.now();
    
    // Track successful API calls
    trackEvent('api_call_success', 'performance', endpoint, Math.round(end - start));
    
    return result;
  } catch (error) {
    const end = performance.now();
    
    // Track failed API calls
    trackEvent('api_call_error', 'performance', endpoint, Math.round(end - start));
    
    throw error;
  }
};
```

### 2. User Analytics

```javascript
// src/utils/analytics.js
export const trackUserAction = (action, category, label, value) => {
  // Google Analytics
  if (window.gtag) {
    window.gtag('event', action, {
      event_category: category,
      event_label: label,
      value: value
    });
  }
  
  // Custom analytics
  if (window.analytics) {
    window.analytics.track(action, {
      category,
      label,
      value
    });
  }
};

export const trackSMSAction = (action, details) => {
  trackUserAction(action, 'sms', details.sender_id, details.recipients_count);
};

export const trackPaymentAction = (action, details) => {
  trackUserAction(action, 'payment', details.provider, details.amount);
};
```

---

## 🐛 Troubleshooting

### 1. Common Issues

#### Build Failures
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
npm run build

# Check for TypeScript errors
npm run type-check

# Check for linting errors
npm run lint
```

#### API Connection Issues
```javascript
// Debug API connection
const debugApiConnection = async () => {
  try {
    const response = await fetch(`${process.env.REACT_APP_API_URL}/health/`);
    console.log('API Health:', response.status);
  } catch (error) {
    console.error('API Connection Error:', error);
  }
};
```

#### Memory Issues
```javascript
// Monitor memory usage
const monitorMemory = () => {
  if (performance.memory) {
    console.log('Memory Usage:', {
      used: Math.round(performance.memory.usedJSHeapSize / 1024 / 1024) + ' MB',
      total: Math.round(performance.memory.totalJSHeapSize / 1024 / 1024) + ' MB',
      limit: Math.round(performance.memory.jsHeapSizeLimit / 1024 / 1024) + ' MB'
    });
  }
};

// Run every 30 seconds
setInterval(monitorMemory, 30000);
```

### 2. Debug Tools

#### Development Tools
```javascript
// src/utils/debug.js
export const debugLog = (message, data) => {
  if (process.env.NODE_ENV === 'development') {
    console.log(`[DEBUG] ${message}`, data);
  }
};

export const debugApiCall = (endpoint, method, data) => {
  debugLog(`API Call: ${method} ${endpoint}`, data);
};

export const debugError = (error, context) => {
  console.error(`[ERROR] ${context}:`, error);
  
  // Send to error tracking
  if (window.Sentry) {
    window.Sentry.captureException(error, { tags: { context } });
  }
};
```

---

## 📋 Deployment Checklist

### Pre-deployment
- [ ] All tests passing
- [ ] Build successful
- [ ] Environment variables configured
- [ ] Security headers set
- [ ] Performance budget met
- [ ] Accessibility tested

### Post-deployment
- [ ] Application loads correctly
- [ ] API connections working
- [ ] Authentication working
- [ ] SMS sending functional
- [ ] Payment flow working
- [ ] Error tracking active
- [ ] Analytics tracking
- [ ] Performance monitoring

### Rollback Plan
- [ ] Previous version available
- [ ] Database migrations reversible
- [ ] Feature flags configured
- [ ] Monitoring alerts set
- [ ] Rollback procedure documented

---

*Last updated: January 2024*
