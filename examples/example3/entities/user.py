from starspring import BaseEntity, Column, Entity


@Entity(table_name="users")
class User(BaseEntity):
    username = Column(type=str, unique=True, nullable=False)
    password = Column(type=str, nullable=False)
    email = Column(type=str, unique=True, nullable=False)
    role = Column(type=str, default="USER")  # USER or ADMIN
    is_active = Column(type=bool, default=True)
