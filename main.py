from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import uuid

app = FastAPI()

# defining what an expense looks like
class Expense(BaseModel):
    title: str
    amount: float
    category: str
    description: Optional[str] = None

# storing expenses in a list for now
# will connect to a proper database later
expenses = []


@app.get("/")
def home():
    return {"message": "my expense tracker api is working!"}


# get all expenses
@app.get("/expenses")
def get_expenses():
    return {"expenses": expenses, "count": len(expenses)}


# add a new expense
@app.post("/expenses")
def add_expense(expense: Expense):
    new_expense = {
        "id": str(uuid.uuid4()),
        "title": expense.title,
        "amount": expense.amount,
        "category": expense.category,
        "description": expense.description
    }
    expenses.append(new_expense)
    return {"message": "added!", "expense": new_expense}


# filter by category
@app.get("/expenses/category/{category}")
def get_by_category(category: str):
    result = [e for e in expenses if e["category"].lower() == category.lower()]
    if not result:
        raise HTTPException(status_code=404, detail="nothing found in this category")
    return {"expenses": result}


# get one expense by id
@app.get("/expenses/{expense_id}")
def get_expense(expense_id: str):
    for e in expenses:
        if e["id"] == expense_id:
            return e
    raise HTTPException(status_code=404, detail="expense not found")


# delete an expense
@app.delete("/expenses/{expense_id}")
def delete_expense(expense_id: str):
    for e in expenses:
        if e["id"] == expense_id:
            expenses.remove(e)
            return {"message": "deleted!"}
    raise HTTPException(status_code=404, detail="expense not found")


# total spending stats
@app.get("/expenses/stats/total")
def get_total():
    total = sum(e["amount"] for e in expenses)

    breakdown = {}
    for e in expenses:
        cat = e["category"]
        if cat not in breakdown:
            breakdown[cat] = 0
        breakdown[cat] += e["amount"]

    return {
        "total": total,
        "num_expenses": len(expenses),
        "by_category": breakdown
    }


# ai analysis - smart spending insights
@app.get("/expenses/ai/analyze")
def analyze_expenses():
    if not expenses:
        raise HTTPException(status_code=404, detail="add some expenses first")

    total = sum(e["amount"] for e in expenses)

    breakdown = {}
    for e in expenses:
        cat = e["category"]
        if cat not in breakdown:
            breakdown[cat] = 0
        breakdown[cat] += e["amount"]

    top_category = max(breakdown, key=breakdown.get)
    top_amount = breakdown[top_category]
    percentage = round((top_amount / total) * 100, 1)

    tips = {
        "Food": "Try meal prepping at home — can save up to 40% on food costs.",
        "Travel": "Use public transport when possible to cut travel costs.",
        "Entertainment": "Look for free events or student discounts in your area.",
        "Shopping": "Wait 24 hours before buying — helps avoid impulse purchases.",
        "Other": "Track these expenses daily to find patterns."
    }

    tip = tips.get(top_category, "Set a monthly budget for each category.")

    analysis = f"""You have spent Rs.{total} in total across {len(expenses)} expenses.
Your highest spending is on {top_category} which is {percentage}% of your total spending (Rs.{top_amount}).
Suggestion: {tip}
Try to reduce {top_category} spending by 20% next month to save Rs.{round(top_amount * 0.2)}."""

    return {
        "total_spent": total,
        "num_expenses": len(expenses),
        "by_category": breakdown,
        "top_spending_category": top_category,
        "ai_suggestions": analysis
    }