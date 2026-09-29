import sqlite3

conn = sqlite3.connect('local_dev.db')
cursor = conn.cursor()
sample_pdf = "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"

cursor.execute("UPDATE product_assets SET file_url = ? WHERE file_url LIKE '%example.com%' OR file_url = '' OR file_url IS NULL", (sample_pdf,))
conn.commit()
print(f"Updated {cursor.rowcount} rows in product_assets table.")
