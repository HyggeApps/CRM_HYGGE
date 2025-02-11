import hubspot  # type: ignore
from hubspot import HubSpot  # type: ignore
from hubspot.crm.companies import ApiException as CompaniesApiException  # type: ignore

# 1) Instantiate the HubSpot client
api_client = HubSpot(access_token="pat-na1-12e28a7d-28d4-4dd7-aac6-393c7af01bec")
companies_api = api_client.crm.companies

try:
    # 2) Retrieve all companies (auto-pagination)
    all_companies = companies_api.get_all()
    
    # 3) Loop through each returned company and print some details
    for idx, company in enumerate(all_companies, start=1):
        print(f"Company #{idx}")
        print(f"  ID: {company.id}")
        
        # Each company’s custom fields (name, domain, etc.) are in 'properties'
        name = company.properties.get("name", "No name found")
        domain = company.properties.get("domain", "No domain found")
        
        print(f"  Name: {name}")
        print(f"  Domain: {domain}")
        print("  -------------------")

except CompaniesApiException as e:
    print("Error retrieving companies:", e)
