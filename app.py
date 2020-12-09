#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import (
    Flask, 
    render_template, 
    request, 
    Response, 
    flash, 
    redirect, 
    url_for
)
from flask import config
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler, error
from flask_wtf import FlaskForm
from sqlalchemy.orm import backref
from forms import *
from flask_migrate import Migrate


#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#
app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
from  models import *
db.create_all()
db.session.commit()
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
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
    error=False
    data=[]
    try:
      venues=Venue.query.order_by(Venue.city,Venue.state).all()
      venuesInSameArea=[]
      venuesInSameArea.clear()
      data.clear()
      venuesInSameArea.append({
        "id": venues[0].id,
        "name": venues[0].name,
        "num_upcoming_shows": len(db.session.query(Show).filter(Show.venue_id == venues[0].id).filter(Show.start_time > datetime.now()).all())
      })
      for i in range(1,len(venues)):
            if venues[i].city==venues[i-1].city and venues[i].state==venues[i-1].state :
                  venuesInSameArea.append({
                  "id": venues[i].id,
                  "name": venues[i].name,
                  "num_upcoming_shows": len(db.session.query(Show).filter(Show.venue_id == venues[i].id).filter(Show.start_time > datetime.now()).all())
                  })
            else :
                  data.append({
                      "city": venues[i-1].city,
                      "state": venues[i-1].state,
                      "venues": venuesInSameArea.copy()
                  })
                  venuesInSameArea.clear()
                  venuesInSameArea.append({
                  "id": venues[i].id,
                  "name": venues[i].name,
                  "num_upcoming_shows": len(db.session.query(Show).filter(Show.venue_id == venues[i].id).filter(Show.start_time > datetime.now()).all())
                  })
      data.append({
        "city": venues[len(venues)-1].city,
        "state": venues[len(venues)-1].state,
        "venues": venuesInSameArea.copy()
                  })
      return render_template('pages/venues.html', areas=data);      
    except :
