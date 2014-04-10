
class Log:
    def get_all_entries(self, db):
        pass


class Tag:
    # returns a list of all tags associated with the log with id `log_id`
    @staticmethod
    def get_log_tags(db, log_id):
        sql = """
            select name from tags t 
            LEFT JOIN logs_tags_assoc a ON a.tagid = t.id
            where a.logid=?"""

        cur = db.execute(sql, [log_id])
        tags = cur.fetchall()
        return [tag['name'] for tag in tags]

    # returns a list of all tags associated with the page with id `page_id`
    @staticmethod
    def get_page_tags(db, page_id):
        sql = """
            select name from tags t 
            LEFT JOIN pages_tags_assoc a ON a.tagid = t.id
            where a.pageid=?"""

        cur = db.execute(sql, [page_id])
        tags = cur.fetchall()
        return [tag['name'] for tag in tags]


