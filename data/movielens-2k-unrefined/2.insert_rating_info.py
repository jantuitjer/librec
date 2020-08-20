import rdflib
import rdfextras
from ttl_util import make_ttl_string, get_header, QUERY_HEADER
from SPARQLWrapper import SPARQLWrapper, TURTLE, RDF, JSON, DIGEST,BASIC, POST

SPARQL_ENDPOINT_QUERY = 'http://localhost:3030/movielens-2k/query'
SPARQL_ENDPOINT_UPDATE = 'http://localhost:3030/movielens-2k/update'
SPARQL_ENDPOINT_UPDATE_GENRE = 'http://localhost:3030/movielens-2k-genre/update'
SPARQL_ENDPOINT_UPDATE_DIRECTOR = 'http://localhost:3030/movielens-2k-director/update'
SPARQL_ENDPOINT_UPDATE_REGION = 'http://localhost:3030/movielens-2k-region/update'



rdfextras.registerplugins() 
QUERY_HEADER = """
prefix schema: <https://schema.org/place> 
prefix rr:	<http://regionrating.example.org/> 
prefix country: <http://country.example.org/> 
prefix dbc:   <http://dbpedia.org/resource/Category:> 
prefix movie: <http://movie.example.org/> 
prefix owl:   <http://www.w3.org/2002/07/owl#> 
prefix director: <http://director.example.org/> 
prefix xsd:   <https://www.w3.org/2011/rdf-wg/wiki/XSD_Datatypes> 
prefix rdfs:  <http://www.w3.org/2000/01/rdf-schema#> 
prefix jt:	<http://schema.example.org/> 
prefix gr:	<http://genrerating.example.org/> 
prefix fr:	<http://filmrating.example.org/> 
prefix dr:	<http://directorrating.example.org/> 
prefix dbo:   <http://dbpedia.org/ontology/> 
prefix ex:	<http://example.org/>
prefix rdf:   <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
prefix genre: <http://genre.example.org/> 
prefix dcterms: <http://dublincore.org/documents/2012/06/14/dcmi-terms/> 
prefix region: <http://region.example.org/>
prefix user:  <http://user.example.org/> 
prefix foaf:  <http://xmlns.com/foaf/0.1/> 
{}"""
#data holding
user_rating_dict = dict()
movie_info_dict = dict()

#
genre_rating_dict = dict()
director_rating_dict = dict()
region_rating_dict = dict()

def insert_user_regionrating(endpoint,insert_query):
	region_endpoint = SPARQLWrapper(SPARQL_ENDPOINT_UPDATE_REGION)
	region_endpoint.setHTTPAuth(BASIC)
	region_endpoint.setCredentials('admin', 'admin')
	region_endpoint.setMethod(POST)
	region_endpoint.setReturnFormat(JSON)
	records = ''
	for userId in region_rating_dict:
		user = region_rating_dict.get(userId)
		for region in user:
			avg_region_rating = user.get(region)
			regionRatingName = 'rr:{}_{}'.format(userId, region)
			record = [regionRatingName, 'jt:regionRatingBelongsTo', 'user:{}'.format(userId)]
			record.extend(['jt:avgRegionRating', avg_region_rating])
			record.extend(['jt:forRegion', 'region:{}'.format(region)])
			records += make_ttl_string(record)
	endpoint.setQuery(insert_query.format(records))
	endpoint.query()
	region_endpoint.setQuery(insert_query.format(records))
	region_endpoint.query()

def insert_user_genrerating(endpoint,insert_query):
	genre_endpoint = SPARQLWrapper(SPARQL_ENDPOINT_UPDATE_GENRE)
	genre_endpoint.setHTTPAuth(BASIC)
	genre_endpoint.setCredentials('admin', 'admin')
	genre_endpoint.setMethod(POST)
	genre_endpoint.setReturnFormat(JSON)
	records = ''
	for userId in genre_rating_dict:
		user = genre_rating_dict.get(userId)
		for genre in user:
			avg_genre_rating = user.get(genre)
			genreRatingName = 'gr:{}_{}'.format(userId, genre)
			record = [genreRatingName, 'jt:genreRatingBelongsTo', 'user:{}'.format(userId)]
			record.extend(['jt:avgGenreRating', avg_genre_rating])
			record.extend(['jt:forGenre', 'genre:{}'.format(genre)])
			records += make_ttl_string(record)
	endpoint.setQuery(insert_query.format(records))
	endpoint.query()
	genre_endpoint.setQuery(insert_query.format(records))
	genre_endpoint.query()