# incase the operation failed we can show empty  page so a user can still use search
      return render_template('pages/venues.html');
      
 
  
  

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  data=[]
  search_term=request.form.get('search_term', '')
  venues=Venue.query.filter(Venue.name.ilike('%'+search_term+'%')).all()
  for venue in venues :
       data.append({
         "id": venue.id,
         "name": venue.name,
         "num_upcoming_shows": len(db.session.query(Show).filter(Show.venue_id == venue.id).filter(Show.start_time > datetime.now()).all()),
       }) 
  response={
    "count": len(data),
    "data": data
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  #try :
    venue=Venue.query.get(venue_id)
    past_shows = db.session.query(Show).join(Artist).filter(Show.venue_id==venue_id).filter(Show.start_time<=datetime.now()).all()
    upcoming_shows = db.session.query(Show).join(Artist).filter(Show.venue_id==venue_id).filter(Show.start_time>datetime.now()).all()
    pshows=[]
    for past_show in past_shows:
      pshows.append({
        "artist_id": past_show.artist_id,
        "artist_name": past_show.artist.name,
        "artist_image_link": past_show.artist.image_link,
        "start_time": str(past_show.start_time)
      })   
    upshows=[]
    for upcoming_show in upcoming_shows:
      upshows.append({
        "artist_id": upcoming_show.artist_id,
        "artist_name": upcoming_show.artist.name,
        "artist_image_link": upcoming_show.artist.image_link,
        "start_time": str(upcoming_show.start_time)
      })    
    data={
      "id": venue.id,
      "name": venue.name,
      "genres": venue.genres,
      "city": venue.city,
      "address": venue.address,
      "state": venue.state,
      "phone": venue.phone,
      "facebook_link": venue.facebook_link,
      "website": venue.website,
      "image_link":venue.image_link,
      "seeking": venue.seeking,
      "seeking_description": venue.seeking_description,
      "past_shows":pshows,
      "upcoming_shows": upshows,
      "past_shows_count": len(pshows),
      "upcoming_shows_count": len(upshows),
    }
    return render_template('pages/show_venue.html', venue=data)
  #except : 
   # return render_template('pages/home.html')

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
  error = False
  try :
    name= request.form['name']
    city = request.form['city']
    state = request.form['state']
    address = request.form['address']
    phone = request.form['phone']
    genres = request.form.getlist('genres')
    facebook_link = request.form['facebook_link']
    #if frontend modified this will be working
    if 'image_link' in request.form :
      image_link = request.form['image_link']
    else :
          image_link= None
    if 'website' in request.form :
      website = request.form['website']
    else :
      website= None 
    if 'seeking' in request.form :
      seeking = True  
    else :
      seeking =False 
    if 'seeking_description' in request.form :
      seeking_description = request.form['seeking_description']
    else :
      seeking_description= None  

    venue = Venue(name=name, city=city, state=state, address=address, phone=phone,
      genres=genres, facebook_link=facebook_link, image_link=image_link, website=website,
      seeking=seeking, seeking_description=seeking_description)
    db.session.add(venue)
    db.session.commit()
  except: 
    error = True
    db.session.rollback()
  finally: 
    db.session.close()
  if error: 
    flash('An error occurred. Venue ' + request.form['name']+ ' could not be listed.')
  else : 
    flash(f'Venue ' + request.form['name'] + ' was successfully listed!')      
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  error = False
  try:
    Venue.query.filter_by(id=venue_id).delete()
    db.session.commit()
  except:
    error = True
    db.session.rollback()
  finally:
    db.session.close()
  if error:
    flash('Deleting Failed! ','error')
  else:
    flash('Venue record was deleted successfully')

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
    data=[]
    data.clear()
    try:
      artists=Artist.query.all()
      for artist in artists:
        data.append({
                    "id"  : artist.id ,
                    "name": artist.name
                    })
      return render_template('pages/artists.html', artists=data)
    except :
  # incase the operation failed we can show empty  page so a user can still use search
      return render_template('pages/artists.html')

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  data=[]
  search_term=request.form.get('search_term', '')
  artists=Artist.query.filter(Artist.name.ilike('%'+search_term+'%')).all()
  for artist in artists :
       data.append({
         "id": artist.id,
         "name": artist.name,
         "num_upcoming_shows": len(db.session.query(Show).filter(Show.artist_id == artist.id).filter(Show.start_time > datetime.now()).all()),
       }) 
  response={
    "count": len(data),
    "data": data
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  try:
    artist=Artist.query.get(artist_id)
    upcoming_shows = db.session.query(Show).join(Venue).filter(Show.artist_id==artist_id).filter(Show.start_time>=datetime.now()).all()
    past_shows = db.session.query(Show).join(Venue).filter(Show.artist_id==artist_id).filter(Show.start_time<datetime.now()).all()    
    pshows=[]
    for past_show in past_shows:
        pshows.append({
         "venue_id": past_show.venue_id,
      "venue_name": past_show.venue.name,
      "artist_image_link": past_show.venue.image_link,
      "start_time": str(past_show.start_time)
        })   
    upshows=[]
    for upcoming_show in upcoming_shows:
        upshows.append({
        "venue_id": upcoming_show.venue_id,
      "venue_name": upcoming_show.venue.name,
      "artist_image_link": upcoming_show.venue.image_link,
        "start_time": str(upcoming_show.start_time)
        })    
    data={
      "id": artist.id,
      "name": artist.name,
      "genres": artist.genres,
      "city": artist.city,
      "state": artist.state,
      "phone": artist.phone,
      "facebook_link": artist.facebook_link,
      "image_link":artist.image_link,
      "website": artist.website,
      "seeking": artist.seeking,
      "seeking_description": artist.seeking_description,
      "past_shows":pshows,
      "upcoming_shows": upshows,
      "past_shows_count": len(pshows),
      "upcoming_shows_count": len(upshows),
    }
    return render_template('pages/show_artist.html', artist=data)
  except : 
      return render_template('pages/home.html')



#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  # TODO: populate form with fields from artist with ID <artist_id>
  artist=Artist.query.get(artist_id)
  form = ArtistForm(name=artist.name,city=artist.city,state=artist.state,
         phone=artist.phone,genres=artist.genres,facebook_link=artist.facebook_link,
         seeking = artist.seeking,
         seeking_description= artist.seeking_description,
         website = artist.website
         )
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  error = False
  try:  
    artist=Artist.query.get(artist_id)
    artist.name= request.form['name']
    artist.city = request.form['city']
    artist.state = request.form['state']
    artist.phone = request.form['phone']
    artist.genres = request.form.getlist('genres')
    artist.facebook_link = request.form['facebook_link']
       #if frontend modified this will be working
    if 'image_link' in request.form :
      artist.image_link = request.form['image_link']
    else :
      artist.image_link= None
    if 'website' in request.form :
      artist.website = request.form['website']
    else :
      artist.website= None 
    if 'seeking' in request.form :
      artist.seeking = True  
    else :
      artist.seeking =False 
    if 'seeking_description' in request.form :
      artist.seeking_description = request.form['seeking_description']
    else :
      artist.seeking_description= None   
    db.session.commit()
  except:
    error = True
    db.session.rollback()
  finally:
    db.session.close()
  if error:
    flash(f'An error occurred. Artist  : '+request.form['name'] +'could not be updated.','error') 
  else:
    flash('Artist ' + request.form['name'] + ' was successfully updated!')

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  # TODO: populate form with values from venue with ID <venue_id>
  venue=Venue.query.get(venue_id)
  form = VenueForm(name=venue.name,city=venue.city,state=venue.state,
         phone=venue.phone,genres=venue.genres,facebook_link=venue.facebook_link,
         address=venue.address,
         website = venue.website,
         seeking = venue.seeking,
         seeking_description= venue.seeking_description
  )

  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  error = False
  try:  
    venue=Venue.query.get(venue_id)
    venue.name= request.form['name']
    venue.city = request.form['city']
    venue.state = request.form['state']
    venue.address = request.form['address']
    venue.phone = request.form['phone']
    venue.genres = request.form.getlist('genres')
    venue.facebook_link = request.form['facebook_link']
       #if frontend modified this will be working
    if 'image_link' in request.form :
      venue.image_link = request.form['image_link']
    else :
      venue.image_link= None
    if 'website' in request.form :
      venue.website = request.form['website']
    else :
      venue.website= None 
    if 'seeking' in request.form :
      venue.seeking = True  
    else :
      venue.seeking =False 
    if 'seeking_description' in request.form :
      venue.seeking_description = request.form['seeking_description']
    else :
      venue.seeking_description= None   
    db.session.commit()
  except:
    error = True
    db.session.rollback()
  finally:
    db.session.close()
  if error:
    flash(f'An error occurred. Venue  : '+request.form['name'] +'could not be updated.','error') 
  else:
    flash('Venue ' + request.form['name'] + ' was successfully updated!')

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
    name= request.form['name']
    city = request.form['city']
    state = request.form['state']
    phone = request.form['phone']
    genres = request.form.getlist('genres')
    facebook_link = request.form['facebook_link']
       #if frontend modified this will be working
    if 'image_link' in request.form :
      image_link = request.form['image_link']
    else :
          image_link= None
    if 'website' in request.form :
      website = request.form['website']
    else :
      website= None 
    if 'seeking' in request.form :
      seeking = True  
    else :
      seeking =False 
    if 'seeking_description' in request.form :
      seeking_description = request.form['seeking_description']
    else :
      seeking_description= None  

    artist = Artist(name=name, city=city, state=state, phone=phone,
      genres=genres, facebook_link=facebook_link, image_link=image_link, website=website,
      seeking=seeking, seeking_description=seeking_description)
    db.session.add(artist)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
  finally:
    db.session.close()
  if error:
  # TODO: on unsuccessful db insert, flash an error instead.
            # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
        flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.','error')
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
 
  shows = db.session.query(Show).join(Artist).join(Venue).all()

  data = []
  for show in shows: 
    data.append({
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "artist_id": show.artist_id,
      "artist_name": show.artist.name, 
      "artist_image_link": show.artist.image_link,
      "start_time": str(show.start_time)
    })

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
  #'start_time''venue_id' 'artist_id'
  error = False
  try: 
    artist_id = request.form['artist_id']
    venue_id = request.form['venue_id']
    start_time = request.form['start_time']
    show = Show(artist_id=artist_id, venue_id=venue_id, start_time=start_time)
    db.session.add(show)
    db.session.commit()
  except: 
    error = True
    db.session.rollback()
  finally: 
    db.session.close()
  if error :
          flash('Faild adding!','error')
  # on successful db insert, flash success
  else :
    flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
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
