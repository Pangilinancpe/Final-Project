# WHAT "services_view.py" displays, yes yes it's all here. Everyone better freaking use this so I'm not the only one on data.py
# ALSO ALSO, samples lang toh, pero if ever pwede na ediiiiiiii edi wow edi lamaw edi 
SERVICES = [
    {"id": "airport_transfer", "name": "Airport Transfer", "description": "One-way transport between the airport and hotel.", "price": 1200, "unit": "trip", "max_quantity": 2},
    {"id": "laundry", "name": "Laundry", "description": "Wash and fold service. Select the number of loads.", "price": 250, "unit": "load", "max_quantity": 10},
    {"id": "spa_massage", "name": "Spa Massage", "description": "Partake in a rejuvenating spa message to melt away your stress.", "price": 800, "unit": "session", "max_quantity": 10},
    {"id": "extra_bed", "name": "Extra Bed", "description": "One bed for one night. Two beds for two nights = 4 bed-nights.", "price": 600, "unit": "bed-night", "max_quantity": 30},
    {"id": "late_checkout", "name": "Late Checkout", "description": "Extend checkout by two hours, once per booking.", "price": 500, "unit": "package", "max_quantity": 1},
    {"id": "celebration_package", "name": "Celebration Package", "description": "Package: Includes a chilled bottle of champagne, artisinal chocolates, and a floral arrangement within your room upon arrival.", "price": 1500, "unit": "package", "max_quantity": 1},
]

# find service item function to find the service because finding the service is needed for the service to be found you get me?
def find_service_item(service_id):
    for service in SERVICES:
        if service["id"] == service_id:
            return service
    return None
