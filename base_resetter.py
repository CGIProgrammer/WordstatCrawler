import pymysql
import sqlite3

sql_create_sections = '''CREATE TABLE IF NOT EXISTS sections(
    id VARCHAR(9),
    name VARCHAR(300),
    PRIMARY KEY (ID)
);'''
sql_create_subsections_rel = '''CREATE TABLE IF NOT EXISTS sections_relations(
    node_id VARCHAR(9),
    parent_id VARCHAR(9),
    level INT(2),
    FOREIGN KEY (node_id)  REFERENCES sections(id),
    FOREIGN KEY (parent_id)  REFERENCES sections(id)
);'''
sql_countries = '''
CREATE TABLE IF NOT EXISTS countries
(
    id INT(5),
    name VARCHAR(200),
    PRIMARY KEY(id)
);'''
sql_regions = '''
CREATE TABLE IF NOT EXISTS regions
(
    id INT(5),
    country INT(5),
    name VARCHAR(200),
    PRIMARY KEY(id),
    FOREIGN KEY (country) REFERENCES countries(id)
);'''
sql_statuses = '''
CREATE TABLE IF NOT EXISTS statuses
(
    ID INT(2) ,
    name CHAR(50),
    PRIMARY KEY (ID)
);'''
sql_requests_history = '''
CREATE TABLE IF NOT EXISTS requests_history
(
    section         INT(9),
    period          DATE,
    requests_count  INT(9),
    update_date     DATETIME,
    status          INT(2),
    FOREIGN KEY (section)  REFERENCES sections(ID),
    FOREIGN KEY (status) REFERENCES statuses(ID)
);'''
sql_region_stats = '''
CREATE TABLE IF NOT EXISTS region_stats(
    section         INT(9),
    region          INT(9),
    requests_count  INT(9),
    update_date     DATETIME,
    status          INT(2),
    FOREIGN KEY (section)  REFERENCES sections(ID),
    FOREIGN KEY (region) REFERENCES regions(ID),
    FOREIGN KEY (status) REFERENCES statuses(ID)
);'''
sql_requests = '''
CREATE TABLE IF NOT EXISTS requests(
    request TEXT(300),
    section VARCHAR(9),
    FOREIGN KEY (section) REFERENCES sections(ID),
    PRIMARY KEY (request)
);'''
sqlite_conn = sqlite3.connect("UN_categories.sqlite")

sqlite_curs = sqlite_conn.cursor()
sqlite_conn.execute('PRAGMA encoding = "UTF-8";')
sqlite_curs.execute('DROP TABLE IF EXISTS sections_relations;')
sqlite_curs.execute('DROP TABLE IF EXISTS sections;')
sqlite_curs.execute('DROP TABLE IF EXISTS countries;')
sqlite_curs.execute('DROP TABLE IF EXISTS regions;')
sqlite_curs.execute('DROP TABLE IF EXISTS statuses;')
sqlite_curs.execute('DROP TABLE IF EXISTS requests_history;')
sqlite_curs.execute('DROP TABLE IF EXISTS region_stats;')

sqlite_curs.execute(sql_create_sections)
sqlite_curs.execute(sql_create_subsections_rel)
sqlite_curs.execute(sql_countries)
sqlite_curs.execute(sql_regions)
sqlite_curs.execute(sql_statuses)
sqlite_curs.execute(sql_requests_history)
sqlite_curs.execute(sql_region_stats)
sqlite_curs.execute(sql_requests)

fp = open('/home/ivan/UN_stat.txt', 'r')
labels = 'abcdefghijklmnopqrstuvwxyz'

lines = fp.read().split('\n')
i=0

sections = {}
subsections = {}
groups = {}
subgroups = {}

while i < len(lines):
    line = lines[i].strip(' ').split()
    if not line:
        i += 1
        continue
    if line[0] == 'Раздел' and line[1][1]=='.':
        section = ' '.join(line[2:])
        section_id = line[1][0]
        sections[section_id] = section
        print(section_id)
        try:
            sqlite_curs.execute('insert into sections(id, name) values("%s", "%s")' % (section_id, section))
        except Exception as e:
            print(e)
            print(len(section), section)
            exit(-1)
        
    elif line[0] == 'Подраздел':
        subsection_id = line[1]
        i += 1
        subsection = lines[i].strip(' ')
        print(section_id,subsection_id)
        subsections[subsection_id] = [subsection, sections[section_id]]
        sqlite_curs.execute('insert into sections(id, name) values("%s", "%s")' % (subsection_id, subsection))
        sqlite_curs.execute('insert into sections_relations(node_id, parent_id, level) values("%s", "%s", 1)' % (subsection_id, section_id))
        group = None
        subgroup = None
        group_id = None
        subgroup_id = None
        
    elif line[0].isdigit() and len(line[0])==3:
        group_id = line[0]
        if not lines[i+1].strip(' ').isdigit():
            i += 1
            group = lines[i].strip(' ')
            print(section_id,subsection_id, group_id)
            sqlite_curs.execute('insert into sections(id, name) values("%s", "%s")' % (group_id, group))
            sqlite_curs.execute('insert into sections_relations(node_id, parent_id, level) values("%s", "%s", 1)' % (group_id, subsection_id))
            sqlite_curs.execute('insert into sections_relations(node_id, parent_id, level) values("%s", "%s", 2)' % (group_id, section_id))
        else:
            group = None
        subgroup = None
        subgroup_id = None
        
    elif line[0].isdigit() and len(line[0])==4:
        subgroup_id = line[0]
        i += 1
        subgroup = lines[i].strip(' ')
        if group is None and group_id is not None:
            group = subgroup
            print(section_id,subsection_id, group_id)
            
            sqlite_curs.execute('insert into sections(id, name) values("%s", "%s")' % (group_id, group))
            sqlite_curs.execute('insert into sections_relations(node_id, parent_id, level) values("%s", "%s", 1)' % (group_id, subsection_id))
            sqlite_curs.execute('insert into sections_relations(node_id, parent_id, level) values("%s", "%s", 2)' % (group_id, section_id))
        
        print(section_id,subsection_id, group_id, subgroup_id, subgroup)
        sqlite_curs.execute('insert into sections(id, name) values("%s", "%s")' % (subgroup_id, subgroup))
        if group_id:
            sqlite_curs.execute('insert into sections_relations(node_id, parent_id, level) values("%s", "%s", 1)' % (subgroup_id, group_id))
        if subsection_id:
            sqlite_curs.execute('insert into sections_relations(node_id, parent_id, level) values("%s", "%s", 2)' % (subgroup_id, subsection_id))
        sqlite_curs.execute('insert into sections_relations(node_id, parent_id, level) values("%s", "%s", 3)' % (subgroup_id, section_id))
        
    i += 1
    
sqlite_conn.commit()
sqlite_conn.close()
