"""Seed test data

Revision ID: <your_new_revision_id>
Revises: 6c59d07f0e99
Create Date: <timestamp>

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
# Note: replace <your_new_revision_id> with the actual ID from the filename
revision = 'd0a56b944ba0'
down_revision = '6c59d07f0e99'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Define table helpers
    buildings_table = sa.table('buildings',
        sa.column('id', sa.Integer),
        sa.column('address', sa.String),
        sa.column('latitude', sa.Float),
        sa.column('longitude', sa.Float)
    )
    activities_table = sa.table('activities',
        sa.column('id', sa.Integer),
        sa.column('name', sa.String),
        sa.column('parent_id', sa.Integer)
    )
    organizations_table = sa.table('organizations',
        sa.column('id', sa.Integer),
        sa.column('name', sa.String),
        sa.column('building_id', sa.Integer)
    )
    phone_numbers_table = sa.table('phone_numbers',
        sa.column('id', sa.Integer),
        sa.column('number', sa.String),
        sa.column('organization_id', sa.Integer)
    )
    organization_activity_association_table = sa.table('organization_activity_association',
        sa.column('organization_id', sa.Integer),
        sa.column('activity_id', sa.Integer)
    )

    # Insert Buildings
    op.bulk_insert(buildings_table, [
        {'id': 1, 'address': 'г. Москва, ул. Ленина, д. 1', 'latitude': 55.7558, 'longitude': 37.6173},
        {'id': 2, 'address': 'г. Новосибирск, ул. Блюхера, 32/1', 'latitude': 54.9833, 'longitude': 82.8958},
        {'id': 3, 'address': 'г. Санкт-Петербург, Невский пр., д. 100', 'latitude': 59.9343, 'longitude': 30.3351},
    ])

    # Insert Activities (with explicit IDs for relationships)
    op.bulk_insert(activities_table, [
        # Level 1
        {'id': 1, 'name': 'Еда', 'parent_id': None},
        {'id': 2, 'name': 'Автомобили', 'parent_id': None},
        # Level 2
        {'id': 3, 'name': 'Мясная продукция', 'parent_id': 1},
        {'id': 4, 'name': 'Молочная продукция', 'parent_id': 1},
        {'id': 5, 'name': 'Легковые', 'parent_id': 2},
        {'id': 6, 'name': 'Грузовые', 'parent_id': 2},
        # Level 3
        {'id': 7, 'name': 'Запчасти', 'parent_id': 5},
        {'id': 8, 'name': 'Аксессуары', 'parent_id': 5},
    ])
    
    # Insert Organizations
    op.bulk_insert(organizations_table, [
        {'id': 1, 'name': 'ООО "Рога и Копыта"', 'building_id': 1},
        {'id': 2, 'name': 'ПАО "Мясокомбинат"', 'building_id': 2},
        {'id': 3, 'name': 'ИП "Молочные реки"', 'building_id': 2},
        {'id': 4, 'name': 'Автосервис "Четыре колеса"', 'building_id': 3},
    ])

    # Insert Phone Numbers
    op.bulk_insert(phone_numbers_table, [
        {'organization_id': 1, 'number': '2-222-222'},
        {'organization_id': 1, 'number': '3-333-333'},
        {'organization_id': 2, 'number': '8-800-555-35-35'},
        {'organization_id': 3, 'number': '8-923-111-22-33'},
        {'organization_id': 4, 'number': '+7 (812) 555-10-20'},
    ])
    
    # Link Organizations and Activities
    op.bulk_insert(organization_activity_association_table, [
        {'organization_id': 1, 'activity_id': 4},
        {'organization_id': 2, 'activity_id': 3},
        {'organization_id': 3, 'activity_id': 4},
        {'organization_id': 4, 'activity_id': 7},
        {'organization_id': 4, 'activity_id': 8},
    ])


def downgrade() -> None:
    # The order of deletion is important to avoid foreign key violations.
    op.execute('DELETE FROM organization_activity_association')
    op.execute('DELETE FROM phone_numbers')
    op.execute('DELETE FROM organizations')
    op.execute('DELETE FROM activities')
    op.execute('DELETE FROM buildings')