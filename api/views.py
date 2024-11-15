import requests
import xml.etree.ElementTree as ET
from django.http import JsonResponse
import logging
import json
from django.views.decorators.csrf import csrf_exempt

# Set up logging
logging.basicConfig(level=logging.INFO)

def get_companies(request):
    try:
        # XML request to get list of companies from Tally
        xml_request = """
        <ENVELOPE>
            <HEADER>
                <VERSION>1</VERSION>
                <TALLYREQUEST>Export</TALLYREQUEST>
                <TYPE>Collection</TYPE>
                <ID>List of Companies</ID>
            </HEADER>
            <BODY>
                <DESC>
                    <STATICVARIABLES>
                        <SVEXPORTFORMAT>XML</SVEXPORTFORMAT>
                    </STATICVARIABLES>
                    <TDL>
                        <![CDATA[
                        [Collection: List of Companies]
                        Type: Company
                        Fetch: NAME
                        ]]>
                    </TDL>
                </DESC>
            </BODY>
        </ENVELOPE>
        """
        
        # Send the request to Tally
        response = requests.post('http://localhost:9000', data=xml_request)
        response.raise_for_status()

        # Parse XML response
        root = ET.fromstring(response.content)
        
        # Extract company names
        companies = []
        for company in root.findall(".//COMPANY"):
            company_name = company.get("NAME")
            if company_name:
                companies.append({"name": company_name})

        logging.info("Companies fetched: %s", companies)
        return JsonResponse(companies, safe=False)

    except requests.exceptions.RequestException as e:
        logging.error("Failed to connect to Tally", exc_info=True)
        return JsonResponse({"error": "Failed to connect to Tally"}, status=500)
    except ET.ParseError as e:
        logging.error("Error parsing XML response", exc_info=True)
        return JsonResponse({"error": "Failed to parse response from Tally"}, status=500)


def get_chart_of_accounts(request, company_name):
        # XML request to get chart of accounts (ledgers) from Tally
        xml_request = f"""
                    <ENVELOPE>
                        <HEADER>
                            <VERSION>1</VERSION>
                            <TALLYREQUEST>Export</TALLYREQUEST>
                            <TYPE>Collection</TYPE>
                            <ID>List of Ledgers</ID>
                        </HEADER>
                        <BODY>
                            <DESC>
                                <STATICVARIABLES>
                                    <SVCURRENTCOMPANY>{company_name}</SVCURRENTCOMPANY>
                                    <SVEXPORTFORMAT>XML</SVEXPORTFORMAT>
                                </STATICVARIABLES>
                                <TDL>
                                    <TDLMESSAGE>
                                        <COLLECTION NAME="List of Ledgers" ISMODIFY="NO">
                                            <TYPE>Ledger</TYPE>
                                            <FETCH>Name, Parent, OpeningBalance, ClosingBalance</FETCH>
                                        </COLLECTION>
                                    </TDLMESSAGE>
                                </TDL>
                            </DESC>
                        </BODY>
                    </ENVELOPE>

        """
        
        # Send the request to Tally
        response = requests.post('http://localhost:9000', data=xml_request)
        # response.raise_for_status()

        print("Raw XML Response:", response.content.decode())
        # Parsing XML response
        xml_data = response.content.decode()
        xml_data = xml_data.replace("&#4;", "")
        root = ET.fromstring(xml_data)
        # root = "abcd"
        print('root')

        # Extract account details
        accounts = []
        print(accounts, 'accounts')
        for ledger in root.findall(".//LEDGER"):
            print(ledger, 'ledger')
            ledger_name = ledger.find("LANGUAGENAME.LIST/NAME.LIST/NAME").text if ledger.find("LANGUAGENAME.LIST/NAME.LIST/NAME") is not None else ""
            parent_group = ledger.find("PARENT").text if ledger.find("PARENT") is not None else ""
            opening_balance = ledger.find("OPENINGBALANCE").text if ledger.find("OPENINGBALANCE") is not None else ""
            closing_balance = ledger.find("CLOSINGBALANCE").text if ledger.find("CLOSINGBALANCE") is not None else ""

            if ledger_name:
                accounts.append({
                    "name": ledger_name,
                    "parent": parent_group,
                    'opening_balance' : opening_balance,
                    "closing_balance": closing_balance,
                })

        return JsonResponse(accounts, safe=False)

