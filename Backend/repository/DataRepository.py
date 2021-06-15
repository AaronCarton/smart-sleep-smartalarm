from logging import log
from .Database import Database


class DataRepository:
    @staticmethod
    def json_or_formdata(request):
        if request.content_type == 'application/json':
            gegevens = request.get_json()
        else:
            gegevens = request.form.to_dict()
        return gegevens

    ############ ALL ############

    @staticmethod
    def add_data(temp, light, sound, airquality):
        sql = "INSERT INTO `readings` (`temp`, `light`, `sound`, `airquality`) VALUES (%s, %s, %s, %s)"
        params = [temp, light, sound, airquality]
        return Database.execute_sql(sql, params)

    @staticmethod
    def get_all_data(date=None):
        if date:
            sql = "SELECT * FROM `readings` WHERE `timestamp` LIKE %s ORDER BY `timestamp` DESC"
            params = [date]
            # print(sql)
            return Database.get_rows(sql, params)
        else:
            sql = "SELECT * FROM `readings` ORDER BY `timestamp` DESC"
            return Database.get_rows(sql)
    
    @staticmethod
    def get_latest_data():
        sql = "SELECT temp, light, sound, airquality FROM smartalarm.readings WHERE readings.timestamp = (SELECT MAX(timestamp) FROM smartalarm.readings);"
        return Database.get_one_row(sql)
    
    @staticmethod
    def get_daily_average(date):
        sql = "SELECT timestamp, round(avg(temp),2) as avg_temp, round(avg(light),2) as avg_light, round(avg(sound),2) as avg_sound, round(avg(airquality),2) as avg_airquality FROM smartalarm.readings WHERE DATE(timestamp) = DATE(%s);"
        params = [date]
        return Database.get_one_row(sql, params)

    @staticmethod
    def get_hourly_average(date):
        sql = "SELECT timestamp, round(avg(temp),2) as avg_temp, round(avg(light),2) as avg_light, round(avg(sound),2) as avg_sound, round(avg(airquality),2) as avg_airquality FROM smartalarm.readings WHERE DATE(timestamp) = DATE(%s) GROUP BY HOUR(timestamp);"
        params = [date]
        return Database.get_rows(sql, params)

    ############ TEMP ############

    @staticmethod
    def get_temp(date=None):
        if date:
            sql = "SELECT temp FROM `readings` WHERE `timestamp` LIKE %s ORDER BY `timestamp` DESC "
            params = [date]
            return Database.get_one_row(sql, params)
        else:
            sql = "SELECT temp FROM `readings` ORDER BY `timestamp` DESC"
            return Database.get_rows(sql)
    
    ############ LIGHT ############

    @staticmethod
    def get_light(date=None):
        if date:
            sql = "SELECT light FROM `readings` WHERE `timestamp` LIKE %s ORDER BY `timestamp` DESC "
            params = [date]
            return Database.get_one_row(sql, params)
        else:
            sql = "SELECT light FROM `readings` ORDER BY `timestamp` DESC"
            return Database.get_rows(sql)
    
    ############ SOUND ############

    @staticmethod
    def get_sound(date=None):
        if date:
            sql = "SELECT sound FROM `readings` WHERE `timestamp` LIKE %s ORDER BY `timestamp` DESC "
            params = [date]
            return Database.get_one_row(sql, params)
        else:
            sql = "SELECT sound FROM `readings` ORDER BY `timestamp` DESC"
            return Database.get_rows(sql)

    ############ AIR ############

    @staticmethod
    def get_air(date=None):
        if date:
            sql = "SELECT air FROM `readings` WHERE `timestamp` LIKE %s ORDER BY `timestamp` DESC "
            params = [date]
            return Database.get_one_row(sql, params)
        else:
            sql = "SELECT air FROM `readings` ORDER BY `timestamp` DESC"
            return Database.get_rows(sql)
    

    ############ ALARM ############

    @staticmethod
    def get_all_alarms():
        sql = "SELECT * FROM `alarm` ORDER BY `enddate` DESC"
        return Database.get_rows(sql)

    @staticmethod
    def get_alarm_by_id(id):
        sql = "SELECT * FROM `alarm` WHERE `id` = %s ORDER BY `enddate` DESC"
        params = [id]
        return Database.get_one_row(sql, params)

    @staticmethod
    def add_alarm(name, date):
        sql = "INSERT INTO `alarm` (`enddate`, `name`) VALUES (%s, %s)"
        params = [date, name]
        return Database.execute_sql(sql, params)
    
    @staticmethod
    def update_alarm_status(id, active):
        sql = "UPDATE `smartalarm`.`alarm` SET `active` = %s WHERE `id` = %s;"
        params = [active, id]
        return Database.execute_sql(sql, params)

    @staticmethod
    def delete_alarm(id):
        sql = "DELETE FROM `alarm` WHERE `alarm`.`id` = %s"
        params = [id]
        return Database.execute_sql(sql, params)

    ############ RGB ############

    @staticmethod
    def get_rgb_settings():
        sql = "SELECT r,g,b,hex FROM `rgb` WHERE id = 1 "
        return Database.get_one_row(sql)
    
    @staticmethod
    def update_rgb_settings(r, g, b, hex):
        sql = "UPDATE `rgb` SET `r` = %s, `g` = %s, `b` = %s, `hex` = %s WHERE `rgb`.`id` = 1 "
        params = [r, g, b, hex]
        return Database.execute_sql(sql, params)

    
