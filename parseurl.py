from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
import re
def construct_url(title,location,time = 336):
    url = 'https://www.linkedin.com/jobs/search'

    parsed_url = urlparse(url)

    query_params = parse_qs(parsed_url.query)

    query_params['keywords'] = title
    query_params['location'] = location
    #query_params['f_TPR'] = f'r{3600*time}'

    new_query_string = urlencode(query_params, doseq=True)


    new_url = urlunparse((
        parsed_url.scheme,
        parsed_url.netloc,
        parsed_url.path,
        parsed_url.params,
        new_query_string,
        parsed_url.fragment
    ))

    return new_url


def remove_url_parameters(url):
    # Parse the URL into its components
    parsed_url = urlparse(url)

    # Rebuild the URL without the query parameters
    url_without_parameters = urlunparse(parsed_url._replace(query=''))

    return url_without_parameters

def originalSubdomain(url):
    pattern = re.compile(r"https://(.*?)\.linkedin\.com")
    match = pattern.search(url)
    if match:
        extracted_word = match.group(1)
        modified_url = url.replace(f"{extracted_word}.", "")
        url = modified_url + f"&originalSubdomain={extracted_word}"
    return url
