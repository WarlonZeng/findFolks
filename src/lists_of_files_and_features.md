# findFolks
findFolks web app done in python-flask with MySQL as db. 

## Lists of files and all features used in this application (sorted by testing order):

### index.html 
1. Shows all events upcoming next 3 days.
2. Shows all interests.
3. Has method to show groups with selected interest.
4. Provides service to login, register.

### viewInterestGroup.html
1. Shows all groups of specified interest (category, keyword). 

### login.html 
1. User interface to log in.

### register.html
1. User interface to register.

### home.html 
1. Shows all groups user is in.
2. Shows all upcoming events user signed up for.
3. Provides service for friends, interests, groups, locations, and events.

### friends.html
1. Shows personal friend requests received.
2. Shows accepted friends.
3. Shows other community members. 
4. Has method to send friend requests and accept friend requests.

### interests.html 
1. Shows all interests, where user is interested in.
2. Shows interests, where user would be interested in based on similar category.
3. Shows other interests people are interested in, where user is not already interested in.
4. Has method to register an interest.

### groups.html 
1. Shows all groups, where user is in.
2. Shows groups, where user might be interested in based on similar category.
3. Shows other groups people are in, where user is not part of.
4. Has a method to create or join a group.

### locations.html
1. Shows all locations, where events have taken place or are planned to be taken at. 
2. Has method to register a location.

### events.html
1. Shows all groups user is authorized to make events for.
2. Shows all upcoming events user signed up for.
3. Shows all upcoming events his/her friends signed up for.
4. Shows all upcoming events user might be interested in, where user did not sign up for.
5. Shows all other upcoming events, where user may not be interested in and did not sign up for.
6. Shows all past events, where user signed up for.
7. Shows all other past events, where user did not sign up for.
8. Shows all ratings for past events, where user is part of the group.
9. Shows all ratings for other past events, where user is not part of the group. 
10. Has method to rate an past event, where user signed up for.
11. Provides method to create an event or sign up for an event.

### createEvent.html
1. Has method to create an event, and a location if a prior location does not fit user's need.