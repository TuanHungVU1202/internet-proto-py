import json
import sqlite3

# SQLite DB Name
import util

DB_Name = '../../database.db'


# ===============================================================
# Database Manager Class

class DatabaseManager():
    def __init__(self):
        self.conn = sqlite3.connect(DB_Name)
        self.conn.execute('pragma foreign_keys = on')
        self.conn.commit()
        self.cur = self.conn.cursor()

    def add_del_update_db_record(self, sql_query, args=()):
        self.cur.execute(sql_query, args)
        self.conn.commit()
        return

    def __del__(self):
        self.cur.close()
        self.conn.close()


# ===============================================================
def create_table():
    db = DatabaseManager()
    db.add_del_update_db_record(
        '''CREATE TABLE IF NOT EXISTS mqtt
             (time_sent real, 
             time_received real, 
             pub_id integer,
             sub_id text,
             topic text, 
             broker text, 
             port text, 
             data text)''')
    del db
    print("Created mqtt table")


def persist_data(json_data, sub_id):
    # Parse Data
    json_obj = json.loads(json_data)
    time_sent = json_obj['time_sent']
    pub_id = json_obj['pub_id']
    topic = json_obj['topic']
    broker = json_obj['broker']
    port = json_obj['port']
    data = str(json_obj['data'])

    time_received = util.get_current_timestamp()

    # Push into DB Table
    db = DatabaseManager()
    db.add_del_update_db_record(
        "insert into mqtt (time_sent, time_received, pub_id, sub_id, topic, broker, port, data) values (?,?,?,?,?,?,?,?)",
        [time_sent, time_received, pub_id, sub_id, topic, broker, port, data])
    del db
    print("Saved to Database.")

# ===============================================================
