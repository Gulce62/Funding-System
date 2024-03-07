import sqlite3
import PySimpleGUI as sg
from datetime import datetime

from company import Company
from tier import Tier


con = sqlite3.connect('Project_db_latest.db')
cur = con.cursor()
cur.execute("PRAGMA foreign_keys = ON")

def window_login():
    layout = [[sg.Text('Welcome to the Online Funding Management System. Please enter your information.')],
              [sg.Text('E-Mail:', size=(10,1)), sg.Input(size=(30,1), key='email')],
              [sg.Text('Password:', size=(10,1)), sg.Input(size=(30,1), key='password')],
              [sg.Button('Login')]]

    return sg.Window('Login Window', layout)

def window_company_owner():
    companies = []
    for row in cur.execute('''SELECT cId, name, contactInfo, description 
                              FROM Company
                              WHERE ownerId = ?''', (login_user_id,)):
        companies.append(Company(row[0], row[1], row[2], row[3]))

    layout = [[sg.Text('Welcome ' + login_user_name)],
              [sg.Listbox(companies, key='companies', size=(50,10))],
              [sg.Button('Info', key='company_info'),
               sg.pin(sg.Button('Product', key='company_product')),
               sg.pin(sg.Button('Log Out', key='logout'))]]

    return sg.Window('Company Owner Window', layout)

def window_companyInfo(company):
    global current_company_id
    current_company_id = company.cId

    layout = [[sg.Text('Company Name: ', size=(15,1), key='text_name'), sg.Input(size=(50,2), key='company_name', default_text=company.name, disabled=True)],
              [sg.Text('Conatact Info: ', size=(15,1), key='text_contactInfo'), sg.Multiline(size=(50,3), key='company_contactInfo', default_text=company.contactInfo, disabled=True)],
              [sg.Text('Description: ', size=(15,1), key='text_description'), sg.Multiline(size=(50,3), key='company_description', default_text=company.desc, disabled=True)],
              [sg.Button('Edit', key='company_edit', visible=(login_user_type=='owner')),
               sg.pin(sg.Button('Save', key='company_save', visible=(login_user_type=='owner'))),
               sg.Push(),
               sg.pin(sg.Button('Back', key='company_back'))]]
    return sg.Window('Information of the Company Window', layout)

def window_investor():
    companies = []
    for row in cur.execute('''SELECT cId, name, contactInfo, description 
                              FROM Company'''):
        companies.append(Company(row[0], row[1], row[2], row[3]))

    layout = [[sg.Text('Welcome ' + login_user_name)],
              [sg.Listbox(companies, key='companies', size=(50,10))],
              [sg.Button('Info', key='company_info'),   
               sg.pin(sg.Button('Product', key='company_product')),
               sg.pin(sg.Button('All Products', key='all_products')),
               sg.pin(sg.Button('Edit Name', key='edit_name')),
               sg.pin(sg.Button('Log Out', key='logout'))]]

    return sg.Window('Investor Window', layout)

def window_admin():
    companies = []
    for row in cur.execute('''SELECT cId, name, contactInfo, description 
                              FROM Company'''):
        companies.append(Company(row[0], row[1], row[2], row[3]))

    layout = [[sg.Text('Welcome ' + login_user_name)],
              [sg.Listbox(companies, key='companies', size=(50,10))],
              [sg.Button('Info', key='company_info'),
               sg.pin(sg.Button('Product', key='company_product')),
               sg.pin(sg.Button('All Products', key='all_products')),
               sg.pin(sg.Button('Log Out', key='logout'))]]

    return sg.Window('Admin Window', layout)

def button_login(values):
    global login_user_id
    global login_user_name
    global login_user_surname
    global login_user_type
    global window

    uemail = values['email']
    upassword = values['password']
    
    if uemail == '':
        sg.popup('Email cannot be empty')
    elif upassword == '':
        sg.popup('Password cannot be empty')
    else:
        # first check if this is a valid user
        cur.execute('SELECT userId, name, surname, userType FROM User WHERE email = ? AND password = ?', (uemail, upassword))
        row = cur.fetchone()
        
        if row is None:
            sg.popup('e-mail or password is wrong!')
        else:
            # this is some existing user, let's keep the ID of this user in the global variable
            login_user_id = row[0]
            # we will use the name in the welcome message
            login_user_name = row[1]
            login_user_surname = row[2]
            # we will use the user type to open different windows
            login_user_type = row[3]
            if login_user_type == 'owner':
                sg.popup('Welcome, ' + login_user_name + ' (Company Owner)')
                window.close()
                window = window_company_owner()
            elif login_user_type == 'investor':
                sg.popup('Welcome, ' + login_user_name + ' (Investor)')
                window.close()
                window = window_investor()
            elif login_user_type == 'admin':
                sg.popup('Welcome, ' + login_user_name + ' (Admin)')
                window.close()
                window = window_admin()

