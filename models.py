class Log:
    @staticmethod
    def get_entry(db, log_id):
        cur = db.execute('select id, body, ts from logs where id=?', [log_id])
        log = cur.fetchone()

        if log is None:
            return None
        else:
            return dict(log)

    @staticmethod
    def get_all_entries(db):
        cur = db.execute('select id, body, ts from logs order by id desc')
        logs = cur.fetchall()
        return [dict(log) for log in logs]


    @staticmethod
    def entry_exists(db, log_id):
        Log.get_entry(db, log_id) is not None


class Page:
    @staticmethod
    def get_page(db, page_id):
        cur = db.execute('select id, name, slug, body from pages where id=?', [page_id])
        page = cur.fetchone()

        if page is None:
            return None
        else:
            return dict(page)

    @staticmethod
    def get_all_pages(db):
        cur = db.execute('select id, name, slug, body from pages order by id desc')
        pages = cur.fetchall()
        return [dict(page) for page in pages]


    @staticmethod
    def page_exists(db, page_id):
        Page.get_entry(db, page_id) is not None



class Tag:
    # returns a list of all tags associated with the log with id `log_id`
    @staticmethod
    def get_log_tag_names(db, log_id):
        sql = """
            select name from tags t 
            LEFT JOIN logs_tags_assoc a ON a.tagid = t.id
            where a.logid=?"""

        cur = db.execute(sql, [log_id])
        tags = cur.fetchall()
        return [tag['name'] for tag in tags]

    # returns a list of all tags associated with the page with id `page_id`
    @staticmethod
    def get_page_tag_names(db, page_id):
        sql = """
            select name from tags t 
            LEFT JOIN pages_tags_assoc a ON a.tagid = t.id
            where a.pageid=?"""

        cur = db.execute(sql, [page_id])
        tags = cur.fetchall()
        return [tag['name'] for tag in tags]


