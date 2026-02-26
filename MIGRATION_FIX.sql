-- =============================================
-- MIGRATION SCRIPT: Para sa existing databases
-- Patakbuhin ito kung mayroon ka nang existing cateringinventory database
-- na gumagamit ng lumang schema (walang bagong columns)
-- =============================================

USE cateringinventory;

-- Add missing columns sa events table
ALTER TABLE events ADD COLUMN IF NOT EXISTS email VARCHAR(255) AFTER fullname;
ALTER TABLE events ADD COLUMN IF NOT EXISTS contact VARCHAR(50) AFTER email;
ALTER TABLE events ADD COLUMN IF NOT EXISTS customer_address VARCHAR(255) AFTER contact;
ALTER TABLE events ADD COLUMN IF NOT EXISTS barangay VARCHAR(100) AFTER city;
ALTER TABLE events ADD COLUMN IF NOT EXISTS venue_address TEXT AFTER barangay;
ALTER TABLE events ADD COLUMN IF NOT EXISTS backdrop VARCHAR(100) AFTER status;

-- Add missing column sa reports table
ALTER TABLE reports ADD COLUMN IF NOT EXISTS created_by VARCHAR(100) AFTER status;
