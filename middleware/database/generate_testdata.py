import sqlite3
import uuid
import time
import random
import base64


# Configuration for data
testdata = 5000


# Create a new SQLite database (or connect to an existing one)
conn = sqlite3.connect('middleware.db')


# Sample data for Lorem Ipsum generation
words = (
    "lorem ipsum dolor sit amet consectetur adipiscing elit sed do eiusmod tempor incididunt ut labore et dolore magna aliqua "
    "ut enim ad minim veniam quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat duis aute irure dolor "
    "in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur excepteur sint occaecat cupidatat non proident "
    "sunt in culpa qui officia deserunt mollit anim id est laborum"
).split()

def generate_sentence(word_count=8):
    return ' '.join(random.choice(words) for _ in range(word_count)).capitalize() + '.'

def generate_paragraph(sentence_count=5):
    return ' '.join(generate_sentence(random.randint(6, 12)) for _ in range(sentence_count))

def generate_lorem_ipsum(paragraph_count=3):
    return '\n\n'.join(generate_paragraph(random.randint(3, 7)) for _ in range(paragraph_count))


def generate_computer_name():
    adjectives = ["Quick", "Lazy", "Sleepy", "Noisy", "Happy", "Sad", "Brave", "Shy"]
    animals = ["Lion", "Tiger", "Bear", "Shark", "Wolf", "Eagle", "Hawk", "Leopard"]
    
    adjective = random.choice(adjectives)
    animal = random.choice(animals)
    number = random.randint(0, 9999)

    computer_name = f"{adjective}{animal}{number:04d}"
    return computer_name

def generate_internal_ip():
    # Define the private IP ranges
    private_ranges = [
        (10, 1, 0, 0, 10, 255, 255, 255),
        (172, 16, 0, 0, 172, 31, 255, 255),
        (192, 168, 0, 0, 192, 168, 255, 255)
    ]

    # Select a random range
    range = random.choice(private_ranges)
    
    # Generate a random IP within the selected range
    octet1 = random.randint(range[0], range[4])
    octet2 = random.randint(range[1], range[5])
    octet3 = random.randint(range[2], range[6])
    octet4 = random.randint(range[3], range[7])

    return f"{octet1}.{octet2}.{octet3}.{octet4}"

def generate_random_port():
    return random.randint(1024, 65535)

def random_binary():
    return random.choice([0, 1])

def generate_random_number(num_digits):
    if num_digits <= 0:
        raise ValueError("Number of digits must be greater than 0")
    lower_bound = 10**(num_digits - 1)
    upper_bound = 10**num_digits - 1
    number = random.randint(lower_bound, upper_bound)
    return number

def get_random_adversary_tool():
    tools = [
        "cobaltstrike", "metasploit", "empire", "havoc", "silver",
        "caldera", "covenant", "deimos", "empire3", "empire5",
        "ibombshell", "koadic", "merlin", "mythic", "nuages",
        "poshc2", "powerhub", "silenttrinity", "sliver", "scythe", 
        "trevorc2"
    ]
    return random.choice(tools)

def generate_random_shell_command():
    commands = [
        "dir", "ipconfig", "netstat", "tasklist", "systeminfo", 
        "whoami", "echo hello", "cd \\", "mkdir testdir", "rmdir testdir",
        "type nul > testfile.txt", "del testfile.txt", "ping 127.0.0.1", 
        "hostname", "set"
    ]
    
    command = random.choice(commands)
    full_command = f"shell {command}"
    encoded_command = base64.b64encode(full_command.encode()).decode()
    
    return encoded_command

def get_random_status():
    statuses = ["queued", "executed", "completed", "notified"]
    return random.choice(statuses)


def get_random_detection_status():
    return "detected" if random.random() < 0.05 else "undetected"

def get_random_source():
    sources = ["auto", "user"]
    return random.choice(sources)