def update_company(updated_values):
    updated_name = updated_values['company_name']
    updated_companyInfo = updated_values['company_contactInfo']
    updated_description = updated_values['company_description']
    cur.execute('''UPDATE Company
                   SET name = ?,
                   contactInfo = ?,
                   description = ?
                   WHERE cId = ?''', (updated_name, updated_companyInfo, updated_description, current_company_id))
    con.commit()

def window_edit_name():
    layout = [[sg.Text('Investor Name: ', size=(15,1), key='i_name'), sg.Input(size=(20,1), key='investor_name', default_text=login_user_name)],
              [sg.Text('Investor Surname: ', size=(15,1), key='i_surname'), sg.Input(size=(20,1), key='investor_surname', default_text=login_user_surname)],
              [sg.pin(sg.Button('Done Editing', key='done_editing')), 
               sg.Push(),
               sg.pin(sg.Button('Back', key='edit_back'))]]

    return sg.Window('Edit Name Window', layout)

def update_name(values):
    global login_user_name
    global login_user_surname

    login_user_name = values["investor_name"]
    login_user_surname = values["investor_surname"]
    cur.execute('''UPDATE User
                   SET name = ?,
                   surname = ?
                   WHERE userId = ?''', (login_user_name, login_user_surname, login_user_id))
    con.commit()

def get_tiers(productId):
    query = '''SELECT t.tId, t.name, t.minDonation FROM Product p, Has_Tier h, Tier t
               WHERE p.pId = h.pId AND h.tId = t.tId AND p.pId = ?
               ORDER BY t.minDonation ASC'''
    tiers = []

    cursor_tier = con.cursor()
    for tier in cursor_tier.execute(query, (productId,)):
        tiers.append(Tier(tier[0], tier[1], tier[2]))

    return tiers

def get_product_donation_percentage(product_id):
    p = cur.execute(
            "SELECT donatedMoney, donationGoal FROM Product WHERE pId = ?",
            (current_product_id,)
        ).fetchone()
    return 100 * p[0] / p[1]
    

def get_product_min_donation(product_id):
    query = """SELECT min(t.minDonation)
               FROM Has_Tier h, Tier t
               WHERE h.tId = t.tId AND h.pId = ?"""
    query_params = (product_id,)
    res = cur.execute(query, query_params).fetchone()

    return res[0] if res[0] else 0

def get_all_types():
    query = '''SELECT DISTINCT p.type FROM Product p'''
    types = []

    cursor_tier = con.cursor()
    for row in cursor_tier.execute(query):
        types.append(row[0])

    return types

def generate_product_array(still_funding=False, use_company=False, product_type=None):
    global product_array

    query_base = '''SELECT p.pId, p.name, p.description, p.donationGoal, p.donatedMoney ,p.targetedDate, p.type
                    FROM Product p WHERE ({})'''
    where_clause = '{} AND {} AND {}'
    query_params = tuple()

    if use_company:
        query_params += (company.cId,)

    if still_funding:
        query_params += (datetime.today().strftime('%Y-%m-%d'),)

    if product_type:
        query_params += (product_type,)

    query = query_base.format(where_clause.format(
        'cId = ?' if use_company else '1 = 1',
        'targetedDate > ?' if still_funding else '1 = 1',
        'type = ?' if product_type else '1 = 1'
    ))

    product_array = []
    cursor_product = con.cursor()
    for row in cursor_product.execute(query, query_params):
        tiers = get_tiers(row[0])
        cur_info_list = [row[0], row[1], row[2], row[3],
                        row[4], row[5], row[6],
                        ",".join([t.name for t in tiers])]
        product_array.append(cur_info_list)

    for p in product_array:
        donation_percentage = round(100 * p[4] / p[3], 2)
        p[4] = donation_percentage

