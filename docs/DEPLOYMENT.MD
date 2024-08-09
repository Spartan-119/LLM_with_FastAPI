Deployment Instructions for LLM Hub
===================================

This document outlines the step-by-step process to deploy the LLM Hub application.
Please follow these instructions carefully to ensure a smooth deployment.

Prerequisites
-------------
- `Git` installed on your server
- `Docker` and `Docker Compose` installed on your server
- `Make` utility installed
- Access to your server via SSH

Deployment Steps
----------------

1. Commit to Version Control System (VCS)
-----------------------------------------
Before deploying, ensure all your changes are committed to your version control
system (e.g., Git).

git add .
git commit -m "Prepare for deployment"
git push origin main  # or your deployment branch


2. Pull Latest Changes
----------------------
SSH into your server and navigate to your project directory. Then pull the
latest changes:

cd /path/to/llm_hub
git pull origin main  # or your deployment branch


3. Create .env File
-------------------
Create a .env file in the project root if it doesn't exist already. This file
should contain all necessary environment variables:

cp .sample.env .env
nano .env  # or use your preferred text editor

Fill in all required environment variables, such as:

POSTGRES_USER=your_db_user
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=llm_hub
OLLAMA_KEEP_ALIVE=24h
OLLAMA_HOST=0.0.0.0
PGADMIN_DEFAULT_EMAIL=your_email@example.com
PGADMIN_DEFAULT_PASSWORD=your_secure_password
DEBUG=False
JWT_SECRET_KEY=your_very_secure_random_string
INITIAL_ADMIN_USERNAME=admin
INITIAL_ADMIN_PASSWORD=your_secure_admin_password

Ensure all passwords and secret keys are strong and unique.


4. Build Docker Images
----------------------
Run the following command to build your Docker images:

make build

This command will build all necessary Docker images based on your Dockerfile
and docker-compose.yml.


5. Start the Application
------------------------
Launch your application using Docker Compose:

make up

This command starts all services defined in your docker-compose.yml file.


6. Apply Database Migrations
----------------------------
Run database migrations to ensure your database schema is up to date:

make apply-migrations

This command applies any pending Alembic migrations to your database.


7. Create Initial Admin User
----------------------------
Create the initial admin user for the application:

make create-initial-user

This command runs a script to create an admin user based on the credentials
specified in your .env file.


8. Configure Reverse Proxy
--------------------------
You have two options for setting up a reverse proxy: Cloudflare Tunnels or Nginx.

Option A: Cloudflare Tunnels
----------------------------
If you choose to use Cloudflare Tunnels, follow the Cloudflare documentation to
set up a tunnel pointing to your application's port (default is 8010).

Option B: Nginx Configuration
-----------------------------
If you prefer to use Nginx, here's a sample configuration:

1. Install Nginx if not already installed:

sudo apt update
sudo apt install nginx

2. Create a new Nginx configuration file:

sudo nano /etc/nginx/sites-available/llm_hub

3. Add the following configuration (adjust as needed):

server {
    listen 80;
    server_name your_domain.com;

    location / {
        proxy_pass http://localhost:8010;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

4. Create a symbolic link to enable the site:

sudo ln -s /etc/nginx/sites-available/llm_hub /etc/nginx/sites-enabled/

5. Test Nginx configuration:

sudo nginx -t

6. If the test is successful, restart Nginx:

sudo systemctl restart nginx

7. (Optional) Set up SSL with Let's Encrypt:

sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your_domain.com

Follow the prompts to complete the SSL setup.


Post-Deployment
---------------
After completing these steps, your LLM Hub should be deployed and accessible.
Be sure to:

- Test the application thoroughly to ensure all features are working as expected.
- Monitor the logs for any errors or issues:
  make logs
- Set up regular backups of your database and any critical data.
