# External imports
import psycopg2
from psycopg2.extras import RealDictCursor

# Internal imports
from config import DATABASE_URL

def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL)
    return conn

def execute_query(query, params=None):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute(query, params)
    conn.commit()
    cursor.close()
    conn.close()

def fetch_query(query, params=None):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute(query, params)
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result

def initalize_database():
    # SQL command to create the "users" table
    create_users_table_sql = """
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        username VARCHAR(100) UNIQUE NOT NULL,
        email VARCHAR(200) UNIQUE NOT NULL,
        password VARCHAR(80) NOT NULL,
        role VARCHAR(100) DEFAULT 'user',
        status VARCHAR(100) DEFAULT 'normal',
        joined_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
        deleted_at TIMESTAMPTZ
    );
    """

    # SQL command to create the "file_groups" table
    create_file_groups_table_sql = """
    CREATE TABLE IF NOT EXISTS uploads (
        id SERIAL PRIMARY KEY,
        title TEXT UNIQUE NOT NULL,
        description TEXT,
        type VARCHAR(100) NOT NULL,
        created_by INT REFERENCES users(id) ON DELETE SET NULL,
        created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
    );
    """

    # SQL command to create the "files" table
    create_files_table_sql = """
    CREATE TABLE IF NOT EXISTS files (
        id SERIAL PRIMARY KEY,
        upload_id INT REFERENCES uploads(id) ON DELETE CASCADE,
        original_file_name TEXT NOT NULL,
        generated_file_name TEXT NOT NULL,
        file_path TEXT NOT NULL,
        file_size BIGINT,
        file_mime TEXT,
        file_ext VARCHAR(50),
        created_by INT REFERENCES users(id) ON DELETE SET NULL,
        uploaded_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
    );
    """

    # SQL command to create the "tags" table
    create_tags_table_sql = """
    CREATE TABLE IF NOT EXISTS tags (
        id SERIAL PRIMARY KEY,
        tag_name VARCHAR(255),
        created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
        created_by INT REFERENCES users(id) ON DELETE SET NULL
    );
    """

    # SQL command to create the "file_group_tags" table (Many-to-Many Relationship)
    create_file_group_tags_table_sql = """
    CREATE TABLE IF NOT EXISTS upload_tags (
        upload_id INT REFERENCES uploads(id) ON DELETE CASCADE,
        tag_id INT REFERENCES tags(id) ON DELETE CASCADE,
        created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (upload_id, tag_id)
    );
    """

    # SQL commands to create indexes for improved performance
    create_indexes_sql = """
    -- Create Index for "users" email
    CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

    -- Create Index for "file_groups" created_by
    CREATE INDEX IF NOT EXISTS idx_file_groups_created_by ON file_groups(created_by);

    -- Create Index for "files" file_group_id
    CREATE INDEX IF NOT EXISTS idx_files_file_group_id ON files(file_group_id);

    -- Create Index for "files" created_by
    CREATE INDEX IF NOT EXISTS idx_files_created_by ON files(created_by);

    -- Create Index for "tags" created_by
    CREATE INDEX IF NOT EXISTS idx_tags_created_by ON tags(created_by);
    """

    execute_query(create_users_table_sql)
    print("1")
    execute_query(create_file_groups_table_sql)
    print("2")
    execute_query(create_files_table_sql)
    print("3")
    execute_query(create_tags_table_sql)
    print("4")
    execute_query(create_file_group_tags_table_sql)
    print("5")
