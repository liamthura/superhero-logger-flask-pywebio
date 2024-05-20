"""
This is a simple CRUD application that allows users to log in, register, add, update, and delete heroes.
The application uses Flask, SQLAlchemy, and PyWebIO to create a simple web application.
PyWebio is used to create the user interface, while Flask and SQLAlchemy are used to handle the backend logic and database operations.
I deployed the app to Vercel, and set-up the database (PostgreSQL) on Render.
The app isn't configured to manage sessions for users. Session management could be added to the app to improve the user experience. Could use Flask's session management capabilities to manage user sessions.
The app does not make use of Flask's routing capabilities. Routing could be added to the app to create a more structured application.
"""

from pywebio import *
from pywebio.input import *
from pywebio.output import *
from pywebio.platform.flask import webio_view
from pywebio import STATIC_PATH, start_server
import argparse
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import create_engine, Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, sessionmaker, declarative_base, relationship

app = Flask(__name__)
# Concecting to the database using SQLAlchemy on Render.com
app.config[
    "SQLALCHEMY_DATABASE_URI"] = "postgresql://superhero_logger_user:DJoKXpCBsqY1skxPvHVsL0K6RjdQWkpu@dpg-cp5shko21fec73ebdrfg-a.frankfurt-postgres.render.com/superhero_logger"

db = SQLAlchemy(app)


class User(db.Model):
    # id = db.Column(db.Integer, primary_key=True)
    # username = db.Column(db.String(20), unique=True, nullable=False)
    # password = db.Column(db.String(60), nullable=False)
    # role = db.Column(db.String(20), nullable=False)

    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    role: Mapped[str]
    heroes: Mapped[list["Hero"]] = relationship("Hero", back_populates="creator", cascade="all, delete")

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username})>"


class Hero(db.Model):
    __tablename__ = 'heroes'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    secret_name: Mapped[str]
    age: Mapped[int]
    created_by: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    creator: Mapped["User"] = relationship("User", back_populates="heroes")

    def __repr__(self):
        return f"<Hero(id= {self.id}, name= {self.name}, secret_name= {self.secret_name}, age= {self.age})>"


# Use app.app_context() to keep running in app's environment (so we can manage database, access and update data)
with app.app_context():
    db.create_all()

# global variables
valid_user = None
dark_mode = False
dark_style = """
<style>
    body, .footer {background-color: #333; color: white;}
    footer {margin-top: auto;}
    table th {background-color: #4a4a4a;}
    table td {background-color: #444;}
    div {background-color: #444; color: white}
    #input-cards, #input-container,  {background-color: #444; white}
    .card-header {background-color: #4a4a4a;}
</style>
"""


# User login screen
@use_scope('ROOT')
def user_login():
    clear()  # to clear previous data if there is
    put_html("<h1>Login / Register</h1>")

    # Defining form fields
    loginInfo = [
        input("What's your username?", name='name', required=True),
        input("What's your password?", type=PASSWORD, name='password', required=True),
        actions("", [
            {'label': 'Login', 'value': 'login', 'type': 'submit'},
            {'label': 'Register', 'value': 'register', 'type': 'submit', 'color': 'secondary'},
        ], name="user_action"),
    ]

    data = input_group("User Log In", loginInfo, cancelable=True)

    if data is None:
        toast('Login not performed', color='warning')
    elif data['user_action'] == 'register':
        add_user(data)
    elif data['user_action'] == 'login':
        verify_user(data['name'], data['password'])


def add_user(user_data):
    clear()
    user_role = 'standard'
    try:
        with app.app_context():
            user_exists = User.query.filter_by(username=user_data['name']).first()
            if user_exists is not None:
                raise ValueError('User already exists')
            security_data = input_group('Security Validation', [
                input('Confirm password', type=PASSWORD, name='confirm_password', required=True),
                checkbox("", options=['Make user an Administrator'], name='is_super_user', required=False)
            ], cancelable=True)
            if security_data is None:
                raise ValueError('Registration cancelled')
            confirm_password = security_data['confirm_password']
            if user_data['password'] != confirm_password:
                toast(f'Passwords do not match', color='error')
                add_user(user_data)
            else:
                if security_data['is_super_user']:
                    user_role = 'super'
                new_user = User(username=user_data['name'], password=user_data['password'], role=user_role)
                db.session.add(new_user)
                db.session.commit()
                # print(session.query(User).all())
    except SQLAlchemyError:
        toast(f'An error occurred', color='error')
    except ValueError as ve:
        toast(f'{str(ve)}', color='error')
    else:
        toast(f'User added, please login with new credentials', color='success')
    finally:
        user_login()


