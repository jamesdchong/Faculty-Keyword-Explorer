import pymysql

db = pymysql.connect(host='localhost',
                user='root',
                password='root_password',
                database='academicworld',
                charset='utf8mb4',
                port=3306,
                cursorclass=pymysql.cursors.DictCursor)

def sql_insert(input_value):
    with db.cursor() as cursor:
        sql = 'CALL sql_insert_procedure("' + input_value + '")'
        cursor.execute(sql)
        db.commit()
    
def sql_delete(input_value):
    with db.cursor() as cursor:
        sql = 'CALL sql_delete_procedure("' + input_value + '")'
        cursor.execute(sql)
        db.commit()

def sql_select():
    with db.cursor() as cursor:
        sql = 'CALL sql_select_procedure;'
        cursor.execute(sql)
        result1 = cursor.fetchall()
        cursor.nextset()
        result2 = cursor.fetchall()
        cursor.nextset()
        result3 = cursor.fetchall()
        return result1, result2, result3

def getFacultyTable(facultyName):
    with db.cursor() as cursor:
        sql = 'CALL getFacultyTable_procedure("' + facultyName + '");'
        cursor.execute(sql)
        facultyTable = cursor.fetchall()
        return facultyTable
    
def updateFacultyTable(facultyName, columnName, inputValue):
    with db.cursor() as cursor:
        sql = 'CALL updateFacultyTable_procedure("' + facultyName + '", "' + columnName + '", "' + inputValue + '");'
        cursor.execute(sql)
        db.commit()
