import json

class CustomerDataManager:
    def __init__(self):
        self.customerFolderPath = "./assets/shop/customers/"

        with open(self.customerFolderPath + "part_meta.json", "r") as f:
            self.customerPartMeta = json.load(f)

    def generateRandomCustomer(self):
        pass

class Customer:
    def __init__(self, customerDataObject):
        pass