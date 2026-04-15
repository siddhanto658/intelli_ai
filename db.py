import csv
import os
import sqlite3


def init_database(db_path="INTELLI.db", contacts_csv_path="contacts.csv"):
    con = sqlite3.connect(db_path)
    cursor = con.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS sys_command(
            id INTEGER PRIMARY KEY,
            name VARCHAR(100) UNIQUE,
            path VARCHAR(1000)
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS web_command(
            id INTEGER PRIMARY KEY,
            name VARCHAR(100) UNIQUE,
            url VARCHAR(1000)
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS contacts(
            id INTEGER PRIMARY KEY,
            name VARCHAR(200),
            mobile_no VARCHAR(255),
            email VARCHAR(255) NULL
        )
        """
    )

    sys_seed = [
        ("one note", r"C:\Program Files\Microsoft Office\root\Office16\ONENOTE.exe"),
        ("whattsApp", r"C:\Program Files\Microsoft Office\root\Office16\ONENOTE.exe"),
        ("chrome", r"C:\Program Files\Google\Chrome\Application\CHROME.exe"),
        ("vlc", r"C:\Program Files\VideoLAN\VLC.exe"),
        ("far cry 6", r"C:\Games\Far Cry 6\bin\FARCRY6.exe"),
        ("assassins creed 3", r"C:\Games\Assassins Creed III.exe"),
    ]
    cursor.executemany(
        "INSERT OR IGNORE INTO sys_command(name, path) VALUES (?, ?)",
        sys_seed,
    )

    web_seed = [
        ("flipkart", "https://www.flipkart.com/"),
        ("youtube", "https://www.youtube.com/"),
        ("amazon", "https://www.amazon.in/"),
        ("netflix", "https://www.netflix.com/in/"),
        ("geeksforgeeks", "https://www.geeksforgeeks.org/"),
        ("javatpoint", "https://www.javatpoint.com/"),
        ("hindustan times", "https://www.hindustantimes.com/"),
    ]
    cursor.executemany(
        "INSERT OR IGNORE INTO web_command(name, url) VALUES (?, ?)",
        web_seed,
    )

    if os.path.exists(contacts_csv_path):
        with open(contacts_csv_path, "r", encoding="utf-8") as csvfile:
            csvreader = csv.reader(csvfile)
            for row in csvreader:
                if len(row) <= 32:
                    continue
                name = row[0].strip()
                mobile_no = row[32].strip()
                if not name or not mobile_no:
                    continue
                cursor.execute(
                    """
                    INSERT INTO contacts(name, mobile_no)
                    SELECT ?, ?
                    WHERE NOT EXISTS(
                        SELECT 1 FROM contacts WHERE name = ? AND mobile_no = ?
                    )
                    """,
                    (name, mobile_no, name, mobile_no),
                )

    con.commit()
    con.close()


if __name__ == "__main__":
    init_database()


