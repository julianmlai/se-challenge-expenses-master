from __future__ import unicode_literals

from django.db import models

# Create your models here.

# I decided to break up the problem into 3 tables (Employee, ExpenseCategories, EmployeeExpense) since
# it's a better design than storing all of the data in a single table. In a single table, you end up 
# duplicating alot of information that won't change very often such as employee info or the expense categories.
# Without normalizing it, each row would include employee name, address, and category which duplicates much of the data
# This solution reduces the amount of repeated data but is not quite correct since an employee that moved would
# create a new entry in the Employee table. In the better case, an employee Id would be passed in or could
# be looked up in another database so an employee that changes names or an employee that moves won't create a
# new Employee record
class Employee(models.Model):
    employee_name = models.CharField(max_length=100)
    employee_address = models.CharField(max_length=200)

class ExpenseCategories(models.Model):
    category = models.CharField(max_length=100)

# on_delete cascade because it wouldn't make sense for an employee expense not to be associated
# with an employee/category
# DecimalField rather than float to handle currency
class EmployeeExpense(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    date = models.DateField()
    category = models.ForeignKey(ExpenseCategories, on_delete=models.CASCADE)
    expense_desc = models.CharField(max_length=200)
    pre_tax_amt = models.DecimalField(max_digits=10, decimal_places=2)
    tax_name = models.CharField(max_length=100)
    tax_amt = models.DecimalField(max_digits=10, decimal_places=2)
