# Python version 2 and version 3 compatibility
from __future__ import (absolute_import, division, print_function, unicode_literals)

import os
import sys
import web
import signal
import mysql.connector


from time import sleep
from threading import Thread, Event
from lang import Answers, Commands
from sql import Database, User, Faq
from helper import Params, ServerExit
from ciscosparkapi import CiscoSparkAPI, Webhook, SparkApiError

__author__ = "Jan Neuzil"
__author_email__ = "janeuzil@cisco.com"
__copyright__ = "Copyright (c) 2018 Cisco and/or its affiliates."
__license__ = "MIT"

# Global parameters variable
p = Params()

# TODO BEAUTIFY CODE AND DIVIDE IT INTO SMALLER MODULES (WHOLE THING CODED IN LESS THAN 2 DAYS)
# TODO NOTIFY USERS AFTER DELETION OF FAQ OR MEDIA?


def system_error(err, msg):
    print("ERROR: " + msg)
    print(err)
    sys.exit(1)


def database_error(room_id, msg):
    send_message(room_id, p.ans.sql_error)
    print(msg)
    send_message(p.admin, msg)


def check_environment():
    print("INFO: Checking moderator environment variables.")
    var = str()
    try:
        for var in p.var:
            if var in os.environ:
                pass
    except KeyError as err:
        system_error(err, "Please set the environment variable " + var + ".")


def check_webhooks():
    # Creating webhooks if not existing
    print("INFO: Checking moderator webhooks with Spark.")
    required_webhooks = [
        "messages created",
        "messages deleted",
        "memberships created",
        "memberships deleted"
    ]
    try:
        webhooks = p.spark.webhooks.list()
        existing_webhooks = list()
        for hook in webhooks:
            existing_webhooks.append(hook.resource + " " + hook.event)

        # Finding missing webhooks by intersecting two sets
        missing_webhooks = list(set(required_webhooks) - set(existing_webhooks))

        # Creating missing webhooks
        for hook in missing_webhooks:
            p.spark.webhooks.create(
                name=hook,
                targetUrl=os.environ['MODERATOR_URL'],
                resource=hook.split()[0],
                event=hook.split()[1]
            )
            print("INFO: Webhook '" + hook + "' successfully created.")
    except SparkApiError as err:
        system_error(err, "Cannot verify lunch menu webhooks with Spark.")


def check_privileges(r):
    if r.room_id == p.admin or r.room_id == p.moderators:
        return True
    else:
        return False


def init_spark():
    api = object()
    try:
        api = CiscoSparkAPI()
    except SparkApiError as err:
        system_error(err, "Unable to initialize Cisco Spark API.")
    return api


def init_database():
    print("INFO: Connecting to the internal database.")
    # Connecting to the database and creating tables if they do not exist
    db = object()
    try:
        db = Database(
            os.environ['DB_HOST'],
            os.environ['DB_USER'],
            os.environ['DB_PASSWD'],
            os.environ['DB_NAME']
        )
        db.create_tables()
    except mysql.connector.Error as err:
        system_error(err, "Cannot initialize the database.")

    return db


def init_params():
    # Getting information about me
    p.me = p.spark.people.me()

    # Get the admin room ID
    p.admin = os.environ['ADMIN_ROOM']

    # Get the moderators room ID
    p.moderators = os.environ['MODERATORS_ROOM']

    # Get the moderator language
    p.lang = os.environ['MODERATOR_LANG']

    # Create the commands for the given language
    p.cmd = Commands(p.lang)

    # Create the answers for given language
    p.ans = Answers(p.lang)

    # Create bot mention for future reference
    p.mention = p.ans.mention.format(p.me.emails[0])

    # Inserting or updating bot user
    data = (p.me.id, p.admin, p.me.displayName, p.me.emails[0], p.admin)
    if not p.db.insert_user(data):
        msg = "ERROR: Cannot insert user in the database."
        print(msg)
        send_message(p.admin, msg)


def format_time(t):
    return t.strftime(p.ans.time)


def format_mention(room_type):
    if room_type == p.direct:
        return str()
    elif room_type == p.group:
        return p.mention


