# example of class

class User:
    def __init__(self, id, name, nric, email, phone_number):
        self.id = id
        self.name = name
        self.nric = nric
        self.email = email
        self.phone_number = phone_number

    def as_tuple(self):
        return (self.id, self.name, self.nric, self.email, self.phone_number)

    def as_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'nric': self.nric,
            'email': self.email,
            'phone_number': self.phone_number
        }


