from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, FloatField, SelectField, DateField, SubmitField
from wtforms.validators import DataRequired, Email

class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Register")

class LoginForm(FlaskForm):
    email = StringField("Email", validators=[Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")

class TransactionForm(FlaskForm):
    amount = FloatField("Amount", validators=[DataRequired()])
    type = SelectField("Type", choices=[('income','Income'), ('expense','Expense')])
    category = SelectField("Category", coerce=int)   # ✅ NEW
    description = StringField("Description")
    date = DateField("Date")
    submit = SubmitField("Save")

