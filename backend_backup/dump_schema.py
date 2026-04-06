from sqlalchemy import create_engine
from sqlalchemy.schema import CreateTable
from app.models.models import Base, User, Role, UserRole, Project, ProjectMember, TimeEntry

# Use a postgresql URL to ensure Postgres syntax
engine = create_engine('postgresql:///')

with open('schema_dump.sql', 'w') as f:
    for table_name, table in Base.metadata.tables.items():
        create_stmt = str(CreateTable(table).compile(engine))
        f.write(f"-- Table: {table_name}\n")
        f.write(create_stmt + ";\n\n")

print("Generated schema_dump.sql")
