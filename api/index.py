from pywebio import *
from pywebio.input import *
from pywebio.output import *
from pywebio.platform.flask import webio_view
from pywebio import STATIC_PATH, start_server
import argparse
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, sessionmaker, declarative_base, relationship, DeclarativeBase

app = Flask(__name__)
app.config[
    "SQLALCHEMY_DATABASE_URI"] = "postgresql://default:UcK1XulWN4AB@ep-tiny-sound-a2lz6d2f.eu-central-1.aws.neon.tech:5432/verceldb?sslmode=require"
# Initialize SQLAlchemy and defining a simple Book model
db = SQLAlchemy(app)


class User(db.Model):
    # id = db.Column(db.Integer, primary_key=True)
    # username = db.Column(db.String(20), unique=True, nullable=False)
    # password = db.Column(db.String(60), nullable=False)
    # role = db.Column(db.String(20), nullable=False)

    # __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    role: Mapped[str]

    # heroes: Mapped[list["Hero"]] = relationship("Hero", back_populates="creator", cascade="all, delete")

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username})>"


with app.app_context():
    db.create_all()


@use_scope('ROOT')
def main():
    new_user = User(username='khantthura', password='helloworld', role='admin')
    db.session.add(new_user)
    db.session.commit()
    put_text('User added')
    put_text(User.query.all())


app.add_url_rule('/', 'webio_view', webio_view(main), methods=['GET', 'POST', 'OPTIONS'])
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", type=int, default=8080)
    args = parser.parse_args()
    start_server(app, port=args.port)
if __name__ == '__main__':
    app()
