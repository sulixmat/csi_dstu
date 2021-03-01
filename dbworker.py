import pymysql
from pymysql.cursors import DictCursor
import json
from config import config, questions
from .statistic import calculate_the_average_score_by_struct

db_config = config['db']


def open_close_connection(qsl_query_func):
    def open_close(*args):
        connection = connect()
        cursor = connection.cursor()
        try:
            response = qsl_query_func(*args, cursor)
        finally:
            pass
        connection.commit()
        connection.close()
        return response

    return open_close


def connect() -> pymysql.connections.Connection:
    try:
        connection = pymysql.connect(
            host=db_config['IP'],
            user=db_config['user'],
            password=db_config['password'],
            db=db_config['name'],
            charset='utf8mb4',
            cursorclass=DictCursor
        )

        cursor = connection.cursor()
        cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS `struct`
            (
                id INTEGER NOT NULL PRIMARY KEY AUTO_INCREMENT,
                name TEXT,
                mean_rateing FLOAT
            )
            '''
        )

        cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS `questions`
            (
                id INTEGER NOT NULL PRIMARY KEY AUTO_INCREMENT,
                q1 FLOAT,
                q2 FLOAT,
                q3 FLOAT,
                q4 FLOAT,
                q5 FLOAT,
                q6 TEXT,
                struct_id INT NOT NULL,
                FOREIGN KEY (struct_id)  REFERENCES struct (id)
            )
            '''
        )

        connection.commit()
        return connection
    except Exception as e:
        print('error is: ', e)
        return False


@open_close_connection
def insert_form(q1: int, q2: int, q3: int, q4: int, q5: int, q6: int, struct_name: str, cursor=None) -> None:
    cursor.execute('SELECT id FROM struct WHERE name = %s', (struct_name,))
    struct_id = cursor.fetchone()
    struct_id = struct_id['id']

    cursor.execute(
        '''
        INSERT INTO `questions`(q1, q2, q3, q4, q5, q6, struct_id)

        VALUES(%s, %s, %s, %s, %s, %s, %s)
        ''',
        (q1, q2, q3, q4, q5, q6, struct_id))


@open_close_connection
def insert_struct(name: str, cursor=None) -> None:
    cursor.execute(
        '''
        INSERT 
        INTO struct(name)
        VALUES(%s)
        ''',
        (name,))


@open_close_connection
def update_mean(struct_name: str, cursor=None):
    cursor.execute('SELECT id FROM struct WHERE name = %s', (struct_name,))
    struct_id = cursor.fetchone()
    struct_id = struct_id['id']

    cursor.executemany(
        '''
        SELECT q1,q2,q3,q4,q5
        FROM questions
        WHERE struct_id = %s 
        ''',
        (struct_id,)
    )

    stats = cursor.fetchall()
    result = calculate_the_average_score_by_struct(stats)
    result = result/len(result)

    cursor.execute(
        '''
        UPDATE struct
        SET mean_rateing = %s
        WHERE id = %s
        ''',
        (result, struct_id))


@open_close_connection
def get_all_form_by_struct(struct_name: str, cursor=None):
    cursor.execute(
        '''
        SELECT q1, q2, q3, q4, q5
        FROM questions INNER JOIN struct ON struct.id = questions.struct_id
        WHERE struct.name = %s
        ''', (struct_name,))

    stats = cursor.fetchall()
    return stats


@open_close_connection
def struct_stats(cursor=None):
    cursor.execute(
        '''
        SELECT name, mean_rateing
        FROM struct
        '''
    )
    data = cursor.fetchall()

    stats = []
    for item in data:
        row = '{} - {} из 100'.format(item['name'], item['mean_rateing'])
        stats.append(row)

    return stats


@open_close_connection
def get_all_stats(cursor=None):
    cursor.executemany(
        '''
        SELECT q1,q2,q3,q4,q5
        FROM questions
        ''')

    cursor.fetchall()


@open_close_connection
def respondents_count_by_struct(struct_name: str, cursor=None):
    cursor.execute(
        '''
        SELECT q1, q2, q3, q4, q5
        FROM questions INNER JOIN struct ON struct.id = questions.struct_id
        WHERE struct.name = %s
        ''', (struct_name,))

    return len(cursor.fetchall())

