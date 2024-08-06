# CS411 Final Project by James Chong

## Title:
Faculty and Keyword Explorer

![Picture1](https://github.com/user-attachments/assets/add3fcf5-bd2a-4023-b68a-54f87d0169bb)
![Picture2](https://github.com/user-attachments/assets/7d56c1c8-dadd-49ba-9d6f-7b13c17e4fcb)


## Purpose:
The application scenario is designed to assist individuals seeking information about specific professors or universities, with a particular focus on how they relate to specific keywords. The target audience includes aspiring university students, current students, researchers, and professors. The goal is to provide valuable insights into faculty and universities, along with their related keywords. For example, an aspiring student interested in machine learning could easily find universities and specific faculty members that are highly correlated with that field. They could then access detailed information about those faculty members to assist with their decision-making process. Similarly, current students or researchers focused on a particular topic or keyword can use the application to identify relevant universities and faculty members.

## Installation:
The application utilizes the given "academicworld" dataset. In addition, I have created two additional tables, "faculty_rec" and "pub_rec," to store recommended faculty and publications based on user-inputted favorite keywords. I have also developed a "faculty_edit_view" that enables the editing of faculty information. To create these features, I executed the following SQL commands:

```
CREATE TABLE faculty_rec (faculty_id int, faculty_name varchar(512), keyword varchar(512), score double);

CREATE TABLE pub_rec (pub_id varchar(512), title varchar(512), keyword varchar(512), score double);

CREATE VIEW faculty_edit_view AS SELECT name, position, research_interest, email, phone, photo_url FROM faculty;
```

To run the application, users should install the necessary dependencies using pip, which can be accomplished by using the following command:
```
pip install pymysql pymongo neo4j pandas dash dash_bootstrap_components
```

## Usage:
Run ```python3 app.py``` then navigate to the local web server specified by Flask. The credentials to connect to MySQL, MongoDB, and Neo4j must be set within the code to successfully access the databases.

## Design:
The overall design implements a grid structure of 6 different figures in two rows of three figures each. Each of the figures serves a different purpose toward the overall application.

1. Favorite Keywords

When the application is first launched, the user does not have any favorite keywords. However, they can input a valid keyword and click the "add" button to add it to their list of favorites. Based on the user's favorite keywords, the application will recommend relevant professors and publications. Recommendations are ordered by the total number of keywords matched and subsequently by a "score" metric. This score is calculated as the sum of the scores of each match.

2. Faculty Directory

Users can select a university and faculty member either by typing the name or by using the dropdown menu. Once a faculty member has been selected, the widget displays relevant information about the faculty member, detailing their name, position, email address, phone number, research interests, number of publications, university affiliation, and a photo.

3. Top Universities By Keyword

Once the user has entered a valid keyword and presses the "submit" button, the widget will generate a bar graph displaying the total keyword score for the top universities. This score is calculated by summing the scores of each faculty member at the university that pertains to the specified keyword.

4. Edit Faculty Information

This widget allows the user to edit some of the personal data for a faculty member. This includes their name, position, research interests, email, phone, and photo url. The user can select any of these options and then input their desired change. When they click the submit button, that change is then shown in the table. 

5. Search Publications by Faculty

This widget allows for the user to find all of the publications by a specific faculty member. In the dropdown, they can select any faculty member and when they select the faculty member, all of the faculty members publications are listed in the table below. This includes the title, venue, year, and number of citations for each of the publications.

6. Top Keywords by University

This widget allows for the user to find the top keywords of each university. In the dropdown, the user can select a specific university. Then, in the bar graph, the top keywords for that specific university are shown based on faculty associated key words.

## Implementation:
Overall, the application was written in python using the Plotly dash framework. The application utilizes data from three separate locations: SQL, MongoDB, and Neo4j. In order to connect to SQL, the application uses pymysql to connect and run each query. In  order to connect to MongoDB, the application utilizes pymongo to connect and run the queries. It also uses pandas for some of the tables. Lastly, for Neo4j, it utilizes a database driver called GraphDatabase to connect and run the queries. It also uses plotly.graph_objs for some of the graphing and dash_bootstrap_components for some styling.

1. Favorite Keywords

This widget uses SQL queries. User-inputted added keywords generate tuples consisting of id, name or title, and keyword score within tables “faculty_rec” and “pub_rec” where each tuple matches the keyword and does not already exist in the table (input_keyword denotes the inputted keyword):
```
INSERT INTO faculty_rec SELECT faculty.id AS faculty_id, faculty.name AS faculty_name, keyword.name AS keyword_name, score FROM faculty, faculty_keyword, keyword WHERE faculty.id=faculty_keyword.faculty_id AND faculty_keyword.keyword_id=keyword.id AND NOT EXISTS (SELECT * FROM faculty_rec WHERE keyword=input_keyword) AND (keyword.name=input_keyword);

INSERT INTO pub_rec SELECT publication.id AS pub_id, title, keyword.name AS keyword, score FROM publication, publication_keyword, keyword WHERE publication.id=publication_keyword.publication_id AND publication_keyword.keyword_id=keyword.id AND NOT EXISTS (SELECT * FROM pub_rec WHERE keyword=input_keyword) AND (keyword.name=input_keyword);
```
User-inputted deleted keywords remove tuples from tables “faculty_rec” and “pub_rec” where each tuple matches the keyword (input_keyword denotes the inputted keyword):
```
DELETE FROM faculty_rec WHERE keyword=input_keyword;

DELETE FROM pub_rec WHERE keyword=input_keyword;
```
The favorite keywords are displayed as the distinct set of keywords of the union of tables “faculty_rec” and “pub_rec”:
```
SELECT DISTINCT keyword FROM faculty_rec UNION SELECT DISTINCT keyword FROM pub_rec;
```
Faculty and publication recommendations are displayed by selecting from each table, sorted by number of matches then score:
```
SELECT faculty_name, COUNT(*) AS num_matches, SUM(score) AS total_score FROM faculty_rec GROUP BY faculty_id, faculty_name ORDER BY num_matches DESC, total_score DESC LIMIT 5;

SELECT title, COUNT(*) AS num_matches, SUM(score) AS total_score FROM pub_rec GROUP BY pub_id, title ORDER BY num_matches DESC, total_score DESC LIMIT 5;
```

2. Faculty Directory

This widget uses MongoDB queries that select the distinct set of universities, and faculty within that university to display in the dropdown menus (input_value denotes the selected university name):
```
db.faculty.distinct("affiliation.name")

db.faculty.distinct("name", {"affiliation.name": input_value})
```

It then matches the given name and projects the relevant fields of the faculty member (input_value denotes the faculty name):
```
db.faculty.aggregate([{$match: {"name":input_value}}, {$project:{"_id":0, "name":1, "position":1, "email":1, "phone":1, "researchInterest":1, "publications":{$size:"$publications"}, "affiliation.name":1, "photoUrl":1}}])
```

3. Top Universities By Keyword

In this widget, faculty members are matched with the inputted keyword, whose summed scores are then associated with their universities ($keyword denotes the inputted keyword):
```
MATCH (k:KEYWORD)<-[interest:INTERESTED_IN]-(f:FACULTY)-[a:AFFILIATION_WITH]->(i:INSTITUTE) WHERE k.name=$keyword RETURN i.name AS university, SUM(interest.score) AS score ORDER BY score DESC LIMIT 10
```

4. Edit Faculty Information

This widget uses SQL queries to both query and update the database. The SQL query gets information from a specific table view that contains faculty information. When the user selects a specific faculty member, it displays the faculty data from the following query (facultyName denotes input faculty name):
```
SELECT * from faculty_edit_view WHERE name=facultyName LIMIT 1;
```

Once the user selects a faculty member, they can then pick one of the faculty member attributes to edit. Once they select one of the attributes, the following query is used to update the SQL table of faculty information that the view keys off of (columnName denotes attribute to be changed, inputValue denotes value of attribute, facultyName deontes input faculty name):
```
UPDATE faculty SET columnName=inputValue WHERE name=facultyName;
```

Once the data is updated, the first query is run again immediately to display any changes in the faculty data. It displays the data in a table using the dash_table in the dash package.

5. Search Publications by Faculty

This widget uses MongoDB queries to find all of the publications for a specific faculty member. The first query utilizes the faculty member MongoDB query that is also used in figure 2 to get all of the faculty member’s names. Once the user selects a faculty member, it then runs the following query to gather all of the publication data for that faculty member (input_value denotes name of faculty):
```
db.faculty.aggregate([{$match: {"name": input_value}}, {$unwind: "$publications"}, {$lookup: {"from": "publications","localField": "publications","foreignField": "id","as": "pubJoin"}}, {$unwind: "$pubJoin"}, {$project: {"_id": 0,"title": "$pubJoin.title","venue": "$pubJoin.venue","year": "$pubJoin.year","numCitations": "$pubJoin.numCitations"}}])
```
This displays all of the publication data for every publication for the selected faculty member, including title, venue, year, and number of citations. It displays the data in a table using the dash_table in the dash package.

6. Top Keywords by University

This widget uses Neo4j queries to find the top keywords for a given university and display them in a bar graph. It first gathers all the university names using the same university MongoDB query as described in the second figure. Once the university is selected, it uses the following Neo4j query to find the top 5 keywords for the selected university and sort them from largest to smallest (where $university denotes university name):
```
MATCH (i1:INSTITUTE where i1.name = $university)-[:AFFILIATION_WITH]-(f:FACULTY)-[:INTERESTED_IN]->(k:KEYWORD) WITH k, count(DISTINCT f) AS faculty_count RETURN k.name AS keyword, faculty_count ORDER BY faculty_count DESC LIMIT 5
```
Once the keywords are gathered, it then uses the plotly.graph_objs package to graph the data in a bar graph.

## Database Techniques:
1. SQL Stored Procedures: I used stored procedures for the “Favorite Keywords” and “Edit Faculty Information” widgets to drastically shorten the length of SQL queries in Python code, as well as save the code in SQL to efficiently run repeatedly.

    - The insert procedure for “Favorite Keywords” combines insert queries as described in the design section. It is invoked with: ```CALL sql_insert_procedure(input_keyword);```

        ```
        DELIMITER //

        CREATE PROCEDURE sql_insert_procedure( IN input_keyword varchar(512) )

        BEGIN

        INSERT INTO faculty_rec SELECT faculty.id AS faculty_id, faculty.name AS faculty_name, keyword.name AS keyword_name, score FROM faculty, faculty_keyword, keyword WHERE faculty.id=faculty_keyword.faculty_id AND faculty_keyword.keyword_id=keyword.id AND NOT EXISTS (SELECT * FROM faculty_rec WHERE keyword=input_keyword) AND (keyword.name=input_keyword);

        INSERT INTO pub_rec SELECT publication.id AS pub_id, title, keyword.name AS keyword, score FROM publication, publication_keyword,
        keyword WHERE publication.id=publication_keyword.publication_id AND publication_keyword.keyword_id=keyword.id AND NOT EXISTS (SELECT * FROM pub_rec WHERE keyword=input_keyword) AND (keyword.name=input_keyword);

        END //

        DELIMITER ;
        ```

    - The delete procedure for “Favorite Keywords” combines delete queries as described in the design section. It is invoked with ```CALL sql_delete_procedure(input_keyword);```
        ```
        DELIMITER //

        CREATE PROCEDURE sql_delete_procedure( IN input_keyword varchar(512) )

        BEGIN

        DELETE FROM faculty_rec WHERE keyword=input_keyword;

        DELETE FROM pub_rec WHERE keyword=input_keyword;

        END //

        DELIMITER ;
        ```

    - The select procedure for “Favorite Keywords” combines select queries as described in the design section. It is invoked with ```CALL sql_select_procedure;```

        ```
        DELIMITER //

        CREATE PROCEDURE sql_select_procedure()

        BEGIN

        SELECT DISTINCT keyword FROM faculty_rec UNION SELECT DISTINCT keyword FROM pub_rec;

        SELECT faculty_name, COUNT(*) AS num_matches, SUM(score) AS total_score FROM faculty_rec GROUP BY faculty_id, faculty_name ORDER BY num_matches DESC, total_score DESC LIMIT 5;

        SELECT title, COUNT(*) AS num_matches, SUM(score) AS total_score FROM pub_rec GROUP BY pub_id, title ORDER BY num_matches DESC, total_score DESC LIMIT 5;

        END //

        DELIMITER ;
        ```


    - The getFacultyTable procedure for “Edit Faculty Information” queries the faculty table view from SQL for displaying in the app when a user is editing faculty information. It is invoked with ```CALL getFacultyTable_procedure(name);```
        ```
        DELIMITER //

        CREATE PROCEDURE getFacultyTable_procedure( IN input_name varchar(512) )

        BEGIN

        SELECT * from faculty_edit_view WHERE name=input_name LIMIT 1;

        END //

        DELIMITER ;
        ```

    - The updateFacultyTable procedure for “Edit Faculty Information” updates the faculty table in the SQL database. The faculty table view used in the getFacultyTable function uses this table. It is invoked with ```CALL updateFacultyTable_procedure(name, column, input);```

        ```
        DELIMITER //

        CREATE PROCEDURE updateFacultyTable_procedure( IN input_name varchar(512), IN input_column varchar(512), IN input_value varchar(512) )

        BEGIN

        SET @s=CONCAT('UPDATE faculty SET ', input_column, '="', input_value, '" WHERE name="', input_name, '"');

        PREPARE stmt1 FROM @s;

        EXECUTE stmt1;

        DEALLOCATE PREPARE stmt1;

        END //

        DELIMITER ;
        ```

2. SQL View: I used a view for the “Edit Faculty Information” widget. This view gathers all of the necessary faculty information that the app allows the user to edit. 

    ```
    CREATE VIEW faculty_edit_view AS SELECT name, position, research_interest, email, phone, photo_url FROM faculty;
    ```

3. MongoDB Indexing: I used indexing for “Faculty Directory” to quickly search and retrieve information with queries that repeatedly lookup the same column.

    ```
    db.faculty.createIndex({name: 1})
    ```
