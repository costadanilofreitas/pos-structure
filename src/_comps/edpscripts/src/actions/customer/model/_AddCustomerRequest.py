class AddCustomerRequest:
    def __init__(self, phone, document, name, zip_code, city, street, neighborhood, number, complement,
                 reference_point):
        # type: (str, str, str, str, str, str, str, str, str, str) -> None
        
        self.phone = phone
        self.document = document
        self.name = name
        self.zip_code = zip_code
        self.city = city
        self.street = street
        self.neighborhood = neighborhood
        self.number = number
        self.complement = complement
        self.reference_point = reference_point