def insert_room(data):
    try:
        room = p.spark.rooms.get(data.roomId)
        print("INFO: New membership created, updating database information.")
    except SparkApiError as err:
        msg = "ERROR: Cannot retrieve room '{0}' detailed information from Spark.\n".format(data.roomId) + str(err)
        print(msg)
        send_message(p.admin, msg)
        return

    # No inner queries allowed within the same table, getting the count of rooms in the database
    cnt = p.db.select_room_cnt(None)
    if not cnt:
        msg = "ERROR: Cannot insert room in the database."
        print(msg)
        send_message(p.admin, msg)
        return

    # Inserting new room in the database
    if room.type == p.direct:
        title = p.ans.room_name.format(room.title)
    else:
        title = room.title
    room_data = (room.id, data.id, cnt[0][0], title, room.type)
    if not p.db.insert_room(room_data):
        msg = "ERROR: Cannot insert room in the database."
        print(msg)
        send_message(p.admin, msg)
        return

    # Inserting new or updating user
    u = insert_user(data, room.id, room.type)
    if not u:
        user_name = "Unknown"
    else:
        user_name = u.user_name

    # Sending welcome message in English
    if room.type == p.direct:
        msg = p.ans.welcome_direct.format(user_name, p.cmd.help)
        send_message(data.roomId, msg)
    elif room.type == p.group:
        msg = p.ans.welcome_group.format(p.cmd.help)
        msg += p.ans.help_group.format(p.me.emails[0], p.cmd.help)
        send_message(data.roomId, msg)
    else:
        msg = "ERROR: Unknown room type, aborting processing."
        print(msg)
        send_message(p.admin, msg)


def update_room(r):
    print("INFO: Membership deleted in the room, updating room database.")
    room_data = (0, r.room_id)
    if not p.db.update_room(room_data):
        msg = "ERROR: Cannot update room in the database."
        print(msg)
        send_message(p.admin, msg)


def select_room(r):
    spaces = p.db.select_room_all(None)
    if not spaces:
        database_error(r.room_id, "ERROR: Cannot get the rooms from the database.")
    else:
        tmp = "- **{0}** - {1}\n"
        msg = str()
        for s in spaces:
            msg += tmp.format(s[3], s[4])
        # Sending the moderators list of all rooms
        send_message(r.room_id, msg)


# Function to check if the room_num is valid or not
def check_room(room_num):
    room_id = p.db.select_space([room_num])
    if not room_id:
        return None
    else:
        return room_id


def insert_user(data, room_id, room_type):
    # Try if the user is already in the database
    u = p.db.select_user([data.personId])
    if u:
        # Return the user information
        if room_type == p.group:
            return u
        # Update the user direct room
        elif room_type == p.direct:
            user_data = (u.user_id, room_id, u.user_name, u.user_email, room_id)
            if not p.db.insert_user(user_data):
                msg = "ERROR: Cannot update user room in the database."
                print(msg)
                send_message(p.admin, msg)
            u.room_id = room_id
            return u
        else:
            return None

    # Get information from Spark and add the new user
    else:
        # Adding new user in the database
        try:
            person = p.spark.people.get(data.personId)
        except SparkApiError as err:
            msg = "ERROR: Cannot retrieve person '{0}' detailed information from Webex.".format(data.personId)
            msg += str(err)
            print(msg)
            send_message(p.admin, msg)
            return None

        print("INFO: Inserting or updating user database.")
        if room_type == "group":
            room_id = None
        user_data = (person.id, room_id, person.displayName, person.emails[0], room_id)
        if not p.db.insert_user(user_data):
            msg = "ERROR: Cannot insert user in the database."
            print(msg)
            send_message(p.admin, msg)
        return User(person.id, room_id, person.displayName, person.emails[0])