def window_product_list(_company=None):
    global current_company_id
    global company

    all_products = _company is None
    company = _company

    if not all_products:
        current_company_id = _company.cId

    generate_product_array(use_company=(not all_products))

    headings = ['ID', 'Name','Description','DonationGoal', 'DonatedMoney(%)', 'targetedDate', 'type', 'tier']
    type_list = get_all_types()
    type_list.append("All")
    # type_list.remove("")
    layout = [[sg.Text('Your Products ')],
              [sg.Combo(type_list, default_value = "All", key = 'product_type', enable_events=True)],
              [sg.Table(values=product_array, headings=headings, vertical_scroll_only=False, key='product_list')],
              [sg.Button('Add Product', key='add_product', visible=(login_user_type=='owner')),
              sg.pin(sg.Button('Add Donation', key='donate_page', visible=(login_user_type=='investor'))),
              sg.pin(sg.Button('Edit Product', key='edit_product', visible=(login_user_type=='owner'))),
              sg.pin(sg.Button('Cancel Funding', key='cancel_funding', visible=(login_user_type=='owner'))),
              sg.pin(sg.Button('Delete Product', key='delete_product', visible=(login_user_type=='admin'))),
              sg.pin(sg.Button('View Comments', key='view_comments')),
              sg.pin(sg.Checkbox('Still funding', key='still_funding', default=False, enable_events=True)),
              sg.Push(),
              sg.pin(sg.Button('Back', key='company_back'))]]

    return sg.Window('Product List Window', layout)

def delete_product(values):
    deleted_product_Id = product_array[values["product_list"][0]][0] 

    delete_product_query = '''DELETE 
                              FROM Product
                              WHERE pId = ?'''

    cursor_delete = con.cursor()
    cursor_delete.execute(delete_product_query, (deleted_product_Id,))
    con.commit()
    return True

def delete_comment(values):
    deleted_comment_Id = comment_array[values["comment_list"][0]][0] 

    delete_comment_query = '''DELETE
                              FROM Comment
                              WHERE comId = ?'''

    cursor_delete = con.cursor()
    cursor_delete.execute(delete_comment_query, (deleted_comment_Id,))
    # cursor_delete.execute(delete_reply_query, (deleted_comment_Id,))
    con.commit()
    return True

def window_donate_page(_product):
    global current_product_id
    global product

    product = _product
    current_product_id = _product[0]

    tiers = get_tiers(current_product_id)
    min_donation_amount = get_product_min_donation(current_product_id)
    default_tier = tiers[0] if tiers else Tier(-1, "", 0)
    layout = [[sg.Text('Donation Progress', size=(15,1)), sg.ProgressBar(100, orientation='h', size = (20,10), key='progress')],
              [sg.Text('Donate Special:', size=(15,1)), sg.Input(str(min_donation_amount), key='donation_amount', size=(20,1))],
              [sg.Combo(tiers, size=(15,1), default_value=(default_tier.name), key='product_tier', enable_events=True)],
              [sg.Button("Donate", key="donate"), sg.Push(), sg.pin(sg.Button('Back', key='product_back'))]]

    return sg.Window("Product Page", layout, finalize=True)

def generate_comment_array():
    global comment_array

    query = '''SELECT DISTINCT c.comId, u.name, u.surname, c.cDate, c.cText, r.rDate, r.rText
                FROM Comment c, User u
                LEFT OUTER JOIN Reply r ON c.comId = r.comId
                WHERE c.pId = ? AND c.investorId = u.userId'''

    comment_array = []
    cursor_comment = con.cursor()
    for row in cursor_comment.execute(query, (current_product_id,)):
        cur_info_list = [row[0], row[1], row[2], row[3], row[4], row[5], row[6]]
        comment_array.append(cur_info_list)

def window_comment_list(_product):
    global current_product_id
    global product

    product = _product
    current_product_id = _product[0]
    product_name = _product[1]

    generate_comment_array()

    headings = ['Comment ID', 'Investor Name', 'Investor Surname', 'Comment Date', 'Comment', 'Reply Date', 'Reply']
    layout = [[sg.Text("Comments of the Product {}".format(product_name))],
              [sg.Table(values=comment_array, headings=headings, vertical_scroll_only=False, key='comment_list')],
              [sg.Button('Add Comment', key='add_comment', visible=(login_user_type=='investor')),
              sg.Button('Delete Comment', key='delete_comment', visible=(login_user_type=='admin')),
              sg.Button('Add Reply', key='add_reply', visible=(login_user_type=='owner')),
              sg.Push(),
              sg.pin(sg.Button('Back', key='product_back'))]]

    return sg.Window('Comment List Window', layout)