def insert_user_directorrating(endpoint, insert_query):
	director_endpoint = SPARQLWrapper(SPARQL_ENDPOINT_UPDATE_DIRECTOR)
	director_endpoint.setHTTPAuth(BASIC)
	director_endpoint.setCredentials('admin', 'admin')
	director_endpoint.setMethod(POST)
	director_endpoint.setReturnFormat(JSON)
	for userId in director_rating_dict:
		records = ''
		user = director_rating_dict.get(userId)
		for directorId in user:
			avg_director_rating = user.get(directorId)
			if avg_director_rating < 3.0:
				continue
			directorRatingName = 'dr:{}_{}'.format(userId,directorId)
			record = [directorRatingName,'jt:directorRatingBelongsTo', 'user:{}'.format(userId)]
			record.extend(['jt:avgDirectorRating', avg_director_rating])
			record.extend(['jt:forDirector', 'director:{}'.format(directorId)])
			records += make_ttl_string(record)
		endpoint.setQuery(insert_query.format(records))
		endpoint.query()
		director_endpoint.setQuery(insert_query.format(records))
		director_endpoint.query()

def insert_user_filmrating(endpoint, insert_query):
	for userId in user_rating_dict:
		records = ''
		user = user_rating_dict.get(userId)
		for movie in user:
			rating = float(user.get(movie).get('rating'))
			time = user.get(movie).get('time')
			record = ['fr:{}_{}'.format(userId, movie), 'jt:wasGivenBy', 'user:{}'.format(userId)]
			record.extend(['jt:hasRated', 'movie:{}'.format(movie)])
			record.extend(['jt:atTime', time])
			record.extend(['jt:withRating', rating])
			records += make_ttl_string(record)
		endpoint.setQuery(insert_query.format(records))
		endpoint.query()


def insert_favorite_genre(endpoint, insert_query):
	records =''
	for userId in genre_rating_dict:
		fav_genre = get_favorite_genre_for_user(userId)
		record = ['user:{}'.format(userId), 'jt:favoriteGenre', 'genre:{}'.format(fav_genre)]
		records += make_ttl_string(record)
	endpoint.setQuery(insert_query.format(records))
	endpoint.query()


def get_favorite_genre_for_user(userId):
	user_genres = genre_rating_dict.get(userId)
	fav_genre = ('Unknown', 0.0)
	for genre in user_genres:
		if user_genres.get(genre) > fav_genre[1]:
			fav_genre = (genre, user_genres.get(genre))
	return fav_genre[0]

def get_favorite_movie_for_user(userId):
	user_movies = user_rating_dict.get(userId)
	fav_movie = ('Unknown', 0.0, 0)
	for movie in user_movies:
		rating = float(user_movies.get(movie).get('rating'))
		time = user_movies.get(movie).get('time')
		if rating > fav_movie[1]:
			fav_movie = (movie, rating, time)
		elif rating == fav_movie[1] and time > fav_movie[2]:
			fav_movie = (movie, rating, time)
	return fav_movie[0]


def expand_semantic():
	endpoint = SPARQLWrapper(SPARQL_ENDPOINT_UPDATE)
	endpoint.setHTTPAuth(BASIC)
	endpoint.setCredentials('admin', 'admin')
	endpoint.setMethod(POST)
	endpoint.setReturnFormat(JSON)
	insert_query = QUERY_HEADER.format('INSERT DATA{{{}}}')
	insert user film ratings
	print('starting inserts')
	insert_favorite_genre(endpoint, insert_query)
	print('done favoriteGenre')
	insert_user_filmrating(endpoint, insert_query)
	print('done filmratings')
	insert_user_genrerating(endpoint, insert_query)
	print('done genreRatings')
	insert_user_regionrating(endpoint, insert_query)
	print('done regionRatings')
	insert_user_directorrating(endpoint, insert_query)
	print('done directorRatings')
	print('done')



