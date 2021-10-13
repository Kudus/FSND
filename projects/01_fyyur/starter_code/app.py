#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import FlaskForm
from sqlalchemy.orm import backref
from forms import *
from flask_migrate import Migrate
from datetime import datetime
import sys
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)
# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

# Implement Show models, and complete all model relationships and properties, as a database migration.

class Show(db.Model):
    __tablename__ = 'Show'
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), primary_key=True)
    start_time = db.Column(db.DateTime, primary_key=True)
    
    artist = db.relationship('Artist', back_populates='venues')
    venue = db.relationship('Venue', back_populates='artists')


class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500), nullable=False, default='venue.jpg')
    genres = db.Column(db.ARRAY(db.String), nullable=False)
    facebook_link = db.Column(db.String(120), nullable=False)
    website_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String)
    
    artists = db.relationship('Show', back_populates='venue')

    def __repr__(self):
      return f'<Venue {self.name} {self.city} {self.state}>'

    # implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.ARRAY(db.String), nullable=False)
    image_link = db.Column(db.String(500), nullable=False, default='artist.jpg')
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean(), default=False)
    seeking_description = db.Column(db.String)

    venues = db.relationship('Show',back_populates='artist')


    def __repr__(self):
      return f'<Artist {self.name} {self.genres} {self.state}>' 

    # implement any missing fields, as a database migration using Flask-Migrate

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  value = str(value)
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Helpers.
#----------------------------------------------------------------------------#

