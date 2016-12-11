#Import Flask Library
from flask import Flask, render_template, request, session, url_for, redirect
import pymysql.cursors


#Initialize the app from Flask
app = Flask(__name__)


#Configure MySQL
conn = pymysql.connect(host='localhost',
                       user='root',
                       password='7183596771',
                       db='findFolks',
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)


# ============================================================================================
# RENDER INITIAL PAGES
# ============================================================================================


@app.route('/')
def hello():
	cursor = conn.cursor()

	upcomingEvents = 'SELECT an_event.event_id, title, an_event.description AS event_description, start_time, end_time, location_name, zipcode, a_group.group_id, a_group.group_name, category, keyword, a_group.description AS group_description FROM an_event NATURAL JOIN organize NATURAL JOIN about JOIN a_group ON(about.group_id = a_group.group_id) WHERE end_time BETWEEN NOW() AND DATE_ADD(NOW(), INTERVAL 3 DAY)'
	cursor.execute(upcomingEvents)
	upcomingEventsData = cursor.fetchall()
	
	allInterests = 'SELECT * FROM interest'
	cursor.execute(allInterests)
	allInterestsData = cursor.fetchall()

	cursor.close()
	return render_template('index.html', upcomingEvents = upcomingEventsData, allInterests = allInterestsData)


@app.route('/register')
def register():
	return render_template('register.html')


@app.route('/login')
def login():
	return render_template('login.html')


@app.route('/registerAuth', methods=['GET', 'POST'])
def registerAuth():
	username = request.form['username']
	password = request.form['password']
	firstName = request.form['firstName']
	lastName = request.form['lastName']
	email = request.form['email']
	zipcode = request.form['zipcode']

	cursor = conn.cursor()
	query = 'SELECT * FROM member WHERE member.username = %s'
	cursor.execute(query, (username))
	data = cursor.fetchone()
	error = None
	if (data):
		error = "This user already exists"
		return render_template('register.html', error = error)
	else:
		query = 'INSERT INTO member(username, password, firstName, lastName, email, zipcode) VALUES(%s, md5(%s), %s, %s, %s, %s)'
		cursor.execute(query, (username, password, firstName, lastName, email, int(zipcode)))
		conn.commit()
		cursor.close()
		return render_template('index.html')


# method for login OK
#use fetchall() if you are expecting more than 1 data row
@app.route('/loginAuth', methods=['GET', 'POST'])
def loginAuth():
	username = request.form['username']
	password = request.form['password']

	cursor = conn.cursor()
	query = 'SELECT * FROM member WHERE username = %s and password = md5(%s)'
	cursor.execute(query, (username, password))
	data = cursor.fetchone()
	cursor.close()
	error = None
	if (data):
		session['username'] = username
		return redirect(url_for('home'))
	else:
		error = 'Invalid login or username'
		return render_template('login.html', error=error)


# ============================================================================================
# RENDER PAGES
# ============================================================================================


@app.route('/viewInterestGroup/<category>/<keyword>')
def viewInterestGroup(category, keyword):
	cursor = conn.cursor();

	interestGroup = 'SELECT * FROM interest NATURAL JOIN a_group NATURAL JOIN about WHERE (category = %s AND keyword = %s)'
	#cursor.execute(query, (username))
	cursor.execute(interestGroup, (category, keyword))
	interestGroupData = cursor.fetchall()
	
	cursor.close()
	return render_template('viewInterestGroup.html', interestGroup = interestGroupData)


@app.route('/home')
def home():
	username = session['username']
	cursor = conn.cursor();

	userGroups = 'SELECT group_id, group_name, description, category, keyword, creator, authorized FROM a_group NATURAL JOIN about NATURAL JOIN belongs_to WHERE (username = %s)'
	cursor.execute(userGroups, (username))
	userGroupsData = cursor.fetchall()

	userUpcomingEvents = 'SELECT an_event.event_id, title, an_event.description AS event_description, start_time, end_time, location_name, zipcode, a_group.group_id, a_group.group_name, category, keyword, a_group.description AS group_description FROM sign_up NATURAL JOIN an_event NATURAL JOIN organize NATURAL JOIN about JOIN a_group ON(organize.group_id = a_group.group_id) WHERE (username = %s) AND (NOW() < end_time)'
	cursor.execute(userUpcomingEvents, (username))
	userUpcomingEventsData = cursor.fetchall()
	
	cursor.close()
	return render_template('home.html', username = username, userGroups = userGroupsData, userUpcomingEvents = userUpcomingEventsData)


