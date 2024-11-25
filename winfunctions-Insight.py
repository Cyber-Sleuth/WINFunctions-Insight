import requests
from bs4 import BeautifulSoup
from googlesearch import search
from tabulate import tabulate
import termcolor
def display_banner():
    banner = r"""
 _    _ _____ _   _ ______                _   _                   _____          _       _     _   
| |  | |_   _| \ | ||  ___|              | | (_)                 |_   _|        (_)     | |   | |  
| |  | | | | |  \| || |_ _   _ _ __   ___| |_ _  ___  _ __  ___    | | _ __  ___ _  __ _| |__ | |_ 
| |/\| | | | | . ` ||  _| | | | '_ \ / __| __| |/ _ \| '_ \/ __|   | || '_ \/ __| |/ _` | '_ \| __|
\  /\  /_| |_| |\  || | | |_| | | | | (__| |_| | (_) | | | \__ \  _| || | | \__ \ | (_| | | | | |_ 
 \/  \/ \___/\_| \_/\_|  \__,_|_| |_|\___|\__|_|\___/|_| |_|___/  \___/_| |_|___/_|\__, |_| |_|\__|
                                                                                    __/ |          
                                                                                   |___/           
                                                By Cyber Sleuth
     """
    print(termcolor.colored(banner, 'cyan', attrs=['bold']))


def google_search_function(function_name):
    """
    Perform a Google search for the given function name and prioritize learn.microsoft.com links.
    """
    query = f"{function_name} site:learn.microsoft.com"
    print(f"[INFO] Searching Google for '{function_name}'...")
    search_results = []
    try:
        for result in search(query, num_results=10):
            if "learn.microsoft.com" in result:
                search_results.append(result)
    except Exception as e:
        print(f"[ERROR] Google search failed: {e}")
        return None

    if not search_results:
        print(f"[ERROR] No results found on learn.microsoft.com for '{function_name}'.")
        return None

    print(f"[INFO] Found {len(search_results)} relevant result(s).")
    return search_results[0]

def scrape_function_details(url):
    """
    Scrape details about the function from the Microsoft Learn documentation page.
    """
    print(f"[INFO] Fetching details from {url}...")
    response = requests.get(url)
    if response.status_code != 200:
        print(f"[ERROR] Failed to fetch page. Status code: {response.status_code}")
        return None

    soup = BeautifulSoup(response.content, 'html.parser')
    data = {
        "Description": "",
        "Syntax": "",
        "Parameters": [],
        "Return Value": "",
        "Remarks": "",
        "Requirements": {}
    }

    description_tag = soup.find('p')
    if description_tag and "function" in description_tag.text.lower():
        data["Description"] = description_tag.text.strip()
    else:
        description_header = soup.find('h1')
        if description_header:
            description_tag = description_header.find_next('p')
            if description_tag:
                data["Description"] = description_tag.text.strip()

    syntax_header = soup.find('h2', string=lambda s: s and "Syntax" in s)
    if syntax_header:
        syntax_code = syntax_header.find_next('pre')
        if syntax_code:
            data["Syntax"] = syntax_code.text.strip()

    params_header = soup.find('h2', string=lambda s: s and "Parameters" in s)
    if params_header:
        param_section = params_header.find_next('ul')
        if param_section:
            for item in param_section.find_all('li'):
                param_name = item.find('strong')
                param_desc = item.get_text(strip=True)
                if param_name:
                    data["Parameters"].append((param_name.text.strip(), param_desc))

    return_header = soup.find('h2', string=lambda s: s and "Return Value" in s)
    if return_header:
        return_value = return_header.find_next('p')
        if return_value:
            data["Return Value"] = return_value.text.strip()
    
    if not data["Return Value"]:
        return_value_table = soup.find('table')
        if return_value_table:
            for row in return_value_table.find_all('tr'):
                cols = row.find_all('td')
                if len(cols) == 2 and "Return value" in cols[0].text:
                    data["Return Value"] = cols[1].text.strip()
                    break

    remarks_header = soup.find('h2', string=lambda s: s and "Remarks" in s)
    if remarks_header:
        remarks = remarks_header.find_next('p')
        if remarks:
            data["Remarks"] = remarks.text.strip()

    requirements_header = soup.find('h2', string=lambda s: s and "Requirements" in s)
    if requirements_header:
        req_table = requirements_header.find_next('table')
        if req_table:
            for row in req_table.find_all('tr')[1:]:
                cols = row.find_all('td')
                if len(cols) == 2:
                    data["Requirements"][cols[0].text.strip()] = cols[1].text.strip()

    return data


def display_function_details(function_name, data, url):
    """
    Display the scraped function details in a readable format with enhanced results.
    """
    if not data:
        print("[ERROR] No data available to display.")
        return

    print(f"\n[INFO] Details for '{function_name}':")

    summary_data = [
        ["Function", function_name],
        ["Description", data["Description"][:150] + "..."] if len(data["Description"]) > 150 else ["Description", data["Description"]],
        ["Syntax", data["Syntax"][:80] + "..."] if len(data["Syntax"]) > 80 else ["Syntax", data["Syntax"]],
        ["Return Value", data["Return Value"][:100] + "..."] if len(data["Return Value"]) > 100 else ["Return Value", data["Return Value"]]
    ]
    print(tabulate(summary_data, headers=["Attribute", "Details"], tablefmt="fancy_grid"))

    print(f"\nFull Documentation: {termcolor.colored(url, 'blue', attrs=['underline'])}\n")

    if data['Parameters']:
        print("\nParameters:")
        print(tabulate(data['Parameters'], headers=["Parameter", "Description"], tablefmt="grid"))

    print(f"\nReturn Value:\n{data['Return Value']}")
    print(f"\nRemarks:\n{data['Remarks']}")

    if data['Requirements']:
        print("\nRequirements:")
        for key, value in data['Requirements'].items():
            print(f"- {key}: {value}")


def main():
    try:
        display_banner()  
        function_name = input("Enter the Windows API function name: ").strip()
        url = google_search_function(function_name)

        if not url:
            return

        details = scrape_function_details(url)
        display_function_details(function_name, details, url)

    except KeyboardInterrupt:
        print("\n[INFO] Process interrupted. Exiting gracefully...")
        exit(0)  

if __name__ == "__main__":
    main()
