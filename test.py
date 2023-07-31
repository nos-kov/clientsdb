import psycopg2
import configparser

config = configparser.ConfigParser()
config.read("pass.ini")


class dbconn:
    ''' set up the db object'''
    def __init__(self, database, user, password) -> None:
        self.database = database
        self.user = user
        self.password = password
    
    def create_conn(self):
        '''set up connection'''
        conn = psycopg2.connect(
                    database=self.database,
                    user=self.user,
                    password=self.password)
        return conn

    def close_conn(self, conn):
        '''closes the connection'''
        conn.close

    def make_query(self, conn, type: str, **kwargs):
        '''make quesry to db'''
        result = ''

        with conn.cursor() as cur:

            table = kwargs.get('table', None)
            value = kwargs.get('value', None)

            if type == 'C':
                query = f"CREATE TABLE IF NOT EXISTS {table} ({value});"
                cur.execute(query)
                conn.commit()

            elif type == 'I':
                
                query = f" INSERT INTO {table} VALUES({value});"
                if "phone" in table:

                    phone = kwargs.get('phone', None)
                    email = kwargs.get('email', None)   
                    cur.execute(query, (phone, email))                 

                elif "client" in table:

                    fname = kwargs.get('fname', None)
                    lname = kwargs.get('lname', None)
                    email = kwargs.get('email', None)    
                    cur.execute(query, (fname, lname, email)) 
                      
                conn.commit()

            elif type == 'U':

                fname = kwargs.get('fname', None)
                lname = kwargs.get('lname', None)
                phone = kwargs.get('phone', None)
                query = f"INSERT INTO {table} values ({phone},"
                " (SELECT email FROM client "
                "c WHERE c.fname = %s and c.lname = %s ));"
                cur.execute(query, (fname, lname)) 
                      
                conn.commit()
                
            elif type == 'CH':

                field = kwargs.get('field', None)
                old_field = kwargs.get('old_field', None)
                upd_val = kwargs.get('upd_val', None)
                lname = kwargs.get('lname', None)

                if field == 'phone':
                    table = 'phone'
                    query = f"UPDATE {table}"
                    f" p SET {field} "
                    f"= %s WHERE p.{field} = %s;"
                    cur.execute(query, (upd_val, old_field))
                else:

                    table = 'client'
                    query = f"UPDATE {table} SET"
                    f" {field} = %s WHERE {field}"
                    f" = %s AND lname = '{lname}';"
                    cur.execute(query, (upd_val, old_field))    
                      
                conn.commit()

            elif type == 'D':

                if table == 'phone':
                    fname = kwargs.get('fname', None)
                    lname = kwargs.get('lname', None)
                    phone = kwargs.get('phone', None)
                    query = f"DELETE FROM {table} "
                    f"WHERE phone = %s AND "
                    f"email =  (SELECT email FROM"
                    f" client c WHERE c.fname = %s and c.lname = %s );"
                    cur.execute(query, (phone, fname, lname)) 
                      
                    conn.commit()

                elif table == 'client':
                    fname = kwargs.get('fname', None)
                    lname = kwargs.get('lname', None)
                    email = kwargs.get('email', None)
                    query = f"DELETE FROM phone WHERE email = %s;"
                    cur.execute(query, (email,))
                    query = f"DELETE FROM {table}"
                    f" WHERE email = %s "
                    f"AND fname = %s AND lname = %s ;"
                    cur.execute(query, (email, fname, lname)) 
                      
                    conn.commit()
            elif type == 'S':
                selection = {
                    'fname': kwargs.get('fname', None),
                    'lname': kwargs.get('lname', None),
                    'email': kwargs.get('email', None),
                    'phone': kwargs.get('phone', None)
                }
                clean_selection = {k: v for k, v in selection.items() if v}
                query_where = ""
                exec_param = ()
                for count, (key, val) in enumerate(clean_selection.items()):
                    if count == len(clean_selection) - 1:
                        query_where += ("p." + key + "= %s" if key == 'phone' 
                                        else "c." + key + "= %s")
                        
                    else:
                        query_where += ("p." + key + "= %s" + " AND " 
                                        if key == 'phone' 
                                        else "c." + key + "= %s" + " AND ")
                    exec_param += (val,)

                query = f"SELECT c.fname, c.lname, c.email, p.phone"
                f" FROM client c LEFT JOIN phone p"
                f" ON c.email = p.email WHERE {query_where};"

                cur.execute(query, exec_param)
                print(cur.fetchall())
                      
                conn.commit()

        return result 

    