def process_message(data):
    message = p.spark.messages.get(data.id)

    # Loop prevention mechanism, do not respond to my own messages
    if message.personId == p.me.id:
        return
    else:
        # Store the incoming message in the database
        # insert_message(message.id, data.roomId, data.personId, None, message.text)

        # Get basic information about the room from the database
        r = p.db.select_room([data.roomId])

        if not r:
            msg = "ERROR: Cannot get the room data - '{0}'.".format(data.roomId)
            print(msg)
            send_message(p.admin, msg)
            return
        print("INFO: New message in the room '{0}' by '<{1}>': '{2}'.".format(
            r.room_name, message.personEmail, message.text)
        )

        # Inserting user in the database for the future reference
        u = insert_user(data, r.room_id, r.room_type)

        text = message.text
        # Trimming the mention tag
        if data.roomType == "group":
            text = str(" ").join(text.split()[1:])

        # Parsing the message received from the user
        cmd, args = parse_message(text)

        # Privilege command to add object like FAQ, media or joke
        if cmd == p.cmd.add:
            if not check_privileges(r):
                send_message(r.room_id, p.ans.unauthorized)
            else:
                obj, args = parse_message(args)

                # Adding new FAQ manually in the database
                if obj == p.cmd.faq:
                    if not args:
                        send_message(r.room_id, p.ans.add_empty)
                    else:
                        room_num, text = parse_message(args)
                        if not room_num or not text:
                            send_message(r.room_id, p.ans.add_empty)
                        else:
                            room_id = check_room(room_num)
                            if not room_id:
                                send_message(r.room_id, p.ans.room_bad.format(format_mention(r.room_type), p.cmd.rooms))
                            else:
                                insert_faq(r, u, text, room_id)

                # Adding new media in the database
                elif obj == p.cmd.media:
                    if not args:
                        send_message(r.room_id, p.ans.add_empty)
                    else:
                        room_num, args = parse_message(args)
                        if not args:
                            send_message(r.room_id, p.ans.add_empty)
                        else:
                            room_id = check_room(room_num)
                            if not room_id:
                                send_message(r.room_id, p.ans.room_bad.format(format_mention(r.room_type), p.cmd.rooms))
                            else:
                                link, text = parse_message(args)
                                if not link or not text:
                                    send_message(r.room_id, p.ans.add_empty)
                                else:
                                    insert_media(r, u, room_id, link, text)

                # Adding new joke in the database
                elif obj == p.cmd.joke:
                    if not args:
                        send_message(r.room_id, p.ans.add_empty)
                    else:
                        insert_joke(r, args)

                # Unknown object
                else:
                    send_message(r.room_id, p.ans.add_help.format(format_mention(r.room_type), p.cmd.add))

        # Privilege command to answer for a question
        elif cmd == p.cmd.answer:
            if not check_privileges(r):
                send_message(r.room_id, p.ans.unauthorized)
            else:
                faq_id, text = parse_message(args)
                if not faq_id:
                    send_message(r.room_id, p.ans.answer_help.format(format_mention(r.room_type), p.cmd.answer))
                elif not text:
                    send_message(r.room_id, p.ans.answer_empty)
                else:
                    faq_id = check_faq(r, u, faq_id)
                    if not faq_id:
                        send_message(r.room_id, p.ans.faq_bad.format(format_mention(r.room_type), p.cmd.faq))
                    else:
                        insert_answer(r, u, faq_id, text)

        # Command to ask question in the FAQ
        elif cmd == p.cmd.ask:
            # Moderators should not ask question, but they can insert FAQ thread
            if check_privileges(r):
                send_message(r.room_id, p.ans.ask_help.format(format_mention(r.room_type), p.cmd.add, p.cmd.faq))
            else:
                if not args:
                    send_message(r.room_id, p.ans.ask_empty)
                else:
                    insert_faq(r, u, args)

        # Command to clear all generated messages from given room
        elif cmd == p.cmd.clear:
            if not check_privileges(r):
                send_message(r.room_id, p.ans.unauthorized)
            else:
                if not args:
                    send_message(r.room_id, p.ans.clear_help.format(format_mention(r.room_type), p.cmd.clear))
                else:
                    room_id = check_room(args)
                    if not room_id:
                        send_message(r.room_id, p.ans.room_bad.format(format_mention(r.room_type), p.cmd.rooms))
                    else:
                        clear_message(r, room_id)

        # Command to add comment to given FAQ
        elif cmd == p.cmd.comment:
            faq_id, text = parse_message(args)
            if not faq_id:
                send_message(r.room_id, p.ans.comment_help.format(format_mention(r.room_type), p.cmd.comment))
            elif not text:
                send_message(r.room_id, p.ans.comment_empty)
            else:
                faq_id = check_faq(r, u, faq_id)
                if not faq_id:
                    send_message(r.room_id, p.ans.faq_bad.format(format_mention(r.room_type), p.cmd.faq))
                else:
                    insert_comment(r, u, faq_id, text)

        # Privilege command to delete object like FAQ, media or joke
        elif cmd == p.cmd.delete:
            if not check_privileges(r):
                send_message(r.room_id, p.ans.unauthorized)
            else:
                obj, args = parse_message(args)

                # Deleting FAQ from the database
                if obj == p.cmd.faq:
                    faq_id = check_faq(r, u, args)
                    if not faq_id:
                        send_message(r.room_id, p.ans.faq_bad.format(format_mention(r.room_type), p.cmd.faq))
                    else:
                        delete_faq(r, faq_id)

                # Deleting media from the database
                elif obj == p.cmd.media:
                    media_id = check_media(args)
                    if not media_id:
                        send_message(
                            r.room_id, p.ans.media_bad.format(format_mention(r.room_type), p.cmd.list, p.cmd.media)
                        )
                    else:
                        delete_media(r, media_id)

                # Adding new joke to the database
                elif obj == p.cmd.joke:
                    joke_id = check_joke(args)
                    if not joke_id:
                        send_message(
                            r.room_id, p.ans.joke_bad.format(format_mention(r.room_type), p.cmd.list, p.cmd.joke)
                        )
                    else:
                        delete_media(r, joke_id)

                # Unknown object
                else:
                    send_message(r.room_id, p.ans.delete_help.format(format_mention(r.room_type), p.cmd.delete))

        # Command to show all FAQ in the room
        elif cmd == p.cmd.faq:
            if not args:
                select_faq(r, u)
            else:
                faq_id = check_faq(r, u, args)
                if not faq_id:
                    send_message(r.room_id, p.ans.faq_bad.format(format_mention(r.room_type), p.cmd.faq))
                else:
                    select_answer(r, faq_id)

        # Command to show help based on the type of the room
        elif cmd == p.cmd.help:
            if not check_privileges(r):
                send_message(r.room_id, p.ans.help_all.format(
                    u.user_name, p.cmd.ask, p.cmd.comment, p.cmd.faq,
                    p.cmd.help, p.cmd.joke, p.cmd.media
                ))
            else:
                send_message(r.room_id, p.ans.help_admin.format(
                    p.cmd.add, p.cmd.answer, p.cmd.clear, p.cmd.comment,
                    p.cmd.delete, p.cmd.faq, p.cmd.help, p.cmd.joke,
                    p.cmd.list, p.cmd.rooms, p.cmd.media
                ))

        # Retrieve a random joke in a given language
        elif cmd == p.cmd.joke:
            select_joke(r)

        # Privilege command to list objects
        elif cmd == p.cmd.list:
            if not check_privileges(r):
                send_message(r.room_id, p.ans.unauthorized)
            else:
                obj, args = parse_message(args)

                # Listing FAQ from the database
                if obj == p.cmd.faq:
                    if args:
                        room_id = check_room(args)
                        if not room_id:
                            send_message(r.room_id, p.ans.room_bad.format(format_mention(r.room_type), p.cmd.rooms))
                        else:
                            list_faq(r, room_id)
                    else:
                        list_faq(r)

                # Listing all medias from the database
                elif obj == p.cmd.media:
                    list_media(r)

                # Listing all jokes to the database
                elif obj == p.cmd.joke:
                    list_joke(r)

                # Unknown object
                else:
                    send_message(r.room_id, p.ans.list_help.format(format_mention(r.room_type), p.cmd.list))

        # Retrieve all media and send them in the ordered list
        elif cmd == p.cmd.media:
            select_media(r)

        # Privilege command to list all the rooms
        elif cmd == p.cmd.rooms:
            if not check_privileges(r):
                send_message(r.room_id, p.ans.unauthorized)
            else:
                select_room(r)

        else:
            print("WARNING: Unknown command received, sending the bot capabilities.")
            send_message(r.room_id, p.ans.fallback.format(p.cmd.help))


