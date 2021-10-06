from app import db, Venue, Artist, Show

v = Venue(name = "Park Square Live Music & Coffee",
genres= ["Rock n Roll", "Jazz", "Classical", "Folk"],
address = "34 Whiskey Moore Ave",
city = "San Francisco",
state = "CA",
phone = "415-000-1234",
website_link = "https://www.parksquarelivemusicandcoffee.com",
facebook_link = "https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
seeking_talent = False,
image_link = "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80")


s1 = Show(start_time = "2035-04-01T20:00:00.000Z")

s2 = Show(start_time = "2035-04-08T20:00:00.000Z")

s3 = Show(start_time = "2035-04-15T20:00:00.000Z")


a = Artist(name = "The Wild Sax Band",
genres = ["Jazz", "Classical"],
city = "San Francisco",
state = "CA",
phone = "432-325-5432")
    

s1.artist = a
s2.artist = a
s3.artist = a

s_list = [s1,s2,s3]

v.artists.extend(s_list)

db.session.add_all(s_list)

db.session.commit()