def add_comment(values):
    comment_date = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
    comment_text = values['comment_text']
    comment_investor_ID = login_user_id
    comment_product_ID = current_product_id

    if comment_text == "" or comment_text.isspace():
        sg.popup('Comment cannot be blank!')
        isBack = False
    else:
        cur.execute('''INSERT INTO Comment
                       (cDate, cText, investorId, pId)
                       VALUES (?, ?, ?, ?)''',
                       (comment_date, comment_text, comment_investor_ID, comment_product_ID))
        con.commit()
        isBack = True
    return isBack

def add_reply(values):
    reply_date = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
    reply_text = values['reply_text']
    reply_comment_ID = current_comment_id
    reply_owner_ID = login_user_id

    if reply_text == "" or reply_text.isspace():
        sg.popup('Reply cannot be blank!')
        isBack = False
    else:
        cur.execute('''INSERT INTO Reply
                       (comId, ownerId, rDate, rText)
                       VALUES (?, ?, ?, ?)''',
                       (reply_comment_ID, reply_owner_ID, reply_date, reply_text))
        con.commit()
        isBack = True
    return isBack
    
def window_add_reply():
    layout = [[sg.Text('Fill below to Add reply')],
              [sg.Text('Reply:', size=(20,3)), sg.Input(size=(60,3), key='reply_text')],
              [sg.Button('Add Reply', key='insert_reply'),
              sg.Push(),
              sg.pin(sg.Button('Back', key='add_comment_back'))]]
    return sg.Window('Add Reply Window', layout)

def window_add_comment():
    layout = [[sg.Text('Fill below to Add comment')],
             [sg.Text('Comment:', size=(15,1)), sg.Multiline(size=(50,3), key='comment_text')],
             [sg.Button('Add Comment', key='insert_comment'),
              sg.Push(),
              sg.pin(sg.Button('Back', key='add_comment_back'))]]
    return sg.Window('Add Comment Window', layout)

def window_add_product():
    layout = [[sg.Text('Fill below to add product')],
            #   [sg.Text('Product ID:', size=(10,1)), sg.Input(size=(30,1), key='product_ID')],
              [sg.Text('Product Name:', size=(10,1)), sg.Input(size=(30,1), key='name')],
              [sg.Text('Description:', size=(10,1)), sg.Input(size=(30,1), key='product_desc')],
              [sg.Text('Donation Goal:', size=(10,1)), sg.Input(size=(30,1), key='product_donation_goal')],
              [sg.Text('Target Date:', size=(10,1)), sg.Input(size=(30,1), key='product_target_date')],
              [sg.Text('Type:', size=(10,1)), sg.Input(size=(30,1), key='product_type')],
              [sg.Button('Add Product', key='insert_product'), 
              sg.Push(),
              sg.pin(sg.Button('Back', key='product_back'))]]
    return sg.Window('Add Product Window', layout)

def window_edit_product(pId):
    global current_product_id
    current_product_id = pId

    tiers = []
    for row in cur.execute("SELECT tId, name, minDonation FROM Tier"):
        tiers.append(Tier(row[0], row[1], row[2]))

    default_tier = tiers[0] if tiers else Tier(-1, "", 0)
    layout = [[sg.Text('Donation goal: '), sg.pin(sg.Input(key='new_donation_goal')), sg.pin(sg.Button("Update", key='update_donation_goal'))],
              [sg.Text('Donation tier: '), sg.pin(sg.Combo(tiers, default_value=(default_tier.name), key='new_donation_tier')), sg.pin(sg.Button("Add", key='add_donation_tier'))],
              [sg.Push(), sg.pin(sg.Button('Back', key='product_back'))]]

    return sg.Window('Edit Product Window', layout)

