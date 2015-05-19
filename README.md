# Safe-Streets-Event-Tracker
A method for tracking incidents that occur during Safe Streets shifts. 

Go to https://safestreets.herokuapp.com/ to use.

## To create db:
```
heroku run python --app safestreets
>>> from app import db
>>> db.create_all()
```