@app.route('/friends')
def friends():
	username = session['username']
	cursor = conn.cursor();

	unverifiedFriends = 'SELECT friend_of FROM friend WHERE (friend_to = %s) AND friend_of NOT IN (SELECT friend_to FROM friend WHERE (friend_of = %s))'
	cursor.execute(unverifiedFriends, (username, username))
	unverifiedFriendsData = cursor.fetchall()

	verifiedFriends = 'SELECT friend_of FROM friend WHERE (friend_to = %s) AND friend_of IN (SELECT friend_to FROM friend WHERE (friend_of = %s))'
	cursor.execute(verifiedFriends, (username, username))
	verifiedFriendsData = cursor.fetchall()

	notFriends = 'SELECT username FROM member WHERE username NOT IN (SELECT friend_of FROM friend WHERE (friend_to = %s)) AND (username != %s)'
	cursor.execute(notFriends, (username, username))
	notFriendsData = cursor.fetchall()
	
	cursor.close()
	return render_template('friends.html', username = username, unverifiedFriends = unverifiedFriendsData, friends = verifiedFriendsData, notFriends = notFriendsData)


@app.route('/interests')
def interests():
	username = session['username']
	cursor = conn.cursor();

	# your interests
	userInterests = 'SELECT * FROM interested_in WHERE username = %s'
	cursor.execute(userInterests, (username))
	userInterestsData = cursor.fetchall()

	# interests other people have that you might be interested in
	userInterestsSuggestions = 'SELECT category, keyword FROM interest WHERE (category, keyword) NOT IN (SELECT category, keyword FROM interested_in WHERE (username = %s)) AND category IN (SELECT category FROM interested_in WHERE (username = %s))'
	cursor.execute(userInterestsSuggestions, (username, username))
	userInterestsSuggestionsData = cursor.fetchall()

	# interests you might not be interested in but you may want to check out anyway
	otherInterests = 'SELECT category, keyword FROM interest WHERE (category, keyword) NOT IN (SELECT category, keyword FROM interested_in WHERE (username = %s)) AND category NOT IN (SELECT category FROM interested_in WHERE (username = %s))'
	cursor.execute(otherInterests, (username, username))
	otherInterestsData = cursor.fetchall()

	cursor.close()
	return render_template('interests.html', username = username, userInterests = userInterestsData, userInterestsSuggestions = userInterestsSuggestionsData, otherInterests = otherInterestsData)


@app.route('/groups')
def groups():
	username = session['username']
	cursor = conn.cursor();

	# groups you are in
	userGroups = 'SELECT group_id, group_name, description, category, keyword, creator, authorized FROM a_group NATURAL JOIN about NATURAL JOIN belongs_to WHERE (username = %s)'
	cursor.execute(userGroups, (username))
	userGroupsData = cursor.fetchall()

	# groups that you might be interested in
	userGroupsSuggestions = 'SELECT category, keyword, group_id, group_name, description, creator FROM a_group NATURAL JOIN about NATURAL JOIN interested_in WHERE category IN (SELECT category FROM interested_in WHERE (username = %s)) AND group_id NOT IN (SELECT group_id FROM belongs_to WHERE (username = %s))'
	cursor.execute(userGroupsSuggestions, (username, username))
	userGroupsSuggestionsData = cursor.fetchall()

	# groups that you might not be interested in but you may want to check out anyway
	otherGroups = 'SELECT category, keyword, group_id, group_name, description, creator FROM a_group NATURAL JOIN about NATURAL JOIN interested_in WHERE category NOT IN (SELECT category FROM interested_in WHERE (username = %s)) AND group_id NOT IN (SELECT group_id FROM belongs_to WHERE (username = %s))'
	cursor.execute(otherGroups, (username, username))
	otherGroupsData = cursor.fetchall()

	cursor.close()
	return render_template('groups.html', username = username, userGroups = userGroupsData, userGroupsSuggestions = userGroupsSuggestionsData, otherGroups = otherGroupsData)


@app.route('/locations')
def locations():
	username = session['username']
	cursor = conn.cursor();

	# all previously established locations
	locations = 'SELECT * FROM location'
	cursor.execute(locations)
	locationsData = cursor.fetchall()

	cursor.close()
	return render_template('locations.html', username = username, locations = locationsData)


