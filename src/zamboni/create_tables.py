from .table_creator import TableCreator
from .table_statements import create_statements
from .db_con import DBConnector

db_connector = DBConnector()
conn = db_connector.connect_db()
creator = TableCreator(conn)

teams_statement = create_statements['teams']
creator.create_table(teams_statement)