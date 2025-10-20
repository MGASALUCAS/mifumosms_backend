# SSL Configuration for Nginx

## 1. Install Certbot (Let's Encrypt)
sudo apt update
sudo apt install certbot python3-certbot-nginx

## 2. Get SSL Certificate
sudo certbot --nginx -d yourdomain.com -d api.yourdomain.com

## 3. Update Nginx Configuration
# /etc/nginx/sites-available/mifumosms
server {
    listen 80;
    server_name 104.131.116.55 https://104.131.116.55 yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name 104.131.116.55 https://104.131.116.55 yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    
    # SSL Security Headers
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

## 4. Test and Reload
sudo nginx -t
sudo systemctl reload nginx

## 5. Update Frontend API Base URL
# Change from: http://104.131.116.55/api/
# Change to:   https://104.131.116.55/api/ (or https://yourdomain.com/api/)