@app.route('/events')
def events():
	username = session['username']
	cursor = conn.cursor();

	# groups you can make events for
	authorizedGroups = 'SELECT group_id, group_name, description, category, keyword, creator, authorized FROM a_group NATURAL JOIN about NATURAL JOIN belongs_to WHERE (username = %s AND authorized = true)'
	cursor.execute(authorizedGroups, (username))
	authorizedGroupsData = cursor.fetchall()

	# upcoming events you signed up for
	userUpcomingEvents = 'SELECT an_event.event_id, title, an_event.description AS event_description, start_time, end_time, location_name, zipcode, a_group.group_id, a_group.group_name, category, keyword, a_group.description AS group_description FROM sign_up NATURAL JOIN an_event NATURAL JOIN organize NATURAL JOIN about JOIN a_group ON(organize.group_id = a_group.group_id) WHERE (username = %s) AND (NOW() < end_time)'
	cursor.execute(userUpcomingEvents, (username))
	userUpcomingEventsData = cursor.fetchall()

	# upcoming events your friends signed up for
	friendsUpcomingEvents = 'SELECT an_event.event_id, title, an_event.description AS event_description, start_time, end_time, location_name, zipcode, username, a_group.group_id, a_group.group_name, category, keyword, a_group.description AS group_description FROM an_event NATURAL JOIN organize NATURAL JOIN sign_up NATURAL JOIN about JOIN a_group ON(organize.group_id = a_group.group_id) WHERE username IN (SELECT friend_of FROM friend WHERE (friend_to = %s) AND friend_of IN (SELECT friend_to FROM friend WHERE (friend_of = %s))) AND (NOW() < end_time)'
	cursor.execute(friendsUpcomingEvents, (username, username))
	friendsUpcomingEventsData = cursor.fetchall()

	# upcoming events you might be interested in
	userUpcomingEventsSuggestions = 'SELECT an_event.event_id, title, an_event.description AS event_description, start_time, end_time, location_name, zipcode, a_group.group_id, a_group.group_name, category, keyword, a_group.description AS group_description FROM an_event NATURAL JOIN organize NATURAL JOIN sign_up NATURAL JOIN about JOIN a_group ON(organize.group_id = a_group.group_id) WHERE (category) IN (SELECT category FROM interested_in WHERE (username = %s)) AND (event_id) NOT IN (SELECT event_id FROM sign_up WHERE (username = %s)) AND (username != %s) AND (NOW() < end_time)'
	cursor.execute(userUpcomingEventsSuggestions, (username, username, username))
	userUpcomingEventsSuggestionsData = cursor.fetchall()

	# upcoming events you might not be interested in but you may want to check out anyway
	otherUpcomingEvents = 'SELECT an_event.event_id, title, an_event.description AS event_description, start_time, end_time, location_name, zipcode, a_group.group_id, a_group.group_name, category, keyword, a_group.description AS group_description FROM an_event NATURAL JOIN organize NATURAL JOIN sign_up NATURAL JOIN about JOIN a_group ON(organize.group_id = a_group.group_id) WHERE (category) NOT IN (SELECT category FROM interested_in WHERE (username = %s)) AND (username != %s) AND (NOW() < end_time)'
	cursor.execute(otherUpcomingEvents, (username, username))
	otherUpcomingEventsData = cursor.fetchall()

	# your past events
	userPastEvents = 'SELECT an_event.event_id, title, an_event.description AS event_description, start_time, end_time, location_name, zipcode, a_group.group_id, a_group.group_name, a_group.description AS group_description, category, keyword, rating AS your_rating FROM sign_up NATURAL JOIN an_event NATURAL JOIN organize NATURAL JOIN about JOIN a_group ON(organize.group_id = a_group.group_id) WHERE (username = %s) AND (NOW() > end_time)'
	cursor.execute(userPastEvents, (username))
	userPastEventsData = cursor.fetchall()

	# past events you didn't attend
	otherPastEvents = 'SELECT DISTINCT an_event.event_id, title, an_event.description AS location_description, start_time, end_time, location_name, zipcode, a_group.group_id, a_group.group_name, category, keyword, a_group.description AS group_description FROM sign_up NATURAL JOIN an_event NATURAL JOIN organize NATURAL JOIN about JOIN a_group ON(organize.group_id = a_group.group_id) WHERE (event_id) NOT IN (SELECT event_id FROM sign_up WHERE (username = %s)) AND (NOW() > end_time)'
	cursor.execute(otherPastEvents, (username))
	otherPastEventsData = cursor.fetchall()


	# rankings of past events you attended
	userPastEventsRatings = 'SELECT an_event.event_id, title, an_event.description AS event_description, start_time, end_time, location_name, zipcode, a_group.group_id, a_group.group_name, a_group.description AS group_description, category, keyword, AVG(rating) AS avg_rating FROM sign_up NATURAL JOIN organize NATURAL JOIN about NATURAL JOIN an_event JOIN a_group ON(organize.group_id = a_group.group_id) WHERE (rating IS NOT NULL) AND (organize.group_id) IN (SELECT group_id FROM belongs_to WHERE (username = %s)) AND (NOW() > end_time) GROUP BY organize.group_id, event_id, category, keyword'
	cursor.execute(userPastEventsRatings, (username))
	userPastEventsRatingsData = cursor.fetchall()

	# rankings of other events you did not attend
	otherPastEventsRatings = 'SELECT an_event.event_id, title, an_event.description AS event_description, start_time, end_time, location_name, zipcode, a_group.group_id, a_group.group_name, a_group.description AS group_description, category, keyword, AVG(rating) AS avg_rating FROM sign_up NATURAL JOIN organize NATURAL JOIN about NATURAL JOIN an_event JOIN a_group ON(organize.group_id = a_group.group_id) WHERE (rating IS NOT NULL) AND (organize.group_id) NOT IN (SELECT group_id FROM belongs_to WHERE (username = %s)) AND (NOW() > end_time) GROUP BY organize.group_id, event_id, category, keyword'
	cursor.execute(otherPastEventsRatings, (username))
	otherPastEventsRatingsData = cursor.fetchall()

	cursor.close()
	return render_template('events.html', username = username, authorizedGroups = authorizedGroupsData, userUpcomingEvents = userUpcomingEventsData, friendsUpcomingEvents = friendsUpcomingEventsData, userUpcomingEventsSuggestions = userUpcomingEventsSuggestionsData, otherUpcomingEvents = otherUpcomingEventsData, userPastEvents = userPastEventsData, otherPastEvents = otherPastEventsData, userPastEventsRatings = userPastEventsRatingsData, otherPastEventsRatings = otherPastEventsRatingsData)


