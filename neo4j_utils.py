from neo4j import GraphDatabase

driver = GraphDatabase.driver("neo4j://localhost:7687", auth=("neo4j", "neo4j"))
session = driver.session(database="academicworld") 

def execute_get_scores(tx, keyword, university_score):
    results = tx.run('MATCH (k:KEYWORD)<-[interest:INTERESTED_IN]-(f:FACULTY)-[a:AFFILIATION_WITH]->(i:INSTITUTE) WHERE k.name=$keyword RETURN i.name AS university, SUM(interest.score) AS score ORDER BY score DESC LIMIT 10', keyword=keyword)
    for record in results:
        university_score[record['university']] = record['score']
    return university_score

def get_scores(input_value):
    university_score = {}
    session.execute_write(execute_get_scores, input_value, university_score)
    return university_score

def executeGetFacultyCount(query, university, faculty_count):
    results = query.run('MATCH (i1:INSTITUTE where i1.name = $university)-[:AFFILIATION_WITH]-(f:FACULTY)-[:INTERESTED_IN]->(k:KEYWORD) WITH k, count(DISTINCT f) AS faculty_count RETURN k.name AS keyword, faculty_count ORDER BY faculty_count DESC LIMIT 5', university=university)
    for record in results:
        faculty_count[record['keyword']] = record['faculty_count']
    return faculty_count

def getFacultyCount(input_value):
    faculty_count = {}
    session.execute_write(executeGetFacultyCount, input_value, faculty_count)
    return faculty_count
