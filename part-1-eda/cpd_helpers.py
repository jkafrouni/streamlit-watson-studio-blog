import requests
import pandas as pd

CPD_URL = "https://api.dataplatform.cloud.ibm.com"


# TODO, cache
def authenticate(apikey):
    """Calls the authentication endpoint for Cloud Pak for Data as a Service,
    and returns authentication headers if successful.
    See https://cloud.ibm.com/apidocs/watson-data-api#creating-an-iam-bearer-token.

    Args:
        apikey (str): An IBM Cloud API key, obtained from https://cloud.ibm.com/iam/apikeys).
    Returns:
        success (bool): Whether authentication was successful
        headers (dict): If success=True, a dictionary with valid authentication headers. Otherwise, None.
        error_msg (str): The text response from the authentication request if the request failed.
    """
    auth_headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': 'Basic Yng6Yng=',
    }

    data = {
        'apikey': apikey,
        'grant_type': 'urn:ibm:params:oauth:grant-type:apikey'
    }

    r = requests.post('https://iam.ng.bluemix.net/identity/token', headers=auth_headers, data=data)

    if r.ok:
        headers = {"Authorization": "Bearer " + r.json()['access_token'], "content-type": "application/json"}
        return True, headers, ""
    else:
        return False, None, r.text


def list_projects(headers):
    """Calls the project list endpoint of Cloud Pak for Data as a Service,
    and returns a list of projects if successful.
    See https://cloud.ibm.com/apidocs/watson-data-api#projects-list.

    Args:
        headers (dict): Authentication headers obtained with authenticate().
    Returns:
        projects (list): A list of (project_name, project_id) tuples.
        error_msg (str): The text response from the request if the request failed.
    """
    r = requests.get(f"{CPD_URL}/v2/projects", headers=headers, params={"limit": 100})
    if r.ok:
        projects = r.json()['resources']
        parsed_projects = [(x['entity']['name'], x['metadata']['guid']) for x in projects]
        return parsed_projects, ""
    else:
        return list(), r.text


def list_datasets(headers, project_id):
    """Calls the search endpoint of Cloud Pak for Data as a Service,
    and returns a list of data assets in a given project if successful.
    See https://cloud.ibm.com/apidocs/watson-data-api#simplesearch.

    Args:
        headers (dict): Authentication headers obtained with authenticate().
        project_id (str): The Watson Studio project id to search in.
    Returns:
        datasets (list): A list of (dataset_name, dataset_id) tuples.
        error_msg (str): The text response from the request if the request failed.
    """
    search_doc = {
        "query": {
            "bool": {
                "must": 
                [
                    {"match": {"metadata.artifact_type": "data_asset"}},
                    {"match": {"entity.assets.project_id": project_id}}
                ]
            }
        }
    }
    r = requests.post(f"{CPD_URL}/v3/search",
                      headers=headers,
                      json=search_doc)

    if r.ok:
        datasets = r.json()['rows']
        parsed_datasets = [(x['metadata']['name'], x['artifact_id']) for x in datasets]
        return parsed_datasets, ""
    else:
        return list(), r.text


# TODO cache
def load_dataset(headers, project_id, dataset_id):
    """Loads into a memory a data asset stored in a Watson Studio project
    on IBM Cloud Pak for Data as a Service.
    Abstracts away three steps:
    - Retrieving a details of a data asset including its attachment id
    - Retrieving the attachment
    - Extracting a signed url from the attachment and using it to load the data into Pandas

    Args:
        headers (dict): Authentication headers obtained with authenticate().
        project_id (str): The Watson Studio project id to search in.
        dataset_id (str): The dataset to load
    Returns:
        df (pd.DataFrame): The dataset loaded into a Pandas DataFrame, empty if any of the HTTP requests fails.
        error_msg (str): If any of the HTTP requests fails, the text response from the first failing
            request.
    """
    r = requests.get(f"{CPD_URL}/v2/data_assets/{dataset_id}",
                     params={"project_id": project_id},
                     headers=headers
                    )
    if r.ok:
        dataset_details = r.json()
        attachment_id = dataset_details['attachments'][0]['id']
    else:
        return pd.DataFrame(), r.text

    r2 = requests.get(f"{CPD_URL}/v2/assets/{dataset_id}/attachments/{attachment_id}",
                      params={"project_id": project_id},
                      headers=headers
                      )
    if r2.ok:
        attachment_details = r2.json()
    else:
        return pd.DataFrame(), r2.text

    try:
        return pd.read_csv(attachment_details['url']), ""
    except Exception as e:
        return pd.DataFrame(), str(e)
