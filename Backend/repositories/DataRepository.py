from .Database import Database


class DataRepository:
    @staticmethod
    def json_or_formdata(request):
        if request.content_type == 'application/json':
            gegevens = request.get_json()
        else:
            gegevens = request.form.to_dict()
        return gegevens

    #########  logging  #########
    @staticmethod
    def read_meting_by_action(type_actie):
        sql = "SELECT waarde from historiek where actieid = %s ORDER BY datum DESC"
        params = [type_actie]
        return Database.get_one_row(sql, params)

    @staticmethod
    def add_meting(datum, waarde, commentaar, deviceid, actieid, productid):
        sql = "INSERT INTO historiek(datum,waarde,commentaar,deviceid,actieid,productid) VALUES(%s,%s,%s,%s,%s,%s)"
        params = [datum, waarde, commentaar, deviceid, actieid, productid]
        return Database.execute_sql(sql, params)

    @staticmethod
    def read_producten():
        sql = "SELECT * from producten where aantal > 0"
        return Database.get_rows(sql)

    @staticmethod
    def add_product(productId):
        sql = "UPDATE producten SET aantal = (aantal + 1) where productId = %s"
        params = [productId]
        return Database.execute_sql(sql, params)

    @staticmethod
    def delete_product(productId):
        sql = "UPDATE producten SET aantal = (aantal - 1) where productId = %s"
        params = [productId]
        return Database.execute_sql(sql, params)

    @staticmethod
    def read_meting_by_device(deviceid):
        sql = "SELECT waarde from historiek where deviceid = %s ORDER BY datum DESC"
        params = [deviceid]
        return Database.get_one_row(sql, params)

    @staticmethod
    def maintenance(type_actie):
        sql = "DELETE from historiek where actieid = %s ORDER BY datum ASC LIMIT 3"
        params = [type_actie]
        return Database.execute_sql(sql, params)

    @staticmethod
    def read_historiek():
        sql = "SELECT historiekId, date_format(datum, '%d/%m %H:%i') as datum, waarde, commentaar from historiek order by datum DESC LIMIT 30"
        return Database.get_rows(sql)

    @staticmethod
    def read_graph_data():
        sql = "select p.categorie, p.hoeveelheid, date_format(datum,'%H:%i') as tijdstip from historiek h inner join producten p on h.productId = p.productId where h.actieId = 2 and date(h.datum) = date(now())"
        return Database.get_rows(sql)
