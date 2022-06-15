import time, json, pymysql, random
import report_helper_functions as rh

CREDS_PATH = '/etc/spearline'
DATABASE = 'spearlinedb_qa'
Enviroment="qa-staging"


def get_db_creds(path_to_db_json):
    try:
        with open(path_to_db_json, 'r') as db:
            return json.load(db)
    except:
        return [f"* ERROR:  Cannot open {path_to_db_json}, or invalid json. Please check the file."]

def pstn_conf_qual_numbers(is_outbound = False):
    global token
    token=rh.get_token()

    global creds, db, cursor
    creds = get_db_creds(CREDS_PATH)
    db = pymysql.connect(**creds[DATABASE])
    cursor = db.cursor()
    
    number_types = [1, 2, 7]

    if not is_outbound:
        app_id = test_type = 1
    else:
        app_id = 1
        test_type = 23
    pstn_conf_qual_numbers = {}

    for iter in range(1, 6):
        number_type = random.choice(number_types)
        region_id=rh.get_individual_resource(token, "company_region")
        ivr_traversal = rh.get_individual_resource(token, "ivr_traversal")
        phone_group = rh.get_individual_resource(token, "phonegroup")
        server_id,  country_code = rh.get_country_id(cursor)
        route_id = rh.get_route_id(cursor, country_code, number_type)
        pesq_server_id = random.randint(1,2)
        desc_id, desc = rh.get_description_id(cursor)
        country_name = rh.get_country_name(cursor, country_code)
        test_type_name = rh.get_test_type(cursor, test_type)
        number_type_value = rh.get_number_type(cursor, number_type)
        result=rh.add_number(token,
                            application_id=app_id,
                            number=str(int(time.time()))[1:],
                            country_code_id=country_code,
                            number_type_id=number_type,
                            phonegroup_id=phone_group,
                            region_id=region_id,
                            ivr_traversal_id=ivr_traversal,
                            test_type_id=test_type,
                            status_id=1)

        assert result["success"], "The success of the operation was not True. The success was: "+str(result["success"])
        assert result["data"]["application_id"]==1, "The application id is not as expected. Expected: 1 Actual: "+str(result["data"]["application_id"])
        print(result)
        keyname = "number" + str(iter)
        numbers_dictionary = {}
        
        numbers_dictionary[keyname] = {'id': result["data"]["id"], 'number': result["data"]["number"], 'country': country_name, 'desc_name': desc, 'phonegroup_id': phone_group, 'route_id': route_id, 'desc_id': desc_id, 'server_id': server_id, 'pesq_server_id': pesq_server_id, 'type': test_type_name, 'number_type': number_type_value}

        pstn_conf_qual_numbers.update(numbers_dictionary)

    print(pstn_conf_qual_numbers)
    return pstn_conf_qual_numbers

def pstn_qual_numbers(is_outbound=False, is_fax=False):
    global token
    token=rh.get_token()

    global creds, db, cursor
    creds = get_db_creds(CREDS_PATH)
    db = pymysql.connect(**creds[DATABASE])
    cursor = db.cursor()

    number_type = 1
    app_id = 2
    if not is_outbound:
        test_type = 2
    elif is_outbound:
        test_type = 77
    elif is_fax:
        test_type = 7
    pstn_qual_numbers = {}
    
    for iter in range(1, 6):
        server_id,  country_code = rh.get_country_id(cursor)
        route_id = rh.get_route_id(cursor, country_code, number_type)
        desc_id, desc = rh.get_description_id(cursor)
        country_name = rh.get_country_name(cursor, country_code)
        test_type_name = rh.get_test_type(cursor, test_type)
        number_type_value = rh.get_number_type(cursor, number_type)
        ivr_traversal = rh.get_individual_resource(token, "ivr_traversal")
        result=rh.add_number(token,
                            application_id=app_id,
                            number=str(int(time.time()))[1:],
                            country_code_id=country_code,
                            number_type_id=number_type,
                            test_type_id=test_type,
                            ivr_traversal_id=ivr_traversal,
                            status_id=1)
        print(result)
        assert result["success"]==True, "The success of the operation was not True. The success was: "+str(result["success"])
        assert result["data"]["application_id"]==2, "The application id is not as expected. Expected: 2 Actual: "+str(result["data"]["application_id"])

        keyname = "number" + str(iter)
        numbers_dictionary = {}
        
        numbers_dictionary[keyname] = {'id': result["data"]["id"], 'number': result["data"]["number"], 'country': country_name, 'desc_name': desc, 'route_id': route_id, 'desc_id': desc_id, 'server_id': server_id, 'type': test_type_name, 'number_type': number_type_value}

        pstn_qual_numbers.update(numbers_dictionary)

    print("pstn_qual_numbers=", pstn_qual_numbers)
    return pstn_qual_numbers