def message_deleted(data):
    try:
        person = p.spark.people.get(data.personId)
        print("INFO: User " + person.displayName + " has deleted its own message.")
    except SparkApiError as err:
        msg = "ERROR: Cannot retrieve person '{0}' detailed information from Webex.\n".format(data.personId) + str(err)
        print(msg)
        send_message(p.admin, msg)


def parse_message(text):
    tmp = text.split()
    if len(tmp) == 0:
        obj = str()
        args = None
    elif len(tmp) == 1:
        obj = tmp[0].lower()
        args = None
    else:
        obj = tmp[0].lower()
        args = " ".join(tmp[1:])

    return obj, args


def send_message(room_id, msg, faq_id=None):
    if not msg:
        msg = "ERROR: Cannot send empty message to the Webex user."
        print(msg)
        send_message(p.admin, msg)
        return
    # Spark does not support messages longer than 10000 characters with encryption
    flag = False
    tmp = str()
    if len(msg) > 8192:
        flag = True
        tmp = msg[8192:]
        msg = msg[:8192]
    try:
        m = p.spark.messages.create(roomId=room_id, markdown=msg)
        insert_message(m.id, room_id, p.me.id, faq_id, msg)
    except SparkApiError as err:
        print("WARNING: Cannot send message to the Webex user.")
        print(err)
    if flag:
        send_message(room_id, tmp)


