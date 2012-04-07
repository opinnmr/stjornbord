"""
Read and write to pykota print quota database.
"""

def get_printquota(user):
    """
    Try to fetch quota status from the PyKota database
    """
    if user.is_authenticated:
        try:
            from django.db import connection, DatabaseError
            cursor = connection.cursor()
            cursor.execute("SELECT balance FROM pykota.users WHERE username = %s", (user.username, ))
            row = cursor.fetchone()
        except DatabaseError:
            row = None

        if row:
            return int(row[0])

    return None

def set_printquota(user, balance):
    """
    Write print quota to the PyKota database. Note that we only
    update the balance field, leaving lifetimepaid unchanged. We
    don't need to keep record of this.
    """
    if user.is_authenticated:
        from django.db import connection, transaction, DatabaseError
        cursor = connection.cursor()
        cursor.execute("UPDATE pykota.users SET balance = %s WHERE username = %s", (balance, user.username, ))
        transaction.commit()