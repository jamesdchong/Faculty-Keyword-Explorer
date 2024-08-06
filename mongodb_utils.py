import pymongo
import pandas as pd

conn=pymongo.MongoClient()
db = conn.academicworld

def get_faculty_info(input_value):
    query = db.faculty.aggregate([
        {"$match": {"name":input_value}},
        {"$project":{"_id":0, "name":1, "position":1, "email":1, "phone":1, "researchInterest":1, "publications":{"$size":"$publications"}, "affiliation.name":1, "photoUrl":1}}
    ])

    faculty_dict = {}
    for x in query:
        for key in x.keys():
            if x[key] is None:
                faculty_dict[key] = "N/A"
            else:
                faculty_dict[key] = x[key]
                
    return faculty_dict

def get_universities():
    query = db.faculty.distinct("affiliation.name")
    return query

def get_faculty(input_value):
    query = db.faculty.distinct("name", {"affiliation.name": input_value})
    return query

def get_faculty_all():
    query = db.faculty.distinct("name")
    return query

def getFacultyPublications(input_value):
    query = db.faculty.aggregate([{"$match": {"name": input_value}},
        {"$unwind": "$publications"},
        {"$lookup": {"from": "publications","localField": "publications","foreignField": "id","as": "pubJoin"}},
        {"$unwind": "$pubJoin"},
        {"$project": {"_id": 0,"title": "$pubJoin.title","venue": "$pubJoin.venue","year": "$pubJoin.year","numCitations": "$pubJoin.numCitations"}}
    ])
    publication_dict = {}
    data = []
    for doc in query:
        row_dict = {'title': doc['title'], 'venue': doc['venue'], 'year': doc['year'], 'numCitations': doc['numCitations']}
        data.append(row_dict)

    for x in query:
        for key in x.keys():
            if x[key] is None:
                publication_dict[key] = "N/A"
            else:
                publication_dict[key] = x[key]
                  
    return data