from zamboni.table_creator import TableCreator
from zamboni.table_statements import create_statements
from zamboni.db_con import DBConnector

db_connector = DBConnector()
conn = db_connector.connect_db()
creator = TableCreator(conn)

statement = create_statements['games']
creator.create_table(statement)
