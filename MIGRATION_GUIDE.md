# Database Migration Guide

This project now includes automatic database migration capabilities using Alembic. The system will automatically detect changes in your SQLAlchemy models and apply the necessary database schema updates.

## How It Works

1. **Automatic Detection**: When you modify your models (add/remove columns, change types, etc.), the system detects these changes
2. **Migration Generation**: Alembic generates migration scripts that describe the changes
3. **Automatic Application**: The migrations are automatically applied to keep your database in sync

## Setup

The migration system is already configured and ready to use. Here's what was set up:

- **Alembic configuration** (`alembic.ini`)
- **Migration environment** (`alembic/env.py`)
- **Auto-migration utilities** (`migration_utils.py`)
- **Database integration** (updated `database.py`)

## Usage

### Automatic Migration (Recommended)

The easiest way to use the system is through automatic migration:

```python
from database import auto_migrate

# This will detect changes and apply them automatically
result = auto_migrate()
print(result)
```

### Command Line Interface

You can also use the command line script:

```bash
# Automatically detect and apply migrations
python run_migrations.py auto

# Check migration status
python run_migrations.py status

# Generate a new migration
python run_migrations.py generate "Add new column to user table"

# Apply pending migrations
python run_migrations.py apply

# Create initial migration (for new setups)
python run_migrations.py init
```

### Programmatic Usage

```python
from migration_utils import AutoMigrationManager

manager = AutoMigrationManager()

# Check status
status = manager.check_migration_status()
print(f"Current revision: {status['current_revision']}")
print(f"Head revision: {status['head_revision']}")
print(f"Up to date: {status['is_up_to_date']}")

# Generate migration
revision = manager.generate_migration("Your migration message")

# Apply migrations
success = manager.apply_migrations()

# Full auto-migration
result = manager.auto_migrate()
```

## Integration with Application Startup

The migration system is integrated into the database initialization:

```python
from database import initialize_database

# This will run auto-migration before creating tables
initialize_database()
```

## What Gets Migrated

The system automatically detects and migrates:

- **New tables** - When you create new model classes
- **New columns** - When you add new fields to existing models
- **Column type changes** - When you modify field types
- **Column constraints** - When you add/remove constraints
- **Indexes** - When you add/remove indexes
- **Foreign keys** - When you add/remove relationships

## Migration Files

Migration files are stored in `alembic/versions/` and follow this naming pattern:
- `{revision_id}_{description}.py`

Example: `001_add_user_email_column.py`

## Best Practices

1. **Always test migrations** on a development database first
2. **Review generated migrations** before applying to production
3. **Use descriptive messages** when generating migrations
4. **Backup your database** before major migrations
5. **Run migrations regularly** to keep schema in sync

## Troubleshooting

### Common Issues

1. **"No changes detected"**
   - Make sure your model changes are properly imported
   - Check that the model is registered with the Base metadata

2. **"Migration conflicts"**
   - Multiple developers may have created conflicting migrations
   - Use `alembic merge` to resolve conflicts

3. **"Database connection errors"**
   - Check your database URL in `alembic.ini`
   - Ensure database credentials are correct

### Manual Migration Commands

If you need to use Alembic directly:

```bash
# Generate migration
alembic revision --autogenerate -m "Your message"

# Apply migrations
alembic upgrade head

# Check current revision
alembic current

# Show migration history
alembic history

# Downgrade to previous revision
alembic downgrade -1
```

## Environment Variables

The system uses these environment variables:

- `DATABASE_URL` - Database connection string
- `SQLALCHEMY_ECHO` - Enable SQL logging (true/false)

## File Structure

```
project/
├── alembic/
│   ├── env.py              # Alembic environment configuration
│   ├── script.py.mako      # Migration template
│   └── versions/           # Migration files
├── alembic.ini             # Alembic configuration
├── migration_utils.py      # Auto-migration utilities
├── run_migrations.py       # Command line interface
└── database.py             # Database configuration (updated)
```

## Example Workflow

1. **Modify a model**:
   ```python
   class User(Base):
       # ... existing fields ...
       email = db(String(255), unique=True)  # New field
   ```

2. **Run auto-migration**:
   ```bash
   python run_migrations.py auto
   ```

3. **Check the result**:
   ```bash
   python run_migrations.py status
   ```

The system will automatically:
- Detect the new `email` field
- Generate a migration script
- Apply the migration to add the column to the database

## Production Considerations

- **Always backup** before running migrations in production
- **Test migrations** on a copy of production data first
- **Monitor migration performance** for large tables
- **Consider downtime** for major schema changes
- **Use maintenance windows** for complex migrations

This migration system ensures your database schema stays in sync with your model changes automatically, reducing manual work and potential errors.
