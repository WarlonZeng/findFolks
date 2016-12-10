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
	return render_template('index.html')


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
		query = 'INSERT INTO member(username, password, firstName, lastName, email, zipcode) VALUES(%s, %s, %s, %s, %s, %s)'
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
	query = 'SELECT * FROM member WHERE username = %s and password = %s'
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


@app.route('/home')
def home():
	username = session['username']
	cursor = conn.cursor();

	query = 'SELECT * FROM a_group'
	#cursor.execute(query, (username))
	cursor.execute(query)
	data = cursor.fetchall()
	
	cursor.close()
	return render_template('home.html', username = username, groups = data)


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

	userInterests = 'SELECT * FROM interested_in WHERE username = %s'
	cursor.execute(userInterests, (username))
	userInterestsData = cursor.fetchall()

	# common category, exclude from belonging to interest already
	userInterestsSuggestions = 'SELECT category, keyword FROM interest WHERE (category, keyword) NOT IN (SELECT category, keyword FROM interested_in WHERE (username = %s)) AND category IN (SELECT category FROM interested_in WHERE (username = %s))'
	cursor.execute(userInterestsSuggestions, (username, username))
	userInterestsSuggestionsData = cursor.fetchall()

	otherInterests = 'SELECT category, keyword FROM interest WHERE (category, keyword) NOT IN (SELECT category, keyword FROM interested_in WHERE (username = %s)) AND category NOT IN (SELECT category FROM interested_in WHERE (username = %s))'
	cursor.execute(otherInterests, (username, username))
	otherInterestsData = cursor.fetchall()

	cursor.close()
	return render_template('interests.html', username = username, userInterests = userInterestsData, userInterestsSuggestions = userInterestsSuggestionsData, otherInterests = otherInterestsData)


@app.route('/groups')
def groups():
	username = session['username']
	cursor = conn.cursor();

	userGroups = 'SELECT group_id, group_name, description, category, keyword, creator, authorized FROM a_group NATURAL JOIN about NATURAL JOIN belongs_to WHERE (username = %s)'
	cursor.execute(userGroups, (username))
	userGroupsData = cursor.fetchall()

	# common category, exclude from belonging to group already
	userGroupsSuggestions = 'SELECT category, keyword, group_id, group_name, description, creator FROM a_group NATURAL JOIN about NATURAL JOIN interested_in WHERE category IN (SELECT category FROM interested_in WHERE (username = %s)) AND group_id NOT IN (SELECT group_id FROM belongs_to WHERE (username = %s))'
	cursor.execute(userGroupsSuggestions, (username, username))
	userGroupsSuggestionsData = cursor.fetchall()

	otherGroups = 'SELECT category, keyword, group_id, group_name, description, creator FROM a_group NATURAL JOIN about NATURAL JOIN interested_in WHERE category NOT IN (SELECT category FROM interested_in WHERE (username = %s)) AND group_id NOT IN (SELECT group_id FROM belongs_to WHERE (username = %s))'
	cursor.execute(otherGroups, (username, username))
	otherGroupsData = cursor.fetchall()

	cursor.close()
	return render_template('groups.html', username = username, userGroups = userGroupsData, userGroupsSuggestions = userGroupsSuggestionsData, otherGroups = otherGroupsData)


@app.route('/locations')
def locations():
	username = session['username']
	cursor = conn.cursor();

	locations = 'SELECT * FROM location'
	cursor.execute(locations)
	locationsData = cursor.fetchall()

	cursor.close()
	return render_template('locations.html', username = username, locations = locationsData)


