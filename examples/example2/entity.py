from starspring import Entity, BaseEntity, Column


@Entity(table_name="users")
class User(BaseEntity):
    name = Column(type=str, nullable=False)
    email = Column(type=str, nullable=False, unique=True)
    age = Column(type=int, nullable=True)
    role = Column(type=str, nullable=False, default='user')
    is_active = Column(type=bool, nullable=False, default=True)