def verify_user(username, password):
    clear()
    global valid_user
    try:
        # with Session() as session:
        with app.app_context():
            valid_user = User.query.filter_by(username=username).first()
    except SQLAlchemyError:
        toast(f'An error occurred', color='error')
    else:
        if valid_user is None:
            toast(f'Invalid user', color='error')
            user_login()
        elif valid_user.password != password:
            toast(f'Invalid login, please check your username and password', color='error')
            user_login()
        else:
            main()


def get_user_id(username=None):
    global valid_user
    if valid_user is not None and username is None:
        return valid_user.id
    elif username is not None:
        # with Session() as session:
        with app.app_context():
            selected_user = User.query.filter_by(username=username).first()
            return selected_user.id
    else:
        return None


def user_logout():
    clear()
    global valid_user
    valid_user = None
    toast('You have been Logged out', color='success')
    main()


@use_scope('ROOT',
           clear=True)  # set scope to clear so every time a button is performed, input groups displays are cleared
def main():
    clear()
    global valid_user
    if dark_mode:
        put_html(dark_style)

    if valid_user is not None:
        put_buttons(['Logout', 'Toggle Dark Mode'], onclick=[user_logout, toggle_dark_mode]).style('float: right;')
    else:
        put_buttons(['Login', 'Toggle Dark Mode'], onclick=[user_login, toggle_dark_mode]).style('float: right;')

    put_html(f'<h1>Welcome, {get_username()}</h1>')
    put_markdown(f'''
* This is a simple CRUD application that allows users to log in, register, add, update, and delete heroes.
* The application uses Flask, SQLAlchemy, and PyWebIO to create a simple web application.
* PyWebio is used to create the user interface, while Flask and SQLAlchemy are used to handle the backend logic and database operations.
* I deployed the app to Vercel, and set-up the database (PostgreSQL) on Render.
* The app isn't configured to manage sessions for users. Session management could be added to the app to improve the user experience. Could use Flask's session management capabilities to manage user sessions.
* The app does not make use of Flask's routing capabilities. Routing could be added to the app to create a more structured application.

* Made by Khant Thura / Liam with <3
    ''')

    if valid_user is None:
        put_table(get_heroes_table(valid_user), header=['ID', 'Name'])
    elif valid_user.role == 'standard':
        put_table(get_heroes_table(valid_user), header=['ID', 'Name', 'Secret Name', 'Age'])
        put_buttons([
            dict(label='Add', value='add', color='primary'),
            dict(label='Update Own', value='update', color='secondary'),
            dict(label='Delete Own', value='delete', color='danger')
        ], onclick=[add_hero, update_hero, delete_hero])
    elif valid_user.role == 'super':
        put_table(get_heroes_table(valid_user), header=['ID', 'Name', 'Secret Name', 'Age', 'Created By'])
        put_buttons([
            dict(label='Add', value='add', color='primary'),
            dict(label='Update', value='update', color='secondary'),
            dict(label='Delete', value='delete', color='danger')
        ], onclick=[add_hero, update_hero, delete_hero])


# Adding the new hero and committing it to the database
def add_hero():
    add_fields = [
        input('Your hero\'s name', name='name', required=True),
        input('Your hero\'s secret name', name='secret_name', required=True),
        input('Your hero\'s age', name='age', type=NUMBER, required=True),
    ]

    user_data = input_group('Add your own super hero', add_fields, cancelable=True)

    # Create a new hero as an Hero object and add it to db
    global valid_user
    if user_data is not None:
        with app.app_context():
            new_hero = Hero(name=user_data['name'], secret_name=user_data['secret_name'], age=user_data['age'],
                            created_by=valid_user.id)
        try:
            # with Session() as session:
            with app.app_context():
                db.session.add(new_hero)
                db.session.commit()
            # print(session.query(Hero).all())
        except SQLAlchemyError:
            toast(f'An error occurred', color='error')
        else:
            toast(f'Hero added', color='success')
        finally:
            main()