def create_client(myconnection):
    
    cfname = input("Enter client's first name:")
    clname = input("Enter client's last name:")
    cemail = input("Enter client's email:")
    cphone = input("Enter client's phone:")
    
    myconnection.make_query(conn,
                            'I',
                            fname=cfname,
                            lname=clname,
                            email=cemail,
                            table='client(fname, lname, email)',
                            value='%s,%s,%s')
    myconnection.make_query(conn,
                            'I',
                            phone=cphone,
                            email=cemail,
                            table='phone(phone, email)',
                            value='%s,%s')


def update_phone(myconnection):
    
    cfname = input("Enter client's first name you'd"
                   " like to add a phone number for:")
    clname = input("Enter client's last name you'd "
                   "like to add a phone number for:")
    cphone = input("Enter client's phone:")
    myconnection.make_query(conn,
                            'U',
                            phone=cphone,
                            fname=cfname,
                            lname=clname,
                            table='phone(phone, email)',
                            value='%s,%s')


def change_client_data(myconnection):

    cfname = input("Enter client's first name:")
    clname = input("Enter client's last name:")
    cfield = input("Enter fieled you'd like to change. "
                   "Possible entries: 'fname' for first name, 'lname' for"
                   " last name, 'phone' for phone, 'email' for email:")
    cold_field = input("Enter old value:")
    cupd_val = input("Enter new value:")
    myconnection.make_query(conn,
                            'CH',
                            table='phone(phone, email)',
                            value='%s,%s,%s',
                            field=cfield,
                            old_field=cold_field,
                            upd_val=cupd_val,
                            lname=clname)


def delete_phone(myconnection):
    cfname = input("Enter client's first name "
                   "you'd like to delete a phone number for:")
    clname = input("Enter client's last name you'd "
                   "like to delete a phone number for:")
    cphone = input("Enter client's phone:")
    myconnection.make_query(conn,
                            'D',
                            phone=cphone,
                            fname=cfname,
                            lname=clname,
                            table='phone',
                            value='%s,%s,%s')


def delete_client(myconnection):
    cfname = input("Enter client's first name you'd like to delete:")
    clname = input("Enter client's last name you'd like to delete:")
    cemail = input("Enter client's email:")
    myconnection.make_query(conn,
                            'D',
                            email=cemail,
                            fname=cfname,
                            lname=clname,
                            table='client',
                            value='%s,%s,%s')


def find_client(myconnection):
    cfname = input("Leave blank or enter client's first name:")
    clname = input("Leave blank or enter client's last name:")
    cphone = input("Leave blank or enter client's phone:")
    cemail = input("Leave blank or enter client's email:")
    myconnection.make_query(conn,
                            'S',
                            fname=cfname,
                            lname=clname,
                            phone=cphone,
                            email=cemail,
                            value='%s,%s,%s,%s')


if __name__ == '__main__':

    myconnection = dbconn(config["dbconnect"]["db"],
                          config["dbconnect"]["user"],
                          config["dbconnect"]["pass"])
    conn = myconnection.create_conn()
    # create tables
    cvalue = "id SERIAL PRIMARY key, fname "
    "VARCHAR(50), lname VARCHAR(50), "
    "email VARCHAR(25) UNIQUE NOT NULL"
    myconnection.make_query(conn, 'C', table='client', value=cvalue)
    cvalue = 'id SERIAL PRIMARY key, phone VARCHAR (12),'
    ' email VARCHAR(25) REFERENCES client(email) ON UPDATE CASCADE'
    myconnection.make_query(conn, 'C', table='phone', value=cvalue)
    # functions
    create_client(myconnection)
    update_phone(myconnection)
    change_client_data(myconnection)
    delete_phone(myconnection)
    delete_client(myconnection)
    find_client(myconnection)
    myconnection.close_conn(conn)