def process_ratings():
	for userId in user_rating_dict:
		user_record = user_rating_dict.get(userId)
		for movieId in user_record:
			rating = float(user_record.get(movieId).get('rating'))
			regions = movie_info_dict.get(movieId).get('regions')
			if region_rating_dict.get(userId) is None:
				region_rating_dict[userId] = dict()
			for region in regions:
				update_dict_entry(region_rating_dict, userId, region, rating)
			director = movie_info_dict.get(movieId).get('director')
			if director_rating_dict.get(userId) is None:
				director_rating_dict[userId] = dict()
			update_dict_entry(director_rating_dict, userId, director, rating)
			genres = movie_info_dict.get(movieId).get('genres')
			if genre_rating_dict.get(userId) is None:
				genre_rating_dict[userId] = dict()
			for genre in genres:
				update_dict_entry(genre_rating_dict, userId, genre, rating)
	calc_avg_ratings_in_dicts()


def calc_avg_ratings_in_dicts():
	dicts = [genre_rating_dict, director_rating_dict, region_rating_dict]
	for dict in dicts:
		for userId in dict:
			for key in dict.get(userId):
				val, amt = dict.get(userId).get(key)
				avg_rating = val / amt
				dict.get(userId)[key] = avg_rating


def update_dict_entry(_dict :dict,user, key, value):
	if _dict.get(user).get(key) is None:
		_dict.get(user)[key] = (value, 1)
	else:
		old_entry = _dict.get(user).get(key)
		new_val = old_entry[0] + value
		new_cnt = old_entry[1] + 1
		_dict.get(user).update({key: (new_val, new_cnt)})


def load_all_movie_info():
	endpoint = SPARQLWrapper(SPARQL_ENDPOINT_QUERY)
	query = 'SELECT ?movie ?genre ?country ?region ?director ?trait ?year WHERE {?movie jt:createdInRegion ?region; schema:datePublished ?year; schema:countryOfOrigin ?country;jt:ofGenre ?genre; schema:director ?director. OPTIONAL{?movie jt:movieTrait ?trait}}'
	endpoint.setQuery(QUERY_HEADER.format(query))
	endpoint.setReturnFormat(JSON)
	results = endpoint.query().convert()
	for result in results["results"]["bindings"]:
		movieId = result.get('movie').get('value').split('/')[-1]
		genre = result.get('genre').get('value').split('/')[-1]
		country = result.get('country').get('value').split('/')[-1]
		region = result.get('region').get('value').split('/')[-1]
		director = result.get('director').get('value').split('/')[-1]
		year = result.get('year').get('value')
		trait = result.get('trait')
		if trait is not None:
			trait = trait.get('value')
		if movie_info_dict.get(movieId) is None:
			movie_info_dict[movieId] = {'genres': [genre], 'year':year, 'country': country, 'regions':[region], 'director': director, 'traits':[trait]}
		else:
			movie = movie_info_dict.get(movieId)
			if not genre in movie.get('genres'):
				movie_info_dict.get(movieId).get('genres').append(genre)
			if not region in movie.get('regions'):
				movie_info_dict.get(movieId).get('regions').append(region)
			if trait is not None and not trait in movie.get('traits'):
				movie_info_dict.get(movieId).get('traits').append(trait)
	print(len(movie_info_dict))


def read_ratings_file(dict):
	f = open('user_ratedmovies-timestamps.dat')
	next(f)
	for line in f:
		user, movie, rating, time = line.split('\t')
		insert_dict = {'rating': rating, 'time': time.strip()}
		if dict.get(user) is None:
			dict[user] = {movie: insert_dict}
		else:
			dict.get(user)[movie] = insert_dict


def main():
	# dummy()
	# exit(2)
	load_all_movie_info()
	read_ratings_file(user_rating_dict)
	process_ratings()
	expand_semantic()


if __name__ == "__main__":
	main()