# Updating a hero by getting it from the db and manipuating one of the fields
def update_hero():
    selected_data = input_group('Select a hero to update', [input('ID of hero to update', name='hero_id', type=NUMBER)],
                                cancelable=True)
    if selected_data is not None:
        try:
            # with Session() as session:
            with app.app_context():
                if valid_user.role == 'standard':
                    selected_hero = Hero.query.filter_by(id=int(selected_data['hero_id']),
                                                         created_by=get_user_id()).first()
                elif valid_user.role == 'super':
                    selected_hero = Hero.query.filter_by(id=int(selected_data['hero_id'])).first()
                if selected_hero is None:
                    raise ValueError('Invalid hero ID or not authorized to update this hero')
                else:
                    update_fields = [
                        input('Hero\'s name', name='name', required=True, value=str(selected_hero.name)),
                        input('Hero\'s secret name', name='secret_name', required=True,
                              value=str(selected_hero.secret_name)),
                        input('Hero\'s age', name='age', type=NUMBER, required=True, value=str(selected_hero.age))
                    ]
                    new_data = input_group('Update your super hero', update_fields, cancelable=True)
                print(selected_hero)
                if new_data is not None:
                    selected_hero.name = new_data['name']
                    selected_hero.secret_name = new_data['secret_name']
                    selected_hero.age = new_data['age']
                    db.session.add(selected_hero)
                    db.session.commit()
                    # print(session.query(Hero).all())
                else:
                    raise ValueError('No changes made')
        except SQLAlchemyError:
            toast(f'An error occurred', color='error')
        except ValueError as ve:
            toast(f'{str(ve)}', color='error')
        else:
            toast(f'{selected_hero.name} was updated', color='success')
        finally:
            main()
    else:
        toast(f'No hero selected', color='warning')


# Deleting a hero
def delete_hero():
    del_fields = [
        input("ID of hero to delete", name='hero_id', type=NUMBER, required=True),
        input("Confirm the name of the hero to delete", name='hero_name', required=True)
    ]

    selected_data = input_group('Delete a hero',
                                [input("ID of hero to delete", name='hero_id', type=NUMBER, required=True)],
                                cancelable=True)

    if selected_data is not None:
        try:
            # with Session() as session:
            with app.app_context():
                if valid_user.role == 'standard':
                    selected_hero = Hero.query.filter_by(id=int(selected_data['hero_id']),
                                                         created_by=get_user_id()).first()
                elif valid_user.role == 'super':
                    selected_hero = Hero.query.filter_by(id=int(selected_data['hero_id'])).first()
                if selected_hero is None:
                    raise ValueError('Invalid hero ID or not authorized to delete this hero')
                else:
                    confirm = input_group("Confirm Deletion", [
                        input("Confirm the name of the hero to delete", name='hero_name', required=True)],
                                          cancelable=True)
                    if confirm['hero_name'] != selected_hero.name:
                        raise ValueError('Hero name does not match')
                    else:
                        db.session.delete(selected_hero)
                        db.session.commit()
                        # print(session.query(Hero).all())
        # to catch error
        except ValueError as ve:
            toast(f'{str(ve)}', color='error')
        else:
            toast(f'{selected_hero.name} was deleted', color='success')
        finally:
            main()


def get_username(user_id=None):
    global valid_user
    if valid_user is not None and user_id is None:
        return valid_user.username
    elif user_id is not None:
        # with Session() as session:
        with app.app_context():
            selected_user = User.query.filter_by(id=user_id).first()
            return selected_user.username
    else:
        return 'Guest User'


def get_heroes_table(user):
    table_data = []
    if user is not None:
        # with Session() as session:
        with app.app_context():
            results = Hero.query.all()
            for hero in results:
                if user.role == 'super':
                    table_data.append([str(hero.id), str(hero.name), str(hero.secret_name), str(hero.age),
                                       str(get_username(hero.created_by))])
                elif user.role == 'standard':
                    table_data.append([str(hero.id), str(hero.name), str(hero.secret_name), str(hero.age)])
    else:
        # with Session() as session:
        with app.app_context():
            results = Hero.query.all()
            for hero in results:
                table_data.append([str(hero.id), str(hero.name)])
    return table_data


def toggle_dark_mode():
    clear()
    global dark_mode
    dark_mode = not dark_mode
    main()


app.add_url_rule('/', 'webio_view', webio_view(main), methods=['GET', 'POST', 'OPTIONS'])
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", type=int, default=8080)
    args = parser.parse_args()
    start_server(app, port=args.port)
if __name__ == '__main__':
    app()
