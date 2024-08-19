from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin
from config import db

# Person ---< Dealer ---< Car
            # fk        # fk

# Person ---< Dealer
# foreign key goes into dealer since it needs to point to an individual person

# Dealer ---< Car
# fk in car because the dealer has many cars


class Person(db.Model, SerializerMixin):

    __tablename__ = 'persons_table'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)

    dealers = db.relationship('Dealer', back_populates='person')

    cars = association_proxy('dealers', 'cars')

    serialize_rules = ('-dealers.person',) # <---- prevents infinite looping
    # tells the serializer to leave out the .person when looking at each dealer in .dealers


class Dealer(db.Model, SerializerMixin):

    __tablename__ = 'dealers_table'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)

    person_id = db.Column(db.Integer, db.ForeignKey('persons_table.id'))

    person = db.relationship('Person', back_populates='dealers')
    cars = db.relationship('Car', back_populates='dealer')

    # sqlalchemy.exc.InvalidRequestError: When initializing mapper Mapper[Dealer(dealers_table)], expression 'person' failed to locate a name ('person'). If this is a class name, consider adding this relationship() to the <class 'models.Dealer'> class after both dependent classes have been defined.

    serialize_rules = ('-person.dealers', '-cars.dealer')

class Car(db.Model, SerializerMixin):

    __tablename__ = 'cars_table'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True) # <-- database constraints
    year = db.Column(db.Integer)

    dealer_id = db.Column(db.Integer, db.ForeignKey('dealers_table.id'))

    dealer = db.relationship('Dealer', back_populates='cars')

    serialize_rules = ('-dealer.cars',)

    @validates('year')
    def validate_year(self, key, incoming_year):
        if incoming_year in range(1908, 2025):
            return incoming_year
        else:
            raise ValueError('Year must be a valid year')