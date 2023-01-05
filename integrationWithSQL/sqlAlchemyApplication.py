import sqlalchemy
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import Session
from sqlalchemy.orm import relationship
from sqlalchemy import Column
from sqlalchemy import func
from sqlalchemy import select
from sqlalchemy import inspect
from sqlalchemy import create_engine
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import ForeignKey


Base = declarative_base()


class User(Base):
    __tablename__ = "user_account"
    # atributos
    id = Column(Integer, primary_key=True)
    name = Column(String)
    fullname = Column(String)

    address = relationship(
        "Address", back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"User(id={self.id}, name={self.name}, fullname={self.fullname})"


class Address(Base):
    __tablename__ = "adress"
    id = Column(Integer, primary_key=True)
    email_address = Column(String(40), nullable=False)
    user_id = Column(Integer, ForeignKey("user_account.id"), nullable=False)

    user = relationship("User", back_populates="address")

    def __repr__(self):
        return f"Address (id={self.id}, email_address={self.email_address})"


print(Address.__tablename__)

# conexão com o banco de dados
engine = create_engine("sqlite://")

# criando as classes como tabelas no banco de dados
Base.metadata.create_all(engine)

inspetor_engine = inspect(engine)
print(inspetor_engine.has_table("user_account"))
print(inspetor_engine.get_table_names())

with Session(engine) as session:
    maria = User(
        name='maria',
        fullname='Maria Moreno',
        address=[Address(email_address='mariamoreno@email.com')]
    )

    eduardo = User(
        name='eduardo',
        fullname='Eduardo Moreno',
        address=[Address(email_address='eduardomoreno@email.com'),
                 Address(email_address='dudumoreno@org.com.br')]
    )

    lionel = User(name='lionel', fullname='Lionel Messi')

    # enviando para o banco de dados (persistência de dados)
    session.add_all([maria, eduardo, lionel])

    session.commit()

stmt = select(User).where(User.name.in_(['maria', 'eduardo']))
print('Recuperando usuarios a partir de condição de filtragem')
for user in session.scalars(stmt):
    print(user)

stmt_address = select(Address).where(Address.user_id.in_([2]))
print('\nRecuperando os endereços de email de eduardo')
for address in session.scalars(stmt_address):
    print(address)

stmt_order = select(User).order_by(User.fullname.desc())
print("\nRecuperando info de maneira ordernada")
for result in session.scalars(stmt_order):
    print(result)

stmt_join = select(User.fullname, Address.email_address).join_from(Address, User)
for result in session.scalars(stmt_join):
    print(result)


connection = engine.connect()
results = connection.execute(stmt_join).fetchall()
print("\nExecutando statement a partir da connection")
for result in results:
    print(result)

stmt_count = select(func.count('*')).select_from(User)
print('\nTotal de instâncias em User')
for result in session.scalars(stmt_count):
    print(result)

session.close()