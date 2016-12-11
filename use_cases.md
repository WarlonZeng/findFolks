# findFolks
findFolks web app done in python-flask with MySQL as db. 

## List of use cases, query, explanation:

Requires no paramters. 
Shows all events upcoming next 3 days.
```sql
SELECT an_event.event_id, title, an_event.description AS event_description, start_time, end_time, location_name, zipcode, a_group.group_id, a_group.group_name, category, keyword, a_group.description AS group_description FROM an_event NATURAL JOIN organize NATURAL JOIN about JOIN a_group ON(about.group_id = a_group.group_id) WHERE end_time BETWEEN NOW() AND DATE_ADD(NOW(), INTERVAL 3 DAY)
```

Requires no paramters. 
Shows all interests.
```sql
SELECT * FROM interest
```

Requires category, keyword. 
Shows all groups of specified interest (category, keyword). 
```sql
SELECT * FROM interest NATURAL JOIN a_group NATURAL JOIN about WHERE (category = %s AND keyword = %s)
```

Requires username, password. 
User interface to log in.
```sql
SELECT * FROM member WHERE username = %s and password = md5(%s)
```

Requires username, password, firstName, lastName, email, zipcode. 
User interface to register.
```sql
INSERT INTO member(username, password, firstName, lastName, email, zipcode) VALUES(%s, md5(%s), %s, %s, %s, %s)
```

Requires username. 
Shows all groups user is in.
```sql
SELECT group_id, group_name, description, category, keyword, creator, authorized FROM a_group NATURAL JOIN about NATURAL JOIN belongs_to WHERE (username = %s)
```

Requires username. 
Shows all upcoming events user signed up for.
```sql
SELECT an_event.event_id, title, an_event.description AS event_description, start_time, end_time, location_name, zipcode, a_group.group_id, a_group.group_name, category, keyword, a_group.description AS group_description FROM sign_up NATURAL JOIN an_event NATURAL JOIN organize NATURAL JOIN about JOIN a_group ON(organize.group_id = a_group.group_id) WHERE (username = %s) AND (NOW() < end_time)
```

Requires username, username. 
Shows personal friend requests received.
```sql
SELECT friend_of FROM friend WHERE (friend_to = %s) AND friend_of NOT IN (SELECT friend_to FROM friend WHERE (friend_of = %s))
```

Requires username, username. 
Shows accepted friends.
```sql
SELECT friend_of FROM friend WHERE (friend_to = %s) AND friend_of IN (SELECT friend_to FROM friend WHERE (friend_of = %s))
```

Requires username, username. 
Shows other community members. 
```sql
SELECT username FROM member WHERE username NOT IN (SELECT friend_of FROM friend WHERE (friend_to = %s)) AND (username != %s)
```

Requires username, username. 
Sends a friend request.
```sql
INSERT INTO friend(friend_of, friend_to) VALUES(%s, %s)
```

Requires username, username. 
Registers a friend from a friend request.
```sql
INSERT INTO friend(friend_of, friend_to) VALUES(%s, %s)
```

Requires username. 
Shows all interests, where user is interested in.
```sql
SELECT * FROM interested_in WHERE username = %s
```

Requires username, username. 
Shows interests, where user would be interested in based on similar category.
```sql
SELECT category, keyword FROM interest WHERE (category, keyword) NOT IN (SELECT category, keyword FROM interested_in WHERE (username = %s)) AND category IN (SELECT category FROM interested_in WHERE (username = %s))
```

Requires username, username. 
Shows other interests people are interested in, where user is not already interested in.
```sql
SELECT category, keyword FROM interest WHERE (category, keyword) NOT IN (SELECT category, keyword FROM interested_in WHERE (username = %s)) AND category NOT IN (SELECT category FROM interested_in WHERE (username = %s))
```

Requires category, keyword, username, category, keyword. 
Register an interest.
```sql
INSERT INTO interest(category, keyword) VALUES(%s, %s); INSERT INTO interested_in(username, category, keyword) VALUES(%s, %s, %s);
```

Requires username. 
Shows all groups, where user is in.
```sql
SELECT group_id, group_name, description, category, keyword, creator, authorized FROM a_group NATURAL JOIN about NATURAL JOIN belongs_to WHERE (username = %s)
```