def get_list_of_vouchers(request, company_name):
        # XML request to get chart of accounts (ledgers) from Tally
        xml_request = f"""
<ENVELOPE>
    <HEADER>
        <VERSION>1</VERSION>
        <TALLYREQUEST>Export</TALLYREQUEST>
        <TYPE>Collection</TYPE>
        <ID>List of Vouchers</ID>
    </HEADER>
    <BODY>
        <DESC>
            <STATICVARIABLES>
                <SVCURRENTCOMPANY>{company_name}</SVCURRENTCOMPANY>
                <SVEXPORTFORMAT>$$SysName:XML</SVEXPORTFORMAT>
            </STATICVARIABLES>
            <TDL>
                <TDLMESSAGE>
                    <COLLECTION NAME="List of Vouchers" ISMODIFY="NO">
                        <TYPE>Voucher</TYPE>
                        <FETCH>GUID,Date, VoucherTypeName, LedgerEntries</FETCH>
                    </COLLECTION>
                </TDLMESSAGE>
            </TDL>
        </DESC>
    </BODY>
</ENVELOPE>


        """
        
        # Send the request to Tally
        response = requests.post('http://localhost:9000', data=xml_request)
        # response.raise_for_status()

        print("Raw XML Response:", response.content.decode())
        # Parsing XML response
        xml_data = response.content.decode()
        xml_data = xml_data.replace("&#4;", "")
        root = ET.fromstring(xml_data)
        # root = "abcd"
        print('root')

        # Extract account details
        voucheraccounts = []
        print(voucheraccounts, 'voucheraccounts')
        for voucher in root.findall(".//VOUCHER"):
            print(voucher, 'voucher')
            voucher_guid = voucher.find("GUID").text if voucher.find("GUID") is not None else ""
            voucher_date = voucher.find("DATE").text if voucher.find("DATE") is not None else ""
            VoucherType_Name = voucher.find("VOUCHERTYPENAME").text if voucher.find("VOUCHERTYPENAME") is not None else ""
            Ledger_Entries = voucher.find("ALLLEDGERENTRIES.LIST/LEDGERNAME").text if voucher.find("ALLLEDGERENTRIES.LIST/LEDGERNAME") is not None else ""
            voucher_amount = voucher.find("ALLLEDGERENTRIES.LIST/AMOUNT").text if voucher.find("ALLLEDGERENTRIES.LIST/AMOUNT") is not None else ""

            if voucher_guid:
                 voucheraccounts.append({
                      "Date": voucher_date,
                      "VoucherTypeName" : VoucherType_Name,
                      "LedgerEntries" : Ledger_Entries,
                      "voucher_amount": voucher_amount,
                 })

        return JsonResponse(voucheraccounts, safe=False)

# @csrf_exempt
# def create_ledger(request,company_name):
#     # Get ledger data from request
#     if request.method == "POST":
#         data = json.loads(request.body)
#         ledger_name = data.get('ledger_name')
#         parent_group = data.get('parent_group')
#         opening_balance = data.get('opening_balance')
    
#     # Create XML payload
#     xml_payload = f"""
#     <ENVELOPE>
#         <HEADER>
#             <TALLYREQUEST>Import Data</TALLYREQUEST>
#         </HEADER>
#         <BODY>
#             <IMPORTDATA>
#                 <REQUESTDESC>
#                     <REPORTNAME>All Masters</REPORTNAME>
#                     <STATICVARIABLES>
#                         <SVCURRENTCOMPANY>{company_name}</SVCURRENTCOMPANY>
#                     </STATICVARIABLES>
#                 </REQUESTDESC>
#                 <REQUESTDATA>
#                     <TALLYMESSAGE xmlns:UDF="TallyUDF">
#                         <LEDGER NAME="{ledger_name}" ACTION="Create">
#                             <NAME>{ledger_name}</NAME>
#                             <PARENT>{parent_group}</PARENT>
#                             <OPENINGBALANCE>{opening_balance}</OPENINGBALANCE>
#                         </LEDGER>
#                     </TALLYMESSAGE>
#                 </REQUESTDATA>
#             </IMPORTDATA>
#         </BODY>
#     </ENVELOPE>
#     """

#     # Send XML to Tally
#     response = requests.post("http://localhost:9000", data=xml_payload, headers={"Content-Type": "text/xml"})

#     if response.status_code == 200:
#         return JsonResponse({"message": "Ledger created successfully!"})
#     else:
#         return JsonResponse({"message": "Failed to create ledger"}, status=400)

import json
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def create_ledger(request):
    if request.method == "POST":
        try:
            # Get ledger data from the request body
            data = json.loads(request.body)
            print(data, 'data')
            ledger_name = data.get('ledger_name')
            parent_group = data.get('parent_group')
            opening_balance = data.get('opening_balance')

            # Validate input data
            if not ledger_name or not parent_group or not opening_balance:
                return JsonResponse({"error": "Missing required fields: ledger_name, parent_group, opening_balance"}, status=400)
            
            # Create XML payload
            xml_payload = f"""
            <ENVELOPE>
                <HEADER>
                    <TALLYREQUEST>Import Data</TALLYREQUEST>
                </HEADER>
                <BODY>
                    <IMPORTDATA>
                        <REQUESTDESC>
                            <REPORTNAME>All Masters</REPORTNAME>
                            <STATICVARIABLES>
                            </STATICVARIABLES>
                        </REQUESTDESC>
                        <REQUESTDATA>
                            <TALLYMESSAGE xmlns:UDF="TallyUDF">
                                <LEDGER NAME="{ledger_name}" ACTION="Create">
                                    <NAME>{ledger_name}</NAME>
                                    <PARENT>{parent_group}</PARENT>
                                    <OPENINGBALANCE>{opening_balance}</OPENINGBALANCE>
                                </LEDGER>
                            </TALLYMESSAGE>
                        </REQUESTDATA>
                    </IMPORTDATA>
                </BODY>
            </ENVELOPE>
            """

            # Send XML payload to Tally
            response = requests.post("http://localhost:9000", data=xml_payload, headers={"Content-Type": "text/xml"})
            print(response, 'response')

            # Check response from Tally
            if response.status_code == 200:
                return JsonResponse({"message": "Ledger created successfully!"})
            else:
                return JsonResponse({"message": "Failed to create ledger", "details": response.text}, status=400)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    
    return JsonResponse({"error": "Invalid request method."}, status=400)
