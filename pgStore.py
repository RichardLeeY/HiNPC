
#connect to aws rds for postgres
import psycopg2 
import boto3
class pgStore:
    def __init__(self,dbname,hostname):
            self.prompt = ""
            self.db = self._connect_to_db(dbname,hostname)
    def _connect_to_db(self,dbname, hostname):
        ssm = boto3.client('ssm')
        parameter = ssm.get_parameter(Name='/pg-pwd', WithDecryption=True)
        # Connect to your postgres DB
        engine = psycopg2.connect(
            database=dbname,
            user="postgres",
            password=parameter.get('Parameter').get('Value'),
            host=hostname,
            port='5432'
        )
        return engine
    def getChatExample(self,choice):
        cur = self.db.cursor()
        cur.execute("select content from game_dialogue where choice = '{}'".format(choice))
        return cur.fetchone()[0]
        
        


