from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from core.forms import *
from core.models import *
import csv
import datetime
from decimal import *
import locale

#TODO:
# Some future iterations to consider
# - Allow multiple csv files to be uploaded at once
# - Allow multiple currencies
# - Add a form so users can submit expenses, not just upload csv files
# - Add a view to look at past expenses

# Create your views here.
def Upload( request ):

    # I used locale to convert expenses to numbers since it would take care of commas (eg 1,000)
    # If multiple currencies are possible, we would need to know what currency it is to be able
    # to parse it. 
    if locale.getlocale()[0] != 'en_US':
        locale.setlocale(locale.LC_ALL, 'en_US')

    expenseDict = None
    fileResults = None
    form = FileUploadForm()
    if request.method == "POST":
        form = FileUploadForm( request.POST, request.FILES )
        
        if form.is_valid():
            fileResults = handle_file(request.FILES['file'])
        else:
            print "Form Errors: " , form.errors
    
    context = {
        "form": form
    }
    if fileResults:
        if fileResults['error']:
            context['error'] = fileResults['error']
        else:   
            expenseDict = fileResults['expenseDict']
            context["expenseDict"] = sorted(expenseDict.iteritems())    
    
    return render( request, "fileUpload.html", context )


def handle_file(csvFile):
    # One thing to consider is how large will the csv files be. 
    reader = csv.reader(csvFile)
    results = {}

    # Validation:
    # - Can also check other things such as all expenses have at most 2 decimal places
    # - order of headings is as expected
    # - each row has the expected number of columns and the values are valid (all expenses are valid numbers etc.)
    # - Could return warnings for duplicate rows. Duplicates may be valid cases so the user would need to investigate
    try:
        headerRow = reader.next()
        if len(headerRow) != 8:
            results['error'] = "Incorrect number of headers"
            return results
    except StopIteration:
        results['error'] = "Empty file"
        return results

    expenseDict = {}
    
    for row in reader:
        # I make the assumption here that the imported data is well-formed. Future iterations should really
        # verify that these values exist before using them, and that the values are sanitized for security
        # reasons. 
        expenseDate = datetime.datetime.strptime(row[0], "%m/%d/%Y")
        preTaxAmt =   locale.atof(row[5])
        
        taxAmt = locale.atof(row[7])
        
        if preTaxAmt < 0 or taxAmt < 0:
            results['error'] = "Negative tax amounts are not allowed"

        employeeName = row[2]
        employeeInfo, createdEmployee = Employee.objects.get_or_create(
                employee_name = employeeName,
                employee_address = row[3]
        )
        
        expenseCat, createdCat = ExpenseCategories.objects.get_or_create(
                category = row[1]
        )
        
        expenseInfo, createdExpense = EmployeeExpense.objects.get_or_create(
            employee = employeeInfo,
            date = expenseDate,
            category = expenseCat,
            expense_desc = row[4],
            pre_tax_amt = preTaxAmt,
            tax_name = row[6],
            tax_amt = taxAmt
        )

        dateKey = expenseDate.strftime('%Y/%m')
        
        # Since this web app displays expenses of the uploaded file, duplicate expenses that were previously created
        # will still be summed if included in the uploaded file
        # This also assumes that all expenses are reported in the same currency ($)
        # I decided to use a dictionary to sum up the per month values because the values are based on the uploaded file
        # I didn't want to query the DB since it wouldn't easily return the data associated with a single file upload.
        if expenseDict.has_key(dateKey):
            expenseDict[dateKey] = expenseDict[dateKey] + preTaxAmt + taxAmt
        else:
            expenseDict[dateKey] = preTaxAmt + taxAmt
    results['expenseDict'] = expenseDict
    results['error'] = None
    return results