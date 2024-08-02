import sqlite3
import os


conn = sqlite3.connect('middleware.db')

############################################################################
# Insert or update middleware settings
############################################################################

def upsert_middleware_configuration(conn, key, value):
    cursor = conn.cursor()
    
    # Check if the key already exists
    cursor.execute("SELECT value FROM middlewareconfiguration WHERE key = ?", (key,))
    row = cursor.fetchone()
    
    if row is None:
        # Insert new record if the key does not exist
        cursor.execute("INSERT INTO middlewareconfiguration (key, value) VALUES (?, ?)", (key, value))
        print(f"Inserted new key: {key}, value: {value}")
    else:
        if(row[0] == ""):
            # Update the existing record if the key exists
            cursor.execute("UPDATE middlewareconfiguration SET value = ? WHERE key = ?", (value, key))
            print(f"Updated key: {key}, value: {value}")
        else:
            print(f"Key already exists with a value - not updating: {key}, value: {row[0]}")
    # Commit the changes
    conn.commit()


upsert_middleware_configuration(conn, 'endpoint', '')
upsert_middleware_configuration(conn, 'port', '45134') 
upsert_middleware_configuration(conn, 'default_scan_profile', '2')
upsert_middleware_configuration(conn, 'cs_teamserver_ip', '')
upsert_middleware_configuration(conn, 'cs_teamserver_port', '50050')
upsert_middleware_configuration(conn, 'cs_teamserver_password', '')


############################################################################
# Insert or update scripts
############################################################################
def upsert_modules_configuration(conn, name, script):
    cursor = conn.cursor()
    
    # Check if the name already exists
    cursor.execute("SELECT script FROM modules WHERE name = ?", (name,))
    row = cursor.fetchone()
    
    if row is None:
        # Insert new record if the name does not exist
        cursor.execute("INSERT INTO modules (name, script) VALUES (?, ?)", (name, script))
        print(f"Inserted new name: {name}")
    else:
        # Update the existing record if the name exists
        cursor.execute("UPDATE modules SET script = ? WHERE name = ?", (script, name))
        print(f"Updated name: {name}")
    
    # Commit the changes
    conn.commit()

# Get the directory of the currently executed script
current_dir = os.path.dirname(os.path.abspath(__file__))

# Define the relative directory containing the scripts
relative_directory = os.path.join(current_dir, '../scripts')

# Normalize the relative directory path
directory = os.path.normpath(relative_directory)

# Initialize a dictionary to store script contents
script_contents = {}

# Connect to the SQLite database
conn = sqlite3.connect('middleware.db')

# Check if the directory exists
if not os.path.exists(directory):
    print(f"The directory {directory} does not exist.")
else:
    # Loop over all files in the specified directory
    for filename in os.listdir(directory):
        # Construct full file path
        file_path = os.path.join(directory, filename)
        
        # Check if it's a file
        if os.path.isfile(file_path):
            with open(file_path, 'r') as file:
                # Read the first line
                first_line = file.readline().strip()
                
                # Initialize the variable to store the content
                content = ""
                
                # Check if the first line contains the pattern
                if first_line.startswith("# ScriptName:"):
                    # Extract the user-defined input "<something>"
                    script_name = first_line.split(":")[1].strip()
                    
                    # Read the rest of the file and store it in the variable
                    content = file.read()

                    # Upsert into the modules table
                    upsert_modules_configuration(conn, script_name, content)
                    
                    # Save the script content in the dictionary with script name as key
                    script_contents[script_name] = content
                else:
                    # If the first line does not contain the pattern, include it in the content
                    content = first_line + "\n" + file.read()
                    
                    # Save the script content in the dictionary with filename as key
                    script_contents[filename] = content

                    # Upsert into the modules table
                    upsert_modules_configuration(conn, filename, content)    
                


############################################################################
# Insert or update module groups for each script
############################################################################
# Check if a module group with the given name exists
def module_group_exists(conn, name):
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM modulegroups WHERE name = ?", (name,))
    return cursor.fetchone()

# Insert a new module group and return its ID
def insert_module_group(conn, name):
    cursor = conn.cursor()
    cursor.execute("INSERT INTO modulegroups (name) VALUES (?)", (name,))
    conn.commit()
    return cursor.lastrowid

# Check if a module group entry exists
def module_group_entry_exists(conn, mapped_module, mapped_modulegroup):
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM modulegroupentries WHERE mapped_module = ? AND mapped_modulegroup = ?", (mapped_module, mapped_modulegroup))
    return cursor.fetchone()

# Insert a new module group entry
def insert_module_group_entry(conn, mapped_module, mapped_modulegroup):
    cursor = conn.cursor()
    cursor.execute("INSERT INTO modulegroupentries (mapped_module, mapped_modulegroup) VALUES (?, ?)", (mapped_module, mapped_modulegroup))
    conn.commit()


cursor = conn.cursor()
cursor.execute("SELECT id, name FROM modules")
modules = cursor.fetchall()


for module_id, module_name in modules:
    # Check if the module group already exists
    module_group = module_group_exists(conn, module_name)
        
    if module_group:
        module_group_id = module_group[0]
        print(f"Module group '{module_name}' already exists with ID {module_group_id}")
    else:
    # Insert a new module group with the same name as the module
        module_group_id = insert_module_group(conn, module_name)
        print(f"Inserted new module group '{module_name}' with ID {module_group_id}")
        
    # Check if the module group entry already exists
    if module_group_entry_exists(conn, module_id, module_group_id):
        print(f"Module group entry for module ID {module_id} and module group ID {module_group_id} already exists")
    else:
    # Insert a new entry into modulegroupentries
        insert_module_group_entry(conn, module_id, module_group_id)
        print(f"Inserted new module group entry for module ID {module_id} and module group ID {module_group_id}")

    # Check if the "RunAllScripts" module group exists
    run_all_group = module_group_exists(conn, "RunAllScripts")
    
    if run_all_group:
        run_all_group_id = run_all_group[0]
        print(f"Module group 'RunAllScripts' already exists with ID {run_all_group_id}")
    else:
        # Insert the "RunAllScripts" module group
        run_all_group_id = insert_module_group(conn, "RunAllScripts")
        print(f"Inserted new module group 'RunAllScripts' with ID {run_all_group_id}")

    # Insert entries for all modules into the "RunAllScripts" module group
    for module_id, module_name in modules:
        if module_group_entry_exists(conn, module_id, run_all_group_id):
            print(f"Module group entry for module ID {module_id} and module group ID {run_all_group_id} already exists")
        else:
            insert_module_group_entry(conn, module_id, run_all_group_id)
            print(f"Inserted new module group entry for module ID {module_id} and module group ID {run_all_group_id}")


conn.commit()
# Close the connection
conn.close()