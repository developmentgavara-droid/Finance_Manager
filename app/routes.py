from flask import Blueprint, render_template, redirect, url_for, flash, request,jsonify
from .models import User, Transaction, Category
from .forms import RegisterForm, LoginForm, TransactionForm
from . import db, login_manager
from flask_login import login_user, login_required, logout_user, current_user
import bcrypt
from datetime import datetime
from collections import defaultdict
main = Blueprint('main', __name__)

@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(id=int(user_id)).first()


@main.route('/')
def home():
    return redirect(url_for('main.login'))

@main.route('/register', methods=['GET','POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed = bcrypt.hashpw(form.password.data.encode('utf-8'), bcrypt.gensalt())
        user = User(username=form.username.data,
                    email=form.email.data,
                    password=hashed.decode('utf-8'))
        db.session.add(user)
        db.session.commit()
        flash("Registered successfully!")
        return redirect(url_for('main.login'))
    return render_template('register.html', form=form)

@main.route('/login', methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user and bcrypt.checkpw(
                form.password.data.encode('utf-8'),
                user.password.encode('utf-8')
            ):
            login_user(user)
            flash("Login successful!")
            return redirect(url_for('main.dashboard'))
        else:
            flash("Invalid email or password")

    return render_template('login.html', form=form)

@main.route('/dashboard')
@login_required
def dashboard():
    transactions = Transaction.query.filter_by(user_id=current_user.id).all()

    income = sum(t.amount for t in transactions if t.type=='income')
    expense = sum(t.amount for t in transactions if t.type=='expense')

    return render_template('dashboard.html',transactions=transactions,income=income,expense=expense)


@main.route('/add', methods=['GET','POST'])
@login_required
def add_transaction():
    form = TransactionForm()

    # Load categories of current user into dropdown
    categories = Category.query.filter_by(user_id=current_user.id).all()
    form.category.choices = [(c.id, c.name) for c in categories]

    if form.validate_on_submit():
        t = Transaction(
            amount=form.amount.data,
            type=form.type.data,
            category_id=form.category.data,   # ✅ SAVE CATEGORY
            description=form.description.data,
            date=form.date.data,
            user_id=current_user.id
        )
        db.session.add(t)
        db.session.commit()
        flash("Transaction added!")
        return redirect(url_for('main.dashboard'))

    return render_template('add_transaction.html', form=form)


@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.login'))
@main.route('/categories', methods=['GET','POST'])
@login_required
def categories():
    if request.method == 'POST':
        name = request.form['name']
        c = Category(name=name, user_id=current_user.id)
        db.session.add(c)
        db.session.commit()

    categories = Category.query.filter_by(user_id=current_user.id).all()
    return render_template('categories.html', categories=categories)


@main.route('/summary')
@login_required
def summary():
    month = request.args.get('month', type=int)
    year = request.args.get('year', type=int)

    if month and year:
        from .services import monthly_summary
        income, expense = monthly_summary(current_user.id, month, year)
        return render_template('summary.html', income=income, expense=expense)

    return render_template('summary.html')
@main.route('/chart-data')
@login_required
def chart_data():
    data = defaultdict(lambda: {'income':0,'expense':0})

    for t in Transaction.query.filter_by(user_id=current_user.id).all():
        key = t.date.strftime('%b')
        data[key][t.type] += t.amount

    labels = list(data.keys())
    income = [data[m]['income'] for m in labels]
    expense = [data[m]['expense'] for m in labels]

    return jsonify({'labels':labels,'income':income,'expense':expense})
@main.route('/edit/<int:id>', methods=['GET','POST'])
@login_required
def edit(id):
    t = Transaction.query.get(id)
    form = TransactionForm(obj=t)

    # ✅ LOAD categories again
    categories = Category.query.filter_by(user_id=current_user.id).all()
    form.category.choices = [(c.id, c.name) for c in categories]

    # ✅ PRESELECT current category
    if request.method == 'GET':
        form.category.data = t.category_id

    if form.validate_on_submit():
        t.amount = form.amount.data
        t.type = form.type.data
        t.category_id = form.category.data   # ✅ SAVE CATEGORY
        t.description = form.description.data
        t.date = form.date.data
        db.session.commit()
        flash("Transaction updated!")
        return redirect(url_for('main.dashboard'))

    return render_template('edit_transaction.html', form=form, transaction=t)


@main.route('/delete/<int:id>')
@login_required
def delete(id):
    t = Transaction.query.get(id)
    db.session.delete(t)
    db.session.commit()
    flash("Transaction deleted!")
    return redirect(url_for('main.dashboard'))

