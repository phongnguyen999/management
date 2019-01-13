# app/admin/views.py

from flask import abort, flash, redirect, render_template, url_for
from flask_login import current_user, login_required
from sqlalchemy import func
from datetime import datetime
from datetime import date, timedelta as _timedelta, datetime

from . import admin
from forms import DepartmentForm, EmployeeAssignForm, RoleForm, EmployeePayroll
from .. import db
from ..models import Department, Employee, Role
from sqlalchemy import desc
class timedelta(_timedelta):
    def __str__(self):
        """
        String representation in form of "HH:MM"
        """
        hours = self.seconds // 3600
        minutes = (self.seconds % 3600) // 60
        return "%d:%02d" % (hours, minutes)

def check_admin():
    """
    Prevent non-admins from accessing the page
    """
    if not current_user.is_admin:
        abort(403)
def getSale(departments):
    salesList = []
    for sales in departments:
        i = sales.salary
        salesList.insert(0,i)
    salesList = sum(salesList)
    # if 10000 <= salesList < 100000:
    #     salesList = str(salesList)[:2]+"K"
    return salesList

def getFactor(companies,selected_company):
    for employee in companies:
        if str(employee.username) == str(selected_company):
            factor = str(employee.role.name)
            break
        else:
            factor = None
    return  factor

def current_week_ending_date():
    return date.today() + timedelta(days=(7 - date.today().weekday()))


def week_ending_dates(weeks=7):

    week_day_date = current_week_ending_date()
    for _ in range(7):
        yield week_day_date
        week_day_date -= timedelta(weeks=1)
# Department Views
@admin.route("/departments/<date:from_date>/<date:to_date>/<employee_code>")
@admin.route("/departments/<date:from_date>/<date:to_date>")
@admin.route("/departments/<employee_code>")
@admin.route('/departments', methods=['GET', 'POST'])
@login_required
def list_departments(employee_code=None,from_date=None, to_date=None):
    """
    List all employees
    """
    check_admin()
    selected_company = Employee.query.filter(Employee.id==employee_code).first() if employee_code else None

    companies = Employee.query.all()
    factor = None
    check = None
    cash = None

    _utcnow = datetime.utcnow().date()
    _isoweek = _utcnow.isocalendar()[1]

    if from_date and to_date:
        # query = (Department.select(Department, Employee).join(Employee,
        #                                                       on=Employee.username)
        #          .where((Department.date >= from_date) & (Department.date <= to_date)))
        if employee_code:
            #departments = db.session.query(Department).filter(func.dayofweek(Department.date) == 2).filter(Department.employee_id == employee_code).all()
            #departments = db.session.query(Department).filter(func.weekofyear(Department.date) == _isoweek).all()
            #departments = Department.query.filter(Department.employee_id == employee_code).all()
            #departments = Department.query.filter_by(user.username=emploee_code).first_or_404()
            departments = db.session.query(Department).filter((Department.date >= from_date) & (Department.date <= to_date)).filter(Department.employee_id == employee_code).all()
            salesList = getSale(departments)

            factor = getFactor(companies,selected_company)

            if factor == "7/3":
                multiplyFactor = 0.7
            elif factor == "6/4":
                multiplyFactor = 0.6
            elif factor == "5/5":
                multiplyFactor = 0.5
            else:
                multiplyFactor = 0

            divide = float(salesList) * multiplyFactor
            float("{0:.1f}".format(divide))
            check = float("{0:.1f}".format(divide)) * 0.7
            cash = float("{0:.1f}".format(divide)) - check
            float("{0:.1f}".format(check))
            float("{0:.1f}".format(cash))


        else:
            departments = db.session.query(Department).filter((Department.date >= from_date) & (Department.date <= to_date)).all()
            salesList = getSale(departments)
            divide = salesList

        #entries = query.execute()
    else:
        departments = Department.query.all()
        salesList = getSale(departments)
        divide = salesList
    week_start_dates = (d + timedelta(days=6) for d in week_ending_dates())

    return render_template('admin/departments/departments.html',companies=companies,selected_company = selected_company,
                           departments=departments, title="Sales", salesList = salesList, divide=divide,
        from_date=from_date,
        to_date=to_date, week_ending_dates=week_ending_dates(),
        week_start_dates=week_start_dates,factor=factor,cash=cash, check=check )