@app.route('/createEvent/<category>/<keyword>/<group_name>/<group_id>')
def eventCreationPage(category, keyword, group_name, group_id):
	username = session['username']
	cursor = conn.cursor();

	# all previously established locations
	locations = 'SELECT * FROM location'
	cursor.execute(locations)
	locationsData = cursor.fetchall()

	cursor.close()
	return render_template('createEvent.html', username = username, category = category, keyword = keyword, group_name = group_name, group_id = group_id, locations = locationsData)


# ============================================================================================
# ROUTES TO GET AND POST
# ============================================================================================


@app.route('/makeFriend', methods=['GET', 'POST'])
def makeFriend():
	username = session['username']
	cursor = conn.cursor();

	target = request.form['target']

	makeFriend = 'INSERT INTO friend(friend_of, friend_to) VALUES(%s, %s)'
	try:
		cursor.execute(makeFriend, (username, target))
		conn.commit()
	except:
		pass

	cursor.close()
	return redirect(url_for('friends'))


@app.route('/verifyFriend/<target>', methods=['GET', 'POST'])
def verifyFriend(target):
	username = session['username']
	cursor = conn.cursor();

	verifiyFriend = 'INSERT INTO friend(friend_of, friend_to) VALUES(%s, %s)'
	try:
		cursor.execute(verifiyFriend, (username, target))
		conn.commit()
	except:
		pass

	cursor.close()
	return redirect(url_for('friends'))


@app.route('/createInterest', methods=['GET', 'POST'])
def createInterest():
	username = session['username']
	cursor = conn.cursor();

	category = request.form['category']
	keyword = request.form['keyword']

	createInterest = 'INSERT INTO interest(category, keyword) VALUES(%s, %s); INSERT INTO interested_in(username, category, keyword) VALUES(%s, %s, %s);'
	try:
		cursor.execute(createInterest, (category, keyword, username, category, keyword))
		conn.commit()
	except:
		pass

	cursor.close()
	return redirect(url_for('interests'))


@app.route('/createGroup', methods=['GET', 'POST'])
def createGroup():
	username = session['username']
	cursor = conn.cursor();

	group_name = request.form['group_name']
	description = request.form['description']
	category = request.form['category']
	keyword = request.form['keyword']

	try: 
		createInterest = 'INSERT INTO interest(category, keyword) VALUES(%s, %s); INSERT INTO interested_in(username, category, keyword) VALUES(%s, %s, %s);'
		cursor.execute(createInterest, (category, keyword, username, category, keyword))
		createGroup = 'INSERT INTO a_group(group_name, description, creator) VALUES(%s, %s, %s); INSERT INTO about(group_id, category, keyword) VALUES(LAST_INSERT_ID(), %s, %s); INSERT INTO belongs_to(group_id, username, authorized) VALUES(LAST_INSERT_ID(), %s, true);'
		cursor.execute(createGroup, (group_name, description, username, category, keyword, username))	
		conn.commit()
	except:
		pass

	cursor.close()
	return redirect(url_for('groups'))