# Function to insert message in the database
def insert_message(msg_id, room_id, user_id, faq_id, text):
    data = (msg_id, room_id, user_id, faq_id, text)
    if not p.db.insert_message(data):
        msg = "ERROR: Cannot insert message in the database."
        print(msg)
        send_message(p.admin, msg)


# Function to delete message from the local database
def delete_message(r, message_id):
    if not p.db.delete_message([message_id]):
        database_error(r.room_id, "ERROR: Cannot delete message in the database.")
    else:
        print("INFO: Message {0} successfully deleted from the database.".format(message_id))


# Function to clear all generated messages using the Webex Teams API
def clear_message(r, room_id):
    messages = p.db.select_message([p.me.id, room_id])
    if not messages:
        if messages is None:
            database_error(r.room_id, "ERROR: Cannot get messages from the database.")
        else:
            send_message(r.room_id, p.ans.room_empty)
    else:
        # Deleting room related generated messages
        for m in messages:
            try:
                p.spark.messages.delete(m[0])
            except SparkApiError as err:
                msg = "ERROR: Cannot delete message '{0}' from Webex.".format(m[0])
                msg += str(err)
                print(msg)
                send_message(p.admin, msg)
            # Delete message from the database
            delete_message(r, m[0])

        send_message(r.room_id, p.ans.clear_success)


# Function to get the newly created FAQ ID
def get_faq(r, u, room_id):
    data = (room_id, u.user_id)
    f = p.db.select_faq_id(data)
    if not f:
        database_error(r.room_id, "ERROR: Cannot select question from the database.")
        return None
    else:
        return f


# Function to create a new FAQ thread from the user
def insert_faq(r, u, text, room_id=None):
    # Insert the question in the database
    if not room_id:
        data = (r.room_id, u.user_id, text)
    # Function to create a FAQ in the given room
    else:
        data = (room_id, u.user_id, text)

    if not p.db.insert_faq(data):
        database_error(r.room_id, "ERROR: Cannot insert question in the database.")
        return

    if not room_id:
        f = get_faq(r, u, r.room_id)
    else:
        f = get_faq(r, u, room_id)
    if not f:
        return

    # Notify user who asked the question about success
    send_message(r.room_id, p.ans.ask_success, f.faq_id)

    if not room_id:
        # Notify moderators about new question
        send_message(
            p.moderators, p.ans.ask_posted.format(u.user_name, text, p.me.emails[0], p.cmd.answer, f.faq_id), f.faq_id
        )


# Function to delete FAQ thread from the database
def delete_faq(r, faq_id):
    # Delete generated messages to FAQ thread
    messages = p.db.select_faq_messages([faq_id])
    if not messages:
        if messages is None:
            database_error(r.room_id, "ERROR: Cannot get the messages related to FAQ ID - {0}.".format(faq_id))

    else:
        for m in messages:
            try:
                p.spark.messages.delete(m[0])
                print("INFO: Message '{0}' successfully deleted from Webex.".format(m[0]))
            except SparkApiError as err:
                msg = "ERROR: Cannot delete message '{0}' from Webex.\n".format(m[0]) + str(err)
                print(msg)
                send_message(p.admin, msg)

    if not p.db.delete_faq([faq_id]):
        database_error(r.room_id, "ERROR: Cannot delete FAQ thread '{0}' from the database".format(faq_id))
    else:
        send_message(r.room_id, p.ans.faq_deleted)


