from csv import DictWriter
from csv import DictReader
import os.path
import hashlib 
from tempfile import NamedTemporaryFile
import shutil

### file names ###

config_file_name = 'config.csv'
config_field_names = ['user_name','password','user_type','privilege_level']

data_file_name = 'data.csv'
data_field_names = ['record_id','user_name','personal_details','sickeness_details','drug_prescriptions','lab_test_prescriptions']

tempfile = NamedTemporaryFile(mode='w+t',delete=False,newline='')

### user types and privilege levels ###

main_user_types = ['patient', 'hospital staff']
privileged_user_types = ['lab staff', 'pharmacy staff', 'nurse', 'doctor']

privilege_levels = ['patient', 'lab staff', 'pharmacy staff', 'nurse', 'doctor']

### mapping of privileges to privilege levels ###

read_privileges = {
    'patient' : ['record_id','user_name','personal_details','sickeness_details','drug_prescriptions','lab_test_prescriptions'], 
    'lab staff' : ['record_id','user_name','personal_details','lab_test_prescriptions'], 
    'pharmacy staff' : ['record_id','user_name','personal_details','drug_prescriptions'], 
    'nurse' : ['record_id','user_name','personal_details','sickeness_details','drug_prescriptions','lab_test_prescriptions'], 
    'doctor' : ['record_id','user_name','personal_details','sickeness_details','drug_prescriptions','lab_test_prescriptions']
}

write_privileges = {
    'patient' : [], 
    'lab staff' : [], 
    'pharmacy staff' : [], 
    'nurse' : ['record_id','user_name','personal_details'], 
    'doctor' : ['record_id','user_name','personal_details','sickeness_details','drug_prescriptions','lab_test_prescriptions']
}

edit_privileges = {
    'patient' : [], 
    'lab staff' : [], 
    'pharmacy staff' : [], 
    'nurse' : ['personal_details'], 
    'doctor' : ['personal_details','sickeness_details','drug_prescriptions','lab_test_prescriptions']
}

allowed_actions = {
    'patient' : ['view my records'], 
    'lab staff' : ['view all records', 'view all records by user name', 'view record by id'], 
    'pharmacy staff' : ['view all records', 'view all records by user name', 'view record by id'], 
    'nurse' : ['view all records', 'view all records by user name', 'view record by id', 'add new record', 'edit record'], 
    'doctor' : ['view all records', 'view all records by user name', 'view record by id', 'add new record', 'edit record'],
}

### helper functions ###

def append_dict_as_row(file_name, dict_of_elem, field_names):
    file_exists = os.path.isfile(file_name)
    with open(file_name, 'a+', newline='') as write_obj:
        dict_writer = DictWriter(write_obj, fieldnames=field_names)
        if not file_exists:
            dict_writer.writeheader()  
        dict_writer.writerow(dict_of_elem)

def hash(str_to_hash):
    return hashlib.md5(str_to_hash.encode()).hexdigest()

### input validations ###

def validate_no_comma(string):
    return not ',' in string

def validate_user_name(user_name):
    file_exists = os.path.isfile(config_file_name)
    if file_exists:
        with open(config_file_name, newline='') as read_obj:
            dict_reader = DictReader(read_obj)
            for row in dict_reader:
                if row['user_name'] == user_name:
                    return False
    if user_name == '':
        return False
    return True

def validate_user_name_exists(user_name):
    file_exists = os.path.isfile(config_file_name)
    if file_exists:
        with open(config_file_name, newline='') as read_obj:
            dict_reader = DictReader(read_obj)
            for row in dict_reader:
                if row['user_name'] == user_name:
                    return True
    return False

def validate_record_id(record_id):
    file_exists = os.path.isfile(data_file_name)
    if file_exists:
        with open(data_file_name, newline='') as read_obj:
            dict_reader = DictReader(read_obj)
            for row in dict_reader:
                if row['record_id'] == record_id:
                    return False
            if record_id == '':
                return False
    return True

### functions ###

