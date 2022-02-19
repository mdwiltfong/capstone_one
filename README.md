# How to Run repo

1. Make sure you are in a virtual enviornment. Run the following code in your terminal.

   - `source venv/bin/activate`

2. You may need to add variables to PATH. Put this in your terminal.

   - ` export FLASK_ENV=development`

3. Now you're ready to run the flask server.

   - ` flask run`

At this point your terminal is running a flask server. You should be able to see the site at `http://127.0.0.1:5000/`

## How to Refresh DB tables

In some cases you may have to refresh your db models. You can follow this procedure to do so. Keep in mind you will have to be in a virtual enviornment while running the flask server:

1. Open iPython by running `ipython`
2. Run `%run app.py`
3. Drop all tables by running `db.drop_all()` If you are getting errors at this point you may have to mainly drop some tables.
4. Run `db.create_all()`
5. You've created the tables but they're empty. You will have to run the seed file by executing `%run seed.py`