def select_faq(r, u):
    privileged = check_privileges(r)
    # Fetch all FAQ threads
    if privileged:
        faq = p.db.select_faq_thread(None)
    # Fetch all FAQ threads in the given room
    else:
        faq = p.db.select_faq_space([r.room_id])
    if not faq:
        if faq is None:
            database_error(r.room_id, "ERROR: Cannot select all FAQ thread from the database based on the room ID.")
            return
        else:
            # Try to get the user FAQ initiated by the user itself
            if r.room_type == p.direct:
                faq = p.db.select_faq_author([u.user_id])
                if not faq:
                    if faq is None:
                        database_error(
                            r.room_id, "ERROR: Cannot select all FAQ thread from the database based on the user ID."
                        )
                    else:
                        send_message(r.room_id, p.ans.faq_empty)
                    return
            else:
                send_message(r.room_id, p.ans.faq_empty)
                return

    # Send the list of questions in the moderators room
    msg = str()
    i = 1
    for f in faq:
        # Determine if the question was answered or not
        if not f[2]:
            tmp = p.ans.no
        else:
            tmp = p.ans.yes
        if privileged:
            msg += p.ans.faq_line.format("- **{0}** -".format(f[0]), f[3], f[1], tmp)
        else:
            msg += p.ans.faq_line.format("- **{0}** -".format(i), f[3], f[1], tmp)
        i += 1

    send_message(r.room_id, msg)


# Function to show all FAQ in a simple list, it can be filtered by room
def list_faq(r, room_id=None):
    if not room_id:
        faq = p.db.select_faq_all(None)
    else:
        faq = p.db.select_faq_room([room_id])

    if not faq:
        if faq is None:
            database_error(r.room_id, "ERROR: Cannot select all FAQ thread from the database.")
        else:
            send_message(r.room_id, p.ans.faq_empty)

    else:
        msg = str()
        tmp = "- **{0}** - {1}\n"
        for f in faq:
            msg += tmp.format(f[0], f[4])

        send_message(r.room_id, msg)


# Function to check if the given FAQ ID is valid and returns the index of requested FAQ
def check_faq(r, u, faq_id):
    if check_privileges(r):
        if not p.db.select_faq([faq_id]):
            return None
        else:
            return faq_id
    else:
        res = p.db.select_faq_room([r.room_id])
        if not res:
            # User is trying to read his own posts posted in other rooms
            if r.room_type == p.direct:
                res = p.db.select_faq_user([u.user_id])
                if not res:
                    return None
            else:
                return None
        try:
            i = int(faq_id)
            if 0 < i <= len(res):
                return res[i-1][0]
            else:
                return None
        except ValueError:
            return None


# Function to get the FAQ thread from the database as an object
def select_thread(r, faq_id):
    threads = p.db.select_answer([faq_id])
    if not threads:
        database_error(r.room_id, "ERROR: Cannot select thread from the database.")
        return None

    else:
        t = threads[0]
        return Faq(t[0], t[1], t[2], t[3], t[4], t[5], t[6], t[7], t[8])


# Function to insert answer for a given question in the database
def insert_answer(r, u, faq_id, text):
    f = p.db.select_faq([faq_id])
    if not f:
        send_message(r.room_id, p.ans.faq_bad.format(format_mention(r.room_type), p.cmd.faq))
        return

    # Get the information about the questioner
    q = p.db.select_user([f.user_id])
    if not q:
        database_error(r.room_id, "ERROR: User does not exist in the database.")
        return

    # Insert answer in the database
    data = (f.faq_id, u.user_id, text, u.user_id, text)
    if not p.db.insert_answer(data):
        database_error(r.room_id, "ERROR: Cannot insert answer in the database.")
        return

    # Sending answer to personal room of the questioner if it exists
    if q.room_id:
        send_message(q.room_id, p.ans.answer_personal.format(u.user_name, f.faq_text, text), f.faq_id)

    # Sending answer to room where the question was published
    if q.room_id != f.room_id:
        send_message(f.room_id, p.ans.answer_group.format(u.user_name, q.user_email, f.faq_text, text), f.faq_id)

    # Sending message to moderators room
    send_message(r.room_id, p.ans.answer_success.format(q.user_name), f.faq_id)