def add_product(values):
    # productID = values['product_ID']
    product_name = values['name']
    product_desc = values['product_desc']
    product_donation_goal = values['product_donation_goal']
    product_target_date = values['product_target_date']
    product_type = values['product_type']
    product_cId = current_company_id
    date_format = "%Y-%m-%d"
    isCorrectDateFormat = True
    try:
        isCorrectDateFormat = bool(datetime.strptime(product_target_date, date_format))
    except ValueError:
        isCorrectDateFormat = False
    product_id_list = []
    for row in cur.execute('''SELECT pId
                              FROM Product'''):
        product_id_list.append(row[0])
    # if str(productID) == '':
    #     sg.popup('Product ID cannot be empty')
    #     isBack = False
    # elif productID.isdigit()==False:
    #     sg.popup('Product ID needs to be an integer!!!')
    #     isBack = False
    # elif int(productID) in product_id_list:
    #     sg.popup('Product ID already taken! Please choose a different ID!!!')
    #     isBack = False
    if product_donation_goal.isdigit()==False and product_donation_goal != '':
        sg.popup('Donation goal needs to be a positive integer!!!')
        isBack = False
    elif (not isCorrectDateFormat) and date_format != '':
        sg.popup('Invalid date format!!! Please use YY-MM-DD')
        isBack = False
    elif not product_type or product_type.isspace():
        sg.popup('Product type cannot be blank! Use Unknown if it is not known.')
        isBack = False
    else:
        cur.execute('''INSERT INTO Product
                       (name, description, donationGoal, targetedDate, type, cId)
                       VALUES (?, ?, ?, ?, ?, ?)''',
                       (product_name, product_desc, product_donation_goal, product_target_date, product_type, product_cId))
        con.commit()
        isBack = True
    return isBack

def update_product(updated_values):
    updated_donationGoal = updated_values['new_donation_goal']
    if updated_donationGoal.isdigit()==False and updated_donationGoal != '':
        sg.popup('Donation goal needs to be a positive integer!!!')
    else:
        cur.execute('''UPDATE Product
                    SET donationGoal = ?
                    WHERE pId = ?''', (updated_donationGoal, current_product_id))
        con.commit()

def add_donation_tier(values):
    has_selected_tier = cur.execute("""SELECT count(*) FROM Has_Tier
                                       WHERE pId = ? AND tId = ?""", (current_product_id, values["new_donation_tier"].tId)).fetchone()[0] != 0

    if has_selected_tier:
        sg.popup("Product already has this tier!")
    else:
        cur.execute("""INSERT INTO Has_Tier
                       (tId, pId) VALUES (?, ?)""", (values["new_donation_tier"].tId, current_product_id))
        con.commit()

