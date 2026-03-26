import csv
import sqlite3

con = sqlite3.connect("INTELLI.db")
cursor = con.cursor()

query = "CREATE TABLE IF NOT EXISTS sys_command(id integer primary key, name VARCHAR(100), path VARCHAR(1000))"
cursor.execute(query)

# Insert system commands with error handling for duplicates
try:
    query = "INSERT INTO sys_command VALUES (null,'one note', 'C:\\Program Files\\Microsoft Office\\root\\Office16\\ONENOTE.exe')"
    cursor.execute(query)
    con.commit()
except:
    pass

try:
    query = "INSERT INTO sys_command VALUES (null,'whatsapp', 'C:\\Program Files\\Microsoft Office\\root\\Office16\\ONENOTE.exe')"
    cursor.execute(query)
    con.commit()
except:
    pass

try:
    query = "INSERT INTO sys_command VALUES (null,'chrome', 'C:\\Program Files\\Google\\Chrome\\Application\\CHROME.exe')"
    cursor.execute(query)
    con.commit()
except:
    pass

try:
    query = "INSERT INTO sys_command VALUES (null,'vlc', 'C:\\Program Files\\VideoLAN\\VLC.exe')"
    cursor.execute(query)
    con.commit()
except:
    pass

try:
    query = "INSERT INTO sys_command VALUES (null,'far cry 6', 'C:\\Games\\Far Cry 6\\bin\\FARCRY6.exe')"
    cursor.execute(query)
    con.commit()
except:
    pass

try:
    query = "INSERT INTO sys_command VALUES (null,'assassins creed 3', 'C:\\Games\\Assassins Creed III.exe')"
    cursor.execute(query)
    con.commit()
except:
    pass

# query = "INSERT INTO sys_command VALUES (null,'Telegram', 'C:\\Program Files\\Microsoft Office\\root\Office16\\ONENOTE.exe')"
# cursor.execute(query)
# con.commit()


query = "CREATE TABLE IF NOT EXISTS web_command(id integer primary key, name VARCHAR(100), url VARCHAR(1000))"
cursor.execute(query)

try:
    query = "INSERT INTO web_command VALUES (null,'flipkart', 'https://www.flipkart.com/')"
    cursor.execute(query)
    con.commit()
except:
    pass

try:
    query = "INSERT INTO web_command VALUES (null,'amazon', 'https://www.amazon.in/')"
    cursor.execute(query)
    con.commit()
except:
    pass

try:
    query = "INSERT INTO web_command VALUES (null,'netflix', 'https://www.netflix.com/in/')"
    cursor.execute(query)
    con.commit()
except:
    pass

try:
    query = "INSERT INTO web_command VALUES (null,'geeksforgeeks', 'https://www.geeksforgeeks.org/')"
    cursor.execute(query)
    con.commit()
except:
    pass

try:
    query = "INSERT INTO web_command VALUES (null,'javatpoint', 'https://www.javatpoint.com/')"
    cursor.execute(query)
    con.commit()
except:
    pass

try:
    query = "INSERT INTO web_command VALUES (null, 'hindustan times', 'https://www.hindustantimes.com/')"
    cursor.execute(query)
    con.commit()
except:
    pass

# query = "INSERT INTO web_command VALUES (null,'xvideos', 'https://www.xvideos.com/')"
# cursor.execute(query)
# con.commit()



# testing module
app_name = "android studio"
cursor.execute('SELECT path FROM sys_command WHERE name = ?', (app_name,))
results = cursor.fetchmany(1)
if results:
    print(results[0][0])
else:
    print("No matching rows found.")

# Create a table with the desired columns
cursor.execute('''CREATE TABLE IF NOT EXISTS contacts (id integer primary key, name VARCHAR(200), mobile_no VARCHAR(255), email VARCHAR(255) NULL)''')

# Read data from CSV if file exists
import os
if os.path.exists('contacts.csv'):
    desired_columns_indices = [0, 1]  # name, mobile_no columns
    
    with open('contacts.csv', 'r', encoding='utf-8') as csvfile:
        csvreader = csv.reader(csvfile)
        next(csvreader)  # Skip header if exists
        for row in csvreader:
            if len(row) >= 2:
                selected_data = [row[i] for i in desired_columns_indices]
                cursor.execute(''' INSERT INTO contacts (id, 'name', 'mobile_no') VALUES (null, ?, ?);''', tuple(selected_data))

# Commit changes and close connection
con.commit()
con.close()

print("Database initialized successfully!")
con.close()

# query = "INSERT INTO contacts VALUES (null,'pawan', '1234567890', 'null')"
# cursor.execute(query)
# con.commit()

# query = 'kunal'
# query = query.strip().lower()

# cursor.execute("SELECT mobile_no FROM contacts WHERE LOWER(name) LIKE ? OR LOWER(name) LIKE ?", ('%' + query + '%', query + '%'))
# results = cursor.fetchall()
# print(results[0][0])


