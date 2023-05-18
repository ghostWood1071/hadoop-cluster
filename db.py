from mysql import connector

class Helper():
    def __init__(self, host, port, user, password, db_name=None):
        self.connect_info = {
            'host': host,
            'port': port,
            'user': user,
            'password': password,
            'db_name': db_name
        }
        if db_name == None:
            self.connector = connector.connect(host = host, port = port, user = user, password = password)
        else:
            self.connector = connector.connect(host = host, port = port, user = user, password = password, database = db_name)
    def init_db(self, db_name):
        try:
            cursor = self.connector.cursor()
            cursor.execute(f"create database if not exists {db_name}")
            self.connector = connector.connect(host = self.connect_info['host'], 
                                               port = self.connect_info['port'], 
                                               user = self.connect_info['user'], 
                                               password = self.connect_info['password'], 
                                               database = db_name)
        except Exception as e:
            print(str(e)) 
    def excute(self, command):
        try:
            cursor = self.connector.cursor()
            cursor.execute(command)
            data = list(cursor)
            return data
        except Exception as e:
            print('error:', str(e))
        cursor = self.connector.cursor()
        cursor.execute("select * from colors")
        for x in cursor:
            print(x)
        cursor.close()
    
    def create_table(self, tbl_name, cols):
        try:
            col_cmd = ','.join(cols) #cols.join(',')
            cursor = self.connector.cursor()
            cursor.execute(f'create table if not exists {tbl_name} ({col_cmd})') 
        except Exception as e:
            print(str(e))
        
            