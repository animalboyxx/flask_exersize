import os
from flask import Flask, render_template, request, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from wtforms.validators import DataRequired
from wtforms import StringField, FloatField, IntegerField, SubmitField, SelectField
from flask_wtf import FlaskForm

from sqlalchemy.sql import func

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret-key-goes-here'
app.config['SQLALCHEMY_DATABASE_URI'] = \
    'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class SpendType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)


class Spending(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    summ = db.Column(db.Float, nullable=False)
    spend_type = db.Column(db.Integer, db.ForeignKey('spend_type.id'))


with app.app_context():
    # db.drop_all()
    db.create_all()


class InputData(FlaskForm):
    summ = FloatField("summ", validators=[DataRequired()])
    # spend_type = IntegerField("spend_type", validators=[DataRequired()])
    # anus = SelectField('ANUS', coerce=str)
    spend_type = SelectField('spend_type', coerce=str)
    submit = SubmitField("Submit")


class InputSpendType(FlaskForm):
    name = StringField("Тип траты", validators=[DataRequired()])
    submit = SubmitField("Отправить")


@app.route("/", methods=["POST", "GET"])
def index():
    form = InputData()
    spendings = Spending.query.all()
    #https://wtforms.readthedocs.io/en/3.0.x/fields/?highlight=selectfield#wtforms.fields.SelectField
    form.spend_type.choices = [g.name for g in SpendType.query.order_by('name')]
    if form.is_submitted():
        add_row = Spending(summ=request.form['summ'],
                           spend_type=SpendType.query.filter(SpendType.name == request.form['spend_type']).first().id)
        try:
            db.session.add(add_row)
            db.session.commit()
            print('все ок')
            return render_template('index.html', form=form, spendings=spendings)
        except Exception:
            print('добавления в БД не случилось, проверьте правильность введенных данных')
    return render_template('index.html', form=form, spendings=spendings)


@app.route("/spend_type", methods=["POST", "GET"])
def spend_type():
    spend_types = SpendType.query.all()
    form = InputSpendType()
    if form.is_submitted():
        add_row = SpendType(name=request.form['name'])
        try:
            db.session.add(add_row)
            db.session.commit()
            print('все ок 2')
        except Exception:
            print('хуев дров')

    return render_template('spend_type.html', spend_types=spend_types, form=form)


if __name__ == '__main__':
    app.run(debug=True, port=5000)
