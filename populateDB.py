from ra_sched import RA, Day, Schedule
from scheduler import scheduling
from datetime import date
import psycopg2
import calendar
import random
import os

def popResHall(cur):
	for n in ['Brandt','Olson','Larsen']:
		cur.execute("INSERT INTO res_hall (name) VALUES ('{}')".format(n))

def popRAs(cur):
	def popBrandtRA(cur):
		cur.execute("SELECT id FROM res_hall WHERE name = 'Brandt';")
		iD = cur.fetchone()[0]

		for n in ["Alfonzo Doerr" , "Lahoma Berns", "Lue Girardin", "Donald Demartini", "Aubrey Mandell", "Stormy Dunigan","Arron Kernan",
				  "Betty Chmiel", "Gerardo Spells", "Epifania Soucy", "Tristan Hedgepeth","Neil Frix","Marvin Cheatam","Carmen Broadnax","Milford Schroyer"]:
			cur.execute("INSERT INTO ra (first_name, last_name, hall_id, date_started, points) VALUES ('{}','{}',{},NOW(),0)".format(n.split()[0],n.split()[1],iD))

	def popLarsenRA(cur):
		cur.execute("SELECT id FROM res_hall WHERE name = 'Larsen';")
		iD = cur.fetchone()[0]

		for n in ["Contessa Clardy", "Lolita Marcelino", "Wan Waddington", "Venus Maus", "Rosamond Chesson" "Mitzie Sickels"]:
			cur.execute("INSERT INTO ra (first_name, last_name, hall_id, date_started, points) VALUES ('{}','{}',{},NOW(),0)".format(n.split()[0],n.split()[1],iD))

	def popOlsonRA(cur):
		cur.execute("SELECT id FROM res_hall WHERE name = 'Olson';")
		iD = cur.fetchone()[0]

		for n in ["Nick Vankirk", "Eldon Sweetman", "Zita Gans", "Claudia Hole", "Dane Agarwal", "Verna Korb", "Ray Housman", "Zulema Robitaille"]:
			cur.execute("INSERT INTO ra (first_name, last_name, hall_id, date_started, points) VALUES ('{}','{}',{},NOW(),0)".format(n.split()[0],n.split()[1],iD))

	popBrandtRA(cur)
	popLarsenRA(cur)
	popOlsonRA(cur)

def popMonth(cur):
	cur.execute("INSERT INTO month (name, year) VALUES ('January',to_date('January 2018', 'Month YYYY'))")
	cur.execute("INSERT INTO month (name, year) VALUES ('February',to_date('February 2018', 'Month YYYY'))")
	cur.execute("INSERT INTO month (name, year) VALUES ('March',to_date('March 2018', 'Month YYYY'))")

def popDay(cur):
	c = calendar.Calendar()
	for m in [("January",1),("February",2),("March",3)]:
		cur.execute("SELECT id FROM month WHERE name = '{}'".format(m[0]))
		mID = cur.fetchone()[0]

		for d in c.itermonthdays(2018,m[1]):
			if d > 0:
				if len(str(d)) < 2:
					dstr = "0"+str(d)
				else:
					dstr = str(d)
				s = dstr +" "+ m[0][:3] +" "+ "2018"
				cur.execute("INSERT INTO day (month_id, date) VALUES ({},to_date('{}', 'DD Mon YYYY'))".format(mID,s))

def popConflicts(cur):
	cur.execute("SELECT id FROM day WHERE month_id = 1;")
	days = cur.fetchall()

	cur.execute("SELECT id FROM ra WHERE hall_id = 1;")
	ras = cur.fetchall()

	for raID in ras:
		daysCopy = days[:]
		for i in range(0,random.randint(0,15)):
			dID = daysCopy.pop(random.randint(0,len(daysCopy)-1))
			cur.execute("INSERT INTO conflicts (ra_id, day_id) VALUES ({},{})".format(raID[0],dID[0]))

def popDuties(cur):
	cur.execute("SELECT year FROM month ORDER BY year ASC;")
	d = cur.fetchone()[0]
	year = d.year
	month = d.month

	cur.execute("""SELECT first_name, last_name, id, hall_id,
						  date_started, cons.array_agg, points
				   FROM ra JOIN (SELECT ra_id, ARRAY_AGG(days.date)
								 FROM conflicts JOIN (SELECT id, date FROM day
													  WHERE month_id = 1) AS days
				   				 ON (conflicts.day_id = days.id)
				  			     GROUP BY ra_id) AS cons
						   ON (ra.id = cons.ra_id)
				   WHERE ra.hall_id = 1;""")

	raList = [RA(res[0],res[1],res[2],res[3],res[4],res[5],res[6]) for res in cur.fetchall()]
	noDutyList = [date(year,month,1),date(year,month,2),date(year,month,3),date(year,month,4),date(year,month,5),date(year,month,6),date(year,month,31)]

	sched = scheduling(raList,year,month,noDutyList)

	days = {}
	cur.execute("SELECT id, date FROM day WHERE month_id = 1;")
	for res in cur.fetchall():
		days[res[1]] = res[0]

	for d in sched:
		for r in d:
			cur.execute("""
			INSERT INTO duties (hall_id,ra_id,day_id,sched_id) VALUES (1,{},{},1);
			""".format(r.getId(),days[d.getDate()],1))

def popSchedule(cur):
	cur.execute("INSERT INTO schedule (hall_id,created) VALUES (1,NOW());")

def main():
	# This program assumes that the database is completely clean
	conn = psycopg2.connect(os.environ["DATABASE_URL"])
	cur = conn.cursor()
	popResHall(cur)
	conn.commit()
	popRAs(cur)
	conn.commit()
	popMonth(cur)
	conn.commit()
	popDay(cur)
	conn.commit()
	popConflicts(cur)
	conn.commit()
	popSchedule(cur)
	conn.commit()
	popDuties(cur)
	conn.commit()

main()
