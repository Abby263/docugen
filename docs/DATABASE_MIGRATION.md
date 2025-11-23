# Database Migration: Clerk Authentication Support

## Problem
After adding Clerk authentication support, the backend was throwing errors:
```
sqlalchemy.exc.OperationalError: (sqlite3.OperationalError) no such column: users.clerk_user_id
```

## Root Cause
The User model was updated to include a new `clerk_user_id` column, but the existing database table didn't have this column. SQLAlchemy's `Base.metadata.create_all()` only creates tables that don't exist - it doesn't alter existing tables.

## Solution
Added a database migration to add the `clerk_user_id` column to the existing `users` table.

### Migration Details
1. Added `clerk_user_id` column (VARCHAR 255)
2. Created a unique index on `clerk_user_id` (SQLite doesn't support adding UNIQUE constraints directly with ALTER TABLE)

### Files Modified
- `backend/database.py`: Added `clerk_user_id` field to User model
- Created temporary migration script to add the column
- Successfully migrated the database

## Updated User Model

```python
class User(Base):
    # ... existing fields ...
    clerk_user_id = Column(String(255), unique=True, index=True, nullable=True)
```

## How to Apply Migration

If you need to apply this migration to a fresh database:

1. **For a fresh database:**
   ```bash
   cd /Users/viprasingh/Developer/xunlong
   PYTHONPATH=/Users/viprasingh/Developer/xunlong python backend/init_db.py
   ```

2. **For an existing database (already applied):**
   The migration has already been applied to the current database.

## Future Migrations

For future schema changes:

1. **Option 1: Use Alembic** (Recommended for production)
   ```bash
   pip install alembic
   alembic init alembic
   # Create migration
   alembic revision --autogenerate -m "description"
   # Apply migration
   alembic upgrade head
   ```

2. **Option 2: Manual SQL Migration**
   - Write a Python script to execute SQL ALTER TABLE commands
   - Handle SQLite limitations (no direct UNIQUE constraint support)

3. **Option 3: Recreate Database** (Development only)
   ```bash
   rm backend/docugen_saas.db
   PYTHONPATH=/Users/viprasingh/Developer/xunlong python backend/init_db.py
   ```

## Verification

After migration, verify the column exists:
```bash
sqlite3 backend/docugen_saas.db "PRAGMA table_info(users);"
```

Expected output should include:
```
clerk_user_id|VARCHAR(255)|0||0
```

Check the unique index:
```bash
sqlite3 backend/docugen_saas.db "SELECT sql FROM sqlite_master WHERE type='index' AND name='idx_users_clerk_user_id';"
```

## Status
✅ Migration completed successfully
✅ Backend running without errors
✅ Clerk authentication fully functional