editing_company = False
window = window_login()
while True:  
    event, values = window.read()
    if event == sg.WIN_CLOSED:
        break

    elif event == "Login":
        button_login(values)

    elif event == "company_info":
        if len(values['companies']) <= 0:
            sg.popup('Please select a company')
        else:
            window.close()
            window = window_companyInfo(values['companies'][0])

    elif event == 'company_edit':
        editing_company = not editing_company
        if editing_company:
            window['company_name'].update(disabled=False)
            window['company_contactInfo'].update(disabled=False)
            window['company_description'].update(disabled=False)
            window['company_edit'].update(text='Stop Editing')
        else:
            window['company_name'].update(disabled=True)
            window['company_contactInfo'].update(disabled=True)
            window['company_description'].update(disabled=True)
            window['company_edit'].update(text='Edit')

    elif event == 'company_save':
        window['company_name'].update(disabled=True)
        window['company_contactInfo'].update(disabled=True)
        window['company_description'].update(disabled=True)
        update_company(values)

    elif event == 'company_back':
        window.close()

        if login_user_type == 'owner':
            window = window_company_owner()
        elif login_user_type == 'investor':
            window = window_investor()
        elif login_user_type == 'admin':
            window = window_admin()

    elif event == 'edit_name':
        window.close()
        window = window_edit_name()
    
    elif event == 'done_editing':
        update_name(values)
        window.close()
        window = window_investor()
    
    elif event == 'edit_back':
        window.close()
        window = window_investor()

    elif event == 'company_product':
        if len(values['companies']) <= 0:
            sg.popup("Please select a company")
        else:
            window.close()
            window = window_product_list(values['companies'][0])

    elif event == 'all_products':
        window.close()
        window = window_product_list(_company=None)

    elif event == "product_type" or event == 'still_funding':
        product_type = values['product_type']
        generate_product_array(
            still_funding=values['still_funding'],
            use_company=(company is not None),
            product_type=(product_type if product_type != 'All' else None)
        )
        window['product_list'].update(values=product_array)

    elif event == 'logout':
        window.close()
        window = window_login()

    elif event == 'add_product':
        window.close()
        window = window_add_product()

    elif event == 'insert_product':
        isBack = add_product(values)
        if isBack:
            window.close()
            window = window_product_list(company)

    elif event == 'product_back':
        window.close()
        window = window_product_list(company)
    
    elif event == 'add_comment_back':
        window.close()
        window = window_comment_list(product)

    elif event == 'edit_product':
        if len(values['product_list']) <= 0:
            sg.popup("Please select a product")
        else:
            window.close()
            window = window_edit_product(product_array[values['product_list'][0]][0])

    elif event == 'update_donation_goal':
        update_product(values)
        # sg.popup(f"Donation goal: {values['new_donation_goal']}")

    elif event == 'add_donation_tier':
        add_donation_tier(values)

    elif event == 'donate_page':
        if len(values["product_list"]) <= 0:
            sg.popup("Please select a product")
        else:
            product_id = product_array[values['product_list'][0]][0]
            today = datetime.today().strftime("%Y-%m-%d")
            if cur.execute(
                "SELECT count(*) FROM Product WHERE pId = ? AND targetedDate <= ?",
                (product_id, today)
            ).fetchone()[0] != 0:
                sg.popup("Product is not being funded")
            else:
                window.close()
                window = window_donate_page(product_array[values['product_list'][0]])
                window["progress"].update(get_product_donation_percentage(product_id))

    elif event == 'cancel_funding':
        if len(values['product_list']) <= 0:
            sg.popup("Please select a product")
        else:
            p_id = product_array[values['product_list'][0]][0]
            today = datetime.today().strftime("%Y-%m-%d")
            if cur.execute("SELECT count(*) FROM Product WHERE pId = ? AND targetedDate <= ?", (p_id, today)).fetchone()[0] != 0:
                sg.popup("Product is not being funded")
            else:
                cur.execute("""UPDATE Product SET targetedDate = ? WHERE pId = ?""", (datetime.today().strftime("%Y-%m-%d"), p_id))
                con.commit()

            generate_product_array(values['still_funding'], True)

            window['product_list'].update(values=product_array)

    elif event == 'view_comments':
        if len(values['product_list']) <= 0:
            sg.popup("Please select a product")
        else:
            window.close()
            window = window_comment_list(product_array[values['product_list'][0]])
        
    elif event == 'add_comment':
        window.close()
        window = window_add_comment()

    elif event == 'add_reply':
        if len(values['comment_list']) <= 0:
            sg.popup("Please select a comment!")
        elif comment_array[values["comment_list"][0]][-1] is None:
            global curent_comment_id 
            current_comment_id = comment_array[values["comment_list"][0]][0]
            window.close()
            window = window_add_reply()

        else:
            sg.popup('This comment is already replied!!!')

    elif event == 'insert_comment':
        isBack = add_comment(values)
        if isBack:
            window.close()
            window = window_comment_list(product)
    
    elif event == 'insert_reply':
        isBack = add_reply(values)
        if isBack:
            window.close()
            window = window_comment_list(product)
    
    elif event == 'delete_comment':
        if len(values['comment_list']) <= 0:
            sg.popup("Please select a comment!")
        else:
            delete_comment(values)
            window.close()
            window = window_comment_list(product)

    elif event == 'delete_product':
        if len(values['product_list']) <= 0:
            sg.popup("Please select a product!")
        else:
            delete_product(values)
            window.close()
            window = window_product_list(company)

    elif event == "product_tier":
        selected_tier = values["product_tier"]
        # donation_amount = get_tier_min_donation(values["product_tier"])
        window["donation_amount"].update(selected_tier.minDonation)

    elif event == "donate":
        min_donation = get_product_min_donation(current_product_id)
        
        try:
            donation_amount = int(values["donation_amount"])
            if donation_amount < min_donation:
                sg.popup("Donation amount cannot be less then minimum {}".format(min_donation))

            cur.execute(
                "UPDATE Product SET donatedMoney = donatedMoney + ? WHERE pId = ?",
                (donation_amount, current_product_id)
            )
            cur.execute(
                """INSERT INTO Donation
                   (donationDate, donationAmount, investorId, pId)
                   VALUES (?, ?, ?, ?)
                """,
                (datetime.today().strftime("%Y-%m-%d %H:%M:%S"), donation_amount,
                 login_user_id, current_product_id)
            )
            con.commit()
            
            window["progress"].update(get_product_donation_percentage(current_product_id))

        except:
            sg.popup("Donation amount must be a postivie integer")
        