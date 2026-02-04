from starspring import Entity, BaseEntity, Column


@Entity(table_name="users")
class User(BaseEntity):
    name = Column(type=str, nullable=False)
    email = Column(type=str, nullable=False, unique=True)
    is_active = Column(type=bool, nullable=False, default=True)
    role = Column(type=str, nullable=False, default="USER")