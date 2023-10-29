# tvBuddy

tvBuddy is built on top of the TV Maze API to display information about TV shows. Users can register, save their favorite shows, actors and actresses, and
get recommendations for new shows

## Website Usage 

Any user can use the tvBuddy website, even if they are not registered or logged in. Unregistered users will not be able to save their favorite shows and actors, 
or get recommendations for new shows. 

The homepage displays a search box where the user can query for a show. The search box form sends a request, from the front-end JS file, to the TV Maze API. 

```Javascript
  const shows = await axios.get(`${apiURL}search/shows?q=${searchTerm}`)
```
The returned show data is then parsed and displayed in the appropriate area with additional links to display more information about the show.

All users (registered and unregistered) will be allowed to search for information about TV shows. 
Only registered users will be given the additional options to save their favorite TV shows, actors and actresses. 
Additionally registered users will be given recommendations based on their saved favorite actors and actresses. The recommendation is based on what other shows the 
users favorite actors and actresses have been in.

## API Reference Website
https://www.tvmaze.com/api

## Tech Stack
1. Python
2. Flask==2.2.2
3. Jinja2==3.1.2py
4. PostgreSQL
5. SQLAlchemy==1.4.46

### Installing and Running

* Clone the repository, ensure the requirements.txt file is in place, and install dependencies
```
pip install -r requirements.txt
```
* The application uses Python for server side functionality which serves Jinja templates to the front end using Flask.
```
flask run
```

## Authors

sKc

## Version History

* 0.1
    * Initial Release





