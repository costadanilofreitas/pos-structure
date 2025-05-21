# -*- coding: utf-8 -*-

from mwhelper import BaseRepository


class RuptureRepository(BaseRepository):
    def __init__(self, mb_context):
        super(RuptureRepository, self).__init__(mb_context)

    def mark_snapshot_as_confirmed(self, snapshot_id):
        def inner_func(conn):
            conn.query("""
                UPDATE RupturaCurrentState
                SET Processed = 1
                WHERE SnapshotId <= '{}'
                  AND Environment = 'Delivery'
                  AND Processed <> 1;
            """.format(snapshot_id))

        self.execute_with_connection(inner_func)

    def get_last_ok_snapshot_id(self):
        def inner_func(conn):
            cursor = conn.select("""
                SELECT SnapshotId
                FROM RupturaCurrentState
                WHERE Environment = 'Delivery'
                  AND Processed <> '999'
                ORDER BY SnapshotId DESC
                LIMIT 1
            """)
            for row in cursor:
                return row.get_entry(0)
            return None
        return self.execute_with_connection(inner_func)

    def get_current_snapshot_id(self):
        def inner_func(conn):
            cursor = conn.select("""
                SELECT seq
                FROM rupturadb.sqlite_sequence
                WHERE name = 'RupturaSnapshot'
            """)
            for row in cursor:
                return row.get_entry(0)
            return None

        return self.execute_with_connection(inner_func)

    def get_snapshot_data(self, snapshot_id):
        def inner_func(conn):
            cursor = conn.select("""
                SELECT InactiveProdList
                FROM RupturaSnapshot
                WHERE ID = {}
                LIMIT 1
            """.format(snapshot_id or 'NULL'))
            for row in cursor:
                return row.get_entry(0).split(',')
            return []

        return self.execute_with_connection(inner_func)

    def is_snapshot_processed(self):
        def inner_func(conn):
            cursor = conn.select("""
                SELECT Processed
                FROM RupturaCurrentState 
                WHERE Environment = 'Delivery' 
                ORDER BY SnapshotId DESC 
                LIMIT 1
            """)

            for row in cursor:
                return bool(int(row.get_entry(0)))

            if cursor.rows() == 0:
                return True

            return False

        return self.execute_with_connection(inner_func)