# Function to select answer
def select_answer(r, faq_id):
    f = select_thread(r, faq_id)
    if not f:
        return

    # Determine if the question was answered or not
    tmp = "- **{0}** ({1}): \"**{2}**\"\n"
    if not f.answer_text:
        flag = True
        text = p.ans.answer_empty
    else:
        flag = False
        text = tmp.format(f.r_user_name, format_time(f.answer_time), f.answer_text)

    # Form a message with the given thread
    msg = p.ans.faq_thread.format(tmp.format(f.q_user_name, format_time(f.faq_time), f.faq_text), text)

    # Add comments to the message, it might be unanswered but commented
    comments = select_comment(r, f.faq_id)
    if comments:
        flag = False
        msg += comments

    if flag:
        send_message(r.room_id, p.ans.answer_empty, f.faq_id)
    else:
        send_message(r.room_id, msg, f.faq_id)


def insert_comment(r, u, faq_id, text):
    f = select_thread(r, faq_id)
    if not f:
        return

    data = (u.user_id, f.faq_id, text)
    if not p.db.insert_comment(data):
        database_error(r.room_id, "ERROR: Cannot insert comment in the database.")

    else:
        # Sending message about successful posting
        send_message(r.room_id, p.ans.comment_success, faq_id)

        # Comment posted by moderator
        if check_privileges(r):
            # Sending answer to personal room if it exists
            if f.q_room_id:
                send_message(f.q_room_id, p.ans.comment_personal.format(
                    u.user_name, f.faq_text, text, p.cmd.comment, faq_id
                ), f.faq_id)

            # Sending answer to room where the question was published
            if f.q_room_id != f.f_room_id:
                send_message(f.f_room_id, p.ans.comment_group.format(
                    u.user_name, f.q_user_name, f.faq_text, text, p.mention, p.cmd.comment, faq_id
                ), f.faq_id)

        # Comment posted by user
        else:
            send_message(p.moderators, p.ans.comment_moderator.format(
                u.user_name, f.q_user_name, f.faq_text, text, p.mention, p.cmd.comment, faq_id
            ), f.faq_id)


def select_comment(r, faq_id):
    comments = p.db.select_comment([faq_id])
    if not comments:
        if comments is None:
            database_error(r.room_id, "ERROR: Cannot get the comments from the database.")
        # No comments in the database with the thread
        return None

    else:
        # Preparing message with media files
        msg = p.ans.comment_header
        tmp = "- **{0}** ({1}): \"**{2}**\"\n"
        for c in comments:
            msg += tmp.format(c[2], format_time(c[0]), c[1])
        return msg


# Function to add media in the database based on the room
def insert_media(r, u, room_id, link, text):
    data = (room_id, u.user_id, link, text)
    if not p.db.insert_media(data):
        database_error(r.room_id, "ERROR: Cannot insert media in the database.")

    else:
        # Sending message to the moderators room
        send_message(r.room_id, p.ans.media_success)

        # Notifying users about newly created media
        send_message(room_id, p.ans.media_posted.format(u.user_name, text, link))


# Function to delete joke from the database
def delete_media(r, media_id):
    if not p.db.delete_media([media_id]):
        database_error(r.room_id, "ERROR: Cannot delete the media from the database.")
    else:
        send_message(r.room_id, p.ans.media_deleted)


# Function to select all media from the database based on the room
def select_media(r):
    if check_privileges(r):
        media = p.db.select_media_all(None)
    else:
        media = p.db.select_media_room([r.room_id])
    if not media:
        if media is None:
            database_error(r.room_id, "ERROR: Cannot get the media from the database.")
        else:
            send_message(r.room_id, p.ans.media_empty)

    else:
        # Preparing message with media files
        msg = str()
        tmp = "{0}. **{1}** - _{2}_ - **[LINK]({3})**\n"
        i = 1
        for m in media:
            msg += tmp.format(i, m[3], m[1], m[2])
            i += 1
        send_message(r.room_id, msg)


# Function to select all media from the database based on the room
def list_media(r):
    media = p.db.select_media_all(None)
    if not media:
        if media is None:
            database_error(r.room_id, "ERROR: Cannot get the media from the database.")
        else:
            send_message(r.room_id, p.ans.media_empty)

    else:
        # Preparing message with media files
        msg = str()
        tmp = "- **{0}** - {1}: {2}\n"
        for m in media:
            msg += tmp.format(m[0], m[3], m[1])
        send_message(r.room_id, msg)


# Function to check if the given media ID is valid
def check_media(media_id):
    if not p.db.select_media([media_id]):
        return None
    else:
        return media_id


# Function to insert a joke in the database
def insert_joke(r, joke):
    if not p.db.insert_joke([joke, p.lang]):
        database_error(r.room_id, "ERROR: Cannot insert joke in the database.")
    else:
        send_message(r.room_id, p.ans.joke_success)


