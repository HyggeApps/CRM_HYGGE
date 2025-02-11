import hubspot # type: ignore
from hubspot import HubSpot # type: ignore
from hubspot.crm.deals import ApiException # type: ignore
from hubspot.crm.owners import ApiException as OwnersApiException # type: ignore
from hubspot.crm.line_items import ApiException as LineItemsApiException # type: ignore
from hubspot.crm.contacts import ApiException as ContactsApiException # type: ignore
from hubspot.crm.companies import ApiException as CompaniesApiException # type: ignore
from hubspot.crm.associations import BatchInputPublicObjectId, PublicObjectId # type: ignore

api_client = HubSpot(access_token="pat-na1-12e28a7d-28d4-4dd7-aac6-393c7af01bec")

deals_api = api_client.crm.deals
owners_api = api_client.crm.owners
line_items_api = api_client.crm.line_items
companies_api = api_client.crm.companies
contacts_api = api_client.crm.contacts
associations_api = api_client.crm.associations

# Obter todos os proprietários e armazenar em um dicionário
owners_dict = {}

try:
    all_owners = owners_api.get_all()

    # Lista para armazenar as informações dos proprietários
    owners_info = []

    owners_details = {}
    
    for owner in all_owners:
        owner_email = owner.email
        owner_id = owner.id
        owners_dict[owner_email] = owner_id
        owners_details[owner_id] = owner