def date_shows(shows):
  upcoming_shows = [show for show in shows if datetime.now() < show.start_time]
  past_shows = [show for show in shows if datetime.now() > show.start_time]
  return upcoming_shows, past_shows

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # replace with real venues data.
  # num_upcoming_shows should be aggregated based on number of upcoming shows per venue
  venues = Venue.query.all()
  location = [ (venue.city, venue.state) for venue in venues ]
  distinct_location = list(set(location))
  data = []
  for loc in distinct_location:
    data.append({ "city": loc[0],
          "state": loc[1],
          "venues": []
          })
    loc_venues = Venue.query.filter_by(city=loc[0], state=loc[1]).all()
    for loc_venue in loc_venues:
      data[-1]["venues"].append({
        "id": loc_venue.id,
        "name": loc_venue.name,
        "num_upcoming_shows": len(date_shows(loc_venue.artists)[0])
      })
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term=request.form.get('search_term', '')
  if search_term:
    response = {}
    response["data"] = Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all()
    response["count"] = len(response["data"])
    return render_template('pages/search_venues.html', results=response, search_term=search_term)
  return redirect(url_for('venues'))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # replace with real venue data from the venues table, using venue_id
  venue = Venue.query.get_or_404(venue_id)
  dated_shows = date_shows(venue.artists)
  data = {"id": venue_id,
          "name": venue.name,
          "genres": venue.genres,
          "address": venue.address,
          "city": venue.city,
          "state": venue.state,
          "phone": venue.phone,
          "website": venue.website_link,
          "facebook_link": venue.facebook_link,
          "seeking_talent": venue.seeking_talent,
          "seeking_description": venue.seeking_description,
          "image_link": venue.image_link,
          "upcoming_shows": dated_shows[0],
          "upcoming_shows_count": len(dated_shows[0]),
          "past_shows": dated_shows[1],
          "past_shows_count": len(dated_shows[1])
          }
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # insert form data as a new Venue record in the db, instead
  try:
    data = request.form
    # modify data to be the data object returned from db insertion
    venue = Venue(name=data['name'],
                  city=data['city'],
                  state=data['state'],
                  address=data['address'],
                  phone=data['phone'],
                  genres=data.getlist('genres'),
                  facebook_link=data['facebook_link'],
                  image_link=data['image_link'],
                  website_link=data['website_link'],
                  seeking_talent= True if data['seeking_talent']=='True' else False,
                  # seeking_talent= True if data['seeking_talent'] else False,
                  # seeking_talent= data['seeking_talent'],
                  seeking_description=data['seeking_description'])
    db.session.add(venue)
    db.session.commit()
    # on successful db insert, flash success
    flash('Venue ' + data['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    # on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Venue ' + data['name'] + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    print(sys.exc_info())
  finally:
    db.session.close()
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>/delete', methods=['POST', 'DELETE'])
def delete_venue(venue_id):
  # Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
    venue = Venue.query.get_or_404(venue_id)
    shows = venue.artists
    copy_of_shows = shows[:]
    for show in copy_of_shows:
      # shows.remove(show)
      db.session.delete(show)
    db.session.delete(venue)
    db.session.commit()
  except:
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return redirect(url_for('index'))
  

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # replace with real data returned from querying the database
  data = Artist.query.all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term=request.form.get('search_term', '')
  if search_term:
    response = {}
    response['data'] = Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).all()
    response['count'] = len(response['data'])
    return render_template('pages/search_artists.html', results=response, search_term=search_term)
  return redirect(url_for('artists'))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # replace with real artist data from the artist table, using artist_id
  artist = Artist.query.get_or_404(artist_id)
  dated_shows = date_shows(artist.venues)
  data = {"id": artist_id,
        "name": artist.name,
        "genres": artist.genres,
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "website": artist.website_link,
        "facebook_link": artist.facebook_link,	
        "seeking_venue": artist.seeking_venue,
        "seeking_description": artist.seeking_description,	
        "image_link": artist.image_link,
        "upcoming_shows": dated_shows[0],
        "upcoming_shows_count": len(dated_shows[0]),
        "past_shows": dated_shows[1],
        "past_shows_count": len(dated_shows[1])
        }
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  # populate form with fields from artist with ID <artist_id>
  artist = Artist.query.get_or_404(artist_id)
  form.name.data = artist.name
  form.city.data = artist.city
  form.state.data = artist.state
  form.phone.data = artist.phone
  form.genres.data = artist.genres
  form.facebook_link.data = artist.facebook_link
  form.image_link.data = artist.image_link
  form.website_link.data = artist.website_link
  form.seeking_venue.data = artist.seeking_venue
  form.seeking_description.data = artist.seeking_description
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  try:
    artist = Artist.query.get_or_404(artist_id)
    data = request.form
    artist.name=data['name']
    artist.city=data['city']
    artist.state=data['state']
    artist.phone=data['phone']
    artist.genres=data.getlist('genres')
    artist.facebook_link=data['facebook_link']
    artist.image_link=data['image_link']
    artist.website_link =data['website_link']
    artist.seeking_venue= True if data['seeking_venue'] else False
    artist.seeking_description=data['seeking_description']

    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  # populate form with values from venue with ID <venue_id>
  venue = Venue.query.get_or_404(venue_id)
  form.name.data = venue.name
  form.city.data = venue.city
  form.state.data = venue.state
  form.address.data = venue.address
  form.phone.data = venue.phone
  form.genres.data = venue.genres
  form.facebook_link.data = venue.facebook_link
  form.image_link.data = venue.image_link
  form.website_link.data = venue.website_link
  form.seeking_talent.data = venue.seeking_talent
  form.seeking_description.data = venue.seeking_description
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  try:
    venue = Venue.query.get_or_404(venue_id)
    data = request.form
    venue.name=data['name']
    venue.city=data['city']
    venue.state=data['state']
    venue.address=data['address']
    venue.phone=data['phone']
    venue.genres=data.getlist('genres')
    venue.facebook_link=data['facebook_link']
    venue.image_link=data['image_link']
    venue.website_link=data['website_link']
    venue.seeking_talent= True if data['seeking_talent'] else False
    venue.seeking_description=data['seeking_description']

    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # insert form data as a new Venue record in the db, instead
  try:
    data = request.form
    # modify data to be the data object returned from db insertion
    artist = Artist(name=data['name'],
                    city=data['city'],
                    state=data['state'],
                    phone=data['phone'],
                    genres=data.getlist('genres'),
                    facebook_link=data['facebook_link'],
                    image_link=data['image_link'],
                    website_link =data['website_link'],
                    seeking_venue= True if data['seeking_venue'] else False,
                    seeking_description=data['seeking_description'])
    db.session.add(artist)
    db.session.commit()
    # on successful db insert, flash success
    flash('Artist ' + data['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    # on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Artist ' + data['name'] + ' could not be listed.')
    print(sys.exc_info())
  finally:
    db.session.close()
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # replace with real venues data.
  shows = Show.query.all()
  data = []
  for show in shows:
    show_dict = {"venue_id": show.venue_id,
                "venue_name": show.venue.name,
                "artist_id": show.artist_id,
                "artist_name": show.artist.name,
                "artist_image_link": show.artist.image_link,
                "start_time": show.start_time
                }
    data.append(show_dict)
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  try:
    data = request.form
    
    show = Show(venue_id=data['venue_id'],
                artist_id=data['artist_id'],
                start_time=data['start_time'])
    db.session.add(show)
    db.session.commit()
    # on successful db insert, flash success
    flash('Show was successfully listed!')
  except:
    db.session.rollback()
    # on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    print(sys.exc_info())
  finally:
    db.session.close()
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
