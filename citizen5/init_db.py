import sqlite3

def init_db(db_name):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    
    # Create table
    c.execute('''CREATE TABLE IF NOT EXISTS votes
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  citizen_id INTEGER,
                  vote TEXT,
                  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    
    # Insert initial citizen data
    c.execute("INSERT OR IGNORE INTO votes (citizen_id, vote) VALUES (?, ?)", (1, "Initialized"))
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db("votes.db")
