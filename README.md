# Superher Logger Flask+Pywebio App with Postgres SQL
Accessibile at: https://superhero-logger-flask-pywebio.vercel.app/

* This is a simple CRUD application that allows users to log in, register, add, update, and delete heroes.
* The application uses Flask, SQLAlchemy, and PyWebIO to create a simple web application.
* PyWebio is used to create the user interface, while Flask and SQLAlchemy are used to handle the backend logic and database operations.
* I deployed the app to Vercel, and set-up the database (PostgreSQL) on Render.
* The app isn't configured to manage sessions for users. Session management could be added to the app to improve the user experience. Could use Flask's session management capabilities to manage user sessions.
* The app does not make use of Flask's routing capabilities. Routing could be added to the app to create a more structured application.

Made by Khant Thura / Liam with <3
Unfortunately, Render free database used on this app only works for 30-days, if you want to clone this project feel free to do so.

## Further Reading
* [Session-based Authentication in flask](https://a4u.medium.com/session-based-authentication-in-flask-d43fe36afc0f)
* [Deploying PostgreSQL in Flask](https://stackoverflow.com/questions/78341763/how-to-deploy-a-postgresql-database-for-flask-app-on-vercel)
* [Connecting Database to Flask](https://medium.com/nerd-for-tech/how-to-connect-database-to-a-flask-app-part-1-60611deea17a)
* [Flask SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/en/3.1.x/)
* [PyWebIO Flask](https://pywebio.readthedocs.io/en/latest/platform.html)
* [Render - Cloud App Hosting](http://render.com)
* [Vercel - Cloud App Hosting](http://vercel.com)
