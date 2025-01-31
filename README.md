# VoucherHub - Flask E-Commerce Application

VoucherHub is a Flask-based e-commerce platform enabling users to discover deals, complete purchases, and manage orders. This document provides comprehensive guidance for local setup and MySQL database integration.

**Note: Admin Role has to be manually edit on Workbench to role "admin"**

---

## 🛠 Prerequisites

### **System Requirements**
- **Python 3.8+**
- **MySQL Server 8.0+** (with MySQL Workbench)
- **Pip** (Python Package Manager)

### **Python Dependencies**
All required packages are listed in `requirements.txt`.

---

## 💻 Local Development Setup

### **1. Clone the Repository**
```bash
git clone https://github.com/Amabellzq/INF2006_Group24.git
```
### **Install Dependencies**
Open your IDE terminal on your project's root directory
```bash
pip install -r requirements.txt
```

### Database Configuration
1. MySQL Setup
Install MySQL Server and MySQL Workbench.

Start MySQL Server.

2. Create Database
Open MySQL Workbench.

Connect to your local MySQL instance.

Execute the following SQL command:
```bash
CREATE DATABASE voucherhub;
```
### Environment Configuration
Place the .env on project's root directory
```bash
# Database Configuration
DB_USER=root
DB_PASSWORD=your_password_that_you_set_on_your_localhostMYSQL
DB_HOST=127.0.0.1
DB_PORT=port_number_that_you_set_for_your_localhostMYSQL
DB_NAME=voucherhub

# Flask Configuration
SECRET_KEY=your_secret_key_here
FLASK_DEBUG=True
CORS_ORIGINS=http://localhost:5000

# MySQL Configuration
MYSQL_DATABASE_CHARSET=utf8mb4
```

###  Migrations
Initialize & Apply Database Schema
Run these commands sequentially:
```bash
# Initialize migration directory
flask db init

# Generate migration script
flask db migrate -m "Initial migration"

# Apply migrations to the database
flask db upgrade
```

### Launching the Application
Start Flask Development Server
```bash
flask run
```
Access the application at:
http://127.0.0.1:5000/
