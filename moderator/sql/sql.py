import mysql.connector


class Room(object):
    def __init__(self, room_id, room_membership, room_num, room_active, room_name, room_type):
        self.room_id = room_id
        self.room_membership = room_membership
        self.room_num = room_num
        self.room_active = room_active
        self.room_name = room_name
        self.room_type = room_type


class User(object):
    def __init__(self, user_id, room_id, user_name, user_email):
        self.user_id = user_id
        self.room_id = room_id
        self.user_name = user_name
        self.user_email = user_email


class Question(object):
    def __init__(self, faq_id, room_id, user_id, faq_time, faq_text):
        self.faq_id = faq_id
        self.room_id = room_id
        self.user_id = user_id
        self.faq_time = faq_time
        self.faq_text = faq_text


class Faq(object):
    def __init__(self, faq_id, f_room_id, faq_text, faq_time, answer_text, answer_time, q_room_id, q_user_name, r_user_name):
        self.faq_id = faq_id
        self.f_room_id = f_room_id
        self.faq_text = faq_text
        self.faq_time = faq_time
        self.answer_text = answer_text
        self.answer_time = answer_time
        self.q_room_id = q_room_id
        self.q_user_name = q_user_name
        self.r_user_name = r_user_name


class Database(object):
    def __init__(self, host, user, password, database):
        try:
            self.__db = mysql.connector.connect(
                user=user,
                password=password,
                host=host,
                database=database
            )
        except mysql.connector.Error as err:
            raise err

        self.__tables = self.Tables()
        self.__insert = self.Insert()
        self.__update = self.Update()
        self.__delete = self.Delete()
        self.__select = self.Select()

    def __del__(self):
        self.__db.close()

    def __commit_sql(self, sql, data):
        try:
            cursor = self.__db.cursor()
            cursor.execute(sql, data)
            self.__db.commit()
            cursor.close()
            return True
        except mysql.connector.Error as err:
            print("ERROR: Cannot execute SQL command in the database.")
            print(err)
            return False

    def __query_sql(self, sql, data):
        try:
            cursor = self.__db.cursor()
            cursor.execute(sql, data)
            result = cursor.fetchall()
            cursor.close()
            return result
        except mysql.connector.Error as err:
            print("ERROR: Cannot query SQL command in the database.")
            print(err)
            return None

    def create_tables(self):
        self.__commit_sql(self.__tables.create_rooms(), None)
        self.__commit_sql(self.__tables.create_users(), None)
        self.__commit_sql(self.__tables.create_faq(), None)
        self.__commit_sql(self.__tables.create_answers(), None)
        self.__commit_sql(self.__tables.create_comments(), None)
        self.__commit_sql(self.__tables.create_messages(), None)
        self.__commit_sql(self.__tables.create_media(), None)
        self.__commit_sql(self.__tables.create_jokes(), None)

    def insert_room(self, data):
        return self.__commit_sql(self.__insert.insert_room(), data)

    def insert_user(self, data):
        return self.__commit_sql(self.__insert.insert_user(), data)

    def insert_faq(self, data):
        return self.__commit_sql(self.__insert.insert_faq(), data)

    def insert_answer(self, data):
        return self.__commit_sql(self.__insert.insert_answer(), data)

    def insert_comment(self, data):
        return self.__commit_sql(self.__insert.insert_comment(), data)

    def insert_message(self, data):
        return self.__commit_sql(self.__insert.insert_message(), data)

    def insert_media(self, data):
        return self.__commit_sql(self.__insert.insert_media(), data)

    def insert_joke(self, data):
        return self.__commit_sql(self.__insert.insert_joke(), data)

    def update_room(self, data):
        return self.__commit_sql(self.__update.update_room(), data)

    def delete_faq(self, data):
        return self.__commit_sql(self.__delete.delete_faq(), data)

    def delete_message(self, data):
        return self.__commit_sql(self.__delete.delete_message(), data)

    def delete_media(self, data):
        return self.__commit_sql(self.__delete.delete_media(), data)

    def delete_joke(self, data):
        return self.__commit_sql(self.__delete.delete_joke(), data)

    def select_room(self, data):
        result = self.__query_sql(self.__select.select_room(), data)
        if result:
            return Room(result[0][0], result[0][1], result[0][2], result[0][3], result[0][4], result[0][5])
        else:
            return None

    def select_room_all(self, data):
        return self.__query_sql(self.__select.select_room_all(), data)

    def select_room_cnt(self, data):
        return self.__query_sql(self.__select.select_room_cnt(), data)

    def select_space(self, data):
        result = self.__query_sql(self.__select.select_space(), data)
        if result:
            return result[0][0]
        else:
            return None

    def select_user(self, data):
        result = self.__query_sql(self.__select.select_user(), data)
        if result:
            return User(result[0][0], result[0][1], result[0][2], result[0][3])
        else:
            return None

    def select_faq(self, data):
        result = self.__query_sql(self.__select.select_faq(), data)
        if result:
            return Question(result[0][0], result[0][1], result[0][2], result[0][3], result[0][4])
        else:
            return None

    def select_faq_all(self, data):
        return self.__query_sql(self.__select.select_faq_all(), data)

    def select_faq_room(self, data):
        return self.__query_sql(self.__select.select_faq_room(), data)

    def select_faq_user(self, data):
        return self.__query_sql(self.__select.select_faq_user(), data)

    def select_faq_id(self, data):
        result = self.__query_sql(self.__select.select_faq_id(), data)
        if result:
            return Question(result[-1][0], result[-1][1], result[-1][2], result[-1][3], result[-1][4])
        else:
            return None

    def select_faq_messages(self, data):
        return self.__query_sql(self.__select.select_faq_msg(), data)

    def select_faq_thread(self, data):
        return self.__query_sql(self.__select.select_faq_thread(), data)

    def select_faq_space(self, data):
        return self.__query_sql(self.__select.select_faq_space(), data)

    def select_faq_author(self, data):
        return self.__query_sql(self.__select.select_faq_author(), data)

    def select_answer(self, data):
        return self.__query_sql(self.__select.select_answer(), data)

    def select_comment(self, data):
        return self.__query_sql(self.__select.select_comment(), data)

    def select_message(self, data):
        return self.__query_sql(self.__select.select_message(), data)

    def select_media(self, data):
        return self.__query_sql(self.__select.select_media(), data)

    def select_media_all(self, data):
        return self.__query_sql(self.__select.select_media_all(), data)

    def select_joke(self, data):
        return self.__query_sql(self.__select.select_joke(), data)

    def select_joke_rand(self, data):
        return self.__query_sql(self.__select.select_joke_rand(), data)

    def select_joke_all(self, data):
        return self.__query_sql(self.__select.select_joke_all(), data)

    class Tables(object):
        def __init__(self):
            self.__rooms = (
                "CREATE TABLE IF NOT EXISTS rooms("
                "room_id VARCHAR(128) NOT NULL,"
                "room_membership VARCHAR(256) NOT NULL,"
                "room_active TINYINT NOT NULL,"
                "room_num INT NOT NULL,"
                "room_name VARCHAR(128) COLLATE utf8_unicode_ci NOT NULL,"
                "room_type VARCHAR(16) NOT NULL,"
                "PRIMARY KEY(room_id))"
            )
            self.__users = (
                "CREATE TABLE IF NOT EXISTS users("
                "user_id VARCHAR(128) NOT NULL,"
                "room_id VARCHAR(128),"
                "user_name VARCHAR(128) COLLATE utf8_unicode_ci NOT NULL,"
                "user_email VARCHAR(32) NOT NULL,"
                "PRIMARY KEY(user_id))"
            )
            self.__faq = (
                "CREATE TABLE IF NOT EXISTS faq("
                "faq_id INT NOT NULL AUTO_INCREMENT,"
                "room_id VARCHAR(128) NOT NULL,"
                "user_id VARCHAR(128) NOT NULL,"
                "faq_time DATETIME NOT NULL,"
                "faq_text TEXT COLLATE utf8_unicode_ci NOT NULL,"
                "PRIMARY KEY(faq_id),"
                "CONSTRAINT room_f_constr FOREIGN KEY(room_id)"
                "REFERENCES rooms(room_id) ON DELETE CASCADE ON UPDATE CASCADE,"
                "CONSTRAINT user_f_constr FOREIGN KEY(user_id)"
                "REFERENCES users(user_id) ON DELETE CASCADE ON UPDATE CASCADE)"
            )
            self.__answers = (
                "CREATE TABLE IF NOT EXISTS answers("
                "answer_id INT NOT NULL,"
                "user_id VARCHAR(128) NOT NULL,"
                "answer_time DATETIME NOT NULL,"
                "answer_text TEXT COLLATE utf8_unicode_ci NOT NULL,"
                "PRIMARY KEY(answer_id),"
                "CONSTRAINT user_a_constr FOREIGN KEY(user_id)"
                "REFERENCES users(user_id) ON DELETE CASCADE ON UPDATE CASCADE,"
                "CONSTRAINT faq_a_constr FOREIGN KEY(answer_id)"
                "REFERENCES faq(faq_id) ON DELETE CASCADE ON UPDATE CASCADE)"
            )
            self.__comments = (
                "CREATE TABLE IF NOT EXISTS comments("
                "comment_id INT NOT NULL AUTO_INCREMENT,"
                "user_id VARCHAR(128) NOT NULL,"
                "faq_id INT NOT NULL,"
                "comment_time DATETIME NOT NULL,"
                "comment_text TEXT COLLATE utf8_unicode_ci NOT NULL,"
                "PRIMARY KEY(comment_id),"
                "CONSTRAINT user_c_constr FOREIGN KEY(user_id)"
                "REFERENCES users(user_id) ON DELETE CASCADE ON UPDATE CASCADE,"
                "CONSTRAINT faq_c_constr FOREIGN KEY(faq_id)"
                "REFERENCES faq(faq_id) ON DELETE CASCADE ON UPDATE CASCADE)"
            )
            self.__messages = (
                "CREATE TABLE IF NOT EXISTS messages("
                "message_id VARCHAR(128) NOT NULL,"
                "room_id VARCHAR(128) NOT NULL,"
                "user_id VARCHAR(128) NOT NULL,"
                "faq_id INT,"
                "message_time DATETIME NOT NULL,"
                "message_text TEXT COLLATE utf8_unicode_ci NOT NULL,"
                "PRIMARY KEY(message_id),"
                "CONSTRAINT room_m_constr FOREIGN KEY(room_id)"
                "REFERENCES rooms(room_id) ON DELETE CASCADE ON UPDATE CASCADE,"
                "CONSTRAINT user_m_constr FOREIGN KEY(user_id)"
                "REFERENCES users(user_id),"
                "CONSTRAINT faq_m_constr FOREIGN KEY(faq_id)"
                "REFERENCES faq(faq_id) ON DELETE CASCADE ON UPDATE CASCADE)"
            )
            self.__media = (
                "CREATE TABLE IF NOT EXISTS media("
                "media_id INT NOT NULL AUTO_INCREMENT,"
                "room_id VARCHAR(128) NOT NULL,"
                "user_id VARCHAR(128) NOT NULL,"
                "media_link TEXT COLLATE utf8_unicode_ci NOT NULL,"
                "media_text TEXT COLLATE utf8_unicode_ci NOT NULL,"
                "PRIMARY KEY(media_id),"
                "CONSTRAINT room_d_constr FOREIGN KEY(room_id)"
                "REFERENCES rooms(room_id) ON DELETE CASCADE ON UPDATE CASCADE,"
                "CONSTRAINT user_d_constr FOREIGN KEY(user_id)"
                "REFERENCES users(user_id) ON DELETE CASCADE ON UPDATE CASCADE)"
            )
            self.__jokes = (
                "CREATE TABLE IF NOT EXISTS jokes("
                "joke_id INT NOT NULL AUTO_INCREMENT,"
                "joke_text TEXT COLLATE utf8_unicode_ci NOT NULL,"
                "joke_lang VARCHAR(4) NOT NULL,"
                "PRIMARY KEY(joke_id))"
            )

        def create_rooms(self):
            return self.__rooms

        def create_users(self):
            return self.__users

        def create_faq(self):
            return self.__faq

        def create_answers(self):
            return self.__answers

        def create_comments(self):
            return self.__comments

        def create_messages(self):
            return self.__messages

        def create_media(self):
            return self.__media

        def create_jokes(self):
            return self.__jokes

    class Insert(object):
        def __init__(self):
            self.__room = (
                "INSERT INTO rooms(room_id, room_membership, room_num, room_active, room_name, room_type)"
                "VALUES(%s, %s, %s, 1, %s, %s) ON DUPLICATE KEY UPDATE room_active = 1"
            )
            self.__user = (
                "INSERT INTO users(user_id, room_id, user_name, user_email)"
                "VALUES(%s, %s, %s, %s) ON DUPLICATE KEY UPDATE room_id = %s"
            )
            self.__faq = "INSERT INTO faq(room_id, user_id, faq_time, faq_text) VALUES(%s, %s, NOW(), %s)"
            self.__answer = (
                "INSERT INTO answers(answer_id, user_id, answer_time, answer_text) VALUES(%s, %s, NOW(), %s) "
                "ON DUPLICATE KEY UPDATE user_id = %s, answer_time = NOW(), answer_text = %s"
            )
            self.__comment = (
                "INSERT INTO comments(user_id, faq_id, comment_time, comment_text) VALUES(%s, %s, NOW(), %s)"
            )
            self.__message = (
                "INSERT INTO messages(message_id, room_id, user_id, faq_id, message_time, message_text)"
                "VALUES(%s, %s, %s, %s, NOW(), %s)"
            )
            self.__media = (
                "INSERT INTO media(room_id, user_id, media_link, media_text) VALUES(%s, %s, %s, %s)"
            )
            self.__joke = "INSERT INTO jokes(joke_text, joke_lang) VALUES(%s, %s)"

        def insert_room(self):
            return self.__room

        def insert_user(self):
            return self.__user

        def insert_faq(self):
            return self.__faq

        def insert_answer(self):
            return self.__answer

        def insert_comment(self):
            return self.__comment

        def insert_message(self):
            return self.__message

        def insert_media(self):
            return self.__media

        def insert_joke(self):
            return self.__joke

    class Update(object):
        def __init__(self):
            self.__room = "UPDATE rooms SET room_active = %s WHERE room_id = %s"

        def update_room(self):
            return self.__room

    class Delete(object):
        def __init__(self):
            self.__faq = "DELETE FROM faq WHERE faq_id = %s"
            self.__message = "DELETE FROM messages WHERE message_id = %s"
            self.__media = "DELETE FROM media WHERE media_id = %s"
            self.__joke = "DELETE FROM jokes WHERE joke_id = %s"

        def delete_faq(self):
            return self.__faq

        def delete_message(self):
            return self.__message

        def delete_media(self):
            return self.__media

        def delete_joke(self):
            return self.__joke

    class Select(object):
        def __init__(self):
            self.__room = "SELECT * FROM rooms WHERE room_id = %s"
            self.__room_all = "SELECT * FROM rooms ORDER BY room_num"
            self.__room_cnt = "SELECT COUNT(*) + 1 FROM rooms"
            self.__space = "SELECT * FROM rooms WHERE room_num = %s"
            self.__user = "SELECT * FROM users WHERE user_id = %s"
            self.__faq = "SELECT * FROM faq WHERE faq_id = %s"
            self.__faq_all = "SELECT * FROM faq ORDER BY faq_id"
            self.__faq_room = "SELECT * FROM faq WHERE room_id = %s"
            self.__faq_user = "SELECT * FROM faq WHERE user_id = %s"
            self.__faq_id = "SELECT * FROM faq WHERE room_id = %s AND user_id = %s ORDER BY faq_id"
            self.__faq_msg = "SELECT message_id FROM messages WHERE faq_id = %s"
            self.__faq_thread = (
                "SELECT f.faq_id, f.faq_text, a.answer_text, u.user_name FROM faq f INNER JOIN users u "
                "ON u.user_id = f.user_id LEFT JOIN answers a ON f.faq_id = a.answer_id ORDER BY faq_id"
            )
            self.__faq_space = (
                "SELECT f.faq_id, f.faq_text, a.answer_text, u.user_name FROM faq f INNER JOIN users u "
                "ON u.user_id = f.user_id LEFT JOIN answers a ON f.faq_id = a.answer_id "
                "WHERE f.room_id = %s ORDER BY faq_id"
            )
            self.__faq_author = (
                "SELECT f.faq_id, f.faq_text, a.answer_text, u.user_name FROM faq f INNER JOIN users u "
                "ON u.user_id = f.user_id LEFT JOIN answers a ON f.faq_id = a.answer_id "
                "WHERE f.user_id = %s ORDER BY faq_id"
            )
            self.__answer = (
                "SELECT f.faq_id, f.room_id, f.faq_text, f.faq_time, a.answer_text, a.answer_time, "
                "q.room_id, q.user_name, r.user_name "
                "FROM faq f INNER JOIN users q ON q.user_id = f.user_id LEFT JOIN answers a ON f.faq_id = a.answer_id "
                "LEFT JOIN users r ON r.user_id = a.user_id WHERE f.faq_id = %s"
            )
            self.__comment = (
                "SELECT c.comment_time, c.comment_text, u.user_name FROM comments c JOIN users u "
                "ON u.user_id = c.user_id WHERE c.faq_id = %s ORDER BY c.comment_time"
            )
            self.__message = (
                "SELECT m.message_id, m.user_id, r.room_type FROM messages m INNER JOIN rooms r "
                "ON m.room_id = r.room_id WHERE m.user_id = %s AND r.room_id = %s"
            )
            self.__media = "SELECT * FROM media WHERE media_id = %s"
            self.__media_all = (
                    "SELECT m.media_id, m.media_text, m.media_link, u.user_name FROM media m INNER JOIN users u "
                    "ON m.user_id = u.user_id ORDER BY m.media_id"
            )
            self.__joke = "SELECT * FROM jokes WHERE joke_id = %s"
            self.__joke_rand = "SELECT joke_text FROM jokes WHERE joke_lang = %s ORDER BY RAND() LIMIT 1"
            self.__joke_all = "SELECT * FROM jokes WHERE joke_lang = %s"

        def select_room(self):
            return self.__room

        def select_room_all(self):
            return self.__room_all

        def select_room_cnt(self):
            return self.__room_cnt

        def select_space(self):
            return self.__space

        def select_user(self):
            return self.__user

        def select_faq(self):
            return self.__faq

        def select_faq_all(self):
            return self.__faq_all

        def select_faq_room(self):
            return self.__faq_room

        def select_faq_user(self):
            return self.__faq_user

        def select_faq_id(self):
            return self.__faq_id

        def select_faq_msg(self):
            return self.__faq_msg

        def select_faq_thread(self):
            return self.__faq_thread

        def select_faq_space(self):
            return self.__faq_space

        def select_faq_author(self):
            return self.__faq_author

        def select_answer(self):
            return self.__answer

        def select_comment(self):
            return self.__comment

        def select_message(self):
            return self.__message

        def select_media(self):
            return self.__media

        def select_media_all(self):
            return self.__media_all

        def select_joke(self):
            return self.__joke

        def select_joke_rand(self):
            return self.__joke_rand

        def select_joke_all(self):
            return self.__joke_all
