# About application

> superuser: admin
> password: qwe123rt

## Install

### Python environment
1. Create virtual environment in root directory of project - `python3.6 -m venv venv`
2. `source env/bin/activate`
3. `pip install -r requirements.txt`

### Data base deploy
1. Install PostgreSql = `sudo apt-get install postgresql postgresql-contrib`
2. Create user 
    ```bash
    createuser --interactive -P
    Enter name of role to add: root
    Enter password for new role: 
    Enter it again: 
    Shall the new role be a superuser? (y/n) y
    ```
3. Create db `createdb comments`
4. Create tables `venv/bin/python3.6 manage.py migrate`

## Run tests
`venv/bin/python3.6 manage.py test .`

## Run project
1. `venv/bin/python3.6 manage.py runserver 8000`
2. Open in browser [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
### About interface
+ [Create new comment](http://127.0.0.1:8000/api/comment/)
+ Get comments top level for entities:
    + comment - [http://127.0.0.1:8000/api/comment/comment/2/](http://127.0.0.1:8000/api/comment/comment/2/) where 
    second `comment` - it is entity identifier and `2` - it is id of parent comment 
    + post - [http://127.0.0.1:8000/api/comment/post/2/](http://127.0.0.1:8000/api/comment/post/2/) where 
    `post` - it is entity identifier and `2` - it is id of entity
    + user - [http://127.0.0.1:8000/api/comment/user/2/](http://127.0.0.1:8000/api/comment/user/2/) where 
    `user` - it is entity identifier and `2` - it is id of entity 
+ Get comments recursively for three entities:
    + comment - [/api/comment/tree/?entity=comment&object_id=2](/api/comment/tree/?entity=comment&object_id=2)
    + post - [/api/comment/tree/?entity=post&object_id=2](/api/comment/tree/?entity=post&object_id=2)
    + user - [/api/comment/tree/?entity=user&object_id=2](/api/comment/tree/?entity=user&object_id=2)
 

## For developers
+ Update requirements - `venv/bin/pip3.6 freeze > requirements.txt`
+ `venv/bin/python3.6 manage.py createsuperuser`
