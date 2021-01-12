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
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# TODO: connect to a local postgresql database
migrate = Migrate(app, db)
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    shows = db.relationship('Show', backref='venue')# default to Lazy = True

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    shows = db.relationship('Show', backref='artist')# default to Lazy = True
    
    # TODO: implement any missing fields, as a database migration using Flask-Migrate
class Show(db.Model):
    __tablename__ = 'show'
    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'))
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'))
    show_time = db.Column(db.DateTime())
# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
  
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

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
  # TODO12: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  #DONE
  data = []
  locations = []
  venues = Venue.query.all()

  for venue in venues:
    locations.append(venue.city)
    locations.append(venue.state)

  for location in locations:
    location = Venue.query.filter_by(city=location[0], state=location[1]).all()
    listVenues = []

    for venue in location:
      listVenues.append({
        'id': venue.id,
        'name': venue.name,
        'num_upcoming_shows': Show.query.filter_by(venue_id=venue.id).count()
      })
    data.append({
      'city': city[0],
      'state': city[1],
      'venues': listVenues
    })

  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO11: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  key = request.form.get('search_term')

  count = Venue.query.filter(Venue.name.ilike('%'+ key +'%')).count()
  venues = Venue.query.filter(Venue.name.ilike('%'+ key +'%')).all()

  listVenue = []
  for venue in venues:
    listVenue.append({
      'id': venue.id,
      'name': venue.name,
      'num_upcoming_shows': Show.query.filter_by(venue_id=venue.id).count()
    })
  response = {
    'count': count,
    'data': listVenue
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO10: replace with real venue data from the venues table, using venue_id
  venue = Venue.query.get(venue_id)
  print(venue)
  shows = Show.query.filter_by(venue_id=venue_id).all()
  past_shows = []
  upcoming_shows = []
  current_time = datetime.now()

  for show in shows:
    data = {
          "artist_id": show.artist_id,
          "artist_name": show.artist.name,
           "artist_image_link": show.artist.image_link,
           "start_time": format_datetime(str(show.show_time))
        }
    if show.show_time > current_time:
      upcoming_shows.append(data)
    else:
      past_shows.append(data)

  data={
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description":venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows)
  }
  #data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  form = request.form.get('seeking_description')
  print(form)
  error = False
  try:
    new_venue_data = Venue(
      name=request.form.get('name'),
      genres=request.form.getlist('genres'),
      address=request.form.get('address'),
      city=request.form.get('city'),
      state=request.form.get('state'),
      phone=request.form.get('phone'),
      website=request.form.get('website'),
      facebook_link=request.form.get('facebook_link'),
      image_link=request.form.get('image_link'),
      seeking_talent=request.form.get('talent') == 'True',
      seeking_description=request.form.get('seeking_description')
      )
    db.session.add(new_venue_data)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
  finally:
    db.session.close()
  if error:
    # TODO: on unsuccessful db insert, flash an error instead.
    # DONE
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  else:
    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')

  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  error = False
  try:
    artist = Artist.query.get(artist_id)
    shows = Show.query.filter_by(artist_id = artist_id)
    for show in shows:
      db.session.delete(show)
      db.session.delete(artist)
      db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
    if not error:
      flash('Artist ' + artist.name + ' was successfully deleted')
      return jsonify({ 'success': True })
  flash('Artist ' + artist.name + ' could not be deleted')
  return jsonify({ 'success': False })
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data = []
  artists = Artist.query.all()
  for artist in artists:
    data.append({
      'id': artist.id,
      'name': artist.name
    })
  return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  key = request.form.get('search_term')
  count = Artist.query.filter(Artist.name.ilike('%'+ key +'%')).count()
  query = Artist.query.filter(Artist.name.ilike('%'+ key +'%')).all()
  listArtists = []

  for artist in query:
    listArtists.append({
      'id': artist.id,
      'name': artist.name,
      'num_upcoming_shows': Show.query.filter_by(artist_id=artist.id).count()
    })
  response = {
    'count': count,
    'data': listArtists
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
# shows the venue page with the given venue_id
# TODO: replace with real venue data from the venues table, using venue_id
  
  past_shows = []
  upcoming_shows = []

  past_shows_count = 0
  upcoming_shows_count = 0

  artist = Artist.query.get(artist_id)


  for show in Show.query.filter_by(artist_id=artist_id).all():
    if show.show_time >= datetime.now():
      venue = Venue.query.get(show.venue_id)
      upcoming_shows_count+=1
      upcoming_shows.append({
        'venue_id': venue.id,
        'venue_name': venue.name,
        'venue_image_link': venue.image_link,
        'start_time': str(show.show_time)
      })
    else:
      venue = Venue.query.get(show.venue_id)
      past_shows_count+=1
      past_shows.append({
        'venue_id': venue.id,
        'venue_name': venue.name,
        'venue_image_link': venue.image_link,
        'start_time': str(show.time)
      })
  data = {
    'id': artist_id,
    'name': artist.name,
    'genres': artist.genres,
    'city': artist.city,
    'state': artist.state,
    'phone': artist.phone,
    'website': artist.website,
    'facebook_link': artist.facebook_link,
    'seeking_venue': True,
    'seeking_description': artist.seeking_description,
    'image_link': artist.image_link,
    'past_shows': past_shows,
    'upcoming_shows':upcoming_shows,
    'past_shows_count': past_shows_count,
    'upcoming_shows_count': upcoming_shows_count
  }
  
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)

  artist_data = {
        "id": artist.id,
        "name": artist.name,
        "genres": artist.genres,
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "facebook_link": artist.facebook_link,
        "image_link": artist.image_link
    }
  # TODO4: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO3: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  # DONE
  try:
    artist = Artist.query.filter_by(id=artist_id).all()[0]

    artist.name=request.form.get('name')
    artist.city=request.form.get('city')
    artist.state=request.form.get('state')
    artist.phone=request.form.get('phone')
    artist.genres=request.form.getlist('genres')
    artist.facebook_link=request.form.get('facebook_link')
    artist.website=request.form.get('website')
    artist.image_link=request.form.get('image_link')
    artist.seeking_venue=request.form.get('seeking_venue') == 'True'
    artist.seeking_description=request.form.get('seeking_description')

    db.session.commit()
  except:
    db.session.rollback()
    flash('An error occurred. Artist could not be updated')
  finally:
    db.session.close()
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  # TODO: populate form with values from venue with ID <venue_id>
  # DONE
  popVenue = Venue.query.get(venue_id)
  venue = {
    "id": popVenue.id,
    "name": popVenue.name,
    "genres": popVenue.genres,
    "address": popVenue.address,
    "city": popVenue.city,
    "state": popVenue.state,
    "phone": popVenue.phone,
    "website": popVenue.website,
    "facebook_link": popVenue.facebook_link,
    "seeking_talent": 'True',
    "seeking_description": popVenue.seeking_description,
    "image_link": popVenue.image_link
  }
  print(venue)
  form = VenueForm(
    name=venue['name'],
    city=venue['city'],
    state=venue['state'],
    address=venue['address'],
    phone=venue['phone'],
    image_link=venue['image_link'],
    genres=venue['genres'],
    facebook_link=venue['facebook_link'],
    website=venue['website'],
    seeking_talent=venue['seeking_talent'],
    seeking_description=venue['seeking_description']
  )
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  #DONE
  error = False
  form = VenueForm()
  try:
    venue = Venue.query.get(venue_id)
    venue.name = form.data['name']
    venue.city = form.data['city']
    venue.state = form.data['state']
    venue.address = form.data['address']
    venue.phone = form.data['phone']
    venue.image_link = form.data['image_link']
    venue.facebook_link = form.data['facebook_link']
    venue.genres = form.data['genres']
    venue.seeking_talent = True
    venue.seeking_description = form.data['seeking_description']
    venue.website = form.data['website']
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  
  # on successful db insert, flash success
  if not error:
    flash('Venue ' + form.data['name'] + ' was successfully Updated!')
  else:
    flash('An error occurred. Venue ' + form.data['name'] + ' could not be Updated.')

  
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
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  error = False
  try:
    new_artist_data = Artist(
        name=request.form.get('name'),
        city=request.form.get('city'),
        state=request.form.get('state'),
        phone=request.form.get('phone'),
        genres=request.form.getlist('genres'),
        facebook_link=request.form.get('facebook_link'),
        image_link=request.form.get('image_link'),
        seeking_venue=request.form.get('seeking_venue') == 'True',
        seeking_description=request.form.get('seeking_description')
      )
    db.session.add(new_artist_data)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    
    db.session.close()
  if error:
    # TODO: on unsuccessful db insert, flash an error instead.
    # DONE
    flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  else:
    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')

  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  # DONE 
  data=[]
  list_of_shows = Show.query.all()
  print(list_of_shows)
  for show in list_of_shows:
    listVenues = Venue.query.get(show.venue_id)
    listArtists = Artist.query.get(show.artist_id)
    data.append(
      {
      'venue_id': show.venue_id,
      'venue_name': listVenues.name,
      'artist_id': show.artist_id,
      'artist_name': listArtists.name,
      'artist_image_link' : listArtists.image_link,
      'start_time': str(show.show_time) 
    }
    )
    print (show.show_time)
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
  # DONE
  time_date = request.form.get('start_time')
  print(time_date)
  error = False
  try:
    new_show_data = Show(
        artist_id=request.form.get('artist_id'),
        venue_id=request.form.get('venue_id'),
        show_time=request.form.get('start_time'),
      )
    db.session.add(new_show_data)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
   # TODO: on unsuccessful db insert, flash an error instead.
   # DONE
   flash('An error occurred. Show could not be listed.')
  
  else:
    # on successful db insert, flash success
    flash('Show was successfully listed!')
  
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
