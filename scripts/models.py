class User:
    def __init__(self, tel_id, username, context, is_blocked, is_admin, id_in_db, phone, descr):
        self.tel_id = tel_id
        self.username = username
        self.context = context
        self.is_blocked = is_blocked
        self.is_admin = is_admin
        self.id_in_db = id_in_db
        self.phone = phone
        self.descr = descr