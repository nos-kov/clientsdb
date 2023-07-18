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
        conn = psycopg2.connect(database=self.database, user =self.user, password =self.password)
        return conn

    def close_conn(self, conn):
        '''closes the connection'''
        conn.close

    def make_query(self, conn, type: str , **kwargs):
        '''make quesry to db'''
        result =''

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
                    cur.execute(query, (fname, lname, email) ) 
                      
                conn.commit()
            elif type == 'S':

                query = f"SELECT * FROM client c INNER JOIN phone p ON c.email = p.email;"
                cur.execute(query)
                result = cur.fetchone()

        return result 

    
    
def create_client():
    
    cfname = input("Enter client's first name:")
    clname = input("Enter client's last name:")
    cemail = input("Enter client's email:")
    cphone = input("Enter client's phone:")
    
    myconnection.make_query(conn, 'I', fname = cfname, lname = clname, email = cemail, table = 'client(fname, lname, email)', value = '%s,%s,%s')
    myconnection.make_query(conn, 'I', phone = cphone, email = cemail, table = 'phone(phone, email)', value = '%s,%s')

if __name__ == '__main__':

    myconnection = dbconn(config["dbconnect"]["db"], config["dbconnect"]["user"], config["dbconnect"]["pass"])
    conn = myconnection.create_conn()
    # create tables
    cvalue = 'id SERIAL PRIMARY key, fname VARCHAR(50), lname VARCHAR(50), email VARCHAR(25) UNIQUE NOT NULL'
    myconnection.make_query(conn, 'C', table = 'client', value = cvalue)
    cvalue = 'id SERIAL PRIMARY key, phone VARCHAR (12), email VARCHAR(25) REFERENCES client(email) '
    myconnection.make_query(conn, 'C', table = 'phone', value = cvalue)
    
    
    

    # insert into
    create_client()

    # select

    myconnection.make_query(conn, 'S', table = 'client c')


    myconnection.close_conn(conn)