def get_random_agent_uuid(conn):
    cursor = conn.cursor()
    
    # Get the total number of rows in the table
    cursor.execute("SELECT COUNT(*) FROM endpoints")
    total_rows = cursor.fetchone()[0]
    
    if total_rows == 0:
        return None

    # Generate a random row number
    random_row = random.randint(0, total_rows - 1)
    
    # Select the uuid from the random row
    cursor.execute(f"SELECT uuid FROM endpoints LIMIT 1 OFFSET {random_row}")
    result = cursor.fetchone()
    
    return result[0] if result else None

def get_random_beacon_buid_and_source(conn):
    cursor = conn.cursor()
    
    # Get the total number of rows in the table
    cursor.execute("SELECT COUNT(*) FROM beacons")
    total_rows = cursor.fetchone()[0]
    
    if total_rows == 0:
        return None

    # Generate a random row number
    random_row = random.randint(0, total_rows - 1)
    
    # Select the buid and source from the random row
    cursor.execute(f"SELECT buid, source FROM beacons LIMIT 1 OFFSET {random_row}")
    result = cursor.fetchone()
    
    return result if result else None


def get_random_beacon_uuid_from_beacons(conn):
    cursor = conn.cursor()
    
    # Get the total number of rows in the table
    cursor.execute("SELECT COUNT(*) FROM beacons")
    total_rows = cursor.fetchone()[0]
    
    if total_rows == 0:
        return None

    # Generate a random row number
    random_row = random.randint(0, total_rows - 1)
    
    # Select the uuid from the random row
    cursor.execute(f"SELECT uuid FROM beacons LIMIT 1 OFFSET {random_row}")
    result = cursor.fetchone()
    
    return result[0] if result else None

# Insert entries into database

## Insert some beacons into the application
for i in range(testdata):
    new_uuid = str(uuid.uuid4())
    buid = str(generate_random_number(10))
    name = generate_computer_name()
    source = get_random_adversary_tool()
    status = "active"

    conn.execute("INSERT INTO beacons (uuid, buid, name, source, status) VALUES (?, ?, ?, ?, ?)", (new_uuid, buid, name, source, status))


for i in range(testdata):
    taskid = str(uuid.uuid4())
    timestamp = int(time.time())

    # select an existing beacon from the table and take its buid, source
    result = get_random_beacon_buid_and_source(conn)
    buid, source = result
    # select another existing beacon and set it as a targetBeacon
    result2 = get_random_beacon_buid_and_source(conn)
    targetbuid, targetsource = result

    command = generate_random_shell_command()
    status = get_random_status()
    result = ""

    conn.execute("INSERT INTO beacon_tasks (taskid, timestamp, source, sourceBeacon, targetBeacon, command, status, result) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (taskid, timestamp, source, buid, targetbuid, command, status, result))



for i in range(testdata):
    new_uuid = str(uuid.uuid4())
    name = generate_computer_name()
    agentmodules = 1
    activated = random_binary()

    # select a beacon as referenceBeacon from the database
    referenceBeacon = get_random_beacon_uuid_from_beacons(conn)

    conn.execute("INSERT INTO endpoints (uuid, name, agentmodules, activated, referenceBeacon) VALUES (?, ?, ?, ?, ?)", (new_uuid, name, agentmodules, activated, referenceBeacon))


for i in range(testdata):
    logcheck = str(uuid.uuid4())
    agentuuid = get_random_agent_uuid(conn)
    timestamp = int(time.time())
    status = get_random_detection_status()
    raw_event = generate_lorem_ipsum(random.randint(1, 30))
    module_uuid = str(uuid.uuid4())
    executed_module = 1
    check_type = get_random_source()
    notified = 1


    conn.execute("INSERT INTO agent_logs (logcheck, agentuuid, timestamp, status, raw_event, module_uuid, executed_module, check_type, notified) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (logcheck, agentuuid, timestamp, status, raw_event, module_uuid, executed_module, check_type, notified))


for i in range(testdata):
    timestamp = int(time.time())
    agentuuid = get_random_agent_uuid(conn)
    command = "logcheck"
    executed = random_binary()

    conn.execute("INSERT INTO agenttasks (timestamp, agentuuid, command, executed) VALUES (?, ?, ?, ?)", (timestamp, agentuuid, command, executed))

conn.commit()
# Close the connection
conn.close()