@app.route('/events')
def events():
	username = session['username']
	cursor = conn.cursor();

	authorizedGroups = 'SELECT group_id, group_name, description, category, keyword, creator, authorized FROM a_group NATURAL JOIN about NATURAL JOIN belongs_to WHERE (username = %s AND authorized = true)'
	cursor.execute(authorizedGroups, (username))
	authorizedGroupsData = cursor.fetchall()

	userUpcomingEvents = 'SELECT * FROM sign_up WHERE (username = %s)'
	cursor.execute(userUpcomingEvents, (username))
	userUpcomingEventsData = cursor.fetchall()

	friendsUpcomingEvents = 'SELECT * FROM an_event NATURAL JOIN organize NATURAL JOIN sign_up WHERE username IN (SELECT friend_of FROM friend WHERE (friend_to = %s) AND friend_of IN (SELECT friend_to FROM friend WHERE (friend_of = %s))) AND start_time > NOW()'
	cursor.execute(friendsUpcomingEvents, (username))
	friendsUpcomingEventsData = cursor.fetchall()

	userGroupsSuggestions = 'SELECT category, keyword, group_id, group_name, description, creator FROM a_group NATURAL JOIN about NATURAL JOIN interested_in WHERE category IN (SELECT category FROM interested_in WHERE (username = %s)) AND group_id NOT IN (SELECT group_id FROM belongs_to WHERE (username = %s))'
	cursor.execute(userGroupsSuggestions, (username, username))
	userGroupsSuggestionsData = cursor.fetchall()

	otherGroups = 'SELECT category, keyword, group_id, group_name, description, creator FROM a_group NATURAL JOIN about NATURAL JOIN interested_in WHERE category NOT IN (SELECT category FROM interested_in WHERE (username = %s)) AND group_id NOT IN (SELECT group_id FROM belongs_to WHERE (username = %s))'
	cursor.execute(otherGroups, (username, username))
	otherGroupsData = cursor.fetchall()

	cursor.close()
	return render_template('events.html', username = username, authorizedGroups = authorizedGroupsData, userUpcomingEvents = userUpcomingEventsData, userGroupsSuggestions = userGroupsSuggestionsData, otherGroups = otherGroupsData)



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
	except MySQLError as e:
		print('Got error {!r}, errno is {}'.format(e, e.args[0]))
		pass

	conn.commit()
	cursor.close()
	return redirect(url_for('friends'))


@app.route('/verifyFriend/<target>', methods=['GET', 'POST'])
def verifyFriend(target):
	username = session['username']
	cursor = conn.cursor();

	verifiyFriend = 'INSERT INTO friend(friend_of, friend_to) VALUES(%s, %s)'
	try:
		cursor.execute(verifiyFriend, (username, target))
	except MySQLError as e:
		print('Got error {!r}, errno is {}'.format(e, e.args[0]))
		pass
	
	conn.commit()
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
	except MySQLError as e:
		print('Got error {!r}, errno is {}'.format(e, e.args[0]))
		pass

	conn.commit()
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

	createInterest = 'INSERT INTO interest(category, keyword) VALUES(%s, %s); INSERT INTO interested_in(username, category, keyword) VALUES(%s, %s, %s);'
	try:
		cursor.execute(createInterest, (category, keyword, username, category, keyword))
	except MySQLError as e:
		print('Got error {!r}, errno is {}'.format(e, e.args[0]))
		pass


	createGroup = 'INSERT INTO a_group(group_name, description, creator) VALUES(%s, %s, %s); INSERT INTO about(group_id, category, keyword) VALUES(LAST_INSERT_ID(), %s, %s); INSERT INTO belongs_to(group_id, username, authorized) VALUES(LAST_INSERT_ID(), %s, true);'
	try:
		cursor.execute(createGroup, (group_name, description, username, category, keyword, username))
	except MySQLError as e:
		print('Got error {!r}, errno is {}'.format(e, e.args[0]))
		pass

	conn.commit()
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
	except MySQLError as e:
		print('Got error {!r}, errno is {}'.format(e, e.args[0]))
		pass

	conn.commit()
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
	cursor.execute(createLocation, (location_name, description, address, int(latitude), int(longitude), int(zipcode)))

	conn.commit()
	cursor.close()
	return redirect(url_for('locations'))


# method to create event
@app.route('/createEvent', methods=['GET', 'POST'])
def createEvent():
	group_id = session['group_id']
	cursor = conn.cursor();

	location_name = request.form['location_name']
	description = request.form['description']
	address = request.form['address']
	latitude = request.form['latitude']
	longitude = request.form['longitude']
	zipcode = request.form['zipcode']


	INSERT INTO an_event(title, description, location_name, start_time, end_time, zipcode) VALUES('sharit project', 'finish pls', 'NYU Poly', NOW() + INTERVAL 1 DAY, NOW() + INTERVAL 2 DAY, 11201)

	createLocation = 'INSERT INTO location(location_name, description, address, latitude, longitude, zipcode) VALUES(%s, %s, %s, %s, %s, %s)'
	cursor.execute(createLocation, (location_name, description, address, int(latitude), int(longitude), int(zipcode)))

	conn.commit()
	cursor.close()
	return redirect(url_for('events'))

	INSERT INTO organize(event_id, group_id) SELECT 7, group_id FROM a_group NATURAL JOIN about WHERE (category = 'cs' AND keyword = 'webdev')


# method to organize
@app.route('/organize', methods=['GET', 'POST'])
def organize():
	cursor = conn.cursor();

	username = request.form['username']
	group_id = request.form['group_id']
	authorized = False

	query = 'INSERT INTO belongs_to(username, group_id) VALUES(%s, %i, %s)'
	cursor.execute(query, (username, group_id, authorized))
	conn.commit()
	cursor.close()
	return redirect(url_for('home'))

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