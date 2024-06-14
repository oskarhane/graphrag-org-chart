import os
from os.path import abspath, dirname
from neo4j import GraphDatabase
from dotenv import load_dotenv
load_dotenv()

NEO4J_URL = os.getenv("NEO4J_URL")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

PATH = dirname(dirname(abspath(__file__)))
FILE = "data/engineering.csv"
FILE_PATH = f"{PATH}/{FILE}"

def main(path):
    file_contents = read_file(path)
    data = map_data(file_contents)
    # print(data[0:3])

    with GraphDatabase.driver(NEO4J_URL, auth=(NEO4J_USER, NEO4J_PASSWORD)) as driver:
        write_titles(driver, data)
        write_managers(driver, data)
        write_locations(driver, data)
        write_teams(driver, data)
        write_engineers(driver, data)

def write_engineers(driver, data):
    # we want to create relationships between engineers and their teams, managers, and titles
    cypher = (
        "WITH $lines as lines UNWIND lines as line "
        "MATCH (title:Title {name: line[3]}), (manager:Manager {name: line[4]}), (location:Location {name: line[6]}), (team:Team {name: line[7]}) "
        "WITH line, title, manager, location, team "
        "MERGE (p:Person {name: line[1] + ' ' + line[0]}) "
        "MERGE (p)-[:HAS_TITLE]->(title) "
        "MERGE (p)<-[:MANAGES]-(manager) "
        "MERGE (p)-[:LOCATED_AT]->(location) "
        "MERGE (p)-[:MEMBER_OF]->(team) "
    )
    driver.execute_query(cypher, lines=data)

def write_teams(driver, data):
    # team names are in index 7
    # find unique team names
    team_names = list(set([line[7] for line in data]))
    print(team_names)
    driver.execute_query("UNWIND $team_names as team_name MERGE (t:Team {name: team_name})", team_names=team_names)

def write_locations(driver, data):
    # locations are in index 6
    # find unique locations
    locations = list(set([line[6] for line in data]))
    print(locations)
    driver.execute_query("UNWIND $locations as location MERGE (l:Location {name: location})", locations=locations)

def write_managers(driver, data):
    # managers are in index 4
    # find unique managers
    managers = list(set([line[4] for line in data]))
    print(managers)
    driver.execute_query("UNWIND $managers as manager MERGE (m:Manager {name: manager})", managers=managers)

def write_titles(driver, data):
    # titles are in index 3
    # find unique titles
    titles = list(set([line[3] for line in data]))
    print(titles)
    driver.execute_query("UNWIND $titles as title MERGE (t:Title {name: title})", titles=titles)

def map_data(file_contents):
    # split on newline, then split on comma, and then strip double quotes
    lines = file_contents.split("\n")
    filtered_list = []
    for line in lines:
        if line:
            filtered_list.append(list(map(lambda x: x.strip('"'), line.split(","))))
    
    return filtered_list

def read_file(path):
    with open(path, "r") as file:
        # skip first line
        file.readline()
        return file.read()


if __name__ == "__main__":
    main(FILE_PATH)
