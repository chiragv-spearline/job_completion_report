import os
import glob
import yaml
import json
import requests
import random
import mysql.connector
import data as data
import report_helper_functions as rh

with open("config.yml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile, Loader=yaml.BaseLoader)

# global token, protocol, server, email, password, api_path, api_url
protocol = cfg["api"]["protocol"]
server = os.getenv('api_server', cfg["api"]["server"])
email = cfg["api"]["user_email"]
password = cfg["api"]["user_pass"]
api_path = cfg["api"]["api_path"]
token_path = cfg["api"]["token_path"]
api_url = protocol+'://'+server+api_path

def add_campaign(token, name=None, test_type_id=None, status=None,
            campaign_time_group_id=None, timezone_id=None, report_interval_id=None,
            campaign_once_off=None, provider=None, prompt=None, numbers=None,
            campaign_report_contact_flag=False, campaign_report_contact=None,
            campaign_report_contact_cc=None, campaign_report_contact_bcc=None):
    """ Add a new campaign, some parameters are mandatory and should always be provided.
    This function can still be called without providing them but the api call will fail without them.
    """
    body_dict={}
    if name is not None:
        body_dict["name"]=name
    if test_type_id is not None:
        body_dict["test_type_id"]=test_type_id
    if campaign_time_group_id is not None:
        body_dict["campaign_time_group_id"]=campaign_time_group_id
    if timezone_id is not None:
        body_dict["timezone_id"]=timezone_id
    if report_interval_id:
        body_dict["report_interval_id"]=report_interval_id
    if status:
        body_dict["status"]=status
    if campaign_once_off:
        body_dict["campaign_once_off"]={"start_time":str(campaign_once_off)}
    if campaign_report_contact_flag:
        body_dict["campaign_report_contact"]={}
    if campaign_report_contact_flag and campaign_report_contact:
        body_dict["campaign_report_contact"]={"email_to":campaign_report_contact}
    if campaign_report_contact_flag and campaign_report_contact_cc:
        body_dict["campaign_report_contact"]["email_cc"]=campaign_report_contact_cc
    if campaign_report_contact_flag and campaign_report_contact_bcc:
        body_dict["campaign_report_contact"]["email_bcc"]=campaign_report_contact_bcc
    if provider:
        body_dict["provider"]=provider
    if prompt:
        body_dict["prompt"]=prompt
    body=json.dumps(body_dict)
    headers = {'Accept': 'application/json',  'Content-Type': 'application/json', 'Authorization': 'Bearer '+token}
    url=api_url+"campaign"
    r = requests.post(url, headers=headers, data=body)
    response=json.loads(r.text)
    number_body=json.dumps(numbers)
    number_url=api_url+"campaign/update_filters/"+str(response["data"]["id"])
    requests.post(number_url, headers=headers, data=number_body)
    print('================campaign_details::::::::::::> ', response)
    return response

def delete_item(token, resource, item_id):
    """Delete a specified item from the system. Must provide the resource and the item id.
    """
    headers = {'Accept': 'application/json', 'Authorization': 'Bearer '+token}
    url=api_url+resource+'/'+str(item_id)
    r = requests.delete(url, headers=headers)
    response=json.loads(r.text)
    return response

def delete_job_processing_data(job_id, job_processing_table):
    """ Delete all job processing data from respected tables
    """
    job_delete_query = "delete from job where id=" + str(job_id)
    job_processing_delete_query = "delete from "+ job_processing_table +" where job_id=" + str(job_id)
    database = mysql.connector.connect(host=cfg["qa_database"]["db_host"],
    user=cfg["qa_database"]["db_user"], password=cfg["qa_database"]["db_pass"], database=cfg["qa_database"]["database"])
    cursorObject = database.cursor()
    cursorObject.execute(job_processing_delete_query)
    cursorObject.execute(job_delete_query)
    database.commit()
    cursorObject.close()
    database.close()

def execute_db_query(query, val):
    """ Execute insert, update query to database
    """
    database = mysql.connector.connect(host=cfg["qa_database"]["db_host"],
    user=cfg["qa_database"]["db_user"], password=cfg["qa_database"]["db_pass"], database=cfg["qa_database"]["database"])
    cursorObject = database.cursor()
    cursorObject.execute(query, val)
    database.commit()
    cursorObject.close()
    database.close()

def execute_select_db_query(query, table_name=None):
    """ Execute select query to database and return
    """
    database = mysql.connector.connect(host=cfg["qa_database"]["db_host"],
    user=cfg["qa_database"]["db_user"], password=cfg["qa_database"]["db_pass"], database=cfg["qa_database"]["database"])
    cursorObject = database.cursor()
    cursorObject.execute(query)
    query_result = cursorObject.fetchall()
    cursorObject.close()
    database.close()
    result_json = {}
    if table_name and len(query_result) > 0:
        if table_name == 'number_table':
            table_header = ['id', 'company_id', 'number', 'country_code_id', 'number_type_id', 'application_id', 'override_route_id', 'gsm_override_route_id', 'is_outbound', 'status']
        elif table_name == 'job_table':
            table_header = ['id', 'company_id', 'campaign_id', 'test_type_id', 'name', 'start_time', 'job_filter_string', 'email_status', 'processing_complete', 'show']
        for i in range(len(table_header)):
            result_json[table_header[i]] = query_result[0][i]
        return result_json
    elif len(query_result) == 1:
        return query_result[0]
    return query_result

def get_token(token_path=token_path):
    """ Get the authorization token needed to use other API functions.
    """
    url = protocol+"://"+server+token_path
    body = {'email':email, 'password':password}
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
    r = requests.post(url, data=json.dumps(body), headers=headers)
    response = json.loads(r.text)
    return response['data']['token']

def get_campaign_numbers_info(number):
    """ Prepare campaign number data in specific format 
    """
    campaign_numbers = []
    campaign_number_details = []
    for key in number:
        number1 = {}
        number1["number_id"] = str(number[key]["id"])
        campaign_numbers.append(number1)
        number2 = {}
        number2["field"] = "number_id"
        number2["operator"] = "="
        number2["value"] = str(number[key]["id"])
        campaign_number_details.append(number2)
    return campaign_numbers, campaign_number_details

def get_random_resource(token, resource):
    """Get a random item id for a specific resource.
    """
    resources=list_resource(token, resource)
    indices=[]
    for el in resources["data"]:
        #Prevent duplicates, just in case
        if el["id"] not in indices:
            indices.append(el["id"])
    return random.choice(indices)

def list_resource(token, resource, item_id=None):
    """Query the api for the selected resource.
    If no item_id is specified it will return all items for that resource.
    """
    headers = {'Accept': 'application/json', 'Authorization': 'Bearer '+token}
    if item_id is not None:
        url=api_url+resource+'/'+str(item_id)
    else:
        url=api_url+resource
    r = requests.get(url, headers=headers)
    response=json.loads(r.text)
    return response

def get_job_processing_table(test_type):
    """ Get Job Processing table according to given test type from database
    """
    job_processing_table_query = "select distinct job_processing_table from test_type where id = %s" % (test_type)
    table_res = rh.execute_select_db_query(job_processing_table_query)
    print('-------job_processing_table--------> ', table_res[0])
    return table_res[0]

def generate_report(campaign, job_id):
    """ This function delete report file if exist any and generate new job completion report
    """
    # Removing existing report file for same campaign
    os.chdir(os.getcwd() + "/csv/")
    file_list = glob.glob(campaign + '*.csv')
    for filename in file_list:
        file_remove_command = 'rm ' + filename
    if len(file_list) > 0:
        os.system('echo %s|sudo -S %s' % (data.sudo_password, file_remove_command))
    # Execute job_report docker container to create job completion report
    os.chdir(os.getcwd() + "/../")
    docker_cmd = 'docker run --rm  -v ' + os.getcwd() + '/csv:/csv:Z --env-file=spearline-env.txt campaign_job_completion python job_report.py qatest ' + str(job_id)
    print(docker_cmd)
    os.system(docker_cmd)
