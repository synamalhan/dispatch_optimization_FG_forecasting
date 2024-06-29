import mysql.connector as sqlcon
conn = sqlcon.connect(host ='localhost', user='root', password='User@123', database='try')
cur = conn.cursor()

data = ['hi','hello','bye#$']

cur.execute("""INSERT INTO new_try1(name, an, ann) VALUES(%s, %s, %s)""", tuple(data))
print("done")
conn.commit()
conn.close()