def register():
    # user name (case sensitive, does not allow '', does not allow duplicates)
    user_name = input('\nEnter a user name : ')
    is_valid_user_name = validate_user_name(user_name)

    while (not is_valid_user_name):
        print('\nuser name is empty or already taken')
        user_name = input('\nEnter a user name : ')
        is_valid_user_name = validate_user_name(user_name)

    no_comma = validate_no_comma(user_name)
    while (not no_comma):
        print('\nuser name cannot contain commas')
        user_input = input('\nEnter a user name : ')
        no_comma = validate_no_comma(user_input)

    # password
    password = input('\nEnter a password : ')
    # hash using md5
    hash_password = hash(password)

    # user_type
    user_type = input('\nSelect user type\n select one of ' + str(main_user_types) + ' : ')
    is_valid_user_type = user_type in main_user_types

    while (not is_valid_user_type):
        print('\nUser type is invalid. Select a type from the given list')
        user_type = input('Select user type\n select one of ' + str(main_user_types) + ' : ')
        is_valid_user_type = user_type in main_user_types
    

    # privilege_level
    if user_type == 'patient':
        privilege_level = 'patient'
    else:
        privileged_user_type = input('\nSelect your role\n select one of ' + str(privileged_user_types) + ' : ')
        is_valid_privileged_user_type = privileged_user_type in privileged_user_types

        while (not is_valid_privileged_user_type):
            print('\nRole is invalid. Select a role from the given list')
            privileged_user_type = input('\nSelect your role\n select one of ' + str(privileged_user_types) + ' : ')
            is_valid_privileged_user_type = privileged_user_type in privileged_user_types
        
        privilege_level = privileged_user_type

    config_record = {
        'user_name' : user_name,
        'password' : hash_password,
        'user_type' : user_type,
        'privilege_level' : privilege_level
    }

    append_dict_as_row(config_file_name, config_record, config_field_names)
    print('\nUser registration successful')

def login():
    with open(config_file_name, newline='') as read_obj:
        dict_reader = DictReader(read_obj)

        user_name = input('\nEnter your user name : ')

        for row in dict_reader:
            if row['user_name'] == user_name:

                password = input('\nEnter your password : ')

                if row['password'] == hash(password):
                    return {
                        'user_name' : user_name,
                        'user_type' : row['user_type'],
                        'privilege_level' : row['privilege_level']
                    }
                print('\nincorrect password')
                return {}
        print('\ninvalid user name')
        return {}
    return {}

def view_all_records(filter_fileds):
    data_exists = False
    file_exists = os.path.isfile(data_file_name)
    if file_exists:
        with open(data_file_name, newline='') as read_obj:
            dict_reader = DictReader(read_obj)
            for row in dict_reader:
                data_exists = True
                print()
                for field in filter_fileds:
                    print (str(field) + ' : ' + row[field]) 
    if not data_exists:
        print('\nNo records found...')

def view_records_by_user_name(user_name, filter_fileds):
    data_exists = False
    file_exists = os.path.isfile(data_file_name)
    if file_exists:
        with open(data_file_name, newline='') as read_obj:
            dict_reader = DictReader(read_obj)
            for row in dict_reader:
                if row['user_name'] == user_name:
                    data_exists = True
                    print()
                    for field in filter_fileds:
                        print (str(field) + ' : ' + row[field])
    if not data_exists:
        print('\nNo matching records found...')

def view_records_by_id(record_id, filter_fileds):
    data_exists = False
    file_exists = os.path.isfile(data_file_name)
    if file_exists:
        with open(data_file_name, newline='') as read_obj:
            dict_reader = DictReader(read_obj)
            for row in dict_reader:
                if row['record_id'] == record_id:
                    data_exists = True
                    print()
                    for field in filter_fileds:
                        print (str(field) + ' : ' + row[field])
    if not data_exists:
        print('\nNo matching records found...')

def add_new_patient_record(filter_fileds):
    new_record = {}
    for field in filter_fileds:
        user_input = input('\nEnter '+ field + ' : ')
        
        if field == 'record_id':
            is_valid_record_id = validate_record_id(user_input)
            while (not is_valid_record_id):
                print('\nrecord id is empty or already used. Try a different id')
                user_input = input('\nEnter '+ field + ' : ')
                is_valid_record_id = validate_record_id(user_input)

        if field == 'user_name':
            user_name_exists = validate_user_name_exists(user_input)
            while (not user_name_exists):
                print('\nThe user name does not exist. Please enter a valid user name')
                user_input = input('\nEnter '+ field + ' : ')
                user_name_exists = validate_user_name_exists(user_input)

        no_comma = validate_no_comma(user_input)
        while (not no_comma):
            print('\ninput cannot contain commas')
            user_input = input('\nEnter '+ field + ' : ')
            no_comma = validate_no_comma(user_input)

        new_record[field] = user_input
    append_dict_as_row(data_file_name, new_record, data_field_names)
    print('\nNew record added...')

