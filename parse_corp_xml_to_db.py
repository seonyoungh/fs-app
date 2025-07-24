import sqlite3
import xml.etree.ElementTree as ET

# XML 파일과 DB 파일 경로
XML_FILE = 'corp.xml'
DB_FILE = 'corp.db'

# SQLite DB 연결 및 테이블 생성
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS corp (
            corp_code TEXT PRIMARY KEY,
            corp_name TEXT,
            stock_code TEXT,
            modify_date TEXT
        )
    ''')
    conn.commit()
    return conn

def parse_and_insert(xml_file, conn):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    c = conn.cursor()
    for item in root.findall('list'):
        corp_code = item.findtext('corp_code')
        corp_name = item.findtext('corp_name')
        stock_code = item.findtext('stock_code')
        modify_date = item.findtext('modify_date')
        c.execute('''
            INSERT OR REPLACE INTO corp (corp_code, corp_name, stock_code, modify_date)
            VALUES (?, ?, ?, ?)
        ''', (corp_code, corp_name, stock_code, modify_date))
    conn.commit()

def main():
    conn = init_db()
    parse_and_insert(XML_FILE, conn)
    conn.close()
    print('DB 변환 완료!')

if __name__ == '__main__':
    main() 