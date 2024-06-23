import requests

url = 'https://specifications.shawinc.com/api/v1/Specifications/CCS72?uid=E2908A32-403E-42DA-81B7-394FFD478BC9&_=1718973106820'

# List of common proxy ports to try
ports_list = ['8080', '3128', '80']

def make_request_with_proxy(url, proxies):
    try:
        response = requests.get(url, proxies=proxies, timeout=10)  # Added timeout to avoid hanging
        response.raise_for_status()  # Raise an exception for 4xx or 5xx status codes
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
    except requests.exceptions.RequestException as err:
        print(f'Request failed: {err}')
    return None

def retry_request_with_ports(url, ip, ports_list):
    for port in ports_list:
        proxy = f'http://{ip}:{port}'
        proxies = {
            'http': proxy,
            'https': proxy,
        }
        
        print(f'Trying proxy {proxy}...')
        result = make_request_with_proxy(url, proxies)
        if result:
            print(f'Successful response: {result}')
            return result  # Return the result if successful
        
        print(f'Proxy {proxy} failed, trying next...')
    
    return None  # Return None if all proxies fail

# Example usage
ip = '106.216.73.41'
result = retry_request_with_ports(url, ip, ports_list)
if result is None:
    print('All proxies failed. Unable to get a successful response.')
