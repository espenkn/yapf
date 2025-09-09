import mysql.connector
from mysql.connector.abstracts import MySQLCursorAbstract, MySQLConnectionAbstract

from devicelab.devicelab import ResultExec

from create_measurements import CreateMeasurement

import pprint

import mysql.connector.cursor

# We might consider using a REST API for this since that is possible, but for now
# I don't want us to bind us to using that unless we agree that should be the way to do this.

class CursorWrapper():
    """
    Wrapper for the cursor object to create a 'self closing' cursor.
    Also has ""autocommit"" on exit.
    """

    def __init__(self, connection: mysql.connector.MySQLConnection):
        self._connection = connection
        self._cursor = None


    def __enter__(self):
        """
        The 'enter' logic for 'with' statements.
        Create mysql cursor.
        """
        self._cursor = self._connection.cursor()
        return self._cursor


    def __exit__(self, type, value, traceback):
        """
        The 'exit' logic for 'with' statements.
        Close mysql cursor
        """

        # We probably want to commit now
        self._connection.commit()

        self._cursor.close()
        self._cursor = None

        if type is not None:
            pp = pprint.PrettyPrinter(indent=4)
            pp.pprint(type)
            pp.pprint(value)
            pp.pprint(traceback)


class PerformanceDb():
    def __init__(self, connection_file):
        self.connection_file = connection_file
        self._connection: mysql.connector.MySQLConnection = None


    def __enter__(self):
        """
        The 'enter' logic for 'with' statements.
        Create mysql connection
        """
        self._connect()
        return self


    def __exit__(self, type, value, traceback):
        """
        The 'exit' logic for 'with' statements.
        Close mysql connection
        """
        self._disconnect()
        self._connection = None

        if type is not None:
            pp = pprint.PrettyPrinter(indent=4)
            pp.pprint(type)
            pp.pprint(value)
            pp.pprint(traceback)


    def _connect(self):
        self._connection = mysql.connector.connect(option_files=self.connection_file)


    def _disconnect(self):
        self._connection.disconnect()


    def getCursor(self) -> CursorWrapper:
        return CursorWrapper(self._connection)


    def insert_performance_test(self, record: dict):
        query = """
            INSERT INTO performance_tests (
                created_at,
                updated_at,
                branch_name,
                gitlab_job_id,
                tag)
            VALUES (
                NOW(),
                NOW(),
                %(branch_name)s,
                %(gitlab_job_id)s,
                %(tag)s)"""

        insert_id = None
        with self.getCursor() as cursor:
            cursor.execute(query, record)
            insert_id = cursor.lastrowid

        return insert_id


    def insert_gitlab_jobs(self, record: dict):
        query = """
            INSERT INTO gitlab_jobs (
                created_at,
                updated_at,
                project_id,
                job_id,
                upstream_project_id,
                upstream_job_id)
            VALUES (
                NOW(),
                NOW(),
                %(project_id)s,
                %(job_id)s,
                %(upstream_project_id)s,
                %(upstream_job_id)s)"""

        insert_id = None
        with self.getCursor() as cursor:
            cursor.execute(query, record)
            insert_id = cursor.lastrowid

        return insert_id


    def insert_shield_run(self, record: dict):
        query = """
            INSERT INTO shield_runs (
                created_at,
                updated_at,
                gitlab_job_id)
            VALUES (
                NOW(),
                NOW(),
                %(branch_name)s,
                %(gitlab_job_id)s)"""

        insert_id = None
        with self.getCursor() as cursor:
            cursor.execute(query, record)
            insert_id = cursor.lastrowid

        return insert_id


    def insert_shield_time_measurements(self, record: dict):
        query = """
            INSERT INTO shield_time_measurements (
                created_at,
                updated_at,
                shield_run_id,
                name,
                time_point,
                elapsed_time)
            VALUES (
                NOW(),
                NOW(),
                %(shield_run_id)s,
                %(name)s,
                %(time_point)s,
                %(elapsed_time)s)"""

        insert_id = None
        with self.getCursor() as cursor:
            cursor.execute(query, record)
            insert_id = cursor.lastrowid

        return insert_id


    def insert_shield_stages_measurements(self, record: dict):
        query = """
            INSERT INTO shield_stages_measurements (
                created_at,
                updated_at,
                shield_run_id,
                name,
                start,
                end)
            VALUES (
                NOW(),
                NOW(),
                %(shield_run_id)s,
                %(name)s,
                %(start)s,
                %(end)s)"""

        insert_id = None
        with self.getCursor() as cursor:
            cursor.execute(query, record)
            insert_id = cursor.lastrowid

        return insert_id


    def parse_insert_checkpoint_results(self, results: ResultExec):
        record = self._create_checkpoint_record(results)
        insert_id = self.insert_shield_stages_measurements(record)
        return insert_id


    def parse_insert_section_results(self, results: ResultExec):
        record = self._create_section_record(results)
        insert_id = self.insert_shield_time_measurements(record)
        return insert_id


    def _create_checkpoint_record(self, results: ResultExec):
        CreateMeasurement.shieldStagesMeasurement()
        pass


    def _create_section_record(self, results: ResultExec):
        pass

