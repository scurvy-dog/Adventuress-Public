# Module for interacting with Influxdb

from influxdb import InfluxDBClient

class Influx:
    # Class object to interact with  influxdb_client
    def __init__ (self, host, port, database):
        '''initialize values'''
        self.host = host
        self.port = port
        self.db = database

    def Open (self):
        # Open connetion to InfluxDb
        error_code =  None

        try:
            self.handle = client = InfluxDBClient(host=self.host, port=self.port)
        except Exception as err:
            error_code = err
            return error_code
        
        # Select database
        self.handle.switch_database(self.db)
        
        return

    def SetDb (self, database):
        # Switch databases
        error_code =  None

        try:
            self.handle.switch_database(database)
            self.db = database
        except Exception as err:
            error_code = err
            return error_code       

        return

    def Write (self, json_body, rp=None):
        # write out data set into Influx
        # Accepts optional argument to set retention policy. Default = None
        error_code =  None

        try:
            self.handle._write_points(json_body,database=self.db,retention_policy=rp,tags=None, time_precision=None)
        except Exception as err:
            error_code = err
            return error_code

        return error_code  

    def Query (self,q):
        # Exeecute query on database handler
        error_code =  None

        try: 
            query_return = self.handle.query(q)
            result = query_return.get_points()
        except Exception as err:
            error_code = err
            return error_code, None

        return error_code, result

    def Close (self):
        # Closes database handler
        error_code =  None

        try: 
            self.handle.close()
        except Exception as err:
            error_code = err
            return error_code

        return  
        