def sip_quality_uri():
    global token
    token=rh.get_token()

    global creds, db, cursor
    creds = get_db_creds(CREDS_PATH)
    db = pymysql.connect(**creds[DATABASE])
    cursor = db.cursor()

    number_type = 1
    app_id = test_type = 12
    sip_quality_uri = {}

    for iter in range(1, 6):
        ivr_traversal = rh.get_individual_resource(token, "ivr_traversal")
        server_id,  country_code = rh.get_country_id(cursor)
        route_id = rh.get_route_id(cursor, country_code, number_type)
        desc_id, desc = rh.get_description_id(cursor)
        country_name = rh.get_country_name(cursor, country_code)
        test_type_name = rh.get_test_type(cursor, test_type)
        number_type_value = rh.get_number_type(cursor, number_type)
        result=rh.add_number(token,
                            application_id=app_id,
                            number=str(int(time.time()))[1:],
                            country_code_id=country_code,
                            number_type_id=number_type,
                            ivr_traversal_id=ivr_traversal)
        print(result)
        assert result["success"]==True, "The success of the operation was not True. The success was: "+str(result["success"])
        assert result["data"]["application_id"]==12, "The application id is not as expected. Expected: 12 Actual: "+str(result["data"]["application_id"])
        
        keyname = "uri" + str(iter)
        uri_dictionary = {}
        
        uri_dictionary[keyname] = {'id': result["data"]["id"], 'uri': result["data"]["number"], 'country': country_name, 'desc_name': desc, 'route_id': route_id, 'desc_id': desc_id, 'server_id': server_id, 'type': test_type_name, 'number_type': number_type_value}

        sip_quality_uri.update(uri_dictionary)

    print("sip_quality_uri=", sip_quality_uri)
    return sip_quality_uri

def sip_conf_quality_uri():
    global token
    token=rh.get_token()

    global creds, db, cursor
    creds = get_db_creds(CREDS_PATH)
    db = pymysql.connect(**creds[DATABASE])
    cursor = db.cursor()

    number_type = 1
    test_type = 20
    app_id = 11
    sip_conf_quality_uri = {}

    for iter in range(1, 6):
        ivr_traversal = rh.get_individual_resource(token, "ivr_traversal")
        phone_group = rh.get_individual_resource(token, "phonegroup")
        server_id,  country_code = rh.get_country_id(cursor)
        route_id = rh.get_route_id(cursor, country_code, number_type)
        desc_id, desc = rh.get_description_id(cursor)
        country_name = rh.get_country_name(cursor, country_code)
        test_type_name = rh.get_test_type(cursor, test_type)
        number_type_value = rh.get_number_type(cursor, number_type)
        region_id = rh.get_individual_resource(token, "company_region")
        result=rh.add_number(token,
                            application_id=app_id,
                            number=str(int(time.time()))[1:],
                            country_code_id=country_code,
                            number_type_id=number_type,
                            phonegroup_id=phone_group,
                            region_id=region_id,
                            ivr_traversal_id=ivr_traversal)
        print(result)
        assert result["success"]==True, "The success of the operation was not True. The success was: "+str(result["success"])
        assert result["data"]["application_id"]==11, "The application id is not as expected. Expected: 11 Actual: "+str(result["data"]["application_id"])

        keyname = "uri" + str(iter)
        uri_dictionary = {}
        
        uri_dictionary[keyname] = {'id': result["data"]["id"], 'uri': result["data"]["number"], 'country': country_name, 'desc_name': desc, 'route_id': route_id, 'desc_id': desc_id, 'server_id': server_id,'type': test_type_name, 'phonegroup_id': phone_group, 'number_type': number_type_value}

        sip_conf_quality_uri.update(uri_dictionary)

    print("sip_conf_quality_uri=", sip_conf_quality_uri)
    return sip_conf_quality_uri