def edit_patient_record(record_id, filter_fileds):
    file_exists = os.path.isfile(data_file_name)
    if file_exists:
        with open(data_file_name, 'rt', newline='') as csvfile, tempfile:
            dict_reader = DictReader(csvfile)
            dict_writer = DictWriter(tempfile, fieldnames=data_field_names)
            dict_writer.writeheader()
            for row in dict_reader:
                if(row['record_id'] == record_id):
                    for field in filter_fileds:
                        do_edit = input('\nDo you want to edit '+ field + ' ? (yes/no) (default is no) : ')
                        if do_edit == 'yes':
                            user_input = input('\nEnter '+ field + ' : ')

                            no_comma = validate_no_comma(user_input)
                            while (not no_comma):
                                print('\ninput cannot contain commas')
                                user_input = input('\nEnter '+ field + ' : ')
                                no_comma = validate_no_comma(user_input)

                            row[field] = user_input
                dict_writer.writerow(row)
        shutil.move(tempfile.name, data_file_name)
        print('\nRecord successfully edited...')
    else:
        print('\nno records to edit...')


# main
init_actions = ['login', 'register']

action = input('Login or Register\n select one of ' + str(init_actions) + ' : ')
is_valid_action = action in init_actions

while (not is_valid_action):
    print('\ninvalid selection')
    action = input('Login or Register\n select one of ' + str(init_actions) + ' : ')
    is_valid_action = action in init_actions

if action == 'register':
    register()
    input('\nPress ENTER to exit')
    exit()

else:
    user = login()
    if user == {}:
        print('\nlogin failed')
        input('\nPress ENTER to exit')
        exit()

    selected_action = input('select the action to perform\n' + str(allowed_actions[user['privilege_level']]) + ' : ')  

    # check if selected action is allowed for the privilege level of user       
    if not selected_action in allowed_actions[user['privilege_level']]:
        print('\ninvalid selection')
        input('\nPress ENTER to exit')
        exit()
    
    if selected_action == 'view my records':
        view_records_by_user_name(user['user_name'], read_privileges[user['privilege_level']])
        input('\nPress ENTER to exit')
        exit()

    if selected_action == 'view all records':
        view_all_records(read_privileges[user['privilege_level']])
        input('\nPress ENTER to exit')
        exit()

    if selected_action == 'view all records by user name':
        user_name = input('Enter a user name : ')
        view_records_by_user_name(user_name, read_privileges[user['privilege_level']])
        input('\nPress ENTER to exit')
        exit()

    if selected_action == 'view record by id':
        record_id = input('Enter a record id : ')
        view_records_by_id(record_id, read_privileges[user['privilege_level']])
        input('\nPress ENTER to exit')
        exit()

    if selected_action == 'add new record':
        add_new_patient_record(write_privileges[user['privilege_level']])
        input('\nPress ENTER to exit')
        exit()

    if selected_action == 'edit record':
        id_known = input('\nDo you know the record id of the record you want to edit ? (yes/no) (default is yes) : ')
        if id_known == 'no':
            user_name_known = input('\nDo you know the user name of the patient ? (yes/no) (default is yes) : ')
            if user_name_known == 'no':
                print ('\nHere is a list of all patient records')
                view_all_records(read_privileges[user['privilege_level']])
                print ('\nYou can find the record id from the above list\n')
            else:
                user_name = input('Enter user name of the patient : ')
                view_records_by_user_name(user_name, read_privileges[user['privilege_level']])
                print ('\nYou can find the record id from the above list\n')
        record_id = input('Enter the record id : ')
        edit_patient_record(record_id, edit_privileges[user['privilege_level']])
        input('\nPress ENTER to exit')
        exit()


