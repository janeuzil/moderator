# moderator

[Cisco Webex Bot](https://developer.webex.com/bots.html)  moderates the FAQ for events:
- setup a moderator room to answer questions generated from users
- handling links for presentations and other media in a consistent manner
- handling the FAQ thread including comments
- tells funny IT jokes

## Technology
- [Python 2.7](https://www.python.org/)
- [MySQL](https://www.mysql.com/) database
- [Docker](https://www.docker.com) container platform
- Python web framework [web.py](http://webpy.org)
- Python [ciscosparkapi](http://ciscosparkapi.readthedocs.io/en/latest/index.html) API

## Capabilities

### User

#### List of commands:
- **ask** &lt;question&gt; - to ask a question
- **comment** &lt;faq number&gt; &lt;comment&gt; - to comment the given FAQ thread
- **faq** \[faq number\] - to list all FAQs or given FAQ thread
- **help** - to show help message
- **joke** - to read an IT joke
- **media** - to show shared presentations and other documents

#### Glossary:
- **&lt;argument&gt;** - mandatory argument
- **\[argument\]** - optional argument

#### Examples:
- **ask Why are we here?** - will ask the question and notify moderators
- **faq** - will list all FAQ in the room
- **faq 1** - will show the specific FAQ thread with answer and comments
- **comment 1 Just to suffer.** - will comment the first FAQ thread and notify moderators
- **media** - will list all media in the room

### Moderator

#### List of commands:
- **add &lt;object&gt; \[room id\] &lt;data&gt;** - to add an object
- **answer &lt;faq id&gt; &lt;answer&gt;** - to answer the question
- **clear &lt;room id&gt;** to delete all generated messages from the room
- **comment &lt;faq id&gt; &lt;comment&gt;** - to comment the given FAQ thread
- **delete &lt;object&gt; &lt;object id&gt;** - to delete the object
- **faq \[faq id\]** - to show given FAQ thread
- **help** - to show help message
- **joke** - to read an IT joke
- **list &lt;object&gt; \[room id\]** - to list all objects or specifically in a given room
- **rooms** - to list all rooms

#### Object types:
- **faq** - FAQ
- **joke** - joke
- **media** - presentations and other documents

#### Glossary:
- **&lt;argument&gt;** - mandatory argument
- **\[argument\]** - optional argument

#### Examples:
- **add media 1 _https://example.com Example presentation_** - will add an presentation and sends notification in the first room
- **add faq 2 _Why we are expensive?_** - will manually insert FAQ in the room number 2
- **list faq** - will list all FAQs in every room
- **answer 4 _We provide solution._** - will answer the question number 4
- **delete faq 1** - will delete FAQ thread including answer, comments and related messages

## Installation
Open the terminal on your machine (e.g. Ubuntu) and install required packages:
```bash
$ sudo apt-get install mysql-server python-pip docker.io
```

Create a new root password for the MySQL database if it does not exist:
```bash
$ mysqladmin -u root password "********";
```
Connect to MySQL database:
```bash
$ mysql -u root -p
```
Create a new database with user for the Webex bot (in this example we will use database **moderator** and user **moderator**):
```sql
CREATE DATABASE moderator;
CREATE USER 'moderator'@'localhost' IDENTIFIED BY '**********';
GRANT ALL ON moderator.* TO 'moderator'@'localhost';
FLUSH PRIVILEGES;
```
Modify configuration file that mysql will listen also on 127.0.0.1 address which will be used with Docker connectivity:
```bash
$ vim /etc/mysql/my.cnf
```
Uncomment or put this line into the configuration file:
```bash
bind-address = 127.0.0.1
```
Restart the MySQL server:
```bash
# /etc/init.d/mysql restart
```

## Configuration
Create a simple Bash script with environmental variables which will help you to run the server in the Docker:
```bash
$ touch run.sh
$ chmod +x run.sh
```
Edit the file with the following lines (Note: Do not forget to change the password):
```bash
#!/bin/bash

sudo docker run -d -ti \
-e MODERATOR_URL="https://janeuzil.cz/api/moderator" \
-e MODERATOR_LANG="cz" \
-e SPARK_ACCESS_TOKEN="*************************" \
-e ADMIN_ROOM="********************" \
-e MODERATORS_ROOM="********************" \
-e DB_HOST="127.0.0.1" \
-e DB_NAME="moderator" \
-e DB_USER="moderator" \
-e DB_PASSWD="*******" \
-p 8080:8080 \
--net=host \
--name moderator \
moderator:latest
```
**Note:** Docker needs root privileges as it needs to access the kernel space.

## Running
Build the Docker image based on the Dockerfile:
```bash
$ sudo docker build -t moderator .
```
Simply run your created Bash script:
```bash
$ ./run.sh
```

## Testing
For coding and testing purposes I have used [PyCharm](https://www.jetbrains.com/pycharm/) with [Docker](https://www.docker.com) running on a public [Ubuntu](https://www.ubuntu.com) server.

To install Docker, run the following command:
```bash
$ sudo apt-get install docker.io
```

Expose the Docker API for remote handling, but only for localhost. For security reasons, we do not want to expose the Docker to the public, we will use SSH tunnel to reach the Docker API. Edit this file:
```bash
$ sudo vim /lib/systemd/system/docker.service
```
Change the variable **ExecStart** to this value:
```bash
ExecStart=/usr/bin/dockerd -H fd:// -H tcp://127.0.0.1:4243 -H unix:///var/run/docker.sock $DOCKER_OPTS
```

To create a secure SSH tunnel to the server, run the following command:
```bash
ssh -f -i ~/.ssh/id_rsa <username>@<host> -L 4243:127.0.0.1:4243 -N
```

## Tunneling
In this section there are described methods if you do not have public URL, or you are behind corporate firewall or proxy.

### Port 8080
You can allow the port 8080 on your local server using uncomplicated firewall utility:
```bash
# ufw allow 8080/tcp
```

### HTTPS
If you are running Apache on your server and you do not want to open the port 8080, you can use **http_proxy** module to redirect the traffic on given URL to your moderator bot. First enable the Apache module:
```bash
# a2enmod proxy_http
# cd /etc/apache2/sites-enabled/
```
Then edit the appropriate configuration file, where you listen to port 443 (e.g. 000-default-le-ssl.conf), with the following line:
```apacheconfig
<IfModule mod_ssl.c>
<VirtualHost *:443>
        .
        .
        .
        ProxyPass "/api/moderator" "http://localhost:8080/api/moderator"
        .
</VirtualHost>
```
Restart the Apache server:
```bash
# /etc/init.d/apache2 restart
```
You should get the JSON health-check using following URL - https://example.com/api/moderator

### Public URL
If you do not have a public URL, but you are running on the local computer, you can use [NGROK](https://ngrok.com). Simply download the binary to your machine and run the following command:
```bash
$ ./ngrok http 8080
```
You will get random public URL (e.g. https://a1b2c3.ngrok.io/) which you can use as the **MODERATOR_URL** variable in your local running script.

