from .models import Transaction
from datetime import datetime
from sqlalchemy import extract
from . import db

def monthly_summary(user_id, month, year):
    income = db.session.query(db.func.sum(Transaction.amount)).filter(
        Transaction.user_id == user_id,
        Transaction.type == 'income',
        extract('month', Transaction.date) == month,
        extract('year', Transaction.date) == year
    ).scalar() or 0

    expense = db.session.query(db.func.sum(Transaction.amount)).filter(
        Transaction.user_id == user_id,
        Transaction.type == 'expense',
        extract('month', Transaction.date) == month,
        extract('year', Transaction.date) == year
    ).scalar() or 0

    return income, expense