# Function to delete joke from the database
def delete_joke(r, joke_id):
    if not p.db.delete_joke([joke_id]):
        database_error(r.room_id, "ERROR: Cannot delete the joke from the database.")
    else:
        send_message(r.room_id, p.ans.joke_deleted)


# Function to select a random joke from the database
def select_joke(r):
    joke = p.db.select_joke_rand([p.lang])
    if not joke:
        if joke is None:
            database_error(r.room_id, "Cannot get the joke from the database.")
        else:
            send_message(r.room_id, p.ans.joke_empty)
    else:
        send_message(r.room_id, joke[0][0])


# Function to select a random joke from the database
def list_joke(r):
    jokes = p.db.select_joke_all([p.lang])
    if not jokes:
        if jokes is None:
            database_error(r.room_id, "Cannot get the all jokes from the database.")
        else:
            send_message(r.room_id, p.ans.joke_empty)
    else:
        msg = str()
        tmp = "- **{0}** - {1}...\n"
        for j in jokes:
            msg += tmp.format(j[0], j[1][:32])

        send_message(r.room_id, msg)


# Function to check if the given joke ID is valid
def check_joke(joke_id):
    if not p.db.select_joke([joke_id]):
        return None
    else:
        return joke_id


class Moderator(object):
    @staticmethod
    def POST():
        print("INFO: New HTTP POST request received.")

        # Creating webhook object
        try:
            webhook = Webhook(web.data())
        except SparkApiError as err:
            print("WARNING: Invalid server request, not a JSON format.")
            print(err)
            return

        # Loop prevention, do not react to events triggered by myself
        if webhook.actorId == p.me.id:
            return

        print("INFO: Spark webhook received - {0} {1}.".format(webhook.resource, webhook.event))

        # Memberships event
        if webhook.resource == "memberships":
            # Register only if the person is me and not others
            if webhook.data.personId != p.me.id:
                print("INFO: Event concerning somebody else, skipping.")
                return
            if webhook.event == "created":
                insert_room(webhook.data)
            elif webhook.event == "deleted":
                r = p.db.select_room([webhook.data.roomId])
                if not r:
                    msg = "ERROR: Cannot get the room data - '{0}'.".format(webhook.data.roomId)
                    print(msg)
                    send_message(p.admin, msg)
                    return
                update_room(r)
            else:
                print("WARNING: Unknown memberships webhook event, discarding request.")

        # Messages event
        elif webhook.resource == "messages":
            if webhook.event == "created":
                process_message(webhook.data)
            elif webhook.event == "deleted":
                message_deleted(webhook.data)
            else:
                print("WARNING: Unknown messages webhook event, discarding request.")

        # Unknown event
        else:
            print("WARNING: Unknown webhook event, discarding event.")


def server_shutdown(signum, frame):
    raise ServerExit("INFO: Signal {0} has been caught, shutting down server.".format(signum))


class Worker(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.shutdown_flag = Event()

    def run(self):
        while not self.shutdown_flag.is_set():
            # Sleeping for a minute before next checking
            sleep(60)

            # Performing database health check each hour to test MySQL connection
            u = p.db.select_user([p.me.id])
            if not u:
                msg = "ERROR: Database connection is broken, cannot retrieve data."
                print(msg)
                send_message(p.admin, msg)


def main():
    # Performing environment and health checks
    check_environment()
    p.spark = CiscoSparkAPI()
    check_webhooks()
    p.db = init_database()
    try:
        init_params()
    except Exception as e:
        system_error(e, "Cannot initialize default parameters.")
    urls = ("/api/moderator", "Moderator")

    app = object()
    thread = object()

    # Registering the signal handlers
    signal.signal(signal.SIGTERM, server_shutdown)
    signal.signal(signal.SIGINT, server_shutdown)

    try:
        thread = Worker()
        thread.start()
        app = web.application(urls, globals())
        app.run()
    except ServerExit as msg:
        # Waiting for the threads
        print(msg)
        print("INFO: Waiting for the thread to finish within a minute.")
        thread.shutdown_flag.set()
        thread.join()
        app.stop()
        print("INFO: Server has been shut down successfully.")
        sys.exit(0)


# Main function starting the web.py web server
if __name__ == '__main__':
    main()
