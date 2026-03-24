"""Initial migration

Revision ID: initial
Revises:
Create Date: 2026-03-24 16:00:00

"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "repositories",
        sa.Column("github_id", sa.BigInteger(), nullable=False),
        sa.Column("full_name", sa.String(), nullable=True),
        sa.Column("stargazer_count", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("last_crawled_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("github_id"),
    )
    op.create_index(
        op.f("ix_repositories_full_name"), "repositories", ["full_name"], unique=True
    )
    op.create_index(
        op.f("ix_repositories_github_id"), "repositories", ["github_id"], unique=False
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_repositories_github_id"), table_name="repositories")
    op.drop_index(op.f("ix_repositories_full_name"), table_name="repositories")
    op.drop_table("repositories")
