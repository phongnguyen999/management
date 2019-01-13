# app/admin/forms.py

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField,DateTimeField
from wtforms.validators import DataRequired
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from datetime import datetime
from datetime import date
from ..models import Department, Role, Employee


class DepartmentForm(FlaskForm):
    """
    Form for admin to add or edit a department
    """
    employee = QuerySelectField(query_factory=lambda: Employee.query.all(),
                                  get_label="username")
    payAmount = IntegerField('Amount')
    #name = StringField('Name', validators=[DataRequired()])
    #description = StringField('Description', validators=[DataRequired()])
    date = DateTimeField(
        "Today", format="%Y-%m-%d",
        default=date.today(), ## Now it will call it everytime.
        validators=[DataRequired()])
    submit = SubmitField('Submit')

class RoleForm(FlaskForm):
    """
    Form for admin to add or edit a role
    """
    name = StringField('Name', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    submit = SubmitField('Submit')

class EmployeePayroll(FlaskForm):
    """
    Assign pay stub
    """
    employee = QuerySelectField(query_factory=lambda: Employee.query.all(),
                                  get_label="username")
    payAmount = IntegerField('Amount')
    submit = SubmitField('Submit')

class EmployeeAssignForm(FlaskForm):
    """
    Form for admin to assign departments and roles to employees
    """
    #department = QuerySelectField(query_factory=lambda: Department.query.all(),
                                  #get_label="name")
    factor = QuerySelectField(query_factory=lambda: Role.query.all(),
                            get_label="name")
    #payAmount = IntegerField('Amount')
    submit = SubmitField('Submit')
