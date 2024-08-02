import sqlite3

# Create a new SQLite database (or connect to an existing one)
conn = sqlite3.connect('middleware.db')

# Create a new table called 'middlewareconfiguration'
conn.execute('''
CREATE TABLE IF NOT EXISTS middlewareconfiguration (
    id INTEGER PRIMARY KEY,
    key TEXT NOT NULL,
    value TEXT
)
''')

# Create a new table called 'endpoints'
conn.execute('''
CREATE TABLE IF NOT EXISTS endpoints (
    id INTEGER PRIMARY KEY,
    uuid TEXT NOT NULL,
    name TEXT NOT NULL DEFAULT '',
    agentmodules INTEGER NOT NULL DEFAULT 0,
    activated INTEGER NOT NULL DEFAULT 0,
    referenceBeacon TEXT DEFAULT ''
)
''')

# Create a new table called 'modules'
conn.execute('''
CREATE TABLE IF NOT EXISTS modules (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL DEFAULT '',
    script TEXT NOT NULL DEFAULT ''
)
''')

# Create a new table called 'modulegroups'
conn.execute('''
CREATE TABLE IF NOT EXISTS modulegroups (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL DEFAULT ''
)
''')

# Create a new table called 'modulegroupentry'
conn.execute('''
CREATE TABLE IF NOT EXISTS modulegroupentries (
    id INTEGER PRIMARY KEY,
    mapped_module INTEGER NOT NULL,
    mapped_modulegroup INTEGER NOT NULL
)
''')

# Create a new table called 'beacon_tasks'
conn.execute('''
CREATE TABLE IF NOT EXISTS beacon_tasks (
    id INTEGER PRIMARY KEY,
    taskid TEXT NOT NULL,
    timestamp TEXT NOT NULL DEFAULT '',
    source TEXT NOT NULL DEFAULT '',
    sourceBeacon TEXT NOT NULL DEFAULT '',
    targetBeacon TEXT NOT NULL DEFAULT '',
    command TEXT NOT NULL DEFAULT '',
    additionalcomandinfos BLOB DEFAULT X'',
    status TEXT NOT NULL DEFAULT '',
    result TEXT NOT NULL DEFAULT ''
)
''')

# Create a new table called 'agent_logs'
conn.execute('''
CREATE TABLE IF NOT EXISTS agent_logs (
    id INTEGER PRIMARY KEY,
    logcheck TEXT NOT NULL DEFAULT '',
    agentuuid TEXT NOT NULL DEFAULT '',
    timestamp TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL DEFAULT '',
    raw_event TEXT NOT NULL DEFAULT '',
    module_uuid TEXT NOT NULL DEFAULT '',
    executed_module INT NOT NULL,
    check_type TEXT NOT NULL DEFAULT '',
    notified INT NOT NULL DEFAULT 0
)
''')

# Create a new table called 'beacons'
conn.execute('''
CREATE TABLE IF NOT EXISTS beacons (
    id INTEGER PRIMARY KEY,
    uuid TEXT NOT NULL,
    buid TEXT NOT NULL,
    name TEXT NOT NULL DEFAULT '',
    source TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL DEFAULT ''
)
''')

# Create a new table called 'agenttasks'
conn.execute('''
CREATE TABLE IF NOT EXISTS agenttasks (
    id INTEGER PRIMARY KEY,
    timestamp TEXT NOT NULL DEFAULT '',
    agentuuid TEXT NOT NULL,
    command TEXT NOT NULL DEFAULT '',
    executed INT NOT NULL DEFAULT 0
)
''')


conn.commit()
# Close the connection
conn.close()