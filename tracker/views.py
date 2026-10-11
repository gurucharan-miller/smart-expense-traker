from datetime import date, timedelta
from decimal import Decimal
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Sum
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from .forms import SignUpForm, ExpenseForm
from .models import Expense
from .utils import predict_category

def signup_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    form = SignUpForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, "Account created successfully.")
        return redirect("dashboard")
    return render(request, "registration/signup.html", {"form": form})

@login_required
def dashboard(request):
    today = timezone.localdate()
    expenses = Expense.objects.filter(user=request.user)
    week_start = today - timedelta(days=today.weekday())
    month_start = today.replace(day=1)
    total = expenses.aggregate(value=Sum("amount"))["value"] or Decimal("0.00")
    weekly = expenses.filter(date__gte=week_start, date__lte=today).aggregate(value=Sum("amount"))["value"] or Decimal("0.00")
    monthly = expenses.filter(date__gte=month_start, date__lte=today).aggregate(value=Sum("amount"))["value"] or Decimal("0.00")
    category_rows = expenses.values("category").annotate(total=Sum("amount")).order_by("-total")
    recent = expenses[:8]
    return render(request, "tracker/dashboard.html", {
        "total": total, "weekly": weekly, "monthly": monthly, "recent": recent,
        "category_labels": [row["category"] for row in category_rows],
        "category_values": [float(row["total"]) for row in category_rows],
    })

@login_required
def expense_list(request):
    expenses = Expense.objects.filter(user=request.user)
    category = request.GET.get("category", "")
    if category:
        expenses = expenses.filter(category=category)
    return render(request, "tracker/expense_list.html", {"expenses": expenses, "category": category, "categories": Expense.CATEGORY_CHOICES})

@login_required
def expense_create(request):
    form = ExpenseForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        expense = form.save(commit=False)
        expense.user = request.user
        if not expense.category or expense.category == "Other":
            expense.category = predict_category(f"{expense.title} {expense.notes}")
        expense.save()
        messages.success(request, "Expense added successfully.")
        return redirect("expense_list")
    return render(request, "tracker/expense_form.html", {"form": form, "heading": "Add expense"})

@login_required
def expense_edit(request, pk):
    expense = get_object_or_404(Expense, pk=pk, user=request.user)
    form = ExpenseForm(request.POST or None, instance=expense)
    if request.method == "POST" and form.is_valid():
        item = form.save(commit=False)
        if item.category == "Other":
            item.category = predict_category(f"{item.title} {item.notes}")
        item.save()
        messages.success(request, "Expense updated successfully.")
        return redirect("expense_list")
    return render(request, "tracker/expense_form.html", {"form": form, "heading": "Edit expense"})

@login_required
def expense_delete(request, pk):
    expense = get_object_or_404(Expense, pk=pk, user=request.user)
    if request.method == "POST":
        expense.delete()
        messages.success(request, "Expense deleted.")
        return redirect("expense_list")
    return render(request, "tracker/expense_confirm_delete.html", {"expense": expense})
