"""empty message

Revision ID: 97f92021c621
Revises: 4cad78e0d717
Create Date: 2019-01-04 22:10:59.653361

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '97f92021c621'
down_revision = '4cad78e0d717'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('departments', sa.Column('employee_id', sa.Integer(), nullable=True))
    op.add_column('departments', sa.Column('salary', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'departments', 'employees', ['employee_id'], ['id'])
    op.drop_constraint(u'employees_ibfk_1', 'employees', type_='foreignkey')
    op.drop_column('employees', 'department_id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('employees', sa.Column('department_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True))
    op.create_foreign_key(u'employees_ibfk_1', 'employees', 'departments', ['department_id'], ['id'])
    op.drop_constraint(None, 'departments', type_='foreignkey')
    op.drop_column('departments', 'salary')
    op.drop_column('departments', 'employee_id')
    # ### end Alembic commands ###
