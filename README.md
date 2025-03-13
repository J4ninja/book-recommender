# Book Recommender Graph System using Amazon Book Review Dataset

## Table of Contents
1. [Development](#development)
   - [Containers](#containers)
   - [Visual Studio Code Devcontainers](#visual-studio-code-devcontainers)
   - [Secret Keys](#secret-keys)
   - [Database Connection](#neo4j-connection)
2. [Running the Application](#running-the-application)

## Development

### Containers
There is no need to install dependencies directly. Dependencies are installed using `Docker` and development can be done in the container environment using `Devcontainer`. Any IDE that supports Dev Containers should work.

### Visual Studio Code Devcontainers
0. Prerequisite: Run Docker Desktop
1. Prerequisite: Install DevContainer extension (VSCode)
2. Reopen this project in DevContainer by clicking bottom right popup or manually using command pallete:

    Open Command Pallete:

        Ctrl (cmd) + Shift + P

    Type in: 

        >Dev Containers: Reopen in Dev Container

3. Wait for Dev Container to build image and open in same window
4. Open up a VSCode Terminal and verify that you are a `root` user

### Secret Keys
Django secret keys are stored in the .env file. For first time set up, create a .env in the project root (the same level as manage.py) and add:
DJANGO_SECRET_KEY='YOUR_SECRET_KEY'

### Database (neo4j) Connection
The Django uses a connection to a cloud hosted neo4j instance. Add the following variables to your .env file (credentials provided via email)
NEO4J_URI=''
NEO4J_USERNAME=''
NEO4J_PASSWORD=''
AURA_INSTANCEID=''
AURA_INSTANCENAME=''

### Importing Data
I've created a management function in management/commands/load_book_data.py to load test data into the database. This is to test data models as well as your database connection.
Neo4j provides fuctionality for bulk imports from the web portal.

## Running the Application
1. Open project in Dev Container
2. Run:

        python manage.py runserver 0.0.0.0:8000

3. Verify in `PORTS` that port 8000 is forwarded to localhost
4. View application in browser at output link

        http://localhost:8000/
