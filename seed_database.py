import sqlite3
from database import init_db, add_user, get_db_connection
from utils import process_and_store_pdf

def seed():
    """Seeds the database with initial data for demonstration."""
    # 1. Initialize the DB schema
    init_db()

    # 2. Add companies
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Using INSERT OR IGNORE to avoid errors on re-runs
        cursor.execute("INSERT OR IGNORE INTO companies (id, name, group_name) VALUES (1, 'Reliance Industries', 'Ambani Group')")
        cursor.execute("INSERT OR IGNORE INTO companies (id, name, group_name) VALUES (2, 'Jio Platforms', 'Ambani Group')")
        cursor.execute("INSERT OR IGNORE INTO companies (id, name, group_name) VALUES (3, 'Other Company', 'Other Group')")
        conn.commit()
        print("Companies seeded.")
    except Exception as e:
        print(f"Error seeding companies: {e}")

    # 3. Add users with different roles
    add_user('mukesh_ambani', 'password123', 'GroupOwner') # Can see all 'Ambani Group' companies
    add_user('reliance_ceo', 'password123', 'CEO') # Can only see 'Reliance Industries'
    add_user('analyst_user', 'password123', 'Analyst') # Can be assigned any company
    add_user('other_ceo', 'password123', 'CEO') # Can only see 'Other Company'

    # 4. Set user permissions based on roles
    # Mukesh Ambani (GroupOwner) gets access to all companies in 'Ambani Group'
    cursor.execute("SELECT id FROM users WHERE username = 'mukesh_ambani'")
    group_owner_id = cursor.fetchone()['id']
    cursor.execute("SELECT id FROM companies WHERE group_name = 'Ambani Group'")
    ambani_companies = cursor.fetchall()
    for company in ambani_companies:
        cursor.execute("INSERT OR IGNORE INTO user_company_permissions (user_id, company_id) VALUES (?, ?)", (group_owner_id, company['id']))

    # Reliance CEO gets access to 'Reliance Industries'
    cursor.execute("SELECT id FROM users WHERE username = 'reliance_ceo'")
    reliance_ceo_id = cursor.fetchone()['id']
    cursor.execute("INSERT OR IGNORE INTO user_company_permissions (user_id, company_id) VALUES (?, ?)", (reliance_ceo_id, 1))

    # Other CEO gets access to 'Other Company'
    cursor.execute("SELECT id FROM users WHERE username = 'other_ceo'")
    other_ceo_id = cursor.fetchone()['id']
    cursor.execute("INSERT OR IGNORE INTO user_company_permissions (user_id, company_id) VALUES (?, ?)", (other_ceo_id, 3))
    
    # Analyst gets access to Reliance Industries for this demo
    cursor.execute("SELECT id FROM users WHERE username = 'analyst_user'")
    analyst_id = cursor.fetchone()['id']
    cursor.execute("INSERT OR IGNORE INTO user_company_permissions (user_id, company_id) VALUES (?, ?)", (analyst_id, 1))

    conn.commit()
    print("User permissions seeded.")

    # 5. Process the PDF for Reliance Industries (Company ID 1)
    # This is an expensive operation and should only be run once.
    # Check if data already exists to avoid reprocessing.
    cursor.execute("SELECT COUNT(*) FROM financial_data WHERE company_id = 1")
    if cursor.fetchone()[0] == 0:
        print("No data found for Reliance Industries. Processing PDF...")
        process_and_store_pdf('data/consolidated.pdf', 1, conn)
    else:
        print("Data for Reliance Industries already exists in the database.")
    # 6. Process the PDF for Jio Platforms (Company ID 2)
    # For this demo, we will re-use the same PDF for Jio.
    cursor.execute("SELECT COUNT(*) FROM financial_data WHERE company_id = 2")
    if cursor.fetchone()[0] == 0:
        print("No data found for Jio Platforms. Processing PDF...")
        process_and_store_pdf('data/consolidated.pdf', 2, conn)
    else:
        print("Data for Jio Platforms already exists in the database.")

    conn.close()
    

if __name__ == '__main__':
    seed()