Requires username, username. 
Shows groups, where user might be interested in based on similar category.
```sql
SELECT category, keyword, group_id, group_name, description, creator FROM a_group NATURAL JOIN about NATURAL JOIN interested_in WHERE category IN (SELECT category FROM interested_in WHERE (username = %s)) AND group_id NOT IN (SELECT group_id FROM belongs_to WHERE (username = %s))
```

Requires username, username. 
Shows other groups people are in, where user is not part of.
```sql
SELECT category, keyword, group_id, group_name, description, creator FROM a_group NATURAL JOIN about NATURAL JOIN interested_in WHERE category NOT IN (SELECT category FROM interested_in WHERE (username = %s)) AND group_id NOT IN (SELECT group_id FROM belongs_to WHERE (username = %s))
```

Requires group_name, description, username, category, keyword, username. 
Creates a group.
```sql
INSERT INTO a_group(group_name, description, creator) VALUES(%s, %s, %s); INSERT INTO about(group_id, category, keyword) VALUES(LAST_INSERT_ID(), %s, %s); INSERT INTO belongs_to(group_id, username, authorized) VALUES(LAST_INSERT_ID(), %s, true);
```

Requires category, keyword, username, category, keyword, group_name, description, username, category, keyword, username. 
Create a group by creating an interest prior.
```sql
INSERT INTO interest(category, keyword) VALUES(%s, %s); INSERT INTO interested_in(username, category, keyword) VALUES(%s, %s, %s);

INSERT INTO a_group(group_name, description, creator) VALUES(%s, %s, %s); INSERT INTO about(group_id, category, keyword) VALUES(LAST_INSERT_ID(), %s, %s); INSERT INTO belongs_to(group_id, username, authorized) VALUES(LAST_INSERT_ID(), %s, true);
```

Requires username, group_name. 
Join a group.
```sql
INSERT INTO belongs_to(group_id, username, authorized) SELECT group_id, %s, false FROM a_group WHERE (group_name = %s)
```

Requires no parameters. 
Shows all locations, where events have taken place or are planned to be taken at. 
```sql
SELECT * FROM location
```

Requires location_name, description, address, int(latitude), int(longitude), int(zipcode). 
Register a location.
```sql
INSERT INTO location(location_name, description, address, latitude, longitude, zipcode) VALUES(%s, %s, %s, %s, %s, %s)
```

Requires username. 
Shows all groups user is authorized to make events for.
```sql
SELECT group_id, group_name, description, category, keyword, creator, authorized FROM a_group NATURAL JOIN about NATURAL JOIN belongs_to WHERE (username = %s AND authorized = true)
```

Requires username. 
Shows all upcoming events user signed up for.
```sql
SELECT an_event.event_id, title, an_event.description AS event_description, start_time, end_time, location_name, zipcode, a_group.group_id, a_group.group_name, category, keyword, a_group.description AS group_description FROM sign_up NATURAL JOIN an_event NATURAL JOIN organize NATURAL JOIN about JOIN a_group ON(organize.group_id = a_group.group_id) WHERE (username = %s) AND (NOW() < end_time)
```

Requires username, username. 
Shows all upcoming events his/her friends signed up for.
```sql
SELECT an_event.event_id, title, an_event.description AS event_description, start_time, end_time, location_name, zipcode, username, a_group.group_id, a_group.group_name, category, keyword, a_group.description AS group_description FROM an_event NATURAL JOIN organize NATURAL JOIN sign_up NATURAL JOIN about JOIN a_group ON(organize.group_id = a_group.group_id) WHERE username IN (SELECT friend_of FROM friend WHERE (friend_to = %s) AND friend_of IN (SELECT friend_to FROM friend WHERE (friend_of = %s))) AND (NOW() < end_time)
```

Requires username, username, username. 
Shows all upcoming events user might be interested in, where user did not sign up for.
```sql
SELECT an_event.event_id, title, an_event.description AS event_description, start_time, end_time, location_name, zipcode, a_group.group_id, a_group.group_name, category, keyword, a_group.description AS group_description FROM an_event NATURAL JOIN organize NATURAL JOIN sign_up NATURAL JOIN about JOIN a_group ON(organize.group_id = a_group.group_id) WHERE (category) IN (SELECT category FROM interested_in WHERE (username = %s)) AND (event_id) NOT IN (SELECT event_id FROM sign_up WHERE (username = %s)) AND (username != %s) AND (NOW() < end_time)
```