# method to join group
@app.route('/joinGroup', methods=['GET', 'POST'])
def joinGroup():
	username = session['username']
	cursor = conn.cursor();

	group_name = request.form['group_name']

	joinGroup = 'INSERT INTO belongs_to(group_id, username, authorized) SELECT group_id, %s, false FROM a_group WHERE (group_name = %s)'
	try:
		cursor.execute(joinGroup, (username, group_name))
		conn.commit()
	except:
		pass

	cursor.close()
	return redirect(url_for('groups'))


@app.route('/createLocation', methods=['GET', 'POST'])
def createLocation():
	username = session['username']
	cursor = conn.cursor();

	location_name = request.form['location_name']
	description = request.form['description']
	address = request.form['address']
	latitude = request.form['latitude']
	longitude = request.form['longitude']
	zipcode = request.form['zipcode']

	createLocation = 'INSERT INTO location(location_name, description, address, latitude, longitude, zipcode) VALUES(%s, %s, %s, %s, %s, %s)'
	try:
		cursor.execute(createLocation, (location_name, description, address, int(latitude), int(longitude), int(zipcode)))
		conn.commit()
	except:
		pass

	cursor.close()
	return redirect(url_for('locations'))


@app.route('/createEvent/<category>/<keyword>/<group_name>/<group_id>', methods=['GET', 'POST'])
def createEvent(category, keyword, group_name, group_id):
	username = session['username']
	cursor = conn.cursor();

	title = request.form['title']
	event_description = request.form['event_description']
	start_time = request.form['start_time']
	end_time = request.form['end_time']

	event_location = request.form['event_location']
	event_zipcode = request.form['event_zipcode']

	location_name = request.form['location_name']
	location_zipcode = request.form['location_zipcode']
	location_description = request.form['location_description']
	address = request.form['address']
	latitude = request.form['latitude']
	longitude = request.form['longitude']

	try:
		if (event_location and event_zipcode):
			createEvent = 'INSERT INTO an_event(title, description, start_time, end_time, location_name, zipcode) VALUES(%s, %s, %s, %s, %s, %s); INSERT INTO sign_up(event_id, username) VALUES(LAST_INSERT_ID(), %s); INSERT INTO organize(event_id, group_id) VALUES(LAST_INSERT_ID(), %s)'
			cursor.execute(createEvent, (title, event_description, start_time, end_time, event_location, event_zipcode, username, group_id))
		else:
			createEventNewLocation = 'INSERT INTO location(location_name, description, address, latitude, longitude, zipcode) VALUES(%s, %s, %s, %s, %s, %s); INSERT INTO an_event(title, description, start_time, end_time, location_name, zipcode) VALUES(%s, %s, %s, %s, %s, %s); INSERT INTO sign_up(event_id, username) VALUES(LAST_INSERT_ID(), %s); INSERT INTO organize(event_id, group_id) VALUES(LAST_INSERT_ID(), %s)'
			cursor.execute(createEventNewLocation, (location_name, location_description, address, latitude, longitude, location_zipcode, title, event_description, start_time, end_time, location_event, location_zipcode, username, group_id))
		conn.commit()
	except:
		pass

	cursor.close()
	return redirect(url_for('events'))


@app.route('/sign_up/<event_id>', methods=['GET', 'POST'])
def sign_up(event_id):
	username = session['username']
	cursor = conn.cursor();

	signUp = 'INSERT INTO sign_up(event_id, username) VALUES(%s, %s)'
	try:
		cursor.execute(signUp, (event_id, username))
		conn.commit()	
	except:
		pass

	cursor.close()
	return redirect(url_for('events'))


@app.route('/rate/<event_id>/<rating>', methods=['GET', 'POST'])
def rate(event_id, rating):
	username = session['username']
	cursor = conn.cursor();

	rate = 'UPDATE sign_up SET rating = %s WHERE event_id = %s AND username = %s'
	try:
		cursor.execute(rate, (rating, event_id, username))
		conn.commit()
	except:
		pass
	
	cursor.close()
	return redirect(url_for('events'))


# method to logout
@app.route('/logout', methods=['GET', 'POST'])
def logout():
	session.pop('username')
	return redirect('/')
		

app.secret_key = 'cat'
#Run the app on localhost port 5000
#debug = True -> you don't have to restart flask
#for changes to go through, TURN OFF FOR PRODUCTION
if __name__ == "__main__":
	app.run('localhost', 5000, debug = True)