#@admin.route('/departments/add/<int:id>', methods=['GET', 'POST'])
@admin.route('/departments/add', methods=['GET', 'POST'])
@login_required
def add_department():
    """
    Add a department to the database
    """
    check_admin()

    add_department = True
    #departments = Department.query.all()
    form = DepartmentForm()
    if form.validate_on_submit():
        #department.employee = form.employee.data
        #department = Department(name=form.name.data, employee = form.employee.data,
                                #description=form.description.data, salary=form.payAmount.data, date = form.date.data)
        department = Department(employee = form.employee.data,
                                salary=form.payAmount.data, date = form.date.data)



        try:
            # add department to the database
            db.session.add(department)
            db.session.commit()
            flash('You have successfully added a new sale.')
        except:
            # in case department name already exists
            flash('Error: department name already exists.')

        # redirect to departments page
        return redirect(url_for('admin.list_departments'))

    # load department template
    return render_template('admin/departments/department.html', action="Add",
                           add_department=add_department, form=form,
                           title="Add Sale")


@admin.route('/departments/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_department(id):
    """
    Edit a department
    """
    check_admin()

    add_department = False

    department = Department.query.get_or_404(id)
    form = DepartmentForm(obj=department)
    if form.validate_on_submit():
        department.employee = form.employee.data
    #    department.name = form.name.data
    #    department.description = form.description.data
        department.salary = form.payAmount.data
        department.date = form.date.data
        db.session.commit()
        flash('You have successfully edited the sale.')

        # redirect to the departments page
        return redirect(url_for('admin.list_departments'))

    #form.description.data = department.description
    #form.name.data = department.name
    return render_template('admin/departments/department.html', action="Edit",
                           add_department=add_department, form=form,
                           department=department, title="Edit Sales")


@admin.route('/departments/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_department(id):
    """
    Delete a department from the database
    """
    check_admin()

    department = Department.query.get_or_404(id)
    db.session.delete(department)
    db.session.commit()
    flash('You have successfully deleted the sale.')

    # redirect to the departments page
    return redirect(url_for('admin.list_departments'))

    return render_template(title="Delete Sales")

@admin.route('/roles')
@login_required
def list_roles():
    check_admin()
    """
    List all roles
    """

    roles = Role.query.all()
    return render_template('admin/roles/roles.html',
                           roles=roles, title='Roles')


@admin.route('/roles/add', methods=['GET', 'POST'])
@login_required
def add_role():
    """
    Add a role to the database
    """
    check_admin()

    add_role = True

    form = RoleForm()
    if form.validate_on_submit():
        role = Role(name=form.name.data,
                    description=form.description.data)

        try:
            # add role to the database
            db.session.add(role)
            db.session.commit()
            flash('You have successfully added a new role.')
        except:
            # in case role name already exists
            flash('Error: role name already exists.')

        # redirect to the roles page
        return redirect(url_for('admin.list_roles'))

    # load role template
    return render_template('admin/roles/role.html', add_role=add_role,
                           form=form, title='Add Role')


@admin.route('/roles/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_role(id):
    """
    Edit a role
    """
    check_admin()

    add_role = False

    role = Role.query.get_or_404(id)
    form = RoleForm(obj=role)
    if form.validate_on_submit():
        role.name = form.name.data
        role.description = form.description.data
        db.session.add(role)
        db.session.commit()
        flash('You have successfully edited the role.')

        # redirect to the roles page
        return redirect(url_for('admin.list_roles'))

    form.description.data = role.description
    form.name.data = role.name
    return render_template('admin/roles/role.html', add_role=add_role,
                           form=form, title="Edit Role")


@admin.route('/roles/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_role(id):
    """
    Delete a role from the database
    """
    check_admin()

    role = Role.query.get_or_404(id)
    db.session.delete(role)
    db.session.commit()
    flash('You have successfully deleted the role.')

    # redirect to the roles page
    return redirect(url_for('admin.list_roles'))

    return render_template(title="Delete Role")

@admin.route('/employees')
@login_required
def list_employees():
    """
    List all employees
    """
    check_admin()

    employees = Employee.query.all()
    return render_template('admin/employees/employees.html',
                           employees=employees, title='Employees')


@admin.route('/employees/assign/<int:id>', methods=['GET', 'POST'])
@login_required
def assign_employee(id):
    """
    Assign a department and a role to an employee
    """
    check_admin()

    employee = Employee.query.get_or_404(id)

    # prevent admin from being assigned a department or role
    if employee.is_admin:
        abort(403)

    form = EmployeeAssignForm(obj=employee)
    if form.validate_on_submit():
        #employee.department = form.department.data
        employee.role = form.factor.data
        #employee.salaries = form.payAmount.data
        db.session.add(employee)
        db.session.commit()
        flash('You have successfully assigned a department and role.')

        # redirect to the roles page
        return redirect(url_for('admin.list_employees'))

    return render_template('admin/employees/employee.html',
                           employee=employee, form=form,
                           title='Assign Employee\'s factor ')
