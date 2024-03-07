class Company:
    def __init__(self, cId, name, contactInfo, desc):
        self.cId = cId
        self.name = name
        self.contactInfo = contactInfo
        self.desc = desc

    def __str__(self):
        return self.name