Requires username, username. 
Shows all other upcoming events, where user may not be interested in and did not sign up for.
```sql
SELECT an_event.event_id, title, an_event.description AS event_description, start_time, end_time, location_name, zipcode, a_group.group_id, a_group.group_name, category, keyword, a_group.description AS group_description FROM an_event NATURAL JOIN organize NATURAL JOIN sign_up NATURAL JOIN about JOIN a_group ON(organize.group_id = a_group.group_id) WHERE (category) NOT IN (SELECT category FROM interested_in WHERE (username = %s)) AND (username != %s) AND (NOW() < end_time)
```

Requires username. 
Shows all past events, where user signed up for.
```sql
SELECT an_event.event_id, title, an_event.description AS event_description, start_time, end_time, location_name, zipcode, a_group.group_id, a_group.group_name, a_group.description AS group_description, category, keyword, rating AS your_rating FROM sign_up NATURAL JOIN an_event NATURAL JOIN organize NATURAL JOIN about JOIN a_group ON(organize.group_id = a_group.group_id) WHERE (username = %s) AND (NOW() > end_time)
```

Requires username. 
Shows all other past events, where user did not sign up for.
```sql
SELECT DISTINCT an_event.event_id, title, an_event.description AS location_description, start_time, end_time, location_name, zipcode, a_group.group_id, a_group.group_name, category, keyword, a_group.description AS group_description FROM sign_up NATURAL JOIN an_event NATURAL JOIN organize NATURAL JOIN about JOIN a_group ON(organize.group_id = a_group.group_id) WHERE (event_id) NOT IN (SELECT event_id FROM sign_up WHERE (username = %s)) AND (NOW() > end_time)
```

Requires username. 
Shows all ratings for past events, where user is part of the group.
```sql
SELECT an_event.event_id, title, an_event.description AS event_description, start_time, end_time, location_name, zipcode, a_group.group_id, a_group.group_name, a_group.description AS group_description, category, keyword, AVG(rating) AS avg_rating FROM sign_up NATURAL JOIN organize NATURAL JOIN about NATURAL JOIN an_event JOIN a_group ON(organize.group_id = a_group.group_id) WHERE (rating IS NOT NULL) AND (organize.group_id) IN (SELECT group_id FROM belongs_to WHERE (username = %s)) AND (NOW() > end_time) GROUP BY organize.group_id, event_id, category, keyword
```

Requires username. 
Shows all ratings for other past events, where user is not part of the group. 
```sql
SELECT an_event.event_id, title, an_event.description AS event_description, start_time, end_time, location_name, zipcode, a_group.group_id, a_group.group_name, a_group.description AS group_description, category, keyword, AVG(rating) AS avg_rating FROM sign_up NATURAL JOIN organize NATURAL JOIN about NATURAL JOIN an_event JOIN a_group ON(organize.group_id = a_group.group_id) WHERE (rating IS NOT NULL) AND (organize.group_id) NOT IN (SELECT group_id FROM belongs_to WHERE (username = %s)) AND (NOW() > end_time) GROUP BY organize.group_id, event_id, category, keyword
```

Requires rating, event_id, username. 
Rate an past event, where user signed up for (it is only visible via href from previous SQL: past events user signed up for)
```sql
UPDATE sign_up SET rating = %s WHERE event_id = %s AND username = %s
```

Requires title, event_description, start_time, end_time, event_location, event_zipcode, username, group_id. 
Creates an event. 
```sql
INSERT INTO an_event(title, description, start_time, end_time, location_name, zipcode) VALUES(%s, %s, %s, %s, %s, %s); INSERT INTO sign_up(event_id, username) VALUES(LAST_INSERT_ID(), %s); INSERT INTO organize(event_id, group_id) VALUES(LAST_INSERT_ID(), %s)
```

Requires location_name, location_description, address, latitude, longitude, location_zipcode, title, event_description, start_time, end_time, location_event, location_zipcode, username, group_id. 
Create an event, and a location if a prior location does not fit user's need.
```sql
INSERT INTO location(location_name, description, address, latitude, longitude, zipcode) VALUES(%s, %s, %s, %s, %s, %s); INSERT INTO an_event(title, description, start_time, end_time, location_name, zipcode) VALUES(%s, %s, %s, %s, %s, %s); INSERT INTO sign_up(event_id, username) VALUES(LAST_INSERT_ID(), %s); INSERT INTO organize(event_id, group_id) VALUES(LAST_INSERT_ID(), %s)
```

Requires event_id, username. 
Sign up for an event.
```sql
INSERT INTO sign_up(event_id, username) VALUES(%s, %s)
```