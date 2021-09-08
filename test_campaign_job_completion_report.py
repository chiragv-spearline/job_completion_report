import os
import csv
import glob
import time
import datetime
import json
import unittest
import report_helper_functions as rh
import data as data
from datetime import timedelta

class test_campaign_job_completion_report_verification(unittest.TestCase):
    """Tests for the campaign job report with different different test-type"""
    @classmethod
    def setUpClass(cls):
        """ Sets up what is needed for all tests
        """
        global main_path
        main_path = os.getcwd()

    def setUp(self):
        """ Set up that happens before each test runs.
        """
        global token
        token = rh.get_token()
        os.chdir(main_path)

    def test_campaign_job_report_conferences_test_type(self):
        """ Campaign job completion report with Conference test-type
        """
        ##----------------- Add Conference test-type campaign -----------------##
        campaign_name = "test_campaign_"+str(int(time.time()))
        campaign_report_contact=[data.email_contact]
        campaign_once_off_time = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M") + ":00"
        campaign_numbers, campaign_number_details = rh.get_campaign_numbers_info(data.pstn_conf_qual_numbers)
        campaign_details = rh.add_campaign(token, name=campaign_name, test_type_id=data.conferences_test_type_id, status=1, numbers=campaign_numbers, report_interval_id=1, timezone_id=data.utc_timezone_id, campaign_once_off=str(campaign_once_off_time), campaign_report_contact_flag=True, campaign_report_contact=campaign_report_contact)
        try:
            ##----------------- Add Campaign Job entry in Job table -----------------##
            campaign_job_insert_val = (data.company_id, campaign_details["data"]["id"], data.conferences_test_type_id, campaign_name, campaign_once_off_time, json.dumps(campaign_number_details))
            campaign_job_insert_query = "insert into job (company_id, campaign_id, test_type_id, name, start_time, job_filter_string) values (%s, %s, %s, %s, %s ,%s)"
            rh.execute_db_query(campaign_job_insert_query, campaign_job_insert_val)
            job_detail_query = "select * from job where campaign_id = %s" % (campaign_details["data"]["id"])
            job_details = rh.execute_select_db_query(job_detail_query, table_name='job_table')
            print('-------job_details--------> ', job_details)
            ##----------------- Get Job Processing table according to Test-type -----------------##
            job_processing_table = rh.get_job_processing_table(data.conferences_test_type_id)
            ##----------------- Enter Job Processing entries -----------------##
            call_start_time = datetime.datetime.strptime(campaign_once_off_time,'%Y-%m-%d %H:%M:%S')
            call_end_time = call_start_time + timedelta(0,3)
            for key in data.pstn_conf_qual_numbers:
                number = data.pstn_conf_qual_numbers[key]
                campaign_job_processing_insert_val = (data.conferences_test_type_id, job_details['id'], number['server_id'], number['server_id'], number['pesq_server_id'], number['id'], data.ivr_spearline_prompt_id, number['id'], data.ivr_spearline_prompt_id, number['phonegroup_id'], number['route_id'], data.cli, call_start_time, call_end_time, 1, 1, number['desc_id'], call_start_time)
                campaign_job_processing_insert_query = "insert into " + job_processing_table + " (test_type_id,job_id,server_id,ddi_server_id,pesq_server_id,number_id,ivr_traversal_id,ddi_number_id,ddi_ivr_traversal_id,phonegroup_id,route_id,cli,call_start_time,call_end_time,processing_complete,test_counter,call_description_id,created_on) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                rh.execute_db_query(campaign_job_processing_insert_query, campaign_job_processing_insert_val)
            # Generate report for conferences test-type
            rh.generate_report(campaign_name, job_details["id"])
            try:
                # Fetch newly created campaign job completion report and verify it
                os.chdir(os.getcwd() + "/csv/")
                result = glob.glob(campaign_name + '*.csv')
                print('Newly fetched CSV report file: ', result[0])
                csv_file_name = result[0]
                csv_file_path = os.getcwd() + "/" + csv_file_name
                with open(csv_file_path, 'r') as file:
                    reader = csv.reader(file)
                    for count, row in enumerate(reader):
                        if count==0:
                            self.assertTrue(row[0] == campaign_name + ' Report', "Mismatch in campaign report title")
                        elif count==1:
                            self.assertTrue(row == data.conferences_testtype_report_headers, "Mismatch in campaign report headers")
                        elif count>1:
                            number_str = str(data.pstn_conf_qual_numbers["number%s" % str(count-1)]['number'])
                            self.assertTrue(len(row) == len(data.conferences_testtype_report_headers), 'Data is not correct')
                            self.assertTrue(row[1] == number_str, 'Incorrect number found: ' + row[1])
                            self.assertTrue(row[2] == campaign_name, 'Incorrect campaign name found: ' + row[2])
                            self.assertTrue(row[3] == data.pstn_conf_qual_numbers["number%s" % str(count-1)]['country'], 'Incorrect country found: ' + row[3])
                            self.assertTrue(row[4] == data.pstn_conf_qual_numbers["number%s" % str(count-1)]['type'], 'Incorrect number-type found: ' + row[4])
                            self.assertTrue(row[5] == number_str + '_customer', 'Incorrect customer found: ' + row[5])
                            self.assertTrue(row[6] == number_str + '_department', 'Incorrect department found: ' + row[6])
                            self.assertTrue(row[7] == number_str + '_location', 'Incorrect location found: ' + row[7])
                            self.assertTrue(row[8] == number_str + '_carrier', 'Incorrect carrier found: ' + row[8])
                            self.assertTrue(row[10] == data.ivr_spearline_prompt, 'Incorrect IVR found: ' + row[10])
                            self.assertTrue(row[11] == str(call_start_time), 'Incorrect Start Time found: ' + row[11])
                            self.assertTrue(row[12] == str(call_end_time), 'Incorrect Call End Time found: ' + row[12])
                            self.assertTrue(row[13] == data.pstn_conf_qual_numbers["number%s" % str(count-1)]['desc_name'], 'Incorrect call description found: ' + row[13])
            finally:
                os.system('echo %s|sudo -S %s' % (data.sudo_password, 'rm ' + csv_file_name))
        finally:
            rh.delete_job_processing_data(job_details['id'], job_processing_table)
            rh.delete_item(token, "campaign", campaign_details["data"]["id"])
    test_campaign_job_report_conferences_test_type.priority=1
    test_campaign_job_report_conferences_test_type.test_area="conferences_test_type"

    def test_campaign_job_report_connection_test_type(self):
        """ Campaign job completion report with Connection test-type
        """
        ##----------------- Add Connection test-type campaign -----------------##
        campaign_name = "test_campaign_"+str(int(time.time()))
        campaign_report_contact=[data.email_contact]
        campaign_once_off_time = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M") + ":00"
        campaign_numbers, campaign_number_details = rh.get_campaign_numbers_info(data.pstn_qual_numbers)
        campaign_details = rh.add_campaign(token, name=campaign_name, test_type_id=data.connection_test_type_id, status=1, numbers=campaign_numbers, report_interval_id=1, timezone_id=data.utc_timezone_id, campaign_once_off=str(campaign_once_off_time), campaign_report_contact_flag=True, campaign_report_contact=campaign_report_contact)
        try:
            campaign_number_update_val = (json.dumps(campaign_number_details), campaign_details["data"]["id"])
            campaign_number_update_query = "update campaign SET filter_string = %s WHERE id = %s"
            rh.execute_db_query(campaign_number_update_query, campaign_number_update_val)
            ##----------------- Add Campaign Job entry in Job table -----------------##
            campaign_job_insert_val = (data.company_id, campaign_details["data"]["id"], data.connection_test_type_id, campaign_name, campaign_once_off_time, json.dumps(campaign_number_details))
            campaign_job_insert_query = "insert into job (company_id, campaign_id, test_type_id, name, start_time, job_filter_string) values (%s, %s, %s, %s, %s ,%s)"
            rh.execute_db_query(campaign_job_insert_query, campaign_job_insert_val)
            job_detail_query = "select * from job where campaign_id = %s" % (campaign_details["data"]["id"])
            job_details = rh.execute_select_db_query(job_detail_query, table_name='job_table')
            print('-------job_details--------> ', job_details)
            ##----------------- Get Job Processing table according to Test-type -----------------##
            job_processing_table = rh.get_job_processing_table(data.connection_test_type_id)
            ##----------------- Enter Job Processing entries -----------------##
            call_start_time = datetime.datetime.strptime(campaign_once_off_time,'%Y-%m-%d %H:%M:%S')
            call_end_time = call_start_time + timedelta(0,3)
            for key in data.pstn_qual_numbers:
                number = data.pstn_qual_numbers[key]
                campaign_job_processing_insert_val = (data.connection_test_type_id, job_details['id'], number['server_id'], number['id'], data.cli, data.ivr_spearline_prompt_id, number['route_id'], call_start_time, call_start_time, call_end_time, 1, number['desc_id'], call_start_time)
                campaign_job_processing_insert_query = "insert into " + job_processing_table + " (test_type_id,job_id,server_id,number_id,cli,ivr_traversal_id,route_id,call_start_time,call_connect_time,call_end_time,processing_complete,call_description_id,created_on) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                rh.execute_db_query(campaign_job_processing_insert_query, campaign_job_processing_insert_val)
            # Generate report for Connection test-type
            rh.generate_report(campaign_name, job_details["id"])
            try:
                # Fetch newly created campaign job completion report and verify it
                os.chdir(os.getcwd() + "/csv/")
                result = glob.glob(campaign_name + '*.csv')
                print('Newly fetched CSV report file: ', result[0])
                csv_file_name = result[0]
                csv_file_path = os.getcwd() + "/" + csv_file_name
                with open(csv_file_path, 'r') as file:
                    reader = csv.reader(file)
                    for count, row in enumerate(reader):
                        if count==0:
                            self.assertTrue(row[0] == campaign_name + ' Report', "Mismatch in campaign report title")
                        elif count==1:
                            self.assertTrue(row == data.connection_testtype_report_headers, "Mismatch in campaign report headers")
                        elif count>1:
                            number_str = str(data.pstn_qual_numbers["number%s" % str(count-1)]['number'])
                            self.assertTrue(len(row) == len(data.connection_testtype_report_headers), 'Data is not correct')
                            self.assertTrue(row[1] == number_str, 'Incorrect number found: ' + row[1])
                            self.assertTrue(row[2] == campaign_name, 'Incorrect campaign name found: ' + row[2])
                            self.assertTrue(row[3] == data.pstn_qual_numbers["number%s" % str(count-1)]['country'], 'Incorrect country found: ' + row[3])
                            self.assertTrue(row[4] == data.pstn_qual_numbers["number%s" % str(count-1)]['type'], 'Incorrect number-type found: ' + row[4])
                            self.assertTrue(row[5] == number_str + '_customer', 'Incorrect customer found: ' + row[5])
                            self.assertTrue(row[6] == number_str + '_department', 'Incorrect department found: ' + row[6])
                            self.assertTrue(row[7] == number_str + '_location', 'Incorrect location found: ' + row[7])
                            self.assertTrue(row[8] == number_str + '_carrier', 'Incorrect carrier found: ' + row[8])
                            self.assertTrue(row[10] == data.ivr_spearline_prompt, 'Incorrect IVR found: ' + row[10])
                            self.assertTrue(row[11] == data.pstn_qual_numbers["number%s" % str(count-1)]['desc_name'], 'Incorrect call description found: ' + row[11])
            finally:
                os.system('echo %s|sudo -S %s' % (data.sudo_password, 'rm ' + csv_file_name))
        finally:
            rh.delete_job_processing_data(job_details['id'], job_processing_table)
            rh.delete_item(token, "campaign", campaign_details["data"]["id"])
    test_campaign_job_report_connection_test_type.priority=1
    test_campaign_job_report_connection_test_type.test_area="connection_test_type"

    def test_campaign_job_report_audio_latency_test_type(self):
        """ Campaign job completion report with Audio Latency test-type
        """
        ##----------------- Add Audio Latency test-type campaign -----------------##
        campaign_name = "test_campaign_"+str(int(time.time()))
        campaign_report_contact=[data.email_contact]
        campaign_once_off_time = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M") + ":00"
        campaign_numbers, campaign_number_details = rh.get_campaign_numbers_info(data.pstn_qual_numbers)
        campaign_details = rh.add_campaign(token, name=campaign_name, test_type_id=data.audio_latency_test_type_id, status=1, numbers=campaign_numbers,  report_interval_id=1, timezone_id=data.utc_timezone_id, campaign_once_off=str(campaign_once_off_time), campaign_report_contact_flag=True, campaign_report_contact=campaign_report_contact)
        try:
            ##----------------- Add Campaign Job entry in Job table -----------------##
            campaign_job_insert_val = (data.company_id, campaign_details["data"]["id"], data.audio_latency_test_type_id, campaign_name, campaign_once_off_time, json.dumps(campaign_number_details))
            campaign_job_insert_query = "insert into job (company_id, campaign_id, test_type_id, name, start_time, job_filter_string) values (%s, %s, %s, %s, %s ,%s)"
            rh.execute_db_query(campaign_job_insert_query, campaign_job_insert_val)
            job_detail_query = "select * from job where campaign_id = %s" % (campaign_details["data"]["id"])
            job_details = rh.execute_select_db_query(job_detail_query, table_name='job_table')
            print('-------job_details--------> ', job_details)
            ##----------------- Get Job Processing table according to Test-type -----------------##
            job_processing_table = rh.get_job_processing_table(data.audio_latency_test_type_id)
            ##----------------- Enter Job Processing entries -----------------##
            call_start_time = datetime.datetime.strptime(campaign_once_off_time,'%Y-%m-%d %H:%M:%S')
            call_end_time = call_start_time + timedelta(0,3)
            for key in data.pstn_qual_numbers:
                number = data.pstn_qual_numbers[key]
                campaign_job_processing_insert_val = (data.audio_latency_test_type_id, job_details['id'], number['server_id'], number['id'], number['route_id'], data.cli, data.ivr_spearline_prompt_id, call_start_time, call_start_time, call_end_time, 1, number['desc_id'], 1, call_start_time)
                campaign_job_processing_insert_query = "insert into " + job_processing_table + " (test_type_id,job_id,server_id,number_id,route_id,cli,ivr_traversal_id,call_start_time,call_connect_time,call_end_time,processing_complete,call_description_id,tone_description,created_on) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                rh.execute_db_query(campaign_job_processing_insert_query, campaign_job_processing_insert_val)
            # Generate report for Audio Latency test-type
            rh.generate_report(campaign_name, job_details["id"])
            try:
                # Fetch newly created campaign job completion report and verify it
                os.chdir(os.getcwd() + "/csv/")
                result = glob.glob(campaign_name + '*.csv')
                print('Newly fetched CSV report file: ', result[0])
                csv_file_name = result[0]
                csv_file_path = os.getcwd() + "/" + csv_file_name
                with open(csv_file_path, 'r') as file:
                    reader = csv.reader(file)
                    for count, row in enumerate(reader):
                        if count==0:
                            self.assertTrue(row[0] == campaign_name + ' Report', "Mismatch in campaign report title")
                        elif count==1:
                            self.assertTrue(row == data.audio_latency_testtype_report_headers, "Mismatch in campaign report headers")
                        elif count>1:
                            number_str = str(data.pstn_qual_numbers["number%s" % str(count-1)]['number'])
                            self.assertTrue(len(row) == len(data.audio_latency_testtype_report_headers), 'Data is not correct')
                            self.assertTrue(row[1] == number_str, 'Incorrect number found: ' + row[1])
                            self.assertTrue(row[2] == campaign_name, 'Incorrect campaign name found: ' + row[2])
                            self.assertTrue(row[3] == data.pstn_qual_numbers["number%s" % str(count-1)]['country'], 'Incorrect country found: ' + row[3])
                            self.assertTrue(row[4] == data.pstn_qual_numbers["number%s" % str(count-1)]['type'], 'Incorrect number-type found: ' + row[4])
                            self.assertTrue(row[5] == number_str + '_customer', 'Incorrect customer found: ' + row[5])
                            self.assertTrue(row[6] == number_str + '_department', 'Incorrect department found: ' + row[6])
                            self.assertTrue(row[7] == number_str + '_location', 'Incorrect location found: ' + row[7])
                            self.assertTrue(row[8] == number_str + '_carrier', 'Incorrect carrier found: ' + row[8])
                            self.assertTrue(row[10] == data.ivr_spearline_prompt, 'Incorrect IVR found: ' + row[10])
                            self.assertTrue(row[11] == data.pstn_qual_numbers["number%s" % str(count-1)]['desc_name'], 'Incorrect call description found: ' + row[11])
            finally:
                os.system('echo %s|sudo -S %s' % (data.sudo_password, 'rm ' + csv_file_name))
        finally:
            rh.delete_job_processing_data(job_details['id'], job_processing_table)
            rh.delete_item(token, "campaign", campaign_details["data"]["id"])
    test_campaign_job_report_audio_latency_test_type.priority=1
    test_campaign_job_report_audio_latency_test_type.test_area="audio_latency_test_type"

    def test_campaign_job_report_conference_single_line_test_type(self):
        """ Campaign job completion report with Conference single line testing test-type
        """
        ##----------------- Add Conference single line testing test-type campaign -----------------##
        campaign_name = "test_campaign_"+str(int(time.time()))
        campaign_report_contact=[data.email_contact]
        campaign_once_off_time = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M") + ":00"
        campaign_numbers, campaign_number_details = rh.get_campaign_numbers_info(data.pstn_conf_qual_numbers)
        campaign_details = rh.add_campaign(token, name=campaign_name, test_type_id=data.single_line_test_type_id, status=1, numbers=campaign_numbers,  report_interval_id=1, timezone_id=data.utc_timezone_id, campaign_once_off=str(campaign_once_off_time), campaign_report_contact_flag=True, campaign_report_contact=campaign_report_contact)
        try:
            ##----------------- Add Campaign Job entry in Job table -----------------##
            campaign_job_insert_val = (data.company_id, campaign_details["data"]["id"], data.single_line_test_type_id, campaign_name, campaign_once_off_time, json.dumps(campaign_number_details))
            campaign_job_insert_query = "insert into job (company_id, campaign_id, test_type_id, name, start_time, job_filter_string) values (%s, %s, %s, %s, %s ,%s)"
            rh.execute_db_query(campaign_job_insert_query, campaign_job_insert_val)
            job_detail_query = "select * from job where campaign_id = %s" % (campaign_details["data"]["id"])
            job_details = rh.execute_select_db_query(job_detail_query, table_name='job_table')
            print('-------job_details--------> ', job_details)
            ##----------------- Get Job Processing table according to Test-type -----------------##
            job_processing_table = rh.get_job_processing_table(data.single_line_test_type_id)
            ##----------------- Enter Job Processing entries -----------------##
            call_start_time = datetime.datetime.strptime(campaign_once_off_time,'%Y-%m-%d %H:%M:%S')
            call_end_time = call_start_time + timedelta(0,3)
            for key in data.pstn_conf_qual_numbers:
                number = data.pstn_conf_qual_numbers[key]
                campaign_job_processing_insert_val = (data.single_line_test_type_id, job_details['id'], number['server_id'], number['id'], number['route_id'], data.cli, data.ivr_spearline_prompt_id, number['phonegroup_id'], call_start_time, call_start_time, call_end_time, 1, number['desc_id'], call_start_time)
                campaign_job_processing_insert_query = "insert into " + job_processing_table + " (test_type_id,job_id,server_id,number_id,route_id,cli,ivr_traversal_id,phonegroup_id,call_start_time,call_connect_time,call_end_time,processing_complete,call_description_id,created_on) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                rh.execute_db_query(campaign_job_processing_insert_query, campaign_job_processing_insert_val)
            # Generate report for Conference single line testing test-type
            rh.generate_report(campaign_name, job_details["id"])
            try:
                # Fetch newly created campaign job completion report and verify it
                os.chdir(os.getcwd() + "/csv/")
                result = glob.glob(campaign_name + '*.csv')
                print('Newly fetched CSV report file: ', result[0])
                csv_file_name = result[0]
                csv_file_path = os.getcwd() + "/" + csv_file_name
                with open(csv_file_path, 'r') as file:
                    reader = csv.reader(file)
                    for count, row in enumerate(reader):
                        if count==0:
                            self.assertTrue(row[0] == campaign_name + ' Report', "Mismatch in campaign report title")
                        elif count==1:
                            self.assertTrue(row == data.single_line_testtype_report_headers, "Mismatch in campaign report headers")
                        elif count>1:
                            number_str = str(data.pstn_conf_qual_numbers["number%s" % str(count-1)]['number'])
                            self.assertTrue(len(row) == len(data.single_line_testtype_report_headers), 'Data is not correct')
                            self.assertTrue(row[1] == number_str, 'Incorrect number found: ' + row[1])
                            self.assertTrue(row[2] == campaign_name, 'Incorrect campaign name found: ' + row[2])
                            self.assertTrue(row[3] == data.pstn_conf_qual_numbers["number%s" % str(count-1)]['country'], 'Incorrect country found: ' + row[3])
                            self.assertTrue(row[4] == data.pstn_conf_qual_numbers["number%s" % str(count-1)]['type'], 'Incorrect number-type found: ' + row[4])
                            self.assertTrue(row[5] == number_str + '_customer', 'Incorrect customer found: ' + row[5])
                            self.assertTrue(row[6] == number_str + '_department', 'Incorrect department found: ' + row[6])
                            self.assertTrue(row[7] == number_str + '_location', 'Incorrect location found: ' + row[7])
                            self.assertTrue(row[8] == number_str + '_carrier', 'Incorrect carrier found: ' + row[8])
                            self.assertTrue(row[10] == data.ivr_spearline_prompt, 'Incorrect IVR found: ' + row[10])
                            self.assertTrue(row[11] == str(call_start_time), 'Incorrect Start Time found: ' + row[11])
                            self.assertTrue(row[12] == str(call_end_time), 'Incorrect Call End Time found: ' + row[12])
                            self.assertTrue(row[13] == data.pstn_conf_qual_numbers["number%s" % str(count-1)]['desc_name'], 'Incorrect call description found: ' + row[13])
            finally:
                os.system('echo %s|sudo -S %s' % (data.sudo_password, 'rm ' + csv_file_name))
        finally:
            rh.delete_job_processing_data(job_details['id'], job_processing_table)
            rh.delete_item(token, "campaign", campaign_details["data"]["id"])
    test_campaign_job_report_conference_single_line_test_type.priority=1
    test_campaign_job_report_conference_single_line_test_type.test_area="conference_single_line_test_type"

    def test_campaign_job_report_in_country_test_type(self):
        """ Campaign job completion report with In-Country testing test-type
        """
        ##----------------- Add In-Country testing test-type campaign -----------------##
        campaign_name = "test_campaign_"+str(int(time.time()))
        campaign_report_contact=[data.email_contact]
        campaign_once_off_time = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M") + ":00"
        campaign_numbers, campaign_number_details = rh.get_campaign_numbers_info(data.pstn_qual_numbers)
        campaign_details = rh.add_campaign(token, name=campaign_name, test_type_id=data.in_country_test_type_id, status=1, numbers=campaign_numbers,  report_interval_id=1, timezone_id=data.utc_timezone_id, campaign_once_off=str(campaign_once_off_time), campaign_report_contact_flag=True, campaign_report_contact=campaign_report_contact)
        try:
            ##----------------- Add Campaign Job entry in Job table -----------------##
            campaign_job_insert_val = (data.company_id, campaign_details["data"]["id"], data.in_country_test_type_id, campaign_name, campaign_once_off_time, json.dumps(campaign_number_details))
            campaign_job_insert_query = "insert into job (company_id, campaign_id, test_type_id, name, start_time, job_filter_string) values (%s, %s, %s, %s, %s ,%s)"
            rh.execute_db_query(campaign_job_insert_query, campaign_job_insert_val)
            job_detail_query = "select * from job where campaign_id = %s" % (campaign_details["data"]["id"])
            job_details = rh.execute_select_db_query(job_detail_query, table_name='job_table')
            print('-------job_details--------> ', job_details)
            ##----------------- Get Job Processing table according to Test-type -----------------##
            job_processing_table = rh.get_job_processing_table(data.in_country_test_type_id)
            ##----------------- Enter Job Processing entries -----------------##
            call_start_time = datetime.datetime.strptime(campaign_once_off_time,'%Y-%m-%d %H:%M:%S')
            call_end_time = call_start_time + timedelta(0,3)
            for key in data.pstn_qual_numbers:
                number = data.pstn_qual_numbers[key]
                campaign_job_processing_insert_val = (data.in_country_test_type_id, job_details['id'], number['server_id'], number['id'], number['route_id'], data.cli, data.ivr_spearline_prompt_id, call_start_time, call_start_time, call_end_time, 1, number['desc_id'], call_start_time)
                campaign_job_processing_insert_query = "insert into " + job_processing_table + " (test_type_id,job_id,server_id,number_id,route_id,cli,ivr_traversal_id,call_start_time,call_connect_time,call_end_time,processing_complete,call_description_id,created_on) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                rh.execute_db_query(campaign_job_processing_insert_query, campaign_job_processing_insert_val)
            # Generate report for In-Country test-type
            rh.generate_report(campaign_name, job_details["id"])
            try:
                # Fetch newly created campaign job completion report and verify it
                os.chdir(os.getcwd() + "/csv/")
                result = glob.glob(campaign_name + '*.csv')
                print('Newly fetched CSV report file: ', result[0])
                csv_file_name = result[0]
                csv_file_path = os.getcwd() + "/" + csv_file_name
                with open(csv_file_path, 'r') as file:
                    reader = csv.reader(file)
                    for count, row in enumerate(reader):
                        if count==0:
                            self.assertTrue(row[0] == campaign_name + ' Report', "Mismatch in campaign report title")
                        elif count==1:
                            self.assertTrue(row == data.in_country_testtype_report_headers, "Mismatch in campaign report headers")
                        elif count>1:
                            number_str = str(data.pstn_qual_numbers["number%s" % str(count-1)]['number'])
                            self.assertTrue(len(row) == len(data.in_country_testtype_report_headers), 'Data is not correct')
                            self.assertTrue(row[1] == number_str, 'Incorrect number found: ' + row[1])
                            self.assertTrue(row[2] == campaign_name, 'Incorrect campaign name found: ' + row[2])
                            self.assertTrue(row[3] == data.pstn_qual_numbers["number%s" % str(count-1)]['country'], 'Incorrect country found: ' + row[3])
                            self.assertTrue(row[4] == data.pstn_qual_numbers["number%s" % str(count-1)]['type'], 'Incorrect number-type found: ' + row[4])
                            self.assertTrue(row[5] == number_str + '_customer', 'Incorrect customer found: ' + row[5])
                            self.assertTrue(row[6] == number_str + '_department', 'Incorrect department found: ' + row[6])
                            self.assertTrue(row[7] == number_str + '_location', 'Incorrect location found: ' + row[7])
                            self.assertTrue(row[8] == number_str + '_carrier', 'Incorrect carrier found: ' + row[8])
                            self.assertTrue(row[10] == data.ivr_spearline_prompt, 'Incorrect IVR found: ' + row[10])
                            self.assertTrue(row[11] == str(call_start_time), 'Incorrect Start Time found: ' + row[11])
                            self.assertTrue(row[12] == str(call_end_time), 'Incorrect Call End Time found: ' + row[12])
                            self.assertTrue(row[13] == data.pstn_qual_numbers["number%s" % str(count-1)]['desc_name'], 'Incorrect call description found: ' + row[13])
            finally:
                os.system('echo %s|sudo -S %s' % (data.sudo_password, 'rm ' + csv_file_name))
        finally:
            rh.delete_job_processing_data(job_details['id'], job_processing_table)
            rh.delete_item(token, "campaign", campaign_details["data"]["id"])
    test_campaign_job_report_in_country_test_type.priority=1
    test_campaign_job_report_in_country_test_type.test_area="in_country_test_type"

    def test_campaign_job_report_agent_connection_test_type(self):
        """ Campaign job completion report with Agent Connection test-type
        """
        ##----------------- Add Agent Connection test-type campaign -----------------##
        campaign_name = "test_campaign_"+str(int(time.time()))
        campaign_report_contact=[data.email_contact]
        campaign_once_off_time = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M") + ":00"
        campaign_numbers, campaign_number_details = rh.get_campaign_numbers_info(data.pstn_qual_numbers)
        campaign_details = rh.add_campaign(token, name=campaign_name, test_type_id=data.agent_connection_test_type_id, status=1, numbers=campaign_numbers,  report_interval_id=1, timezone_id=data.utc_timezone_id, campaign_once_off=str(campaign_once_off_time), campaign_report_contact_flag=True, campaign_report_contact=campaign_report_contact)
        try:
            ##----------------- Add Campaign Job entry in Job table -----------------##
            campaign_job_insert_val = (data.company_id, campaign_details["data"]["id"], data.agent_connection_test_type_id, campaign_name, campaign_once_off_time, json.dumps(campaign_number_details))
            campaign_job_insert_query = "insert into job (company_id, campaign_id, test_type_id, name, start_time, job_filter_string) values (%s, %s, %s, %s, %s ,%s)"
            rh.execute_db_query(campaign_job_insert_query, campaign_job_insert_val)
            job_detail_query = "select * from job where campaign_id = %s" % (campaign_details["data"]["id"])
            job_details = rh.execute_select_db_query(job_detail_query, table_name='job_table')
            print('-------job_details--------> ', job_details)
            ##----------------- Get Job Processing table according to Test-type -----------------##
            job_processing_table = rh.get_job_processing_table(data.agent_connection_test_type_id)
            ##----------------- Enter Job Processing entries -----------------##
            call_start_time = datetime.datetime.strptime(campaign_once_off_time,'%Y-%m-%d %H:%M:%S')
            call_end_time = call_start_time + timedelta(0,3)
            agent_confirmation_time = call_start_time + timedelta(0,56)
            for key in data.pstn_qual_numbers:
                number = data.pstn_qual_numbers[key]
                campaign_job_processing_insert_val = (data.agent_connection_test_type_id, job_details['id'], number['server_id'], number['id'], number['route_id'], data.cli, data.ivr_spearline_prompt_id, call_start_time, call_start_time, call_end_time, agent_confirmation_time, data.dtmf, 1, number['desc_id'], call_start_time)
                campaign_job_processing_insert_query = "insert into " + job_processing_table + " (test_type_id,job_id,server_id,number_id,route_id,cli,ivr_traversal_id,call_start_time,call_connect_time,call_end_time,agent_confirmation_time,received_dtmf,processing_complete,call_description_id,created_on) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                rh.execute_db_query(campaign_job_processing_insert_query, campaign_job_processing_insert_val)
            # Generate report for Agent Connection test-type
            rh.generate_report(campaign_name, job_details["id"])
            try:
                # Fetch newly created campaign job completion report and verify it
                os.chdir(os.getcwd() + "/csv/")
                result = glob.glob(campaign_name + '*.csv')
                print('Newly fetched CSV report file: ', result[0])
                csv_file_name = result[0]
                csv_file_path = os.getcwd() + "/" + csv_file_name
                with open(csv_file_path, 'r') as file:
                    reader = csv.reader(file)
                    for count, row in enumerate(reader):
                        if count==0:
                            self.assertTrue(row[0] == campaign_name + ' Report', "Mismatch in campaign report title")
                        elif count==1:
                            self.assertTrue(row == data.agent_connection_testtype_report_headers, "Mismatch in campaign report headers")
                        elif count>1:
                            number_str = str(data.pstn_qual_numbers["number%s" % str(count-1)]['number'])
                            self.assertTrue(len(row) == len(data.agent_connection_testtype_report_headers), 'Data is not correct')
                            self.assertTrue(row[1] == number_str, 'Incorrect number found: ' + row[1])
                            self.assertTrue(row[2] == campaign_name, 'Incorrect campaign name found: ' + row[2])
                            self.assertTrue(row[3] == data.pstn_qual_numbers["number%s" % str(count-1)]['country'], 'Incorrect country found: ' + row[3])
                            self.assertTrue(row[4] == data.pstn_qual_numbers["number%s" % str(count-1)]['type'], 'Incorrect number-type found: ' + row[4])
                            self.assertTrue(row[5] == number_str + '_customer', 'Incorrect customer found: ' + row[5])
                            self.assertTrue(row[6] == number_str + '_department', 'Incorrect department found: ' + row[6])
                            self.assertTrue(row[7] == number_str + '_location', 'Incorrect location found: ' + row[7])
                            self.assertTrue(row[8] == number_str + '_carrier', 'Incorrect carrier found: ' + row[8])
                            self.assertTrue(row[10] == data.ivr_spearline_prompt, 'Incorrect IVR found: ' + row[10])
                            self.assertTrue(row[11] == data.dtmf, 'Incorrect Received DTMF found: ' + row[11])
                            self.assertTrue(row[12] == str(agent_confirmation_time), 'Incorrect Agent Confirmation Time found: ' + row[12])
                            self.assertTrue(row[13] == data.pstn_qual_numbers["number%s" % str(count-1)]['desc_name'], 'Incorrect call description found: ' + row[13])
            finally:
                os.system('echo %s|sudo -S %s' % (data.sudo_password, 'rm ' + csv_file_name))
        finally:
            rh.delete_job_processing_data(job_details['id'], job_processing_table)
            rh.delete_item(token, "campaign", campaign_details["data"]["id"])
    test_campaign_job_report_agent_connection_test_type.priority=1
    test_campaign_job_report_agent_connection_test_type.test_area="agent_connection_test_type"
    
    def test_campaign_job_report_sip_trunk_test_type(self):
        """ Campaign job completion report with Sip Trunk test-type
        """
        ##----------------- Add Sip Trunk test-type campaign -----------------##
        campaign_name = "test_campaign_"+str(int(time.time()))
        campaign_report_contact=[data.email_contact]
        campaign_once_off_time = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M") + ":00"
        campaign_numbers, campaign_number_details = rh.get_campaign_numbers_info(data.sip_quality_uri)
        campaign_details = rh.add_campaign(token, name=campaign_name, test_type_id=data.sip_trunk_test_type_id, status=1, numbers=campaign_numbers,  report_interval_id=1, timezone_id=data.utc_timezone_id, campaign_once_off=str(campaign_once_off_time), campaign_report_contact_flag=True, campaign_report_contact=campaign_report_contact)
        try:
            ##----------------- Add Campaign Job entry in Job table -----------------##
            campaign_job_insert_val = (data.company_id, campaign_details["data"]["id"], data.sip_trunk_test_type_id, campaign_name, campaign_once_off_time, json.dumps(campaign_number_details))
            campaign_job_insert_query = "insert into job (company_id, campaign_id, test_type_id, name, start_time, job_filter_string) values (%s, %s, %s, %s, %s ,%s)"
            rh.execute_db_query(campaign_job_insert_query, campaign_job_insert_val)
            job_detail_query = "select * from job where campaign_id = %s" % (campaign_details["data"]["id"])
            job_details = rh.execute_select_db_query(job_detail_query, table_name='job_table')
            print('-------job_details--------> ', job_details)
            ##----------------- Get Job Processing table according to Test-type -----------------##
            job_processing_table = rh.get_job_processing_table(data.sip_trunk_test_type_id)
            ##----------------- Enter Job Processing entries -----------------##
            call_start_time = datetime.datetime.strptime(campaign_once_off_time,'%Y-%m-%d %H:%M:%S')
            call_end_time = call_start_time + timedelta(0,3)
            for key in data.sip_quality_uri:
                uri = data.sip_quality_uri[key]
                campaign_job_processing_insert_val = (data.sip_trunk_test_type_id, job_details['id'], uri['server_id'], uri['id'], 1, 1, data.cli, data.dtmf, data.ivr_spearline_prompt_id, call_start_time, call_start_time, call_end_time, 1, uri['desc_id'], call_start_time)
                campaign_job_processing_insert_query = "insert into " + job_processing_table + " (test_type_id,job_id,server_id,number_id,sip_trunk_id,trunk_prefix_id,cli,received_dtmf,ivr_traversal_id,call_start_time,call_connect_time,call_end_time,processing_complete,call_description_id,created_on) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                rh.execute_db_query(campaign_job_processing_insert_query, campaign_job_processing_insert_val)
            # Generate report for Sip Trunk test-type
            rh.generate_report(campaign_name, job_details["id"])
            try:
                # Fetch newly created campaign job completion report and verify it
                os.chdir(os.getcwd() + "/csv/")
                result = glob.glob(campaign_name + '*.csv')
                print('Newly fetched CSV report file: ', result[0])
                csv_file_name = result[0]
                csv_file_path = os.getcwd() + "/" + csv_file_name
                with open(csv_file_path, 'r') as file:
                    reader = csv.reader(file)
                    for count, row in enumerate(reader):
                        if count==0:
                            self.assertTrue(row[0] == campaign_name + ' Report', "Mismatch in campaign report title")
                        elif count==1:
                            self.assertTrue(row == data.sip_trunk_testtype_report_headers, "Mismatch in campaign report headers")
                        elif count>1:
                            uri_str = str(data.sip_quality_uri["uri%s" % str(count-1)]['uri'])
                            self.assertTrue(len(row) == len(data.sip_trunk_testtype_report_headers), 'Data is not correct')
                            self.assertTrue(row[1] == uri_str, 'Incorrect URI found: ' + row[1])
                            self.assertTrue(row[2] == campaign_name, 'Incorrect campaign name found: ' + row[2])
                            self.assertTrue(row[3] == data.sip_quality_uri["uri%s" % str(count-1)]['country'], 'Incorrect country found: ' + row[3])
                            self.assertTrue(row[4] == data.sip_quality_uri["uri%s" % str(count-1)]['type'], 'Incorrect uri-type found: ' + row[4])
                            self.assertTrue(row[5] == uri_str + '_customer', 'Incorrect customer found: ' + row[5])
                            self.assertTrue(row[6] == uri_str + '_department', 'Incorrect department found: ' + row[6])
                            self.assertTrue(row[7] == uri_str + '_location', 'Incorrect location found: ' + row[7])
                            self.assertTrue(row[8] == uri_str + '_carrier', 'Incorrect carrier found: ' + row[8])
                            self.assertTrue(row[10] == data.ivr_spearline_prompt, 'Incorrect IVR found: ' + row[10])
                            self.assertTrue(row[11] == str(call_start_time), 'Incorrect Start Time found: ' + row[11])
                            self.assertTrue(row[12] == str(call_end_time), 'Incorrect Call End Time found: ' + row[12])
                            self.assertTrue(row[13] == data.sip_quality_uri["uri%s" % str(count-1)]['desc_name'], 'Incorrect call description found: ' + row[13])
            finally:
                os.system('echo %s|sudo -S %s' % (data.sudo_password, 'rm ' + csv_file_name))
        finally:
            rh.delete_job_processing_data(job_details['id'], job_processing_table)
            rh.delete_item(token, "campaign", campaign_details["data"]["id"])
    test_campaign_job_report_sip_trunk_test_type.priority=1
    test_campaign_job_report_sip_trunk_test_type.test_area="sip_trunk_test_type"

    def test_campaign_job_report_conference_longcall_test_type(self):
        """ Campaign job completion report with Conference Long Call test-type
        """
        ##----------------- Add Conference Long Call test-type campaign -----------------##
        campaign_name = "test_campaign_"+str(int(time.time()))
        campaign_report_contact=[data.email_contact]
        campaign_once_off_time = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M") + ":00"
        campaign_numbers, campaign_number_details = rh.get_campaign_numbers_info(data.pstn_conf_qual_numbers)
        campaign_details = rh.add_campaign(token, name=campaign_name, test_type_id=data.conference_longcall_test_type_id, status=1, numbers=campaign_numbers, report_interval_id=1, timezone_id=data.utc_timezone_id, campaign_once_off=str(campaign_once_off_time), campaign_report_contact_flag=True, campaign_report_contact=campaign_report_contact)
        try:
            ##----------------- Add Campaign Job entry in Job table -----------------##
            campaign_job_insert_val = (data.company_id, campaign_details["data"]["id"], data.conference_longcall_test_type_id, campaign_name, campaign_once_off_time, json.dumps(campaign_number_details))
            campaign_job_insert_query = "insert into job (company_id, campaign_id, test_type_id, name, start_time, job_filter_string) values (%s, %s, %s, %s, %s ,%s)"
            rh.execute_db_query(campaign_job_insert_query, campaign_job_insert_val)
            job_detail_query = "select * from job where campaign_id = %s" % (campaign_details["data"]["id"])
            job_details = rh.execute_select_db_query(job_detail_query, table_name='job_table')
            print('-------job_details--------> ', job_details)
            ##----------------- Get Job Processing table according to Test-type -----------------##
            job_processing_table = rh.get_job_processing_table(data.conference_longcall_test_type_id)
            ##----------------- Enter Job Processing entries -----------------##
            call_start_time = datetime.datetime.strptime(campaign_once_off_time,'%Y-%m-%d %H:%M:%S')
            call_end_time = call_start_time + timedelta(0,3)
            for key in data.pstn_conf_qual_numbers:
                number = data.pstn_conf_qual_numbers[key]
                campaign_job_processing_insert_val = (data.conference_longcall_test_type_id, job_details['id'], 4200, 2, number['server_id'], number['server_id'], number['id'], data.ivr_spearline_prompt_id, number['id'], data.ivr_spearline_prompt_id, number['phonegroup_id'], number['route_id'], data.cli, call_start_time, call_start_time, call_end_time, 1, 1, number['desc_id'], call_start_time)
                campaign_job_processing_insert_query = "insert into " + job_processing_table + " (test_type_id,job_id,call_length,silence,server_id,ddi_server_id,number_id,ivr_traversal_id,ddi_number_id,ddi_ivr_traversal_id,phonegroup_id,route_id,cli,call_start_time,call_connect_time,call_end_time,processing_complete,test_counter,call_description_id,created_on) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                rh.execute_db_query(campaign_job_processing_insert_query, campaign_job_processing_insert_val)
            # Generate report for conference long call test-type
            rh.generate_report(campaign_name, job_details["id"])
            try:
                # Fetch newly created campaign job completion report and verify it
                os.chdir(os.getcwd() + "/csv/")
                result = glob.glob(campaign_name + '*.csv')
                print('Newly fetched CSV report file: ', result[0])
                csv_file_name = result[0]
                csv_file_path = os.getcwd() + "/" + csv_file_name
                with open(csv_file_path, 'r') as file:
                    reader = csv.reader(file)
                    for count, row in enumerate(reader):
                        if count==0:
                            self.assertTrue(row[0] == campaign_name + ' Report', "Mismatch in campaign report title")
                        elif count==1:
                            self.assertTrue(row == data.conference_longcall_testtype_report_headers, "Mismatch in campaign report headers")
                        elif count>1:
                            number_str = str(data.pstn_conf_qual_numbers["number%s" % str(count-1)]['number'])
                            self.assertTrue(len(row) == len(data.conference_longcall_testtype_report_headers), 'Data is not correct')
                            self.assertTrue(row[1] == number_str, 'Incorrect number found: ' + row[1])
                            self.assertTrue(row[2] == campaign_name, 'Incorrect campaign name found: ' + row[2])
                            self.assertTrue(row[3] == data.pstn_conf_qual_numbers["number%s" % str(count-1)]['country'], 'Incorrect country found: ' + row[3])
                            self.assertTrue(row[4] == data.pstn_conf_qual_numbers["number%s" % str(count-1)]['type'], 'Incorrect number-type found: ' + row[4])
                            self.assertTrue(row[5] == number_str + '_customer', 'Incorrect customer found: ' + row[5])
                            self.assertTrue(row[6] == number_str + '_department', 'Incorrect department found: ' + row[6])
                            self.assertTrue(row[7] == number_str + '_location', 'Incorrect location found: ' + row[7])
                            self.assertTrue(row[8] == number_str + '_carrier', 'Incorrect carrier found: ' + row[8])
                            self.assertTrue(row[10] == data.ivr_spearline_prompt, 'Incorrect IVR found: ' + row[10])
                            self.assertTrue(row[11] == str(call_start_time), 'Incorrect Start Time found: ' + row[11])
                            self.assertTrue(row[12] == str(call_end_time), 'Incorrect Call End Time found: ' + row[12])
                            self.assertTrue(row[13] == data.pstn_conf_qual_numbers["number%s" % str(count-1)]['desc_name'], 'Incorrect state found: ' + row[13])
                            self.assertTrue(row[16] == 'group_' + number_str, 'Incorrect phonegroup found: ' + row[16])
                            self.assertTrue(row[17] == number_str + '_region', 'Incorrect region found: ' + row[17])
                            self.assertTrue(row[20] == number_str + '_bridge', 'Incorrect bridge found: ' + row[20])
            finally:
                os.system('echo %s|sudo -S %s' % (data.sudo_password, 'rm ' + csv_file_name))
        finally:
            rh.delete_job_processing_data(job_details['id'], job_processing_table)
            rh.delete_item(token, "campaign", campaign_details["data"]["id"])
    test_campaign_job_report_conference_longcall_test_type.priority=1
    test_campaign_job_report_conference_longcall_test_type.test_area="conference_longcall_test_type"

    def test_campaign_job_report_conference_with_tones_test_type(self):
        """ Campaign job completion report with Conference With Tones test-type
        """
        ##----------------- Add Conference With Tones test-type campaign -----------------##
        campaign_name = "test_campaign_"+str(int(time.time()))
        campaign_report_contact=[data.email_contact]
        campaign_once_off_time = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M") + ":00"
        campaign_numbers, campaign_number_details = rh.get_campaign_numbers_info(data.pstn_conf_qual_numbers)
        campaign_details = rh.add_campaign(token, name=campaign_name, test_type_id=data.conference_with_tones_test_type_id, status=1, numbers=campaign_numbers, report_interval_id=1, timezone_id=data.utc_timezone_id, campaign_once_off=str(campaign_once_off_time), campaign_report_contact_flag=True, campaign_report_contact=campaign_report_contact)
        try:
            ##----------------- Add Campaign Job entry in Job table -----------------##
            campaign_job_insert_val = (data.company_id, campaign_details["data"]["id"], data.conference_with_tones_test_type_id, campaign_name, campaign_once_off_time, json.dumps(campaign_number_details))
            campaign_job_insert_query = "insert into job (company_id, campaign_id, test_type_id, name, start_time, job_filter_string) values (%s, %s, %s, %s, %s ,%s)"
            rh.execute_db_query(campaign_job_insert_query, campaign_job_insert_val)
            job_detail_query = "select * from job where campaign_id = %s" % (campaign_details["data"]["id"])
            job_details = rh.execute_select_db_query(job_detail_query, table_name='job_table')
            print('-------job_details--------> ', job_details)
            ##----------------- Get Job Processing table according to Test-type -----------------##
            job_processing_table = rh.get_job_processing_table(data.conference_with_tones_test_type_id)
            ##----------------- Enter Job Processing entries -----------------##
            call_start_time = datetime.datetime.strptime(campaign_once_off_time,'%Y-%m-%d %H:%M:%S')
            call_end_time = call_start_time + timedelta(0,3)
            for key in data.pstn_conf_qual_numbers:
                number = data.pstn_conf_qual_numbers[key]
                campaign_job_processing_insert_val = (data.conference_with_tones_test_type_id, job_details['id'], number['server_id'], number['server_id'], number['id'], data.ivr_spearline_prompt_id, number['id'], data.ivr_spearline_prompt_id, number['phonegroup_id'], number['route_id'], data.cli, call_start_time, call_start_time, call_end_time, 1, 1, number['desc_id'], call_start_time)
                campaign_job_processing_insert_query = "insert into " + job_processing_table + " (test_type_id,job_id,server_id,ddi_server_id,number_id,ivr_traversal_id,ddi_number_id,ddi_ivr_traversal_id,phonegroup_id,route_id,cli,call_start_time,call_connect_time,call_end_time,processing_complete,test_counter,call_description_id,created_on) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                rh.execute_db_query(campaign_job_processing_insert_query, campaign_job_processing_insert_val)
            # Generate report for conference with tones test-type
            rh.generate_report(campaign_name, job_details["id"])
            try:
                # Fetch newly created campaign job completion report and verify it
                os.chdir(os.getcwd() + "/csv/")
                result = glob.glob(campaign_name + '*.csv')
                print('Newly fetched CSV report file: ', result[0])
                csv_file_name = result[0]
                csv_file_path = os.getcwd() + "/" + csv_file_name
                with open(csv_file_path, 'r') as file:
                    reader = csv.reader(file)
                    for count, row in enumerate(reader):
                        if count==0:
                            self.assertTrue(row[0] == campaign_name + ' Report', "Mismatch in campaign report title")
                        elif count==1:
                            self.assertTrue(row == data.conference_with_tones_testtype_report_headers, "Mismatch in campaign report headers")
                        elif count>1:
                            number_str = str(data.pstn_conf_qual_numbers["number%s" % str(count-1)]['number'])
                            self.assertTrue(len(row) == len(data.conference_with_tones_testtype_report_headers), 'Data is not correct')
                            self.assertTrue(row[1] == number_str, 'Incorrect number found: ' + row[1])
                            self.assertTrue(row[2] == campaign_name, 'Incorrect campaign name found: ' + row[2])
                            self.assertTrue(row[3] == data.pstn_conf_qual_numbers["number%s" % str(count-1)]['country'], 'Incorrect country found: ' + row[3])
                            self.assertTrue(row[4] == data.pstn_conf_qual_numbers["number%s" % str(count-1)]['type'], 'Incorrect number-type found: ' + row[4])
                            self.assertTrue(row[5] == number_str + '_customer', 'Incorrect customer found: ' + row[5])
                            self.assertTrue(row[6] == number_str + '_department', 'Incorrect department found: ' + row[6])
                            self.assertTrue(row[7] == number_str + '_location', 'Incorrect location found: ' + row[7])
                            self.assertTrue(row[8] == number_str + '_carrier', 'Incorrect carrier found: ' + row[8])
                            self.assertTrue(row[10] == data.ivr_spearline_prompt, 'Incorrect IVR found: ' + row[10])
                            self.assertTrue(row[11] == str(call_start_time), 'Incorrect Start Time found: ' + row[11])
                            self.assertTrue(row[12] == str(call_end_time), 'Incorrect Call End Time found: ' + row[12])
                            self.assertTrue(row[13] == data.pstn_conf_qual_numbers["number%s" % str(count-1)]['desc_name'], 'Incorrect state found: ' + row[13])
            finally:
                os.system('echo %s|sudo -S %s' % (data.sudo_password, 'rm ' + csv_file_name))
        finally:
            rh.delete_job_processing_data(job_details['id'], job_processing_table)
            rh.delete_item(token, "campaign", campaign_details["data"]["id"])
    test_campaign_job_report_conference_with_tones_test_type.priority=1
    test_campaign_job_report_conference_with_tones_test_type.test_area="conference_with_tones_test_type"

    def test_campaign_job_report_international_conference_test_type(self):
        """ Campaign job completion report with International Conference test-type
        """
        ##----------------- Add International Conference test-type campaign -----------------##
        campaign_name = "test_campaign_"+str(int(time.time()))
        campaign_report_contact=[data.email_contact]
        campaign_once_off_time = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M") + ":00"
        campaign_numbers, campaign_number_details = rh.get_campaign_numbers_info(data.pstn_conf_qual_numbers)
        campaign_details = rh.add_campaign(token, name=campaign_name, test_type_id=data.international_conference_test_type_id, status=1, numbers=campaign_numbers, report_interval_id=1, timezone_id=data.utc_timezone_id, campaign_once_off=str(campaign_once_off_time), campaign_report_contact_flag=True, campaign_report_contact=campaign_report_contact)
        try:
            ##----------------- Add Campaign Job entry in Job table -----------------##
            campaign_job_insert_val = (data.company_id, campaign_details["data"]["id"], data.international_conference_test_type_id, campaign_name, campaign_once_off_time, json.dumps(campaign_number_details))
            campaign_job_insert_query = "insert into job (company_id, campaign_id, test_type_id, name, start_time, job_filter_string) values (%s, %s, %s, %s, %s ,%s)"
            rh.execute_db_query(campaign_job_insert_query, campaign_job_insert_val)
            job_detail_query = "select * from job where campaign_id = %s" % (campaign_details["data"]["id"])
            job_details = rh.execute_select_db_query(job_detail_query, table_name='job_table')
            print('-------job_details--------> ', job_details)
            ##----------------- Get Job Processing table according to Test-type -----------------##
            job_processing_table = rh.get_job_processing_table(data.international_conference_test_type_id)
            ##----------------- Enter Job Processing entries -----------------##
            call_start_time = datetime.datetime.strptime(campaign_once_off_time,'%Y-%m-%d %H:%M:%S')
            call_end_time = call_start_time + timedelta(0,3)
            for key in data.pstn_conf_qual_numbers:
                number = data.pstn_conf_qual_numbers[key]
                campaign_job_processing_insert_val = (data.international_conference_test_type_id, job_details['id'], number['server_id'], number['server_id'], number['id'], data.ivr_spearline_prompt_id, number['id'], data.ivr_spearline_prompt_id, number['phonegroup_id'], number['route_id'], data.cli, call_start_time, call_start_time, call_end_time, 1, 1, number['desc_id'], call_start_time)
                campaign_job_processing_insert_query = "insert into " + job_processing_table + " (test_type_id,job_id,server_id,ddi_server_id,number_id,ivr_traversal_id,ddi_number_id,ddi_ivr_traversal_id,phonegroup_id,route_id,cli,call_start_time,call_connect_time,call_end_time,processing_complete,test_counter,call_description_id,created_on) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                rh.execute_db_query(campaign_job_processing_insert_query, campaign_job_processing_insert_val)
            # Generate report for international conference test-type
            rh.generate_report(campaign_name, job_details["id"])
            try:
                # Fetch newly created campaign job completion report and verify it
                os.chdir(os.getcwd() + "/csv/")
                result = glob.glob(campaign_name + '*.csv')
                print('Newly fetched CSV report file: ', result[0])
                csv_file_name = result[0]
                csv_file_path = os.getcwd() + "/" + csv_file_name
                with open(csv_file_path, 'r') as file:
                    reader = csv.reader(file)
                    for count, row in enumerate(reader):
                        if count==0:
                            self.assertTrue(row[0] == campaign_name + ' Report', "Mismatch in campaign report title")
                        elif count==1:
                            self.assertTrue(row == data.international_conference_testtype_report_headers, "Mismatch in campaign report headers")
                        elif count>1:
                            number_str = str(data.pstn_conf_qual_numbers["number%s" % str(count-1)]['number'])
                            self.assertTrue(len(row) == len(data.international_conference_testtype_report_headers), 'Data is not correct')
                            self.assertTrue(row[1] == number_str, 'Incorrect number found: ' + row[1])
                            self.assertTrue(row[2] == campaign_name, 'Incorrect campaign name found: ' + row[2])
                            self.assertTrue(row[3] == data.pstn_conf_qual_numbers["number%s" % str(count-1)]['country'], 'Incorrect country found: ' + row[3])
                            self.assertTrue(row[4] == data.pstn_conf_qual_numbers["number%s" % str(count-1)]['type'], 'Incorrect number-type found: ' + row[4])
                            self.assertTrue(row[5] == number_str + '_customer', 'Incorrect customer found: ' + row[5])
                            self.assertTrue(row[6] == number_str + '_department', 'Incorrect department found: ' + row[6])
                            self.assertTrue(row[7] == number_str + '_location', 'Incorrect location found: ' + row[7])
                            self.assertTrue(row[8] == number_str + '_carrier', 'Incorrect carrier found: ' + row[8])
                            self.assertTrue(row[10] == data.ivr_spearline_prompt, 'Incorrect IVR found: ' + row[10])
                            self.assertTrue(row[11] == str(call_start_time), 'Incorrect Start Time found: ' + row[11])
                            self.assertTrue(row[12] == str(call_end_time), 'Incorrect Call End Time found: ' + row[12])
                            self.assertTrue(row[13] == data.pstn_conf_qual_numbers["number%s" % str(count-1)]['desc_name'], 'Incorrect state found: ' + row[13])
            finally:
                os.system('echo %s|sudo -S %s' % (data.sudo_password, 'rm ' + csv_file_name))
        finally:
            rh.delete_job_processing_data(job_details['id'], job_processing_table)
            rh.delete_item(token, "campaign", campaign_details["data"]["id"])
    test_campaign_job_report_international_conference_test_type.priority=1
    test_campaign_job_report_international_conference_test_type.test_area="international_conference_test_type"

    def test_campaign_job_report_outbound_conference_test_type(self):
        """ Campaign job completion report with Outbound Conference test-type
        """
        ##----------------- Add Outbound Conference test-type campaign -----------------##
        campaign_name = "test_campaign_"+str(int(time.time()))
        campaign_report_contact=[data.email_contact]
        campaign_once_off_time = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M") + ":00"
        campaign_numbers, campaign_number_details = rh.get_campaign_numbers_info(data.pstn_conf_qual_numbers)
        campaign_details = rh.add_campaign(token, name=campaign_name, test_type_id=data.outbound_conference_test_type_id, status=1, numbers=campaign_numbers, report_interval_id=1, timezone_id=data.utc_timezone_id, campaign_once_off=str(campaign_once_off_time), campaign_report_contact_flag=True, campaign_report_contact=campaign_report_contact)
        try:
            ##----------------- Add Campaign Job entry in Job table -----------------##
            campaign_job_insert_val = (data.company_id, campaign_details["data"]["id"], data.outbound_conference_test_type_id, campaign_name, campaign_once_off_time, json.dumps(campaign_number_details))
            campaign_job_insert_query = "insert into job (company_id, campaign_id, test_type_id, name, start_time, job_filter_string) values (%s, %s, %s, %s, %s ,%s)"
            rh.execute_db_query(campaign_job_insert_query, campaign_job_insert_val)
            job_detail_query = "select * from job where campaign_id = %s" % (campaign_details["data"]["id"])
            job_details = rh.execute_select_db_query(job_detail_query, table_name='job_table')
            print('-------job_details--------> ', job_details)
            ##----------------- Get Job Processing table according to Test-type -----------------##
            job_processing_table = rh.get_job_processing_table(data.outbound_conference_test_type_id)
            ##----------------- Enter Job Processing entries -----------------##
            call_start_time = datetime.datetime.strptime(campaign_once_off_time,'%Y-%m-%d %H:%M:%S')
            call_end_time = call_start_time + timedelta(0,3)
            for key in data.pstn_conf_qual_numbers:
                number = data.pstn_conf_qual_numbers[key]
                campaign_job_processing_insert_val = (data.outbound_conference_test_type_id, job_details['id'], number['server_id'], number['id'], data.ivr_spearline_prompt_id, 1, number['route_id'], data.cli, call_start_time, call_start_time, call_end_time, 1, 1, number['desc_id'], call_start_time)
                campaign_job_processing_insert_query = "insert into " + job_processing_table + " (test_type_id,job_id,server_id,number_id,ivr_traversal_id,outbound_bridge_ddi_id,route_id,cli,call_start_time,call_connect_time,call_end_time,processing_complete,test_counter,call_description_id,created_on) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                rh.execute_db_query(campaign_job_processing_insert_query, campaign_job_processing_insert_val)
            # Generate report for outbound conference test-type
            rh.generate_report(campaign_name, job_details["id"])
            try:
                # Fetch newly created campaign job completion report and verify it
                os.chdir(os.getcwd() + "/csv/")
                result = glob.glob(campaign_name + '*.csv')
                print('Newly fetched CSV report file: ', result[0])
                csv_file_name = result[0]
                csv_file_path = os.getcwd() + "/" + csv_file_name
                with open(csv_file_path, 'r') as file:
                    reader = csv.reader(file)
                    for count, row in enumerate(reader):
                        if count==0:
                            self.assertTrue(row[0] == campaign_name + ' Report', "Mismatch in campaign report title")
                        elif count==1:
                            self.assertTrue(row == data.outbound_conference_testtype_report_headers, "Mismatch in campaign report headers")
                        elif count>1:
                            number_str = str(data.pstn_conf_qual_numbers["number%s" % str(count-1)]['number'])
                            self.assertTrue(len(row) == len(data.outbound_conference_testtype_report_headers), 'Data is not correct')
            finally:
                os.system('echo %s|sudo -S %s' % (data.sudo_password, 'rm ' + csv_file_name))
        finally:
            rh.delete_job_processing_data(job_details['id'], job_processing_table)
            rh.delete_item(token, "campaign", campaign_details["data"]["id"])
    test_campaign_job_report_outbound_conference_test_type.priority=1
    test_campaign_job_report_outbound_conference_test_type.test_area="outbound_conference_test_type"

    def test_campaign_job_report_linktest_test_type(self):
        """ Campaign job completion report with Link Test test-type
        """
        ##----------------- Add Link Test test-type campaign -----------------##
        campaign_name = "test_campaign_"+str(int(time.time()))
        campaign_report_contact=[data.email_contact]
        campaign_once_off_time = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M") + ":00"
        campaign_numbers, campaign_number_details = rh.get_campaign_numbers_info(data.pstn_conf_qual_numbers)
        campaign_details = rh.add_campaign(token, name=campaign_name, test_type_id=data.linktest_test_type_id, status=1, numbers=campaign_numbers, report_interval_id=1, timezone_id=data.utc_timezone_id, campaign_once_off=str(campaign_once_off_time), campaign_report_contact_flag=True, campaign_report_contact=campaign_report_contact)
        try:
            ##----------------- Add Campaign Job entry in Job table -----------------##
            campaign_job_insert_val = (data.company_id, campaign_details["data"]["id"], data.linktest_test_type_id, campaign_name, campaign_once_off_time, json.dumps(campaign_number_details))
            campaign_job_insert_query = "insert into job (company_id, campaign_id, test_type_id, name, start_time, job_filter_string) values (%s, %s, %s, %s, %s ,%s)"
            rh.execute_db_query(campaign_job_insert_query, campaign_job_insert_val)
            job_detail_query = "select * from job where campaign_id = %s" % (campaign_details["data"]["id"])
            job_details = rh.execute_select_db_query(job_detail_query, table_name='job_table')
            print('-------job_details--------> ', job_details)
            ##----------------- Get Job Processing table according to Test-type -----------------##
            job_processing_table = rh.get_job_processing_table(data.linktest_test_type_id)
            ##----------------- Enter Job Processing entries -----------------##
            call_start_time = datetime.datetime.strptime(campaign_once_off_time,'%Y-%m-%d %H:%M:%S')
            call_end_time = call_start_time + timedelta(0,3)
            for key in data.pstn_conf_qual_numbers:
                number = data.pstn_conf_qual_numbers[key]
                campaign_job_processing_insert_val = (data.linktest_test_type_id, job_details['id'], number['server_id'], number['server_id'], number['id'], data.ivr_spearline_prompt_id, number['id'], data.ivr_spearline_prompt_id, number['phonegroup_id'], number['route_id'], data.cli, call_start_time, call_start_time, call_end_time, 1, 1, number['desc_id'], call_start_time)
                campaign_job_processing_insert_query = "insert into " + job_processing_table + " (test_type_id,job_id,server_id,ddi_server_id,number_id,ivr_traversal_id,ddi_number_id,ddi_ivr_traversal_id,phonegroup_id,route_id,cli,call_start_time,call_connect_time,call_end_time,processing_complete,test_counter,call_description_id,created_on) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                rh.execute_db_query(campaign_job_processing_insert_query, campaign_job_processing_insert_val)
            # Generate report for Link Test test-type
            rh.generate_report(campaign_name, job_details["id"])
            try:
                # Fetch newly created campaign job completion report and verify it
                os.chdir(os.getcwd() + "/csv/")
                result = glob.glob(campaign_name + '*.csv')
                print('Newly fetched CSV report file: ', result[0])
                csv_file_name = result[0]
                csv_file_path = os.getcwd() + "/" + csv_file_name
                with open(csv_file_path, 'r') as file:
                    reader = csv.reader(file)
                    for count, row in enumerate(reader):
                        if count==0:
                            self.assertTrue(row[0] == campaign_name + ' Report', "Mismatch in campaign report title")
                        elif count==1:
                            self.assertTrue(row == data.linktest_testtype_report_headers, "Mismatch in campaign report headers")
                        elif count>1:
                            number_str = str(data.pstn_conf_qual_numbers["number%s" % str(count-1)]['number'])
                            self.assertTrue(len(row) == len(data.linktest_testtype_report_headers), 'Data is not correct')
                            self.assertTrue(row[1] == number_str, 'Incorrect number found: ' + row[1])
                            self.assertTrue(row[2] == campaign_name, 'Incorrect campaign name found: ' + row[2])
                            self.assertTrue(row[3] == data.pstn_conf_qual_numbers["number%s" % str(count-1)]['country'], 'Incorrect country found: ' + row[3])
                            self.assertTrue(row[4] == data.pstn_conf_qual_numbers["number%s" % str(count-1)]['type'], 'Incorrect number-type found: ' + row[4])
                            self.assertTrue(row[5] == number_str + '_customer', 'Incorrect customer found: ' + row[5])
                            self.assertTrue(row[6] == number_str + '_department', 'Incorrect department found: ' + row[6])
                            self.assertTrue(row[7] == number_str + '_location', 'Incorrect location found: ' + row[7])
                            self.assertTrue(row[8] == number_str + '_carrier', 'Incorrect carrier found: ' + row[8])
                            self.assertTrue(row[10] == data.ivr_spearline_prompt, 'Incorrect IVR found: ' + row[10])
                            self.assertTrue(row[11] == str(call_start_time), 'Incorrect Start Time found: ' + row[11])
                            self.assertTrue(row[12] == str(call_end_time), 'Incorrect Call End Time found: ' + row[12])
                            self.assertTrue(row[13] == data.pstn_conf_qual_numbers["number%s" % str(count-1)]['desc_name'], 'Incorrect state found: ' + row[13])
            finally:
                os.system('echo %s|sudo -S %s' % (data.sudo_password, 'rm ' + csv_file_name))
        finally:
            rh.delete_job_processing_data(job_details['id'], job_processing_table)
            rh.delete_item(token, "campaign", campaign_details["data"]["id"])
    test_campaign_job_report_linktest_test_type.priority=1
    test_campaign_job_report_linktest_test_type.test_area="linktest_test_type"

    def test_campaign_job_report_conference_with_provider_test_type(self):
        """ Campaign job completion report with Conference with Provider test-type
        """
        ##----------------- Add Conference with Provider test-type campaign -----------------##
        campaign_name = "test_campaign_"+str(int(time.time()))
        campaign_report_contact=[data.email_contact]
        campaign_once_off_time = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M") + ":00"
        campaign_numbers, campaign_number_details = rh.get_campaign_numbers_info(data.pstn_conf_qual_numbers)
        provider=rh.get_random_resource(token, "provider")
        campaign_details = rh.add_campaign(token, name=campaign_name, test_type_id=data.conference_with_provider_test_type_id, status=1, numbers=campaign_numbers, provider=[provider], report_interval_id=1, timezone_id=data.utc_timezone_id, campaign_once_off=str(campaign_once_off_time), campaign_report_contact_flag=True, campaign_report_contact=campaign_report_contact)
        try:
            ##----------------- Add Campaign Job entry in Job table -----------------##
            campaign_job_insert_val = (data.company_id, campaign_details["data"]["id"], data.conference_with_provider_test_type_id, campaign_name, campaign_once_off_time, json.dumps(campaign_number_details))
            campaign_job_insert_query = "insert into job (company_id, campaign_id, test_type_id, name, start_time, job_filter_string) values (%s, %s, %s, %s, %s ,%s)"
            rh.execute_db_query(campaign_job_insert_query, campaign_job_insert_val)
            job_detail_query = "select * from job where campaign_id = %s" % (campaign_details["data"]["id"])
            job_details = rh.execute_select_db_query(job_detail_query, table_name='job_table')
            print('-------job_details--------> ', job_details)
            ##----------------- Get Job Processing table according to Test-type -----------------##
            job_processing_table = rh.get_job_processing_table(data.conference_with_provider_test_type_id)
            ##----------------- Enter Job Processing entries -----------------##
            call_start_time = datetime.datetime.strptime(campaign_once_off_time,'%Y-%m-%d %H:%M:%S')
            call_end_time = call_start_time + timedelta(0,3)
            for key in data.pstn_conf_qual_numbers:
                number = data.pstn_conf_qual_numbers[key]
                campaign_job_processing_insert_val = (data.conference_with_provider_test_type_id, job_details['id'], number['server_id'], number['server_id'], number['pesq_server_id'], number['id'], data.ivr_spearline_prompt_id, number['id'], data.ivr_spearline_prompt_id, number['phonegroup_id'], number['route_id'], data.cli, call_start_time, call_end_time, 1, 1, number['desc_id'], call_start_time)
                campaign_job_processing_insert_query = "insert into " + job_processing_table + " (test_type_id,job_id,server_id,ddi_server_id,pesq_server_id,number_id,ivr_traversal_id,ddi_number_id,ddi_ivr_traversal_id,phonegroup_id,route_id,cli,call_start_time,call_end_time,processing_complete,test_counter,call_description_id,created_on) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                rh.execute_db_query(campaign_job_processing_insert_query, campaign_job_processing_insert_val) 
            # Generate report for Conference with Provider test-type
            rh.generate_report(campaign_name, job_details["id"])
            try:
                # Fetch newly created campaign job completion report and verify it
                os.chdir(os.getcwd() + "/csv/")
                result = glob.glob(campaign_name + '*.csv')
                print('Newly fetched CSV report file: ', result[0])
                csv_file_name = result[0]
                csv_file_path = os.getcwd() + "/" + csv_file_name
                with open(csv_file_path, 'r') as file:
                    reader = csv.reader(file)
                    for count, row in enumerate(reader):
                        if count==0:
                            self.assertTrue(row[0] == campaign_name + ' Report', "Mismatch in campaign report title")
                        elif count==1:
                            self.assertTrue(row == data.conference_with_provider_report_headers, "Mismatch in campaign report headers")
                        elif count>1:
                            number_str = str(data.pstn_conf_qual_numbers["number%s" % str(count-1)]['number'])
                            self.assertTrue(len(row) == len(data.conference_with_provider_report_headers), 'Data is not correct')
                            self.assertTrue(row[1] == number_str, 'Incorrect number found: ' + row[1])
                            self.assertTrue(row[2] == campaign_name, 'Incorrect campaign name found: ' + row[2])
                            self.assertTrue(row[3] == data.pstn_conf_qual_numbers["number%s" % str(count-1)]['country'], 'Incorrect country found: ' + row[3])
                            self.assertTrue(row[4] == data.pstn_conf_qual_numbers["number%s" % str(count-1)]['type'], 'Incorrect number-type found: ' + row[4])
                            self.assertTrue(row[5] == number_str + '_customer', 'Incorrect customer found: ' + row[5])
                            self.assertTrue(row[6] == number_str + '_department', 'Incorrect department found: ' + row[6])
                            self.assertTrue(row[7] == number_str + '_location', 'Incorrect location found: ' + row[7])
                            self.assertTrue(row[8] == number_str + '_carrier', 'Incorrect carrier found: ' + row[8])
                            self.assertTrue(row[10] == data.ivr_spearline_prompt, 'Incorrect IVR found: ' + row[10])
                            self.assertTrue(row[11] == str(call_start_time), 'Incorrect Start Time found: ' + row[11])
                            self.assertTrue(row[12] == str(call_end_time), 'Incorrect Call End Time found: ' + row[12])
                            self.assertTrue(row[13] == data.pstn_conf_qual_numbers["number%s" % str(count-1)]['desc_name'], 'Incorrect state found: ' + row[13])
            finally:
                os.system('echo %s|sudo -S %s' % (data.sudo_password, 'rm ' + csv_file_name))
        finally:
            rh.delete_job_processing_data(job_details['id'], job_processing_table)
            rh.delete_item(token, "campaign", campaign_details["data"]["id"])
    test_campaign_job_report_conference_with_provider_test_type.priority=1
    test_campaign_job_report_conference_with_provider_test_type.test_area="conference_with_provider_test_type"

    def test_campaign_job_report_conference_with_fixed_ivr_test_type(self):
        """ Campaign job completion report with Conference with Fixed IVR test-type
        """
        ##----------------- Add Conference with Fixed IVR test-type campaign -----------------##
        campaign_name = "test_campaign_"+str(int(time.time()))
        campaign_report_contact=[data.email_contact]
        campaign_once_off_time = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M") + ":00"
        campaign_numbers, campaign_number_details = rh.get_campaign_numbers_info(data.pstn_conf_qual_numbers)
        campaign_details = rh.add_campaign(token, name=campaign_name, test_type_id=data.conference_with_fixed_ivr_test_type_id, status=1, numbers=campaign_numbers, report_interval_id=1, timezone_id=data.utc_timezone_id, campaign_once_off=str(campaign_once_off_time), campaign_report_contact_flag=True, campaign_report_contact=campaign_report_contact)
        try:
            ##----------------- Add Campaign Job entry in Job table -----------------##
            campaign_job_insert_val = (data.company_id, campaign_details["data"]["id"], data.conference_with_fixed_ivr_test_type_id, campaign_name, campaign_once_off_time, json.dumps(campaign_number_details))
            campaign_job_insert_query = "insert into job (company_id, campaign_id, test_type_id, name, start_time, job_filter_string) values (%s, %s, %s, %s, %s ,%s)"
            rh.execute_db_query(campaign_job_insert_query, campaign_job_insert_val)
            job_detail_query = "select * from job where campaign_id = %s" % (campaign_details["data"]["id"])
            job_details = rh.execute_select_db_query(job_detail_query, table_name='job_table')
            print('-------job_details--------> ', job_details)
            ##----------------- Get Job Processing table according to Test-type -----------------##
            job_processing_table = rh.get_job_processing_table(data.conference_with_fixed_ivr_test_type_id)
            ##----------------- Enter Job Processing entries -----------------##
            call_start_time = datetime.datetime.strptime(campaign_once_off_time,'%Y-%m-%d %H:%M:%S')
            call_end_time = call_start_time + timedelta(0,3)
            for key in data.pstn_conf_qual_numbers:
                number = data.pstn_conf_qual_numbers[key]
                campaign_job_processing_insert_val = (data.conference_with_fixed_ivr_test_type_id, job_details['id'], number['server_id'], number['server_id'], number['pesq_server_id'], number['id'], data.ivr_spearline_prompt_id, number['id'], data.ivr_spearline_prompt_id, number['phonegroup_id'], number['route_id'], data.cli, call_start_time, call_end_time, 1, 1, number['desc_id'], call_start_time)
                campaign_job_processing_insert_query = "insert into " + job_processing_table + " (test_type_id,job_id,server_id,ddi_server_id,pesq_server_id,number_id,ivr_traversal_id,ddi_number_id,ddi_ivr_traversal_id,phonegroup_id,route_id,cli,call_start_time,call_end_time,processing_complete,test_counter,call_description_id,created_on) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                rh.execute_db_query(campaign_job_processing_insert_query, campaign_job_processing_insert_val) 
            # Generate report for Conference with Fixed IVR test-type
            rh.generate_report(campaign_name, job_details["id"])
            try:
                # Fetch newly created campaign job completion report and verify it
                os.chdir(os.getcwd() + "/csv/")
                result = glob.glob(campaign_name + '*.csv')
                print('Newly fetched CSV report file: ', result[0])
                csv_file_name = result[0]
                csv_file_path = os.getcwd() + "/" + csv_file_name
                with open(csv_file_path, 'r') as file:
                    reader = csv.reader(file)
                    for count, row in enumerate(reader):
                        if count==0:
                            self.assertTrue(row[0] == campaign_name + ' Report', "Mismatch in campaign report title")
                        elif count==1:
                            self.assertTrue(row == data.conference_with_fixed_ivr_report_headers, "Mismatch in campaign report headers")
                        elif count>1:
                            number_str = str(data.pstn_conf_qual_numbers["number%s" % str(count-1)]['number'])
                            self.assertTrue(len(row) == len(data.conference_with_fixed_ivr_report_headers), 'Data is not correct')
                            self.assertTrue(row[1] == number_str, 'Incorrect number found: ' + row[1])
                            self.assertTrue(row[2] == campaign_name, 'Incorrect campaign name found: ' + row[2])
                            self.assertTrue(row[3] == data.pstn_conf_qual_numbers["number%s" % str(count-1)]['country'], 'Incorrect country found: ' + row[3])
                            self.assertTrue(row[4] == data.pstn_conf_qual_numbers["number%s" % str(count-1)]['type'], 'Incorrect number-type found: ' + row[4])
                            self.assertTrue(row[5] == number_str + '_customer', 'Incorrect customer found: ' + row[5])
                            self.assertTrue(row[6] == number_str + '_department', 'Incorrect department found: ' + row[6])
                            self.assertTrue(row[7] == number_str + '_location', 'Incorrect location found: ' + row[7])
                            self.assertTrue(row[8] == number_str + '_carrier', 'Incorrect carrier found: ' + row[8])
                            self.assertTrue(row[10] == data.ivr_spearline_prompt, 'Incorrect IVR found: ' + row[10])
                            self.assertTrue(row[11] == str(call_start_time), 'Incorrect Start Time found: ' + row[11])
                            self.assertTrue(row[12] == str(call_end_time), 'Incorrect Call End Time found: ' + row[12])
                            self.assertTrue(row[13] == data.pstn_conf_qual_numbers["number%s" % str(count-1)]['desc_name'], 'Incorrect state found: ' + row[13])
            finally:
                os.system('echo %s|sudo -S %s' % (data.sudo_password, 'rm ' + csv_file_name))
        finally:
            rh.delete_job_processing_data(job_details['id'], job_processing_table)
            rh.delete_item(token, "campaign", campaign_details["data"]["id"])
    test_campaign_job_report_conference_with_fixed_ivr_test_type.priority=1
    test_campaign_job_report_conference_with_fixed_ivr_test_type.test_area="conference_with_fixed_ivr_test_type"

    def test_campaign_job_report_webex_controlled_ddi_conference_test_type(self):
        """ Campaign job completion report with WebEx Controlled DDI conference test-type
        """
        ##----------------- Add WebEx Controlled DDI conference test-type campaign -----------------##
        campaign_name = "test_campaign_"+str(int(time.time()))
        campaign_report_contact=[data.email_contact]
        campaign_once_off_time = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M") + ":00"
        campaign_numbers, campaign_number_details = rh.get_campaign_numbers_info(data.pstn_conf_qual_numbers)
        campaign_details = rh.add_campaign(token, name=campaign_name, test_type_id=data.webex_controlled_ddi_conference_test_type_id, status=1, numbers=campaign_numbers, report_interval_id=1, timezone_id=data.utc_timezone_id, campaign_once_off=str(campaign_once_off_time), campaign_report_contact_flag=True, campaign_report_contact=campaign_report_contact)
        try:
            ##----------------- Add Campaign Job entry in Job table -----------------##
            campaign_job_insert_val = (data.company_id, campaign_details["data"]["id"], data.webex_controlled_ddi_conference_test_type_id, campaign_name, campaign_once_off_time, json.dumps(campaign_number_details))
            campaign_job_insert_query = "insert into job (company_id, campaign_id, test_type_id, name, start_time, job_filter_string) values (%s, %s, %s, %s, %s ,%s)"
            rh.execute_db_query(campaign_job_insert_query, campaign_job_insert_val)
            job_detail_query = "select * from job where campaign_id = %s" % (campaign_details["data"]["id"])
            job_details = rh.execute_select_db_query(job_detail_query, table_name='job_table')
            print('-------job_details--------> ', job_details)
            ##----------------- Get Job Processing table according to Test-type -----------------##
            job_processing_table = rh.get_job_processing_table(data.webex_controlled_ddi_conference_test_type_id)
            ##----------------- Enter Job Processing entries -----------------##
            call_start_time = datetime.datetime.strptime(campaign_once_off_time,'%Y-%m-%d %H:%M:%S')
            call_end_time = call_start_time + timedelta(0,3)
            for key in data.pstn_conf_qual_numbers:
                number = data.pstn_conf_qual_numbers[key]
                campaign_job_processing_insert_val = (data.webex_controlled_ddi_conference_test_type_id, job_details['id'], number['server_id'], number['pesq_server_id'], number['id'], data.ivr_spearline_prompt_id, number['id'], data.ivr_spearline_prompt_id, number['phonegroup_id'], number['route_id'], data.cli, call_start_time, call_start_time, call_end_time, 1, 1, number['desc_id'], call_start_time)
                campaign_job_processing_insert_query = "insert into " + job_processing_table + " (test_type_id,job_id,server_id,pesq_server_id,number_id,ivr_traversal_id,ddi_number_id,ddi_ivr_traversal_id,phonegroup_id,route_id,cli,call_start_time,call_connect_time,call_end_time,processing_complete,test_counter,call_description_id,created_on) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                rh.execute_db_query(campaign_job_processing_insert_query, campaign_job_processing_insert_val) 
            # Generate report for WebEx Controlled DDI conference test-type
            rh.generate_report(campaign_name, job_details["id"])
            try:
                # Fetch newly created campaign job completion report and verify it
                os.chdir(os.getcwd() + "/csv/")
                result = glob.glob(campaign_name + '*.csv')
                print('Newly fetched CSV report file: ', result[0])
                csv_file_name = result[0]
                csv_file_path = os.getcwd() + "/" + csv_file_name
                with open(csv_file_path, 'r') as file:
                    reader = csv.reader(file)
                    for count, row in enumerate(reader):
                        if count==0:
                            self.assertTrue(row[0] == campaign_name + ' Report', "Mismatch in campaign report title")
                        elif count==1:
                            self.assertTrue(row == data.webex_controlled_ddi_conference_report_headers, "Mismatch in campaign report headers")
                        elif count>1:
                            number_str = str(data.pstn_conf_qual_numbers["number%s" % str(count-1)]['number'])
                            self.assertTrue(len(row) == len(data.webex_controlled_ddi_conference_report_headers), 'Data is not correct')
                            self.assertTrue(row[1] == number_str, 'Incorrect number found: ' + row[1])
                            self.assertTrue(row[2] == campaign_name, 'Incorrect campaign name found: ' + row[2])
                            self.assertTrue(row[3] == data.pstn_conf_qual_numbers["number%s" % str(count-1)]['country'], 'Incorrect country found: ' + row[3])
                            self.assertTrue(row[4] == data.pstn_conf_qual_numbers["number%s" % str(count-1)]['type'], 'Incorrect number-type found: ' + row[4])
                            self.assertTrue(row[5] == number_str + '_customer', 'Incorrect customer found: ' + row[5])
                            self.assertTrue(row[6] == number_str + '_department', 'Incorrect department found: ' + row[6])
                            self.assertTrue(row[7] == number_str + '_location', 'Incorrect location found: ' + row[7])
                            self.assertTrue(row[8] == number_str + '_carrier', 'Incorrect carrier found: ' + row[8])
                            self.assertTrue(row[10] == data.ivr_spearline_prompt, 'Incorrect IVR found: ' + row[10])
                            self.assertTrue(row[11] == str(call_start_time), 'Incorrect Start Time found: ' + row[11])
                            self.assertTrue(row[12] == str(call_end_time), 'Incorrect Call End Time found: ' + row[12])
                            self.assertTrue(row[13] == data.pstn_conf_qual_numbers["number%s" % str(count-1)]['desc_name'], 'Incorrect state found: ' + row[13])
            finally:
                os.system('echo %s|sudo -S %s' % (data.sudo_password, 'rm ' + csv_file_name))
        finally:
            rh.delete_job_processing_data(job_details['id'], job_processing_table)
            rh.delete_item(token, "campaign", campaign_details["data"]["id"])
    test_campaign_job_report_webex_controlled_ddi_conference_test_type.priority=1
    test_campaign_job_report_webex_controlled_ddi_conference_test_type.test_area="webex_controlled_ddi_conference_test_type"

    def test_campaign_job_report_area_connection_test_type(self):
        """ Campaign job completion report with Area Connection Test test-type
        """
        ##----------------- Add Area Connection Test test-type campaign -----------------##
        campaign_name = "test_campaign_"+str(int(time.time()))
        campaign_report_contact=[data.email_contact]
        campaign_once_off_time = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M") + ":00"
        provider = rh.get_random_resource(token, "provider")
        campaign_numbers, campaign_number_details = rh.get_campaign_numbers_info(data.pstn_qual_numbers)
        campaign_details = rh.add_campaign(token, name=campaign_name, test_type_id=data.area_connection_test_type_id, status=1, numbers=campaign_numbers, report_interval_id=1, timezone_id=data.utc_timezone_id, campaign_once_off=str(campaign_once_off_time), provider=[provider], campaign_report_contact_flag=True, campaign_report_contact=campaign_report_contact)
        try:
            campaign_number_update_val = (json.dumps(campaign_number_details), campaign_details["data"]["id"])
            campaign_number_update_query = "update campaign SET filter_string = %s WHERE id = %s"
            rh.execute_db_query(campaign_number_update_query, campaign_number_update_val)
            ##----------------- Add Campaign Job entry in Job table -----------------##
            campaign_job_insert_val = (data.company_id, campaign_details["data"]["id"], data.area_connection_test_type_id, campaign_name, campaign_once_off_time, json.dumps(campaign_number_details))
            campaign_job_insert_query = "insert into job (company_id, campaign_id, test_type_id, name, start_time, job_filter_string) values (%s, %s, %s, %s, %s ,%s)"
            rh.execute_db_query(campaign_job_insert_query, campaign_job_insert_val)
            job_detail_query = "select * from job where campaign_id = %s" % (campaign_details["data"]["id"])
            job_details = rh.execute_select_db_query(job_detail_query, table_name='job_table')
            print('-------job_details--------> ', job_details)
            ##----------------- Get Job Processing table according to Test-type -----------------##
            job_processing_table = rh.get_job_processing_table(data.area_connection_test_type_id)
            #----------------- Enter Job Processing entries -----------------##
            call_start_time = datetime.datetime.strptime(campaign_once_off_time,'%Y-%m-%d %H:%M:%S')
            call_end_time = call_start_time + timedelta(0,3)
            for key in data.pstn_qual_numbers:
                number = data.pstn_qual_numbers[key]
                campaign_job_processing_insert_val = (data.area_connection_test_type_id, job_details['id'], number['server_id'], number['id'], number['route_id'], data.cli, data.ivr_spearline_prompt_id, call_start_time, call_start_time, call_end_time, 1, number['desc_id'], call_start_time)
                campaign_job_processing_insert_query = "insert into " + job_processing_table + " (test_type_id,job_id,server_id,number_id,route_id,cli,ivr_traversal_id,call_start_time,call_connect_time,call_end_time,processing_complete,call_description_id,created_on) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                rh.execute_db_query(campaign_job_processing_insert_query, campaign_job_processing_insert_val)
            # Generate report for Area Connection Test test-type
            rh.generate_report(campaign_name, job_details["id"])
            try:
                # Fetch newly created campaign job completion report and verify it
                os.chdir(os.getcwd() + "/csv/")
                result = glob.glob(campaign_name + '*.csv')
                print('Newly fetched CSV report file: ', result[0])
                csv_file_name = result[0]
                csv_file_path = os.getcwd() + "/" + csv_file_name
                with open(csv_file_path, 'r') as file:
                    reader = csv.reader(file)
                    for count, row in enumerate(reader):
                        if count==0:
                            self.assertTrue(row[0] == campaign_name + ' Report', "Mismatch in campaign report title")
                        elif count==1:
                            self.assertTrue(row == data.area_connection_test_report_headers, "Mismatch in campaign report headers")
                        elif count>1:
                            number_str = str(data.pstn_qual_numbers["number%s" % str(count-1)]['number'])
                            self.assertTrue(len(row) == len(data.area_connection_test_report_headers), 'Data is not correct')
                            self.assertTrue(row[1] == number_str, 'Incorrect number found: ' + row[1])
                            self.assertTrue(row[2] == campaign_name, 'Incorrect campaign name found: ' + row[2])
                            self.assertTrue(row[3] == data.pstn_qual_numbers["number%s" % str(count-1)]['country'], 'Incorrect country found: ' + row[3])
                            self.assertTrue(row[4] == data.pstn_qual_numbers["number%s" % str(count-1)]['type'], 'Incorrect number-type found: ' + row[4])
                            self.assertTrue(row[5] == number_str + '_customer', 'Incorrect customer found: ' + row[5])
                            self.assertTrue(row[6] == number_str + '_department', 'Incorrect department found: ' + row[6])
                            self.assertTrue(row[7] == number_str + '_location', 'Incorrect location found: ' + row[7])
                            self.assertTrue(row[8] == number_str + '_carrier', 'Incorrect carrier found: ' + row[8])
                            self.assertTrue(row[10] == data.ivr_spearline_prompt, 'Incorrect IVR found: ' + row[10])
                            self.assertTrue(row[11] == data.pstn_qual_numbers["number%s" % str(count-1)]['desc_name'], 'Incorrect call description found: ' + row[11])
            finally:
                os.system('echo %s|sudo -S %s' % (data.sudo_password, 'rm ' + csv_file_name))
        finally:
            rh.delete_job_processing_data(job_details['id'], job_processing_table)
            rh.delete_item(token, "campaign", campaign_details["data"]["id"])
    test_campaign_job_report_area_connection_test_type.priority=1
    test_campaign_job_report_area_connection_test_type.test_area="area_connection_test_type"

    def test_campaign_job_report_audio_latency_with_provider_test_type(self):
        """ Campaign job completion report with Audio Latency with Provider Test test-type
        """
        ##----------------- Add Audio Latency with Provider Test test-type campaign -----------------##
        campaign_name = "test_campaign_"+str(int(time.time()))
        campaign_report_contact=[data.email_contact]
        campaign_once_off_time = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M") + ":00"
        provider = rh.get_random_resource(token, "provider")
        campaign_numbers, campaign_number_details = rh.get_campaign_numbers_info(data.pstn_qual_numbers)
        campaign_details = rh.add_campaign(token, name=campaign_name, test_type_id=data.audio_latency_with_provider_test_type_id, status=1, numbers=campaign_numbers, report_interval_id=1, timezone_id=data.utc_timezone_id, campaign_once_off=str(campaign_once_off_time), provider=[provider], campaign_report_contact_flag=True, campaign_report_contact=campaign_report_contact)
        try:
            campaign_number_update_val = (json.dumps(campaign_number_details), campaign_details["data"]["id"])
            campaign_number_update_query = "update campaign SET filter_string = %s WHERE id = %s"
            rh.execute_db_query(campaign_number_update_query, campaign_number_update_val)
            ##----------------- Add Campaign Job entry in Job table -----------------##
            campaign_job_insert_val = (data.company_id, campaign_details["data"]["id"], data.audio_latency_with_provider_test_type_id, campaign_name, campaign_once_off_time, json.dumps(campaign_number_details))
            campaign_job_insert_query = "insert into job (company_id, campaign_id, test_type_id, name, start_time, job_filter_string) values (%s, %s, %s, %s, %s ,%s)"
            rh.execute_db_query(campaign_job_insert_query, campaign_job_insert_val)
            job_detail_query = "select * from job where campaign_id = %s" % (campaign_details["data"]["id"])
            job_details = rh.execute_select_db_query(job_detail_query, table_name='job_table')
            print('-------job_details--------> ', job_details)
            ##----------------- Get Job Processing table according to Test-type -----------------##
            job_processing_table = rh.get_job_processing_table(data.audio_latency_with_provider_test_type_id)
            #----------------- Enter Job Processing entries -----------------##
            call_start_time = datetime.datetime.strptime(campaign_once_off_time,'%Y-%m-%d %H:%M:%S')
            call_end_time = call_start_time + timedelta(0,3)
            for key in data.pstn_qual_numbers:
                number = data.pstn_qual_numbers[key]
                campaign_job_processing_insert_val = (data.audio_latency_with_provider_test_type_id, job_details['id'], number['server_id'], number['id'], number['route_id'], data.cli, data.ivr_spearline_prompt_id, call_start_time, call_start_time, call_end_time, 1, number['desc_id'], call_start_time)
                campaign_job_processing_insert_query = "insert into " + job_processing_table + " (test_type_id,job_id,server_id,number_id,route_id,cli,ivr_traversal_id,call_start_time,call_connect_time,call_end_time,processing_complete,call_description_id,created_on) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                rh.execute_db_query(campaign_job_processing_insert_query, campaign_job_processing_insert_val)
            # Generate report for Audio Latency with Provider Test test-type
            rh.generate_report(campaign_name, job_details["id"])
            try:
                # Fetch newly created campaign job completion report and verify it
                os.chdir(os.getcwd() + "/csv/")
                result = glob.glob(campaign_name + '*.csv')
                print('Newly fetched CSV report file: ', result[0])
                csv_file_name = result[0]
                csv_file_path = os.getcwd() + "/" + csv_file_name
                with open(csv_file_path, 'r') as file:
                    reader = csv.reader(file)
                    for count, row in enumerate(reader):
                        if count==0:
                            self.assertTrue(row[0] == campaign_name + ' Report', "Mismatch in campaign report title")
                        elif count==1:
                            self.assertTrue(row == data.audio_latency_testtype_report_headers, "Mismatch in campaign report headers")
                        elif count>1:
                            number_str = str(data.pstn_qual_numbers["number%s" % str(count-1)]['number'])
                            self.assertTrue(len(row) == len(data.audio_latency_testtype_report_headers), 'Data is not correct')
                            self.assertTrue(row[1] == number_str, 'Incorrect number found: ' + row[1])
                            self.assertTrue(row[2] == campaign_name, 'Incorrect campaign name found: ' + row[2])
                            self.assertTrue(row[3] == data.pstn_qual_numbers["number%s" % str(count-1)]['country'], 'Incorrect country found: ' + row[3])
                            self.assertTrue(row[4] == data.pstn_qual_numbers["number%s" % str(count-1)]['type'], 'Incorrect number-type found: ' + row[4])
                            self.assertTrue(row[5] == number_str + '_customer', 'Incorrect customer found: ' + row[5])
                            self.assertTrue(row[6] == number_str + '_department', 'Incorrect department found: ' + row[6])
                            self.assertTrue(row[7] == number_str + '_location', 'Incorrect location found: ' + row[7])
                            self.assertTrue(row[8] == number_str + '_carrier', 'Incorrect carrier found: ' + row[8])
                            self.assertTrue(row[10] == data.ivr_spearline_prompt, 'Incorrect IVR found: ' + row[10])
                            self.assertTrue(row[11] == data.pstn_qual_numbers["number%s" % str(count-1)]['desc_name'], 'Incorrect call description found: ' + row[11])
            finally:
                os.system('echo %s|sudo -S %s' % (data.sudo_password, 'rm ' + csv_file_name))
        finally:
            rh.delete_job_processing_data(job_details['id'], job_processing_table)
            rh.delete_item(token, "campaign", campaign_details["data"]["id"])
    test_campaign_job_report_audio_latency_with_provider_test_type.priority=1
    test_campaign_job_report_audio_latency_with_provider_test_type.test_area="audio_latency_with_provider_test_type"

    def test_campaign_job_report_connection_for_5_sec_test_type(self):
        """ Campaign job completion report with Connection for 5 sec test-type
        """
        ##----------------- Add Connection for 5 sec test-type campaign -----------------##
        campaign_name = "test_campaign_"+str(int(time.time()))
        campaign_report_contact=[data.email_contact]
        campaign_once_off_time = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M") + ":00"
        campaign_numbers, campaign_number_details = rh.get_campaign_numbers_info(data.pstn_qual_numbers)
        campaign_details = rh.add_campaign(token, name=campaign_name, test_type_id=data.connection_for_5_sec_test_type_id, status=1, numbers=campaign_numbers, report_interval_id=1, timezone_id=data.utc_timezone_id, campaign_once_off=str(campaign_once_off_time), campaign_report_contact_flag=True, campaign_report_contact=campaign_report_contact)
        try:
            campaign_number_update_val = (json.dumps(campaign_number_details), campaign_details["data"]["id"])
            campaign_number_update_query = "update campaign SET filter_string = %s WHERE id = %s"
            rh.execute_db_query(campaign_number_update_query, campaign_number_update_val)
            ##----------------- Add Campaign Job entry in Job table -----------------##
            campaign_job_insert_val = (data.company_id, campaign_details["data"]["id"], data.connection_for_5_sec_test_type_id, campaign_name, campaign_once_off_time, json.dumps(campaign_number_details))
            campaign_job_insert_query = "insert into job (company_id, campaign_id, test_type_id, name, start_time, job_filter_string) values (%s, %s, %s, %s, %s ,%s)"
            rh.execute_db_query(campaign_job_insert_query, campaign_job_insert_val)
            job_detail_query = "select * from job where campaign_id = %s" % (campaign_details["data"]["id"])
            job_details = rh.execute_select_db_query(job_detail_query, table_name='job_table')
            print('-------job_details--------> ', job_details)
            ##----------------- Get Job Processing table according to Test-type -----------------##
            job_processing_table = rh.get_job_processing_table(data.connection_for_5_sec_test_type_id)
            #----------------- Enter Job Processing entries -----------------##
            call_start_time = datetime.datetime.strptime(campaign_once_off_time,'%Y-%m-%d %H:%M:%S')
            call_end_time = call_start_time + timedelta(0,3)
            for key in data.pstn_qual_numbers:
                number = data.pstn_qual_numbers[key]
                campaign_job_processing_insert_val = (data.connection_test_type_id, job_details['id'], number['server_id'], number['id'], data.cli, data.ivr_spearline_prompt_id, number['route_id'], call_start_time, call_start_time, call_end_time, 1, number['desc_id'], call_start_time)
                campaign_job_processing_insert_query = "insert into " + job_processing_table + " (test_type_id,job_id,server_id,number_id,cli,ivr_traversal_id,route_id,call_start_time,call_connect_time,call_end_time,processing_complete,call_description_id,created_on) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                rh.execute_db_query(campaign_job_processing_insert_query, campaign_job_processing_insert_val)
            # Generate report for Connection for 5 sec test-type
            rh.generate_report(campaign_name, job_details["id"])
            try:
                # Fetch newly created campaign job completion report and verify it
                os.chdir(os.getcwd() + "/csv/")
                result = glob.glob(campaign_name + '*.csv')
                print('Newly fetched CSV report file: ', result[0])
                csv_file_name = result[0]
                csv_file_path = os.getcwd() + "/" + csv_file_name
                with open(csv_file_path, 'r') as file:
                    reader = csv.reader(file)
                    for count, row in enumerate(reader):
                        if count==0:
                            self.assertTrue(row[0] == campaign_name + ' Report', "Mismatch in campaign report title")
                        elif count==1:
                            self.assertTrue(row == data.connection_testtype_report_headers, "Mismatch in campaign report headers")
                        elif count>1:
                            number_str = str(data.pstn_qual_numbers["number%s" % str(count-1)]['number'])
                            self.assertTrue(len(row) == len(data.connection_testtype_report_headers), 'Data is not correct')
                            self.assertTrue(row[1] == number_str, 'Incorrect number found: ' + row[1])
                            self.assertTrue(row[2] == campaign_name, 'Incorrect campaign name found: ' + row[2])
                            self.assertTrue(row[3] == data.pstn_qual_numbers["number%s" % str(count-1)]['country'], 'Incorrect country found: ' + row[3])
                            self.assertTrue(row[4] == data.pstn_qual_numbers["number%s" % str(count-1)]['type'], 'Incorrect number-type found: ' + row[4])
                            self.assertTrue(row[5] == number_str + '_customer', 'Incorrect customer found: ' + row[5])
                            self.assertTrue(row[6] == number_str + '_department', 'Incorrect department found: ' + row[6])
                            self.assertTrue(row[7] == number_str + '_location', 'Incorrect location found: ' + row[7])
                            self.assertTrue(row[8] == number_str + '_carrier', 'Incorrect carrier found: ' + row[8])
                            self.assertTrue(row[10] == data.ivr_spearline_prompt, 'Incorrect IVR found: ' + row[10])
                            self.assertTrue(row[11] == data.pstn_qual_numbers["number%s" % str(count-1)]['desc_name'], 'Incorrect call description found: ' + row[11])
            finally:
                os.system('echo %s|sudo -S %s' % (data.sudo_password, 'rm ' + csv_file_name))
        finally:
            rh.delete_job_processing_data(job_details['id'], job_processing_table)
            rh.delete_item(token, "campaign", campaign_details["data"]["id"])
    test_campaign_job_report_connection_for_5_sec_test_type.priority=1
    test_campaign_job_report_connection_for_5_sec_test_type.test_area="connection_for_5_sec_test_type"

    def test_campaign_job_report_contact_center_polqa_test_type(self):
        """ Campaign job completion report with Contact Center (POLQA) test-type
        """
        ##----------------- Add Contact Center (POLQA) test-type campaign -----------------##
        campaign_name = "test_campaign_"+str(int(time.time()))
        campaign_report_contact=[data.email_contact]
        campaign_once_off_time = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M") + ":00"
        campaign_numbers, campaign_number_details = rh.get_campaign_numbers_info(data.pstn_qual_numbers)
        campaign_details = rh.add_campaign(token, name=campaign_name, test_type_id=data.contact_center_polqa_test_type_id, status=1, numbers=campaign_numbers, report_interval_id=1, timezone_id=data.utc_timezone_id, campaign_once_off=str(campaign_once_off_time), campaign_report_contact_flag=True, campaign_report_contact=campaign_report_contact)
        try:
            campaign_number_update_val = (json.dumps(campaign_number_details), campaign_details["data"]["id"])
            campaign_number_update_query = "update campaign SET filter_string = %s WHERE id = %s"
            rh.execute_db_query(campaign_number_update_query, campaign_number_update_val)
            ##----------------- Add Campaign Job entry in Job table -----------------##
            campaign_job_insert_val = (data.company_id, campaign_details["data"]["id"], data.contact_center_polqa_test_type_id, campaign_name, campaign_once_off_time, json.dumps(campaign_number_details))
            campaign_job_insert_query = "insert into job (company_id, campaign_id, test_type_id, name, start_time, job_filter_string) values (%s, %s, %s, %s, %s ,%s)"
            rh.execute_db_query(campaign_job_insert_query, campaign_job_insert_val)
            job_detail_query = "select * from job where campaign_id = %s" % (campaign_details["data"]["id"])
            job_details = rh.execute_select_db_query(job_detail_query, table_name='job_table')
            print('-------job_details--------> ', job_details)
            ##----------------- Get Job Processing table according to Test-type -----------------##
            job_processing_table = rh.get_job_processing_table(data.contact_center_polqa_test_type_id)
            #----------------- Enter Job Processing entries -----------------##
            call_start_time = datetime.datetime.strptime(campaign_once_off_time,'%Y-%m-%d %H:%M:%S')
            call_end_time = call_start_time + timedelta(0,3)
            for key in data.pstn_qual_numbers:
                number = data.pstn_qual_numbers[key]
                campaign_job_processing_insert_val = (data.contact_center_polqa_test_type_id, job_details['id'], number['server_id'], number['server_id'], number['id'], number['route_id'], data.cli, data.ivr_spearline_prompt_id, call_start_time, call_start_time, call_end_time, 1, number['desc_id'], call_start_time)
                campaign_job_processing_insert_query = "insert into " + job_processing_table + " (test_type_id,job_id,server_id,pesq_server_id,number_id,route_id,cli,ivr_traversal_id,call_start_time,call_connect_time,call_end_time,processing_complete,call_description_id,created_on) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                rh.execute_db_query(campaign_job_processing_insert_query, campaign_job_processing_insert_val)
            # Generate report for Contact Center (POLQA) test-type
            rh.generate_report(campaign_name, job_details["id"])
            try:
                # Fetch newly created campaign job completion report and verify it
                os.chdir(os.getcwd() + "/csv/")
                result = glob.glob(campaign_name + '*.csv')
                print('Newly fetched CSV report file: ', result[0])
                csv_file_name = result[0]
                csv_file_path = os.getcwd() + "/" + csv_file_name
                with open(csv_file_path, 'r') as file:
                    reader = csv.reader(file)
                    for count, row in enumerate(reader):
                        if count==0:
                            self.assertTrue(row[0] == campaign_name + ' Report', "Mismatch in campaign report title")
                        elif count==1:
                            self.assertTrue(row == data.contact_center_polqa_reports_header, "Mismatch in campaign report headers")
                        elif count>1:
                            number_str = str(data.pstn_qual_numbers["number%s" % str(count-1)]['number'])
                            self.assertTrue(len(row) == len(data.contact_center_polqa_reports_header), 'Data is not correct')
                            self.assertTrue(row[1] == number_str, 'Incorrect number found: ' + row[1])
                            self.assertTrue(row[2] == campaign_name, 'Incorrect campaign name found: ' + row[2])
                            self.assertTrue(row[3] == data.pstn_qual_numbers["number%s" % str(count-1)]['country'], 'Incorrect country found: ' + row[3])
                            self.assertTrue(row[4] == data.pstn_qual_numbers["number%s" % str(count-1)]['type'], 'Incorrect number-type found: ' + row[4])
                            self.assertTrue(row[5] == number_str + '_customer', 'Incorrect customer found: ' + row[5])
                            self.assertTrue(row[6] == number_str + '_department', 'Incorrect department found: ' + row[6])
                            self.assertTrue(row[7] == number_str + '_location', 'Incorrect location found: ' + row[7])
                            self.assertTrue(row[8] == number_str + '_carrier', 'Incorrect carrier found: ' + row[8])
                            self.assertTrue(row[10] == data.ivr_spearline_prompt, 'Incorrect IVR found: ' + row[10])
                            self.assertTrue(row[11] == str(call_start_time), 'Incorrect Start Time found: ' + row[11])
                            self.assertTrue(row[12] == str(call_end_time), 'Incorrect Call End Time found: ' + row[12])
                            self.assertTrue(row[13] == data.pstn_qual_numbers["number%s" % str(count-1)]['desc_name'], 'Incorrect state found: ' + row[13])
            finally:
                os.system('echo %s|sudo -S %s' % (data.sudo_password, 'rm ' + csv_file_name))
        finally:
            rh.delete_job_processing_data(job_details['id'], job_processing_table)
            rh.delete_item(token, "campaign", campaign_details["data"]["id"])
    test_campaign_job_report_contact_center_polqa_test_type.priority=1
    test_campaign_job_report_contact_center_polqa_test_type.test_area="contact_center_polqa_test_type"

    def test_campaign_job_report_contact_center_polqa_single_segment_test_type(self):
        """ Campaign job completion report with Contact Center (POLQA) - Single Segment test-type
        """
        ##----------------- Add Contact Center (POLQA) - Single Segment test-type campaign -----------------##
        campaign_name = "test_campaign_"+str(int(time.time()))
        campaign_report_contact=[data.email_contact]
        campaign_once_off_time = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M") + ":00"
        campaign_numbers, campaign_number_details = rh.get_campaign_numbers_info(data.pstn_qual_numbers)
        campaign_details = rh.add_campaign(token, name=campaign_name, test_type_id=data.contact_center_polqa_single_segment_test_type_id, status=1, numbers=campaign_numbers, report_interval_id=1, timezone_id=data.utc_timezone_id, campaign_once_off=str(campaign_once_off_time), campaign_report_contact_flag=True, campaign_report_contact=campaign_report_contact)
        try:
            campaign_number_update_val = (json.dumps(campaign_number_details), campaign_details["data"]["id"])
            campaign_number_update_query = "update campaign SET filter_string = %s WHERE id = %s"
            rh.execute_db_query(campaign_number_update_query, campaign_number_update_val)
            ##----------------- Add Campaign Job entry in Job table -----------------##
            campaign_job_insert_val = (data.company_id, campaign_details["data"]["id"], data.contact_center_polqa_single_segment_test_type_id, campaign_name, campaign_once_off_time, json.dumps(campaign_number_details))
            campaign_job_insert_query = "insert into job (company_id, campaign_id, test_type_id, name, start_time, job_filter_string) values (%s, %s, %s, %s, %s ,%s)"
            rh.execute_db_query(campaign_job_insert_query, campaign_job_insert_val)
            job_detail_query = "select * from job where campaign_id = %s" % (campaign_details["data"]["id"])
            job_details = rh.execute_select_db_query(job_detail_query, table_name='job_table')
            print('-------job_details--------> ', job_details)
            ##----------------- Get Job Processing table according to Test-type -----------------##
            job_processing_table = rh.get_job_processing_table(data.contact_center_polqa_single_segment_test_type_id)
            #----------------- Enter Job Processing entries -----------------##
            call_start_time = datetime.datetime.strptime(campaign_once_off_time,'%Y-%m-%d %H:%M:%S')
            call_end_time = call_start_time + timedelta(0,3)
            for key in data.pstn_qual_numbers:
                number = data.pstn_qual_numbers[key]
                campaign_job_processing_insert_val = (data.contact_center_polqa_single_segment_test_type_id, job_details['id'], number['server_id'], number['server_id'], number['id'], number['route_id'], data.cli, data.ivr_spearline_prompt_id, call_start_time, call_start_time, call_end_time, 1, number['desc_id'], call_start_time)
                campaign_job_processing_insert_query = "insert into " + job_processing_table + " (test_type_id,job_id,server_id,pesq_server_id,number_id,route_id,cli,ivr_traversal_id,call_start_time,call_connect_time,call_end_time,processing_complete,call_description_id,created_on) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                rh.execute_db_query(campaign_job_processing_insert_query, campaign_job_processing_insert_val)
            # Generate report for Contact Center (POLQA) - Single Segment test-type
            rh.generate_report(campaign_name, job_details["id"])
            try:
                # Fetch newly created campaign job completion report and verify it
                os.chdir(os.getcwd() + "/csv/")
                result = glob.glob(campaign_name + '*.csv')
                print('Newly fetched CSV report file: ', result[0])
                csv_file_name = result[0]
                csv_file_path = os.getcwd() + "/" + csv_file_name
                with open(csv_file_path, 'r') as file:
                    reader = csv.reader(file)
                    for count, row in enumerate(reader):
                        if count==0:
                            self.assertTrue(row[0] == campaign_name + ' Report', "Mismatch in campaign report title")
                        elif count==1:
                            self.assertTrue(row == data.contact_center_polqa_reports_header, "Mismatch in campaign report headers")
                        elif count>1:
                            number_str = str(data.pstn_qual_numbers["number%s" % str(count-1)]['number'])
                            self.assertTrue(len(row) == len(data.contact_center_polqa_reports_header), 'Data is not correct')
                            self.assertTrue(row[1] == number_str, 'Incorrect number found: ' + row[1])
                            self.assertTrue(row[2] == campaign_name, 'Incorrect campaign name found: ' + row[2])
                            self.assertTrue(row[3] == data.pstn_qual_numbers["number%s" % str(count-1)]['country'], 'Incorrect country found: ' + row[3])
                            self.assertTrue(row[4] == data.pstn_qual_numbers["number%s" % str(count-1)]['type'], 'Incorrect number-type found: ' + row[4])
                            self.assertTrue(row[5] == number_str + '_customer', 'Incorrect customer found: ' + row[5])
                            self.assertTrue(row[6] == number_str + '_department', 'Incorrect department found: ' + row[6])
                            self.assertTrue(row[7] == number_str + '_location', 'Incorrect location found: ' + row[7])
                            self.assertTrue(row[8] == number_str + '_carrier', 'Incorrect carrier found: ' + row[8])
                            self.assertTrue(row[10] == data.ivr_spearline_prompt, 'Incorrect IVR found: ' + row[10])
                            self.assertTrue(row[11] == str(call_start_time), 'Incorrect Start Time found: ' + row[11])
                            self.assertTrue(row[12] == str(call_end_time), 'Incorrect Call End Time found: ' + row[12])
                            self.assertTrue(row[13] == data.pstn_qual_numbers["number%s" % str(count-1)]['desc_name'], 'Incorrect state found: ' + row[13])
            finally:
                os.system('echo %s|sudo -S %s' % (data.sudo_password, 'rm ' + csv_file_name))
        finally:
            rh.delete_job_processing_data(job_details['id'], job_processing_table)
            rh.delete_item(token, "campaign", campaign_details["data"]["id"])
    test_campaign_job_report_contact_center_polqa_single_segment_test_type.priority=1
    test_campaign_job_report_contact_center_polqa_single_segment_test_type.test_area="contact_center_polqa_single_segment_test_type"

    def test_campaign_job_report_contact_center_google_test_type(self):
        """ Campaign job completion report with Contact Center (Google) test-type
        """
        ##----------------- Add Contact Center (Google) test-type campaign -----------------##
        campaign_name = "test_campaign_"+str(int(time.time()))
        campaign_report_contact=[data.email_contact]
        campaign_once_off_time = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M") + ":00"
        campaign_numbers, campaign_number_details = rh.get_campaign_numbers_info(data.pstn_qual_numbers)
        campaign_details = rh.add_campaign(token, name=campaign_name, test_type_id=data.contact_center_google_test_type_id, status=1, numbers=campaign_numbers, report_interval_id=1, timezone_id=data.utc_timezone_id, campaign_once_off=str(campaign_once_off_time), campaign_report_contact_flag=True, campaign_report_contact=campaign_report_contact)
        try:
            campaign_number_update_val = (json.dumps(campaign_number_details), campaign_details["data"]["id"])
            campaign_number_update_query = "update campaign SET filter_string = %s WHERE id = %s"
            rh.execute_db_query(campaign_number_update_query, campaign_number_update_val)
            ##----------------- Add Campaign Job entry in Job table -----------------##
            campaign_job_insert_val = (data.company_id, campaign_details["data"]["id"], data.contact_center_google_test_type_id, campaign_name, campaign_once_off_time, json.dumps(campaign_number_details))
            campaign_job_insert_query = "insert into job (company_id, campaign_id, test_type_id, name, start_time, job_filter_string) values (%s, %s, %s, %s, %s ,%s)"
            rh.execute_db_query(campaign_job_insert_query, campaign_job_insert_val)
            job_detail_query = "select * from job where campaign_id = %s" % (campaign_details["data"]["id"])
            job_details = rh.execute_select_db_query(job_detail_query, table_name='job_table')
            print('-------job_details--------> ', job_details)
            ##----------------- Get Job Processing table according to Test-type -----------------##
            job_processing_table = rh.get_job_processing_table(data.contact_center_google_test_type_id)
            #----------------- Enter Job Processing entries -----------------##
            call_start_time = datetime.datetime.strptime(campaign_once_off_time,'%Y-%m-%d %H:%M:%S')
            call_end_time = call_start_time + timedelta(0,3)
            for key in data.pstn_qual_numbers:
                number = data.pstn_qual_numbers[key]
                campaign_job_processing_insert_val = (data.contact_center_google_test_type_id, job_details['id'], number['server_id'], number['id'], number['route_id'], data.cli, data.ivr_spearline_prompt_id, call_start_time, call_start_time, call_end_time, 1, number['desc_id'], call_start_time)
                campaign_job_processing_insert_query = "insert into " + job_processing_table + " (test_type_id,job_id,server_id,number_id,route_id,cli,ivr_traversal_id,call_start_time,call_connect_time,call_end_time,processing_complete,call_description_id,created_on) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                rh.execute_db_query(campaign_job_processing_insert_query, campaign_job_processing_insert_val)
            # Generate report for Contact Center (Google) test-type
            rh.generate_report(campaign_name, job_details["id"])
            try:
                # Fetch newly created campaign job completion report and verify it
                os.chdir(os.getcwd() + "/csv/")
                result = glob.glob(campaign_name + '*.csv')
                print('Newly fetched CSV report file: ', result[0])
                csv_file_name = result[0]
                csv_file_path = os.getcwd() + "/" + csv_file_name
                with open(csv_file_path, 'r') as file:
                    reader = csv.reader(file)
                    for count, row in enumerate(reader):
                        if count==0:
                            self.assertTrue(row[0] == campaign_name + ' Report', "Mismatch in campaign report title")
                        elif count==1:
                            self.assertTrue(row == data.contact_center_polqa_reports_header, "Mismatch in campaign report headers")
                        elif count>1:
                            number_str = str(data.pstn_qual_numbers["number%s" % str(count-1)]['number'])
                            self.assertTrue(len(row) == len(data.contact_center_polqa_reports_header), 'Data is not correct')
            finally:
                os.system('echo %s|sudo -S %s' % (data.sudo_password, 'rm ' + csv_file_name))
        finally:
            rh.delete_job_processing_data(job_details['id'], job_processing_table)
            rh.delete_item(token, "campaign", campaign_details["data"]["id"])
    test_campaign_job_report_contact_center_google_test_type.priority=1
    test_campaign_job_report_contact_center_google_test_type.test_area="contact_center_google_test_type"

    def test_campaign_job_report_dtmf_with_quality_test_type(self):
        """ Campaign job completion report with DTMF With Quality test-type
        """
        ##----------------- Add DTMF With Quality test-type campaign -----------------##
        campaign_name = "test_campaign_"+str(int(time.time()))
        campaign_report_contact=[data.email_contact]
        provider=rh.get_random_resource(token, "provider")
        campaign_once_off_time = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M") + ":00"
        campaign_numbers, campaign_number_details = rh.get_campaign_numbers_info(data.pstn_qual_numbers)
        campaign_details = rh.add_campaign(token, name=campaign_name, test_type_id=data.dtmf_with_quality_test_type_id, status=1, numbers=campaign_numbers, provider=[provider], report_interval_id=1, timezone_id=data.utc_timezone_id, campaign_once_off=str(campaign_once_off_time), campaign_report_contact_flag=True, campaign_report_contact=campaign_report_contact)
        try:
            campaign_number_update_val = (json.dumps(campaign_number_details), campaign_details["data"]["id"])
            campaign_number_update_query = "update campaign SET filter_string = %s WHERE id = %s"
            rh.execute_db_query(campaign_number_update_query, campaign_number_update_val)
            ##----------------- Add Campaign Job entry in Job table -----------------##
            campaign_job_insert_val = (data.company_id, campaign_details["data"]["id"], data.dtmf_with_quality_test_type_id, campaign_name, campaign_once_off_time, json.dumps(campaign_number_details))
            campaign_job_insert_query = "insert into job (company_id, campaign_id, test_type_id, name, start_time, job_filter_string) values (%s, %s, %s, %s, %s ,%s)"
            rh.execute_db_query(campaign_job_insert_query, campaign_job_insert_val)
            job_detail_query = "select * from job where campaign_id = %s" % (campaign_details["data"]["id"])
            job_details = rh.execute_select_db_query(job_detail_query, table_name='job_table')
            print('-------job_details--------> ', job_details)
            ##----------------- Get Job Processing table according to Test-type -----------------##
            job_processing_table = rh.get_job_processing_table(data.dtmf_with_quality_test_type_id)
            #----------------- Enter Job Processing entries -----------------##
            call_start_time = datetime.datetime.strptime(campaign_once_off_time,'%Y-%m-%d %H:%M:%S')
            call_end_time = call_start_time + timedelta(0,3)
            for key in data.pstn_qual_numbers:
                number = data.pstn_qual_numbers[key]
                campaign_job_processing_insert_val = (data.dtmf_with_quality_test_type_id, job_details['id'], number['server_id'], number['id'], number['route_id'], data.cli, data.ivr_spearline_prompt_id, call_start_time, call_start_time, call_end_time, 1, number['desc_id'], call_start_time)
                campaign_job_processing_insert_query = "insert into " + job_processing_table + " (test_type_id,job_id,server_id,number_id,route_id,cli,ivr_traversal_id,call_start_time,call_connect_time,call_end_time,processing_complete,call_description_id,created_on) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                rh.execute_db_query(campaign_job_processing_insert_query, campaign_job_processing_insert_val)
            # Generate report for DTMF With Quality test-type
            rh.generate_report(campaign_name, job_details["id"])
            try:
                # Fetch newly created campaign job completion report and verify it
                os.chdir(os.getcwd() + "/csv/")
                result = glob.glob(campaign_name + '*.csv')
                print('Newly fetched CSV report file: ', result[0])
                csv_file_name = result[0]
                csv_file_path = os.getcwd() + "/" + csv_file_name
                with open(csv_file_path, 'r') as file:
                    reader = csv.reader(file)
                    for count, row in enumerate(reader):
                        if count==0:
                            self.assertTrue(row[0] == campaign_name + ' Report', "Mismatch in campaign report title")
                        elif count==1:
                            self.assertTrue(row == data.dtmf_with_quality_reports_header, "Mismatch in campaign report headers")
                        elif count>1:
                            number_str = str(data.pstn_qual_numbers["number%s" % str(count-1)]['number'])
                            self.assertTrue(len(row) == len(data.dtmf_with_quality_reports_header), 'Data is not correct')
                            self.assertTrue(row[1] == number_str, 'Incorrect number found: ' + row[1])
                            self.assertTrue(row[2] == campaign_name, 'Incorrect campaign name found: ' + row[2])
                            self.assertTrue(row[3] == data.pstn_qual_numbers["number%s" % str(count-1)]['country'], 'Incorrect country found: ' + row[3])
                            self.assertTrue(row[4] == data.pstn_qual_numbers["number%s" % str(count-1)]['type'], 'Incorrect number-type found: ' + row[4])
                            self.assertTrue(row[5] == number_str + '_customer', 'Incorrect customer found: ' + row[5])
                            self.assertTrue(row[6] == number_str + '_department', 'Incorrect department found: ' + row[6])
                            self.assertTrue(row[7] == number_str + '_location', 'Incorrect location found: ' + row[7])
                            self.assertTrue(row[8] == number_str + '_carrier', 'Incorrect carrier found: ' + row[8])
                            self.assertTrue(row[10] == data.ivr_spearline_prompt, 'Incorrect IVR found: ' + row[10])
                            self.assertTrue(row[11] == str(call_start_time), 'Incorrect Start Time found: ' + row[11])
                            self.assertTrue(row[12] == str(call_end_time), 'Incorrect Call End Time found: ' + row[12])
                            self.assertTrue(row[13] == data.pstn_qual_numbers["number%s" % str(count-1)]['desc_name'], 'Incorrect state found: ' + row[13])
            finally:
                os.system('echo %s|sudo -S %s' % (data.sudo_password, 'rm ' + csv_file_name))
        finally:
            rh.delete_job_processing_data(job_details['id'], job_processing_table)
            rh.delete_item(token, "campaign", campaign_details["data"]["id"])
    test_campaign_job_report_dtmf_with_quality_test_type.priority=1
    test_campaign_job_report_dtmf_with_quality_test_type.test_area="dtmf_with_quality_test_type"

    def test_campaign_job_report_dtmf_with_quality_different_prompt_test_type(self):
        """ Campaign job completion report with DTMF With Quality (Different prompt) test-type
        """
        ##----------------- Add DTMF With Quality (Different prompt) test-type campaign -----------------##
        campaign_name = "test_campaign_"+str(int(time.time()))
        campaign_report_contact=[data.email_contact]
        provider=rh.get_random_resource(token, "provider")
        campaign_once_off_time = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M") + ":00"
        campaign_numbers, campaign_number_details = rh.get_campaign_numbers_info(data.pstn_qual_numbers)
        campaign_details = rh.add_campaign(token, name=campaign_name, test_type_id=data.dtmf_with_quality_different_prompt_test_type_id, status=1, numbers=campaign_numbers, provider=[provider], report_interval_id=1, timezone_id=data.utc_timezone_id, campaign_once_off=str(campaign_once_off_time), campaign_report_contact_flag=True, campaign_report_contact=campaign_report_contact)
        try:
            campaign_number_update_val = (json.dumps(campaign_number_details), campaign_details["data"]["id"])
            campaign_number_update_query = "update campaign SET filter_string = %s WHERE id = %s"
            rh.execute_db_query(campaign_number_update_query, campaign_number_update_val)
            ##----------------- Add Campaign Job entry in Job table -----------------##
            campaign_job_insert_val = (data.company_id, campaign_details["data"]["id"], data.dtmf_with_quality_different_prompt_test_type_id, campaign_name, campaign_once_off_time, json.dumps(campaign_number_details))
            campaign_job_insert_query = "insert into job (company_id, campaign_id, test_type_id, name, start_time, job_filter_string) values (%s, %s, %s, %s, %s ,%s)"
            rh.execute_db_query(campaign_job_insert_query, campaign_job_insert_val)
            job_detail_query = "select * from job where campaign_id = %s" % (campaign_details["data"]["id"])
            job_details = rh.execute_select_db_query(job_detail_query, table_name='job_table')
            print('-------job_details--------> ', job_details)
            ##----------------- Get Job Processing table according to Test-type -----------------##
            job_processing_table = rh.get_job_processing_table(data.dtmf_with_quality_different_prompt_test_type_id)
            #----------------- Enter Job Processing entries -----------------##
            call_start_time = datetime.datetime.strptime(campaign_once_off_time,'%Y-%m-%d %H:%M:%S')
            call_end_time = call_start_time + timedelta(0,3)
            for key in data.pstn_qual_numbers:
                number = data.pstn_qual_numbers[key]
                campaign_job_processing_insert_val = (data.dtmf_with_quality_different_prompt_test_type_id, job_details['id'], number['server_id'], number['id'], number['route_id'], data.cli, data.ivr_spearline_prompt_id, call_start_time, call_start_time, call_end_time, 1, number['desc_id'], call_start_time)
                campaign_job_processing_insert_query = "insert into " + job_processing_table + " (test_type_id,job_id,server_id,number_id,route_id,cli,ivr_traversal_id,call_start_time,call_connect_time,call_end_time,processing_complete,call_description_id,created_on) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                rh.execute_db_query(campaign_job_processing_insert_query, campaign_job_processing_insert_val)
            # Generate report for DTMF With Quality (Different prompt) test-type
            rh.generate_report(campaign_name, job_details["id"])
            try:
                # Fetch newly created campaign job completion report and verify it
                os.chdir(os.getcwd() + "/csv/")
                result = glob.glob(campaign_name + '*.csv')
                print('Newly fetched CSV report file: ', result[0])
                csv_file_name = result[0]
                csv_file_path = os.getcwd() + "/" + csv_file_name
                with open(csv_file_path, 'r') as file:
                    reader = csv.reader(file)
                    for count, row in enumerate(reader):
                        if count==0:
                            self.assertTrue(row[0] == campaign_name + ' Report', "Mismatch in campaign report title")
                        elif count==1:
                            self.assertTrue(row == data.dtmf_with_quality_reports_header, "Mismatch in campaign report headers")
                        elif count>1:
                            number_str = str(data.pstn_qual_numbers["number%s" % str(count-1)]['number'])
                            self.assertTrue(len(row) == len(data.dtmf_with_quality_reports_header), 'Data is not correct')
                            self.assertTrue(row[1] == number_str, 'Incorrect number found: ' + row[1])
                            self.assertTrue(row[2] == campaign_name, 'Incorrect campaign name found: ' + row[2])
                            self.assertTrue(row[3] == data.pstn_qual_numbers["number%s" % str(count-1)]['country'], 'Incorrect country found: ' + row[3])
                            self.assertTrue(row[4] == data.pstn_qual_numbers["number%s" % str(count-1)]['type'], 'Incorrect number-type found: ' + row[4])
                            self.assertTrue(row[5] == number_str + '_customer', 'Incorrect customer found: ' + row[5])
                            self.assertTrue(row[6] == number_str + '_department', 'Incorrect department found: ' + row[6])
                            self.assertTrue(row[7] == number_str + '_location', 'Incorrect location found: ' + row[7])
                            self.assertTrue(row[8] == number_str + '_carrier', 'Incorrect carrier found: ' + row[8])
                            self.assertTrue(row[10] == data.ivr_spearline_prompt, 'Incorrect IVR found: ' + row[10])
                            self.assertTrue(row[11] == str(call_start_time), 'Incorrect Start Time found: ' + row[11])
                            self.assertTrue(row[12] == str(call_end_time), 'Incorrect Call End Time found: ' + row[12])
                            self.assertTrue(row[13] == data.pstn_qual_numbers["number%s" % str(count-1)]['desc_name'], 'Incorrect state found: ' + row[13])
            finally:
                os.system('echo %s|sudo -S %s' % (data.sudo_password, 'rm ' + csv_file_name))
        finally:
            rh.delete_job_processing_data(job_details['id'], job_processing_table)
            rh.delete_item(token, "campaign", campaign_details["data"]["id"])
    test_campaign_job_report_dtmf_with_quality_different_prompt_test_type.priority=1
    test_campaign_job_report_dtmf_with_quality_different_prompt_test_type.test_area="dtmf_with_quality_different_prompt_test_type"

    def test_campaign_job_report_dtmf_with_quality_and_cli_check_test_type(self):
        """ Campaign job completion report with DTMF With Quality and CLI check test-type
        """
        ##----------------- Add DTMF With Quality and CLI check test-type campaign -----------------##
        campaign_name = "test_campaign_"+str(int(time.time()))
        campaign_report_contact=[data.email_contact]
        provider=rh.get_random_resource(token, "provider")
        campaign_once_off_time = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M") + ":00"
        campaign_numbers, campaign_number_details = rh.get_campaign_numbers_info(data.pstn_qual_numbers)
        campaign_details = rh.add_campaign(token, name=campaign_name, test_type_id=data.dtmf_with_quality_and_cli_check_test_type_id, status=1, numbers=campaign_numbers, provider=[provider], report_interval_id=1, timezone_id=data.utc_timezone_id, campaign_once_off=str(campaign_once_off_time), campaign_report_contact_flag=True, campaign_report_contact=campaign_report_contact)
        try:
            campaign_number_update_val = (json.dumps(campaign_number_details), campaign_details["data"]["id"])
            campaign_number_update_query = "update campaign SET filter_string = %s WHERE id = %s"
            rh.execute_db_query(campaign_number_update_query, campaign_number_update_val)
            ##----------------- Add Campaign Job entry in Job table -----------------##
            campaign_job_insert_val = (data.company_id, campaign_details["data"]["id"], data.dtmf_with_quality_and_cli_check_test_type_id, campaign_name, campaign_once_off_time, json.dumps(campaign_number_details))
            campaign_job_insert_query = "insert into job (company_id, campaign_id, test_type_id, name, start_time, job_filter_string) values (%s, %s, %s, %s, %s ,%s)"
            rh.execute_db_query(campaign_job_insert_query, campaign_job_insert_val)
            job_detail_query = "select * from job where campaign_id = %s" % (campaign_details["data"]["id"])
            job_details = rh.execute_select_db_query(job_detail_query, table_name='job_table')
            print('-------job_details--------> ', job_details)
            ##----------------- Get Job Processing table according to Test-type -----------------##
            job_processing_table = rh.get_job_processing_table(data.dtmf_with_quality_and_cli_check_test_type_id)
            #----------------- Enter Job Processing entries -----------------##
            call_start_time = datetime.datetime.strptime(campaign_once_off_time,'%Y-%m-%d %H:%M:%S')
            call_end_time = call_start_time + timedelta(0,3)
            for key in data.pstn_qual_numbers:
                number = data.pstn_qual_numbers[key]
                campaign_job_processing_insert_val = (data.dtmf_with_quality_and_cli_check_test_type_id, job_details['id'], number['server_id'], number['id'], number['route_id'], data.cli, data.ivr_spearline_prompt_id, call_start_time, call_start_time, call_end_time, 1, number['desc_id'], call_start_time)
                campaign_job_processing_insert_query = "insert into " + job_processing_table + " (test_type_id,job_id,server_id,number_id,route_id,cli,ivr_traversal_id,call_start_time,call_connect_time,call_end_time,processing_complete,call_description_id,created_on) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                rh.execute_db_query(campaign_job_processing_insert_query, campaign_job_processing_insert_val)
            # Generate report for DTMF With Quality and CLI check test-type
            rh.generate_report(campaign_name, job_details["id"])
            try:
                # Fetch newly created campaign job completion report and verify it
                os.chdir(os.getcwd() + "/csv/")
                result = glob.glob(campaign_name + '*.csv')
                print('Newly fetched CSV report file: ', result[0])
                csv_file_name = result[0]
                csv_file_path = os.getcwd() + "/" + csv_file_name
                with open(csv_file_path, 'r') as file:
                    reader = csv.reader(file)
                    for count, row in enumerate(reader):
                        if count==0:
                            self.assertTrue(row[0] == campaign_name + ' Report', "Mismatch in campaign report title")
                        elif count==1:
                            self.assertTrue(row == data.dtmf_with_quality_reports_header, "Mismatch in campaign report headers")
                        elif count>1:
                            number_str = str(data.pstn_qual_numbers["number%s" % str(count-1)]['number'])
                            self.assertTrue(len(row) == len(data.dtmf_with_quality_reports_header), 'Data is not correct')
                            self.assertTrue(row[1] == number_str, 'Incorrect number found: ' + row[1])
                            self.assertTrue(row[2] == campaign_name, 'Incorrect campaign name found: ' + row[2])
                            self.assertTrue(row[3] == data.pstn_qual_numbers["number%s" % str(count-1)]['country'], 'Incorrect country found: ' + row[3])
                            self.assertTrue(row[4] == data.pstn_qual_numbers["number%s" % str(count-1)]['type'], 'Incorrect number-type found: ' + row[4])
                            self.assertTrue(row[5] == number_str + '_customer', 'Incorrect customer found: ' + row[5])
                            self.assertTrue(row[6] == number_str + '_department', 'Incorrect department found: ' + row[6])
                            self.assertTrue(row[7] == number_str + '_location', 'Incorrect location found: ' + row[7])
                            self.assertTrue(row[8] == number_str + '_carrier', 'Incorrect carrier found: ' + row[8])
                            self.assertTrue(row[10] == data.ivr_spearline_prompt, 'Incorrect IVR found: ' + row[10])
                            self.assertTrue(row[11] == str(call_start_time), 'Incorrect Start Time found: ' + row[11])
                            self.assertTrue(row[12] == str(call_end_time), 'Incorrect Call End Time found: ' + row[12])
                            self.assertTrue(row[13] == data.pstn_qual_numbers["number%s" % str(count-1)]['desc_name'], 'Incorrect state found: ' + row[13])
            finally:
                os.system('echo %s|sudo -S %s' % (data.sudo_password, 'rm ' + csv_file_name))
        finally:
            rh.delete_job_processing_data(job_details['id'], job_processing_table)
            rh.delete_item(token, "campaign", campaign_details["data"]["id"])
    test_campaign_job_report_dtmf_with_quality_and_cli_check_test_type.priority=1
    test_campaign_job_report_dtmf_with_quality_and_cli_check_test_type.test_area="dtmf_with_quality_and_cli_check_test_type"

    def test_campaign_job_report_fax_test_type(self):
        """ Campaign job completion report with Fax test-type
        """
        ##----------------- Add Fax test-type campaign -----------------##
        campaign_name = "test_campaign_"+str(int(time.time()))
        campaign_report_contact=[data.email_contact]
        provider=rh.get_random_resource(token, "provider")
        campaign_once_off_time = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M") + ":00"
        campaign_numbers, campaign_number_details = rh.get_campaign_numbers_info(data.pstn_qual_numbers)
        campaign_details = rh.add_campaign(token, name=campaign_name, test_type_id=data.fax_test_type_id, status=1, numbers=campaign_numbers, provider=[provider], report_interval_id=1, timezone_id=data.utc_timezone_id, campaign_once_off=str(campaign_once_off_time), campaign_report_contact_flag=True, campaign_report_contact=campaign_report_contact)
        try:
            campaign_number_update_val = (json.dumps(campaign_number_details), campaign_details["data"]["id"])
            campaign_number_update_query = "update campaign SET filter_string = %s WHERE id = %s"
            rh.execute_db_query(campaign_number_update_query, campaign_number_update_val)
            ##----------------- Add Campaign Job entry in Job table -----------------##
            campaign_job_insert_val = (data.company_id, campaign_details["data"]["id"], data.fax_test_type_id, campaign_name, campaign_once_off_time, json.dumps(campaign_number_details))
            campaign_job_insert_query = "insert into job (company_id, campaign_id, test_type_id, name, start_time, job_filter_string) values (%s, %s, %s, %s, %s ,%s)"
            rh.execute_db_query(campaign_job_insert_query, campaign_job_insert_val)
            job_detail_query = "select * from job where campaign_id = %s" % (campaign_details["data"]["id"])
            job_details = rh.execute_select_db_query(job_detail_query, table_name='job_table')
            print('-------job_details--------> ', job_details)
            ##----------------- Get Job Processing table according to Test-type -----------------##
            job_processing_table = rh.get_job_processing_table(data.fax_test_type_id)
            #----------------- Enter Job Processing entries -----------------##
            call_start_time = datetime.datetime.strptime(campaign_once_off_time,'%Y-%m-%d %H:%M:%S')
            call_end_time = call_start_time + timedelta(0,3)
            for key in data.pstn_qual_numbers:
                number = data.pstn_qual_numbers[key]
                campaign_job_processing_insert_val = (data.fax_test_type_id, job_details['id'], number['server_id'], number['id'], number['route_id'], data.cli, data.ivr_spearline_prompt_id, call_start_time, call_start_time, call_end_time, 1, number['desc_id'], call_start_time)
                campaign_job_processing_insert_query = "insert into " + job_processing_table + " (test_type_id,job_id,server_id,number_id,route_id,cli,ivr_traversal_id,call_start_time,call_connect_time,call_end_time,processing_complete,call_description_id,created_on) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            rh.execute_db_query(campaign_job_processing_insert_query, campaign_job_processing_insert_val)
            # Generate report for Fax test-type
            rh.generate_report(campaign_name, job_details["id"])
            try:
            # Fetch newly created campaign job completion report and verify it
                os.chdir(os.getcwd() + "/csv/")
                result = glob.glob(campaign_name + '*.csv')
                print('Newly fetched CSV report file: ', result[0])
                csv_file_name = result[0]
                csv_file_path = os.getcwd() + "/" + csv_file_name
                with open(csv_file_path, 'r') as file:
                    reader = csv.reader(file)
                    for count, row in enumerate(reader):
                        if count==0:
                            self.assertTrue(row[0] == campaign_name + ' Report', "Mismatch in campaign report title")
                        elif count==1:
                            self.assertTrue(row == data.fax_reports_header, "Mismatch in campaign report headers")
                        elif count>1:
                            number_str = str(data.pstn_qual_numbers["number%s" % str(count-1)]['number'])
                            self.assertTrue(len(row) == len(data.fax_reports_header), 'Data is not correct')
                            self.assertTrue(row[1] == number_str, 'Incorrect number found: ' + row[1])
                            self.assertTrue(row[2] == campaign_name, 'Incorrect campaign name found: ' + row[2])
                            self.assertTrue(row[3] == data.pstn_qual_numbers["number%s" % str(count-1)]['country'], 'Incorrect country found: ' + row[3])
                            self.assertTrue(row[4] == data.pstn_qual_numbers["number%s" % str(count-1)]['type'], 'Incorrect number-type found: ' + row[4])
                            self.assertTrue(row[5] == number_str + '_customer', 'Incorrect customer found: ' + row[5])
                            self.assertTrue(row[6] == number_str + '_department', 'Incorrect department found: ' + row[6])
                            self.assertTrue(row[7] == number_str + '_location', 'Incorrect location found: ' + row[7])
                            self.assertTrue(row[8] == number_str + '_carrier', 'Incorrect carrier found: ' + row[8])
                            self.assertTrue(row[10] == data.ivr_spearline_prompt, 'Incorrect IVR found: ' + row[10])
                            self.assertTrue(row[11] == data.pstn_qual_numbers["number%s" % str(count-1)]['desc_name'], 'Incorrect state found: ' + row[11])
            finally:
                os.system('echo %s|sudo -S %s' % (data.sudo_password, 'rm ' + csv_file_name))
        finally:
            rh.delete_job_processing_data(job_details['id'], job_processing_table)
            rh.delete_item(token, "campaign", campaign_details["data"]["id"])
    test_campaign_job_report_fax_test_type.priority=1
    test_campaign_job_report_fax_test_type.test_area="fax_test_type"

    def test_campaign_job_report_in_country_outbound_latency_test_type(self):
        """ Campaign job completion report with In Country Outbound Latency test-type
        """
        ##----------------- Add In Country Outbound Latency test-type campaign -----------------##
        campaign_name = "test_campaign_"+str(int(time.time()))
        campaign_report_contact=[data.email_contact]
        campaign_once_off_time = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M") + ":00"
        campaign_numbers, campaign_number_details = rh.get_campaign_numbers_info(data.pstn_qual_numbers)
        campaign_details = rh.add_campaign(token, name=campaign_name, test_type_id=data.in_country_outbound_latency_test_type_id, status=1, numbers=campaign_numbers,  report_interval_id=1, timezone_id=data.utc_timezone_id, campaign_once_off=str(campaign_once_off_time), campaign_report_contact_flag=True, campaign_report_contact=campaign_report_contact)
        try:
            ##----------------- Add Campaign Job entry in Job table -----------------##
            campaign_job_insert_val = (data.company_id, campaign_details["data"]["id"], data.in_country_outbound_latency_test_type_id, campaign_name, campaign_once_off_time, json.dumps(campaign_number_details))
            campaign_job_insert_query = "insert into job (company_id, campaign_id, test_type_id, name, start_time, job_filter_string) values (%s, %s, %s, %s, %s ,%s)"
            rh.execute_db_query(campaign_job_insert_query, campaign_job_insert_val)
            job_detail_query = "select * from job where campaign_id = %s" % (campaign_details["data"]["id"])
            job_details = rh.execute_select_db_query(job_detail_query, table_name='job_table')
            print('-------job_details--------> ', job_details)
            ##----------------- Get Job Processing table according to Test-type -----------------##
            job_processing_table = rh.get_job_processing_table(data.in_country_outbound_latency_test_type_id)
            ##----------------- Enter Job Processing entries -----------------##
            call_start_time = datetime.datetime.strptime(campaign_once_off_time,'%Y-%m-%d %H:%M:%S')
            call_end_time = call_start_time + timedelta(0,3)
            for key in data.pstn_qual_numbers:
                number = data.pstn_qual_numbers[key]
                campaign_job_processing_insert_val = (data.in_country_outbound_latency_test_type_id, job_details['id'], number['server_id'], number['id'], number['route_id'], data.cli, call_start_time, call_start_time, call_end_time, 1, number['desc_id'], call_start_time)
                campaign_job_processing_insert_query = "insert into " + job_processing_table + " (test_type_id,job_id,server_id,number_id,route_id,cli,call_start_time,call_connect_time,call_end_time,processing_complete,call_description_id,created_on) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                rh.execute_db_query(campaign_job_processing_insert_query, campaign_job_processing_insert_val)
            # Generate report for In Country Outbound Latency test-type
            rh.generate_report(campaign_name, job_details["id"])
            try:
                # Fetch newly created campaign job completion report and verify it
                os.chdir(os.getcwd() + "/csv/")
                result = glob.glob(campaign_name + '*.csv')
                print('Newly fetched CSV report file: ', result[0])
                csv_file_name = result[0]
                csv_file_path = os.getcwd() + "/" + csv_file_name
                with open(csv_file_path, 'r') as file:
                    reader = csv.reader(file)
                    for count, row in enumerate(reader):
                        if count==0:
                            self.assertTrue(row[0] == campaign_name + ' Report', "Mismatch in campaign report title")
                        elif count==1:
                            self.assertTrue(row == data.in_country_testtype_report_headers, "Mismatch in campaign report headers")
                        elif count>1:
                            number_str = str(data.pstn_qual_numbers["number%s" % str(count-1)]['number'])
                            self.assertTrue(len(row) == len(data.in_country_testtype_report_headers), 'Data is not correct')
                            self.assertTrue(row[1] == number_str, 'Incorrect number found: ' + row[1])
                            self.assertTrue(row[2] == campaign_name, 'Incorrect campaign name found: ' + row[2])
                            self.assertTrue(row[3] == data.pstn_qual_numbers["number%s" % str(count-1)]['country'], 'Incorrect country found: ' + row[3])
                            self.assertTrue(row[4] == data.pstn_qual_numbers["number%s" % str(count-1)]['type'], 'Incorrect number-type found: ' + row[4])
                            self.assertTrue(row[5] == number_str + '_customer', 'Incorrect customer found: ' + row[5])
                            self.assertTrue(row[6] == number_str + '_department', 'Incorrect department found: ' + row[6])
                            self.assertTrue(row[7] == number_str + '_location', 'Incorrect location found: ' + row[7])
                            self.assertTrue(row[8] == number_str + '_carrier', 'Incorrect carrier found: ' + row[8])
                            self.assertTrue(row[10] == data.ivr_spearline_prompt, 'Incorrect IVR found: ' + row[10])
                            self.assertTrue(row[11] == str(call_start_time), 'Incorrect Start Time found: ' + row[11])
                            self.assertTrue(row[12] == str(call_end_time), 'Incorrect Call End Time found: ' + row[12])
                            self.assertTrue(row[13] == data.pstn_qual_numbers["number%s" % str(count-1)]['desc_name'], 'Incorrect state found: ' + row[13])
            finally:
                os.system('echo %s|sudo -S %s' % (data.sudo_password, 'rm ' + csv_file_name))
        finally:
            rh.delete_job_processing_data(job_details['id'], job_processing_table)
            rh.delete_item(token, "campaign", campaign_details["data"]["id"])
    test_campaign_job_report_in_country_outbound_latency_test_type.priority=1
    test_campaign_job_report_in_country_outbound_latency_test_type.test_area="in_country_outbound_latency_test_type"

    def test_campaign_job_report_in_country_outbound_two_way_voice_assure_test_type(self):
        """ Campaign job completion report with In Country Outbound Two Way Voice Assure test-type
        """
        ##----------------- Add In Country Outbound Two Way Voice Assure test-type campaign -----------------##
        campaign_name = "test_campaign_"+str(int(time.time()))
        campaign_report_contact=[data.email_contact]
        campaign_once_off_time = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M") + ":00"
        campaign_numbers, campaign_number_details = rh.get_campaign_numbers_info(data.pstn_qual_numbers)
        campaign_details = rh.add_campaign(token, name=campaign_name, test_type_id=data.in_country_outbound_two_way_voice_assure_test_type_id, status=1, numbers=campaign_numbers,  report_interval_id=1, timezone_id=data.utc_timezone_id, campaign_once_off=str(campaign_once_off_time), campaign_report_contact_flag=True, campaign_report_contact=campaign_report_contact)
        try:
            ##----------------- Add Campaign Job entry in Job table -----------------##
            campaign_job_insert_val = (data.company_id, campaign_details["data"]["id"], data.in_country_outbound_two_way_voice_assure_test_type_id, campaign_name, campaign_once_off_time, json.dumps(campaign_number_details))
            campaign_job_insert_query = "insert into job (company_id, campaign_id, test_type_id, name, start_time, job_filter_string) values (%s, %s, %s, %s, %s ,%s)"
            rh.execute_db_query(campaign_job_insert_query, campaign_job_insert_val)
            job_detail_query = "select * from job where campaign_id = %s" % (campaign_details["data"]["id"])
            job_details = rh.execute_select_db_query(job_detail_query, table_name='job_table')
            print('-------job_details--------> ', job_details)
            ##----------------- Get Job Processing table according to Test-type -----------------##
            job_processing_table = rh.get_job_processing_table(data.in_country_outbound_two_way_voice_assure_test_type_id)
            ##----------------- Enter Job Processing entries -----------------##
            call_start_time = datetime.datetime.strptime(campaign_once_off_time,'%Y-%m-%d %H:%M:%S')
            call_end_time = call_start_time + timedelta(0,3)
            for key in data.pstn_qual_numbers:
                number = data.pstn_qual_numbers[key]
                campaign_job_processing_insert_val = (data.in_country_outbound_two_way_voice_assure_test_type_id, job_details['id'], number['server_id'], number['id'], number['route_id'], data.cli, call_start_time, call_start_time, call_end_time, 1, number['desc_id'], call_start_time)
                campaign_job_processing_insert_query = "insert into " + job_processing_table + " (test_type_id,job_id,server_id,number_id,route_id,cli,call_start_time,call_connect_time,call_end_time,processing_complete,call_description_id,created_on) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                rh.execute_db_query(campaign_job_processing_insert_query, campaign_job_processing_insert_val)
            # Generate report for In Country Outbound Two Way Voice Assure test-type
            rh.generate_report(campaign_name, job_details["id"])
            try:
                # Fetch newly created campaign job completion report and verify it
                os.chdir(os.getcwd() + "/csv/")
                result = glob.glob(campaign_name + '*.csv')
                print('Newly fetched CSV report file: ', result[0])
                csv_file_name = result[0]
                csv_file_path = os.getcwd() + "/" + csv_file_name
                with open(csv_file_path, 'r') as file:
                    reader = csv.reader(file)
                    for count, row in enumerate(reader):
                        if count==0:
                            self.assertTrue(row[0] == campaign_name + ' Report', "Mismatch in campaign report title")
                        elif count==1:
                            self.assertTrue(row == data.in_country_testtype_report_headers, "Mismatch in campaign report headers")
                        elif count>1:
                            number_str = str(data.pstn_qual_numbers["number%s" % str(count-1)]['number'])
                            self.assertTrue(len(row) == len(data.in_country_testtype_report_headers), 'Data is not correct')
                            self.assertTrue(row[1] == number_str, 'Incorrect number found: ' + row[1])
                            self.assertTrue(row[2] == campaign_name, 'Incorrect campaign name found: ' + row[2])
                            self.assertTrue(row[3] == data.pstn_qual_numbers["number%s" % str(count-1)]['country'], 'Incorrect country found: ' + row[3])
                            self.assertTrue(row[4] == data.pstn_qual_numbers["number%s" % str(count-1)]['type'], 'Incorrect number-type found: ' + row[4])
                            self.assertTrue(row[5] == number_str + '_customer', 'Incorrect customer found: ' + row[5])
                            self.assertTrue(row[6] == number_str + '_department', 'Incorrect department found: ' + row[6])
                            self.assertTrue(row[7] == number_str + '_location', 'Incorrect location found: ' + row[7])
                            self.assertTrue(row[8] == number_str + '_carrier', 'Incorrect carrier found: ' + row[8])
                            self.assertTrue(row[10] == data.ivr_spearline_prompt, 'Incorrect IVR found: ' + row[10])
                            self.assertTrue(row[11] == str(call_start_time), 'Incorrect Start Time found: ' + row[11])
                            self.assertTrue(row[12] == str(call_end_time), 'Incorrect Call End Time found: ' + row[12])
                            self.assertTrue(row[13] == data.pstn_qual_numbers["number%s" % str(count-1)]['desc_name'], 'Incorrect state found: ' + row[13])
            finally:
                os.system('echo %s|sudo -S %s' % (data.sudo_password, 'rm ' + csv_file_name))
        finally:
            rh.delete_job_processing_data(job_details['id'], job_processing_table)
            rh.delete_item(token, "campaign", campaign_details["data"]["id"])
    test_campaign_job_report_in_country_outbound_two_way_voice_assure_test_type.priority=1
    test_campaign_job_report_in_country_outbound_two_way_voice_assure_test_type.test_area="in_country_outbound_two_way_voice_assure_test_type"

    def test_campaign_job_report_in_country_mobile_test_type(self):
        """ Campaign job completion report with In Country Mobile test-type
        """
        ##----------------- Add In Country Mobile test-type campaign -----------------##
        campaign_name = "test_campaign_"+str(int(time.time()))
        campaign_report_contact=[data.email_contact]
        provider=rh.get_random_resource(token, "provider")
        campaign_once_off_time = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M") + ":00"
        campaign_numbers, campaign_number_details = rh.get_campaign_numbers_info(data.pstn_qual_numbers)
        campaign_details = rh.add_campaign(token, name=campaign_name, test_type_id=data.in_country_mobile_test_type_id, status=1, numbers=campaign_numbers,  report_interval_id=1, timezone_id=data.utc_timezone_id, provider=[provider], campaign_once_off=str(campaign_once_off_time), campaign_report_contact_flag=True, campaign_report_contact=campaign_report_contact)
        try:
            ##----------------- Add Campaign Job entry in Job table -----------------##
            campaign_job_insert_val = (data.company_id, campaign_details["data"]["id"], data.in_country_mobile_test_type_id, campaign_name, campaign_once_off_time, json.dumps(campaign_number_details))
            campaign_job_insert_query = "insert into job (company_id, campaign_id, test_type_id, name, start_time, job_filter_string) values (%s, %s, %s, %s, %s ,%s)"
            rh.execute_db_query(campaign_job_insert_query, campaign_job_insert_val)
            job_detail_query = "select * from job where campaign_id = %s" % (campaign_details["data"]["id"])
            job_details = rh.execute_select_db_query(job_detail_query, table_name='job_table')
            print('-------job_details--------> ', job_details)
            ##----------------- Get Job Processing table according to Test-type -----------------##
            job_processing_table = rh.get_job_processing_table(data.in_country_mobile_test_type_id)
            ##----------------- Enter Job Processing entries -----------------##
            call_start_time = datetime.datetime.strptime(campaign_once_off_time,'%Y-%m-%d %H:%M:%S')
            call_end_time = call_start_time + timedelta(0,3)
            for key in data.pstn_qual_numbers:
                number = data.pstn_qual_numbers[key]
                campaign_job_processing_insert_val = (data.in_country_mobile_test_type_id, job_details['id'], number['server_id'], number['id'], number['route_id'], data.cli, data.ivr_spearline_prompt_id, call_start_time, call_start_time, call_end_time, 1, number['desc_id'], call_start_time)
                campaign_job_processing_insert_query = "insert into " + job_processing_table + " (test_type_id,job_id,server_id,number_id,route_id,cli,ivr_traversal_id,call_start_time,call_connect_time,call_end_time,processing_complete,call_description_id,created_on) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                rh.execute_db_query(campaign_job_processing_insert_query, campaign_job_processing_insert_val)
            # Generate report for In Country Mobile test-type
            rh.generate_report(campaign_name, job_details["id"])
            try:
                # Fetch newly created campaign job completion report and verify it
                os.chdir(os.getcwd() + "/csv/")
                result = glob.glob(campaign_name + '*.csv')
                print('Newly fetched CSV report file: ', result[0])
                csv_file_name = result[0]
                csv_file_path = os.getcwd() + "/" + csv_file_name
                with open(csv_file_path, 'r') as file:
                    reader = csv.reader(file)
                    for count, row in enumerate(reader):
                        if count==0:
                            self.assertTrue(row[0] == campaign_name + ' Report', "Mismatch in campaign report title")
                        elif count==1:
                            self.assertTrue(row == data.in_country_testtype_report_headers, "Mismatch in campaign report headers")
                        elif count>1:
                            number_str = str(data.pstn_qual_numbers["number%s" % str(count-1)]['number'])
                            self.assertTrue(len(row) == len(data.in_country_testtype_report_headers), 'Data is not correct')
                            self.assertTrue(row[1] == number_str, 'Incorrect number found: ' + row[1])
                            self.assertTrue(row[2] == campaign_name, 'Incorrect campaign name found: ' + row[2])
                            self.assertTrue(row[3] == data.pstn_qual_numbers["number%s" % str(count-1)]['country'], 'Incorrect country found: ' + row[3])
                            self.assertTrue(row[4] == data.pstn_qual_numbers["number%s" % str(count-1)]['type'], 'Incorrect number-type found: ' + row[4])
                            self.assertTrue(row[5] == number_str + '_customer', 'Incorrect customer found: ' + row[5])
                            self.assertTrue(row[6] == number_str + '_department', 'Incorrect department found: ' + row[6])
                            self.assertTrue(row[7] == number_str + '_location', 'Incorrect location found: ' + row[7])
                            self.assertTrue(row[8] == number_str + '_carrier', 'Incorrect carrier found: ' + row[8])
                            self.assertTrue(row[10] == data.ivr_spearline_prompt, 'Incorrect IVR found: ' + row[10])
                            self.assertTrue(row[11] == str(call_start_time), 'Incorrect Start Time found: ' + row[11])
                            self.assertTrue(row[12] == str(call_end_time), 'Incorrect Call End Time found: ' + row[12])
                            self.assertTrue(row[13] == data.pstn_qual_numbers["number%s" % str(count-1)]['desc_name'], 'Incorrect state found: ' + row[13])
            finally:
                os.system('echo %s|sudo -S %s' % (data.sudo_password, 'rm ' + csv_file_name))
        finally:
            rh.delete_job_processing_data(job_details['id'], job_processing_table)
            rh.delete_item(token, "campaign", campaign_details["data"]["id"])
    test_campaign_job_report_in_country_mobile_test_type.priority=1
    test_campaign_job_report_in_country_mobile_test_type.test_area="in_country_mobile_test_type"

    def test_campaign_job_report_in_country_pstn_echo_test_with_quality_test_type(self):
        """ Campaign job completion report with In-country PSTN Echo test with Quality test-type
        """
        ##----------------- Add In-country PSTN Echo test with Quality test-type campaign -----------------##
        campaign_name = "test_campaign_"+str(int(time.time()))
        campaign_report_contact=[data.email_contact]
        campaign_once_off_time = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M") + ":00"
        campaign_numbers, campaign_number_details = rh.get_campaign_numbers_info(data.pstn_qual_numbers)
        campaign_details = rh.add_campaign(token, name=campaign_name, test_type_id=data.in_country_pstn_echo_test_with_quality_test_type_id, status=1, numbers=campaign_numbers,  report_interval_id=1, timezone_id=data.utc_timezone_id, campaign_once_off=str(campaign_once_off_time), campaign_report_contact_flag=True, campaign_report_contact=campaign_report_contact)
        try:
            ##----------------- Add Campaign Job entry in Job table -----------------##
            campaign_job_insert_val = (data.company_id, campaign_details["data"]["id"], data.in_country_pstn_echo_test_with_quality_test_type_id, campaign_name, campaign_once_off_time, json.dumps(campaign_number_details))
            campaign_job_insert_query = "insert into job (company_id, campaign_id, test_type_id, name, start_time, job_filter_string) values (%s, %s, %s, %s, %s ,%s)"
            rh.execute_db_query(campaign_job_insert_query, campaign_job_insert_val)
            job_detail_query = "select * from job where campaign_id = %s" % (campaign_details["data"]["id"])
            job_details = rh.execute_select_db_query(job_detail_query, table_name='job_table')
            print('-------job_details--------> ', job_details)
            ##----------------- Get Job Processing table according to Test-type -----------------##
            job_processing_table = rh.get_job_processing_table(data.in_country_pstn_echo_test_with_quality_test_type_id)
            ##----------------- Enter Job Processing entries -----------------##
            call_start_time = datetime.datetime.strptime(campaign_once_off_time,'%Y-%m-%d %H:%M:%S')
            call_end_time = call_start_time + timedelta(0,3)
            for key in data.pstn_qual_numbers:
                number = data.pstn_qual_numbers[key]
                campaign_job_processing_insert_val = (data.in_country_pstn_echo_test_with_quality_test_type_id, job_details['id'], number['server_id'], number['id'], number['route_id'], data.cli, data.ivr_spearline_prompt_id, call_start_time, call_start_time, call_end_time, 1, number['desc_id'], 1, call_start_time)
                campaign_job_processing_insert_query = "insert into " + job_processing_table + " (test_type_id,job_id,server_id,number_id,route_id,cli,ivr_traversal_id,call_start_time,call_connect_time,call_end_time,processing_complete,call_description_id,tone_description,created_on) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                rh.execute_db_query(campaign_job_processing_insert_query, campaign_job_processing_insert_val)
            # Generate report for In-country PSTN Echo test with Quality test-type
            rh.generate_report(campaign_name, job_details["id"])
            try:
                # Fetch newly created campaign job completion report and verify it
                os.chdir(os.getcwd() + "/csv/")
                result = glob.glob(campaign_name + '*.csv')
                print('Newly fetched CSV report file: ', result[0])
                csv_file_name = result[0]
                csv_file_path = os.getcwd() + "/" + csv_file_name
                with open(csv_file_path, 'r') as file:
                    reader = csv.reader(file)
                    for count, row in enumerate(reader):
                        if count==0:
                            self.assertTrue(row[0] == campaign_name + ' Report', "Mismatch in campaign report title")
                        elif count==1:
                            self.assertTrue(row == data.in_country_testtype_report_headers, "Mismatch in campaign report headers")
                        elif count>1:
                            number_str = str(data.pstn_qual_numbers["number%s" % str(count-1)]['number'])
                            self.assertTrue(len(row) == len(data.in_country_testtype_report_headers), 'Data is not correct')
                            self.assertTrue(row[1] == number_str, 'Incorrect number found: ' + row[1])
                            self.assertTrue(row[2] == campaign_name, 'Incorrect campaign name found: ' + row[2])
                            self.assertTrue(row[3] == data.pstn_qual_numbers["number%s" % str(count-1)]['country'], 'Incorrect country found: ' + row[3])
                            self.assertTrue(row[4] == data.pstn_qual_numbers["number%s" % str(count-1)]['type'], 'Incorrect number-type found: ' + row[4])
                            self.assertTrue(row[5] == number_str + '_customer', 'Incorrect customer found: ' + row[5])
                            self.assertTrue(row[6] == number_str + '_department', 'Incorrect department found: ' + row[6])
                            self.assertTrue(row[7] == number_str + '_location', 'Incorrect location found: ' + row[7])
                            self.assertTrue(row[8] == number_str + '_carrier', 'Incorrect carrier found: ' + row[8])
                            self.assertTrue(row[10] == data.ivr_spearline_prompt, 'Incorrect IVR found: ' + row[10])
                            self.assertTrue(row[11] == str(call_start_time), 'Incorrect Start Time found: ' + row[11])
                            self.assertTrue(row[12] == str(call_end_time), 'Incorrect Call End Time found: ' + row[12])
                            self.assertTrue(row[13] == data.pstn_qual_numbers["number%s" % str(count-1)]['desc_name'], 'Incorrect state found: ' + row[13])
            finally:
                os.system('echo %s|sudo -S %s' % (data.sudo_password, 'rm ' + csv_file_name))
        finally:
            rh.delete_job_processing_data(job_details['id'], job_processing_table)
            rh.delete_item(token, "campaign", campaign_details["data"]["id"])
    test_campaign_job_report_in_country_pstn_echo_test_with_quality_test_type.priority=1
    test_campaign_job_report_in_country_pstn_echo_test_with_quality_test_type.test_area="in_country_pstn_echo_test_with_quality_test_type"

    def test_campaign_job_report_international_connection_test_type(self):
        """ Campaign job completion report with International Connection test-type
        """
        ##----------------- Add International Connection test-type campaign -----------------##
        campaign_name = "test_campaign_"+str(int(time.time()))
        campaign_report_contact=[data.email_contact]
        campaign_once_off_time = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M") + ":00"
        campaign_numbers, campaign_number_details = rh.get_campaign_numbers_info(data.pstn_qual_numbers)
        campaign_details = rh.add_campaign(token, name=campaign_name, test_type_id=data.international_connection_test_type_id, status=1, numbers=campaign_numbers, report_interval_id=1, timezone_id=data.utc_timezone_id, campaign_once_off=str(campaign_once_off_time), campaign_report_contact_flag=True, campaign_report_contact=campaign_report_contact)
        try:
            campaign_number_update_val = (json.dumps(campaign_number_details), campaign_details["data"]["id"])
            campaign_number_update_query = "update campaign SET filter_string = %s WHERE id = %s"
            rh.execute_db_query(campaign_number_update_query, campaign_number_update_val)
            ##----------------- Add Campaign Job entry in Job table -----------------##
            campaign_job_insert_val = (data.company_id, campaign_details["data"]["id"], data.international_connection_test_type_id, campaign_name, campaign_once_off_time, json.dumps(campaign_number_details))
            campaign_job_insert_query = "insert into job (company_id, campaign_id, test_type_id, name, start_time, job_filter_string) values (%s, %s, %s, %s, %s ,%s)"
            rh.execute_db_query(campaign_job_insert_query, campaign_job_insert_val)
            job_detail_query = "select * from job where campaign_id = %s" % (campaign_details["data"]["id"])
            job_details = rh.execute_select_db_query(job_detail_query, table_name='job_table')
            print('-------job_details--------> ', job_details)
            ##----------------- Get Job Processing table according to Test-type -----------------##
            job_processing_table = rh.get_job_processing_table(data.international_connection_test_type_id)
            ##----------------- Enter Job Processing entries -----------------##
            call_start_time = datetime.datetime.strptime(campaign_once_off_time,'%Y-%m-%d %H:%M:%S')
            call_end_time = call_start_time + timedelta(0,3)
            for key in data.pstn_qual_numbers:
                number = data.pstn_qual_numbers[key]
                campaign_job_processing_insert_val = (data.international_connection_test_type_id, job_details['id'], number['server_id'], number['id'], number['route_id'], data.cli, data.ivr_spearline_prompt_id, call_start_time, call_start_time, call_end_time, 1, number['desc_id'], call_start_time)
                campaign_job_processing_insert_query = "insert into " + job_processing_table + " (test_type_id,job_id,server_id,number_id,route_id,cli,ivr_traversal_id,call_start_time,call_connect_time,call_end_time,processing_complete,call_description_id,created_on) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                rh.execute_db_query(campaign_job_processing_insert_query, campaign_job_processing_insert_val)
            # Generate report for International Connection test-type
            rh.generate_report(campaign_name, job_details["id"])
            try:
                # Fetch newly created campaign job completion report and verify it
                os.chdir(os.getcwd() + "/csv/")
                result = glob.glob(campaign_name + '*.csv')
                print('Newly fetched CSV report file: ', result[0])
                csv_file_name = result[0]
                csv_file_path = os.getcwd() + "/" + csv_file_name
                with open(csv_file_path, 'r') as file:
                    reader = csv.reader(file)
                    for count, row in enumerate(reader):
                        if count==0:
                            self.assertTrue(row[0] == campaign_name + ' Report', "Mismatch in campaign report title")
                        elif count==1:
                            self.assertTrue(row == data.connection_testtype_report_headers, "Mismatch in campaign report headers")
                        elif count>1:
                            number_str = str(data.pstn_qual_numbers["number%s" % str(count-1)]['number'])
                            self.assertTrue(len(row) == len(data.connection_testtype_report_headers), 'Data is not correct')
                            self.assertTrue(row[1] == number_str, 'Incorrect number found: ' + row[1])
                            self.assertTrue(row[2] == campaign_name, 'Incorrect campaign name found: ' + row[2])
                            self.assertTrue(row[3] == data.pstn_qual_numbers["number%s" % str(count-1)]['country'], 'Incorrect country found: ' + row[3])
                            self.assertTrue(row[4] == data.pstn_qual_numbers["number%s" % str(count-1)]['type'], 'Incorrect number-type found: ' + row[4])
                            self.assertTrue(row[5] == number_str + '_customer', 'Incorrect customer found: ' + row[5])
                            self.assertTrue(row[6] == number_str + '_department', 'Incorrect department found: ' + row[6])
                            self.assertTrue(row[7] == number_str + '_location', 'Incorrect location found: ' + row[7])
                            self.assertTrue(row[8] == number_str + '_carrier', 'Incorrect carrier found: ' + row[8])
                            self.assertTrue(row[10] == data.ivr_spearline_prompt, 'Incorrect IVR found: ' + row[10])
                            self.assertTrue(row[11] == str(call_start_time), 'Incorrect Start Time found: ' + row[11])
                            self.assertTrue(row[12] == str(call_end_time), 'Incorrect Call End Time found: ' + row[12])
                            self.assertTrue(row[13] == data.pstn_qual_numbers["number%s" % str(count-1)]['desc_name'], 'Incorrect state found: ' + row[13])
            finally:
                os.system('echo %s|sudo -S %s' % (data.sudo_password, 'rm ' + csv_file_name))
        finally:
            rh.delete_job_processing_data(job_details['id'], job_processing_table)
            rh.delete_item(token, "campaign", campaign_details["data"]["id"])
    test_campaign_job_report_international_connection_test_type.priority=1
    test_campaign_job_report_international_connection_test_type.test_area="international_connection_test_type"

    def test_campaign_job_report_international_dial_test_type(self):
        """ Campaign job completion report with International Dial test-type
        """
        ##----------------- Add International Dial test-type campaign -----------------##
        campaign_name = "test_campaign_"+str(int(time.time()))
        campaign_report_contact=[data.email_contact]
        campaign_once_off_time = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M") + ":00"
        campaign_numbers, campaign_number_details = rh.get_campaign_numbers_info(data.pstn_qual_numbers)
        campaign_details = rh.add_campaign(token, name=campaign_name, test_type_id=data.international_dial_test_type_id, status=1, numbers=campaign_numbers, report_interval_id=1, timezone_id=data.utc_timezone_id, campaign_once_off=str(campaign_once_off_time), campaign_report_contact_flag=True, campaign_report_contact=campaign_report_contact)
        try:
            campaign_number_update_val = (json.dumps(campaign_number_details), campaign_details["data"]["id"])
            campaign_number_update_query = "update campaign SET filter_string = %s WHERE id = %s"
            rh.execute_db_query(campaign_number_update_query, campaign_number_update_val)
            ##----------------- Add Campaign Job entry in Job table -----------------##
            campaign_job_insert_val = (data.company_id, campaign_details["data"]["id"], data.international_dial_test_type_id, campaign_name, campaign_once_off_time, json.dumps(campaign_number_details))
            campaign_job_insert_query = "insert into job (company_id, campaign_id, test_type_id, name, start_time, job_filter_string) values (%s, %s, %s, %s, %s ,%s)"
            rh.execute_db_query(campaign_job_insert_query, campaign_job_insert_val)
            job_detail_query = "select * from job where campaign_id = %s" % (campaign_details["data"]["id"])
            job_details = rh.execute_select_db_query(job_detail_query, table_name='job_table')
            print('-------job_details--------> ', job_details)
            ##----------------- Get Job Processing table according to Test-type -----------------##
            job_processing_table = rh.get_job_processing_table(data.international_dial_test_type_id)
            ##----------------- Enter Job Processing entries -----------------##
            call_start_time = datetime.datetime.strptime(campaign_once_off_time,'%Y-%m-%d %H:%M:%S')
            call_end_time = call_start_time + timedelta(0,3)
            for key in data.pstn_qual_numbers:
                number = data.pstn_qual_numbers[key]
                campaign_job_processing_insert_val = (data.international_dial_test_type_id, job_details['id'], number['server_id'], number['id'], number['route_id'], data.cli, data.ivr_spearline_prompt_id, call_start_time, call_start_time, call_end_time, 1, number['desc_id'], call_start_time)
                campaign_job_processing_insert_query = "insert into " + job_processing_table + " (test_type_id,job_id,server_id,number_id,route_id,cli,ivr_traversal_id,call_start_time,call_connect_time,call_end_time,processing_complete,call_description_id,created_on) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                rh.execute_db_query(campaign_job_processing_insert_query, campaign_job_processing_insert_val)
            # Generate report for International Dial test-type
            rh.generate_report(campaign_name, job_details["id"])
            try:
                # Fetch newly created campaign job completion report and verify it
                os.chdir(os.getcwd() + "/csv/")
                result = glob.glob(campaign_name + '*.csv')
                print('Newly fetched CSV report file: ', result[0])
                csv_file_name = result[0]
                csv_file_path = os.getcwd() + "/" + csv_file_name
                with open(csv_file_path, 'r') as file:
                    reader = csv.reader(file)
                    for count, row in enumerate(reader):
                        if count==0:
                            self.assertTrue(row[0] == campaign_name + ' Report', "Mismatch in campaign report title")
                        elif count==1:
                            self.assertTrue(row == data.international_dial_test_reports_header, "Mismatch in campaign report headers")
                        elif count>1:
                            number_str = str(data.pstn_qual_numbers["number%s" % str(count-1)]['number'])
                            self.assertTrue(len(row) == len(data.international_dial_test_reports_header), 'Data is not correct')
                            self.assertTrue(row[1] == number_str, 'Incorrect number found: ' + row[1])
                            self.assertTrue(row[2] == campaign_name, 'Incorrect campaign name found: ' + row[2])
                            self.assertTrue(row[3] == data.pstn_qual_numbers["number%s" % str(count-1)]['country'], 'Incorrect country found: ' + row[3])
                            self.assertTrue(row[4] == data.pstn_qual_numbers["number%s" % str(count-1)]['type'], 'Incorrect number-type found: ' + row[4])
                            self.assertTrue(row[5] == number_str + '_customer', 'Incorrect customer found: ' + row[5])
                            self.assertTrue(row[6] == number_str + '_department', 'Incorrect department found: ' + row[6])
                            self.assertTrue(row[7] == number_str + '_location', 'Incorrect location found: ' + row[7])
                            self.assertTrue(row[8] == number_str + '_carrier', 'Incorrect carrier found: ' + row[8])
                            self.assertTrue(row[10] == data.ivr_spearline_prompt, 'Incorrect IVR found: ' + row[10])
                            self.assertTrue(row[11] == str(call_start_time), 'Incorrect Start Time found: ' + row[11])
                            self.assertTrue(row[12] == str(call_end_time), 'Incorrect Call End Time found: ' + row[12])
                            self.assertTrue(row[13] == data.pstn_qual_numbers["number%s" % str(count-1)]['desc_name'], 'Incorrect state found: ' + row[13])
            finally:
                os.system('echo %s|sudo -S %s' % (data.sudo_password, 'rm ' + csv_file_name))
        finally:
            rh.delete_job_processing_data(job_details['id'], job_processing_table)
            rh.delete_item(token, "campaign", campaign_details["data"]["id"])
    test_campaign_job_report_international_dial_test_type.priority=1
    test_campaign_job_report_international_dial_test_type.test_area="international_dial_test_type"

    def test_campaign_job_report_international_pstn_echo_test_type(self):
        """ Campaign job completion report with International PSTN Echo test test-type
        """
        ##----------------- Add International PSTN Echo test test-type campaign -----------------##
        campaign_name = "test_campaign_"+str(int(time.time()))
        campaign_report_contact=[data.email_contact]
        campaign_once_off_time = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M") + ":00"
        campaign_numbers, campaign_number_details = rh.get_campaign_numbers_info(data.pstn_qual_numbers)
        campaign_details = rh.add_campaign(token, name=campaign_name, test_type_id=data.international_pstn_echo_test_type_id, status=1, numbers=campaign_numbers,  report_interval_id=1, timezone_id=data.utc_timezone_id, campaign_once_off=str(campaign_once_off_time), campaign_report_contact_flag=True, campaign_report_contact=campaign_report_contact)
        try:
            ##----------------- Add Campaign Job entry in Job table -----------------##
            campaign_job_insert_val = (data.company_id, campaign_details["data"]["id"], data.international_pstn_echo_test_type_id, campaign_name, campaign_once_off_time, json.dumps(campaign_number_details))
            campaign_job_insert_query = "insert into job (company_id, campaign_id, test_type_id, name, start_time, job_filter_string) values (%s, %s, %s, %s, %s ,%s)"
            rh.execute_db_query(campaign_job_insert_query, campaign_job_insert_val)
            job_detail_query = "select * from job where campaign_id = %s" % (campaign_details["data"]["id"])
            job_details = rh.execute_select_db_query(job_detail_query, table_name='job_table')
            print('-------job_details--------> ', job_details)
            ##----------------- Get Job Processing table according to Test-type -----------------##
            job_processing_table = rh.get_job_processing_table(data.international_pstn_echo_test_type_id)
            ##----------------- Enter Job Processing entries -----------------##
            call_start_time = datetime.datetime.strptime(campaign_once_off_time,'%Y-%m-%d %H:%M:%S')
            call_end_time = call_start_time + timedelta(0,3)
            for key in data.pstn_qual_numbers:
                number = data.pstn_qual_numbers[key]
                campaign_job_processing_insert_val = (data.international_pstn_echo_test_type_id, job_details['id'], number['server_id'], number['id'], number['route_id'], data.cli, data.ivr_spearline_prompt_id, call_start_time, call_start_time, call_end_time, 1, number['desc_id'], 1, call_start_time)
                campaign_job_processing_insert_query = "insert into " + job_processing_table + " (test_type_id,job_id,server_id,number_id,route_id,cli,ivr_traversal_id,call_start_time,call_connect_time,call_end_time,processing_complete,call_description_id,tone_description,created_on) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                rh.execute_db_query(campaign_job_processing_insert_query, campaign_job_processing_insert_val)
            # Generate report for International PSTN Echo test test-type
            rh.generate_report(campaign_name, job_details["id"])
            try:
                # Fetch newly created campaign job completion report and verify it
                os.chdir(os.getcwd() + "/csv/")
                result = glob.glob(campaign_name + '*.csv')
                print('Newly fetched CSV report file: ', result[0])
                csv_file_name = result[0]
                csv_file_path = os.getcwd() + "/" + csv_file_name
                with open(csv_file_path, 'r') as file:
                    reader = csv.reader(file)
                    for count, row in enumerate(reader):
                        if count==0:
                            self.assertTrue(row[0] == campaign_name + ' Report', "Mismatch in campaign report title")
                        elif count==1:
                            self.assertTrue(row == data.audio_latency_testtype_report_headers, "Mismatch in campaign report headers")
                        elif count>1:
                            number_str = str(data.pstn_qual_numbers["number%s" % str(count-1)]['number'])
                            self.assertTrue(len(row) == len(data.audio_latency_testtype_report_headers), 'Data is not correct')
                            self.assertTrue(row[1] == number_str, 'Incorrect number found: ' + row[1])
                            self.assertTrue(row[2] == campaign_name, 'Incorrect campaign name found: ' + row[2])
                            self.assertTrue(row[3] == data.pstn_qual_numbers["number%s" % str(count-1)]['country'], 'Incorrect country found: ' + row[3])
                            self.assertTrue(row[4] == data.pstn_qual_numbers["number%s" % str(count-1)]['type'], 'Incorrect number-type found: ' + row[4])
                            self.assertTrue(row[5] == number_str + '_customer', 'Incorrect customer found: ' + row[5])
                            self.assertTrue(row[6] == number_str + '_department', 'Incorrect department found: ' + row[6])
                            self.assertTrue(row[7] == number_str + '_location', 'Incorrect location found: ' + row[7])
                            self.assertTrue(row[8] == number_str + '_carrier', 'Incorrect carrier found: ' + row[8])
                            self.assertTrue(row[10] == data.ivr_spearline_prompt, 'Incorrect IVR found: ' + row[10])
                            self.assertTrue(row[11] == data.pstn_qual_numbers["number%s" % str(count-1)]['desc_name'], 'Incorrect call description found: ' + row[11])
            finally:
                os.system('echo %s|sudo -S %s' % (data.sudo_password, 'rm ' + csv_file_name))
        finally:
            rh.delete_job_processing_data(job_details['id'], job_processing_table)
            rh.delete_item(token, "campaign", campaign_details["data"]["id"])
    test_campaign_job_report_international_pstn_echo_test_type.priority=1
    test_campaign_job_report_international_pstn_echo_test_type.test_area="international_pstn_echo_test_type"
