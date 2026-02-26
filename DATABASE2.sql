-- =============================================
-- Janet's Quality Catering - Database Schema
-- FIXED VERSION: Lahat ng columns tugma na sa models.py at app.py
-- =============================================

-- 1. Create Database
CREATE DATABASE IF NOT EXISTS cateringinventory;
USE cateringinventory;

-- 2. Users Table (Para sa Login at Roles)
CREATE TABLE IF NOT EXISTS users (
    id VARCHAR(36) PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(100) NOT NULL,
    role VARCHAR(20) DEFAULT 'ADMIN' -- 'ADMIN' (Read-only) o 'OWNER' (CRUD)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 3. Categories Table (Para sa Inventory Classification)
CREATE TABLE IF NOT EXISTS categories (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    category_name VARCHAR(100) UNIQUE NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 4. Inventory Table (Stock Monitoring)
CREATE TABLE IF NOT EXISTS inventory (
    item_id VARCHAR(36) PRIMARY KEY,
    category_id INT,
    item_name VARCHAR(255) NOT NULL,
    beginning_qty INT DEFAULT 0,
    previous_qty INT DEFAULT 0,
    extra_qty INT DEFAULT 0,
    ending_qty INT DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (category_id) REFERENCES categories(category_id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 5. Events Table (FIXED: Idinagdag lahat ng missing columns mula sa eventform.html)
CREATE TABLE IF NOT EXISTS events (
    id VARCHAR(36) PRIMARY KEY,
    event_name VARCHAR(255) NOT NULL,
    event_date DATE NOT NULL,
    fullname VARCHAR(255),
    email VARCHAR(255),               -- FIX: Bagong column mula sa eventform
    contact VARCHAR(50),              -- FIX: Bagong column mula sa eventform
    customer_address VARCHAR(255),    -- FIX: Bagong column mula sa eventform
    province VARCHAR(100),
    city VARCHAR(100),
    barangay VARCHAR(100),            -- FIX: Bagong column mula sa eventform
    venue_address TEXT,               -- FIX: Bagong column mula sa eventform
    location VARCHAR(255),
    pax INT DEFAULT 50,
    status VARCHAR(50) DEFAULT 'Pending',
    backdrop VARCHAR(100),            -- FIX: Bagong column para sa selected backdrop
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 6. Reports Table (FIXED: Idinagdag ang created_by column)
CREATE TABLE IF NOT EXISTS reports (
    id VARCHAR(36) PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    content TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) DEFAULT 'Generated',
    created_by VARCHAR(100)           -- FIX: Bagong column na ginagamit sa app.py
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ---------------------------------------------------
-- INITIAL DATA (Optional: Para may laman agad)
-- ---------------------------------------------------

-- Default Accounts (Passwords are plain text here; in production, use hashing)
INSERT INTO users (id, username, password, role) VALUES 
(UUID(), 'admin', 'admin123', 'ADMIN'),
(UUID(), 'owner', 'owner123', 'OWNER');

-- Default Categories
INSERT INTO categories (category_name) VALUES 
('Silverware'), 
('Dinnerware'), 
('Glassware'), 
('Linens');

-- Sample Inventory Items - Silverware (ID: 1)
INSERT INTO inventory (item_id, category_id, item_name, beginning_qty, ending_qty) VALUES 
(UUID(), 1, 'Spoon', 100, 100),
(UUID(), 1, 'Fork', 100, 100),
(UUID(), 1, 'Teaspoon', 50, 50),
(UUID(), 1, 'Dinner Knife', 80, 80),
(UUID(), 1, 'Serving Spoon', 30, 30);

-- Dinnerware (ID: 2)
INSERT INTO inventory (item_id, category_id, item_name, beginning_qty, ending_qty) VALUES 
(UUID(), 2, 'Dinner Plate', 150, 150),
(UUID(), 2, 'Soup Bowl', 100, 100),
(UUID(), 2, 'Salad Plate', 100, 100);

-- Glassware (ID: 3)
INSERT INTO inventory (item_id, category_id, item_name, beginning_qty, ending_qty) VALUES 
(UUID(), 3, 'Wine Glass', 60, 60),
(UUID(), 3, 'Water Goblet', 120, 120),
(UUID(), 3, 'Juice Glass', 100, 100);

-- Linens (ID: 4)
INSERT INTO inventory (item_id, category_id, item_name, beginning_qty, ending_qty) VALUES 
(UUID(), 4, 'Table Cloth (White)', 40, 40),
(UUID(), 4, 'Table Napkin (Pink)', 200, 200),
(UUID(), 4, 'Seat Cover', 150, 150);

-- Sample Events
INSERT INTO events (id, event_name, event_date, location, fullname, email, contact, customer_address, province, city, barangay, venue_address, pax, status) VALUES 
(UUID(), 'Cruz Wedding', '2024-05-20', 'Blue Gardens', 'Juan Cruz', 'juan@email.com', '09171234567', 'Brgy. San Jose, Guiguinto', 'Bulacan', 'Guiguinto', 'San Jose', 'Blue Gardens Event Place, Guiguinto, Bulacan', 150, 'Confirmed'),
(UUID(), 'Santillan 18th Birthday', '2024-06-15', 'Casa Milagros', 'Maria Santillan', 'maria@email.com', '09181234567', 'Commonwealth, QC', 'Metro Manila', 'Quezon City', 'Commonwealth', 'Casa Milagros, Commonwealth Ave, QC', 100, 'Pending'),
(UUID(), 'TechCorp Seminar', '2024-07-02', 'Grand Hotel', 'Robert Fox', 'robert@email.com', '09191234567', 'Makati Ave, Makati', 'Metro Manila', 'Makati', 'Poblacion', 'Grand Hotel Ballroom, Makati', 75, 'Confirmed');

-- Sample Reports
INSERT INTO reports (id, title, content, status, created_by) VALUES 
(UUID(), 'Monthly Inventory Audit - April', 'All silverware accounted for. 2 glasses broken during Cruz event.', 'Generated', 'owner'),
(UUID(), 'Quarterly Sales Summary', 'Total of 15 events handled for Q1 2024.', 'Generated', 'owner');
