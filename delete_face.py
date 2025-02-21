import sqlite3

# Connect to database
conn = sqlite3.connect('suspects.db')
c = conn.cursor()

# Ask the user how they want to delete the suspect
choice = input("Delete by (1) Table ID or (2) Suspect Information (Name, ID, Nationality)? Enter 1 or 2: ")

if choice == '1':
    # Delete by Table ID
    table_id = input("Enter the table ID: ")
    c.execute("DELETE FROM suspects WHERE id=?", (table_id,))

elif choice == '2':
    # Delete by Suspect Information
    name = input("Enter the suspect's name: ")
    suspect_id = input("Enter the suspect's ID number: ")
    nationality = input("Enter the suspect's nationality: ")
    c.execute("DELETE FROM suspects WHERE name=? AND id_number=? AND nationality=?", (name, suspect_id, nationality))

else:
    print("Invalid choice. No action taken.")

conn.commit()
conn.close()

print("Suspect deletion process completed.")
