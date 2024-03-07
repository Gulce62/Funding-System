class Tier:
    def __init__(self, tId, name, minDonation):
        self.tId = tId
        self.name = name
        self.minDonation = minDonation
    
    def __str__(self):
        return self.name

    def __eq__(self, other: "Tier"):
        return self.tId == other.tId