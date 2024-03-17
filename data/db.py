import pandas as pd
import sqlite3
import os
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base


def get_session():
    if os.path.exists('accounts.db'):
        pass
    else:
        excel_to_sql('data.xlsx')

    Base = declarative_base()

    class Account(Base):
        __tablename__ = 'accounts'
        account_number = Column(Integer, primary_key=True)
        privatekey = Column(String)
        proxystring = Column(String)
        Task_101 = Column(Integer)
        Task_102 = Column(Integer)
        Task_103 = Column(Integer)
        Task_104 = Column(Integer)
        Task_201 = Column(Integer)
        Task_202 = Column(Integer)
        Task_203 = Column(Integer)
        Task_204 = Column(Integer)
        Task_205 = Column(Integer)
        Task_206 = Column(Integer)
        Task_301 = Column(Integer)
        Task_302 = Column(Integer)
        Task_303 = Column(Integer)
        Task_304 = Column(Integer)
        Task_305 = Column(Integer)
        Task_401 = Column(Integer)
        Task_402 = Column(Integer)
        Task_403 = Column(Integer)
        Task_404 = Column(Integer)
        Task_405 = Column(Integer)
        Task_406 = Column(Integer)
        Task_407 = Column(Integer)
        Task_408 = Column(Integer)
        Task_501 = Column(Integer)
        Task_502 = Column(Integer)
        Task_503 = Column(Integer)
        Task_504 = Column(Integer)
        Task_505 = Column(Integer)
        Task_506 = Column(Integer)
        Task_507 = Column(Integer)
        Task_508 = Column(Integer)
        Task_509 = Column(Integer)
        Task_601 = Column(Integer)
        Task_602 = Column(Integer)
        Task_603 = Column(Integer)
        Task_604 = Column(Integer)
        Task_605 = Column(Integer)
        Task_606 = Column(Integer)
        Task_607 = Column(Integer)
        Task_608 = Column(Integer)
        Task_609 = Column(Integer)
        Task_610 = Column(Integer)
        Task_611 = Column(Integer)
        Task_701 = Column(Integer)
        Task_702 = Column(Integer)
        Task_703 = Column(Integer)
        Task_704 = Column(Integer)
        Task_705 = Column(Integer)
        Task_706 = Column(Integer)
        Task_707 = Column(Integer)
        Task_708 = Column(Integer)
        Task_709 = Column(Integer)
        Task_710 = Column(Integer)
        Task_711 = Column(Integer)
        Task_801 = Column(Integer)
        Task_802 = Column(Integer)
        Task_803 = Column(Integer)

    engine = create_engine('sqlite:///accounts.db')
    Base.metadata.create_all(engine)
    DBSession = sessionmaker(bind=engine)
    return DBSession, Account


def excel_to_sql(excel_path):
    db_name = 'accounts.db'
    df = pd.read_excel(excel_path)

    # Ensure column names are valid SQLite identifiers
    df.columns = [col.replace(' ', '_').lower() for col in df.columns]

    # Step 2: Connect to the SQL database
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Step 3: Create a SQL table
    # Dynamically build column definitions, ensuring no trailing commas
    task_columns = ', '.join(["{} INTEGER".format(col) for col in df.columns[3:]])
    create_table_query = f"""
        CREATE TABLE IF NOT EXISTS accounts (
            account_number INTEGER PRIMARY KEY,
            privatekey TEXT,
            proxystring TEXT,
            {task_columns}
        )
        """

    try:
        cursor.execute(create_table_query)
    except sqlite3.OperationalError as e:
        print(f"Error creating table: {e}")
        return

    data_tuples = list(df.itertuples(index=False, name=None))
    placeholders = ', '.join(['?'] * len(df.columns))
    insert_query = "INSERT OR IGNORE INTO accounts VALUES ({})".format(placeholders)

    for row in data_tuples:
        try:
            cursor.execute(insert_query, row)
        except sqlite3.IntegrityError as e:
            print(f"Error inserting {row}: {e}")

    # Commit changes and close the connection
    conn.commit()
    conn.close()


if __name__ == '__main__':
    excel_to_sql('data.xlsx')