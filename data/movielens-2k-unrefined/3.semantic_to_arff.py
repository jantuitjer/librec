import rdflib
import rdfextras
import sys
import operator
from arff_util import get_arff_header
from ttl_util import make_ttl_string, get_header, QUERY_HEADER
from SPARQLWrapper import SPARQLWrapper, TURTLE, RDF, JSON, DIGEST,BASIC, POST
from contextlib import suppress

SPARQL_ENDPOINT_QUERY_GENRE = 'http://localhost:3030/movielens-2k-genre-likes/query'
SPARQL_ENDPOINT_QUERY_DIRECTOR = 'http://localhost:3030/movielens-2k-director-likes/query'
SPARQL_ENDPOINT_QUERY_REGION = 'http://localhost:3030/movielens-2k-region-likes/query'
SPARQL_ENDPOINT_QUERY_ALL = 'http://localhost:3030/movielens-2k/query'

user_rating_dict = dict()
movie_info_dict = dict()
user_likes_director_dict = dict()
user_likes_region_dict = dict()
user_likes_genre_dict = dict()

genre_encoding_dict = dict()
director_encoding_dict = dict()
region_encoding_dict = dict()
year_encoding_dict = dict()
trait_encoding_dict = dict()
country_encoding_dict = dict()

movie_arff_info_dict = dict()
topk_likes_dict = dict()
year_set = set()
director_set = set()
region_set=set()
country_set=set()
trait_set=set()
genre_set=set()

favorite_dict = dict()

def fill_tmp_dict(dicy: dict, results, key : str):
	for record in results["results"]["bindings"]:
		user = record.get('user').get('value').split('/')[-1]
		entry = record.get(key).get('value').split('/')[-1]
		rating = record.get('rating').get('value')
		if dicy.get(user) is None:
			dicy[user] = {entry: rating}
		else:
			dicy.get(user).update({entry: rating})


def get_preference_values(limit: bool):
	director_query = 'SELECT ?user ?director ?rating WHERE {?dr jt:avgDirectorRating ?rating;  jt:forDirector ?director; jt:directorRatingBelongsTo ?user} ORDER BY ?user'
	genre_query = 'SELECT ?user ?genre ?rating WHERE {?gr jt:genreRatingBelongsTo ?user; jt:forGenre ?genre; jt:avgGenreRating ?rating} ORDER BY ?user'
	region_query= 'SELECT ?user ?region ?rating WHERE {?rr jt:regionRatingBelongsTo ?user; jt:forRegion ?region; jt:avgRegionRating ?rating} ORDER BY ?user'
	endpoint = SPARQLWrapper(SPARQL_ENDPOINT_QUERY_ALL)
	endpoint.setReturnFormat(JSON)
	endpoint.setQuery(QUERY_HEADER.format(director_query))
	director_results = endpoint.query().convert()
	endpoint.setQuery(QUERY_HEADER.format(genre_query))
	genre_results = endpoint.query().convert()
	endpoint.setQuery(QUERY_HEADER.format(region_query))
	region_results = endpoint.query().convert()
	likes_directors = dict()
	likes_genres = dict()
	likes_regions = dict()
	fill_tmp_dict(likes_directors, director_results,'director')
	fill_tmp_dict(likes_genres, genre_results, 'genre')
	fill_tmp_dict(likes_regions, region_results, 'region')
	for userId in likes_directors:
		sorted_directors = sorted(likes_directors.get(userId).items(),key=operator.itemgetter(1),reverse=True)
		sorted_genres = sorted(likes_genres.get(userId).items(),key=operator.itemgetter(1),reverse=True)
		sorted_regions = sorted(likes_regions.get(userId).items(),key=operator.itemgetter(1), reverse=True)
        if limit:
            sorted_directors = sorted_directors[:5]
            sorted_genres = sorted_directors[:5]
            sorted_regions = sorted_regions[:5]
		directors = []
		genres = []
		regions = []
		for director in sorted_directors:
			directors.append(director[0])
		for genre in sorted_genres:
			genres.append(genre[0])
		for region in sorted_regions:
			regions.append(region[0])
		topk_likes_dict[userId] = {'directors': directors, 'genres' : genres, 'regions' : regions}


def write_encoding_file(preEncoded: bool, limit: bool):
	if preEncoded:
		path = '../movielens-2k-arff-extended/pre_encoding_table_.txt'
	else:
		path = '../movielens-2k-arff-extended/encoding_table_.txt'
	f = open(path, 'w')
	line = '{}: {} :{}\n'
	for year in year_encoding_dict:
		f.write(line.format(year_encoding_dict.get(year), year, 'year'))
	for country in country_encoding_dict:
		f.write(line.format(country_encoding_dict.get(country), country, 'country'))
	for director in director_encoding_dict:
		f.write(line.format(director_encoding_dict.get(director), director, 'director'))
	for region in region_encoding_dict:
		f.write(line.format(region_encoding_dict.get(region), region, 'region'))
	for genre in genre_encoding_dict:
		f.write(line.format(genre_encoding_dict.get(genre), genre, 'genre'))
	for trait in trait_encoding_dict:
		f.write(line.format(trait_encoding_dict.get(trait), trait, 'trait'))
	f.close()


def get_encoding_of(dicty: dict, entry):
	if dicty.get(entry) is None:
		dicty[entry] = encoding()
		# print(entry, dicty.get(entry))
	return dicty.get(entry)


def make_review_string(info: list):
	review =''
	for elem in info:
		review += '{}:'.format(elem)
	return review

def preencode():
	# year, country, director, region, genre, trait
	sets = [year_set, country_set, director_set, region_set, genre_set, trait_set]
	dicts = [year_encoding_dict, country_encoding_dict, director_encoding_dict, region_encoding_dict, genre_encoding_dict, trait_encoding_dict]
	for i in range(len(sets)):
		set = sorted(sets[i])
		dicty = dicts[i]
		for entry in set:
			if dicty.get(entry) is None:
				dicty[entry] = encoding()


def filter_genres(_genres):
	toRemove = set()
	if 'Detective' in _genres:
		toRemove.add('PoliceMovie')
		toRemove.add('Film-Noir')
	if 'ActionThriller' in _genres:
		toRemove.add('Action')
		toRemove.add('Thriller')
	if 'ActionComedy' in _genres:
		toRemove.add('Action')
		toRemove.add('Comedy')
	if 'PoliceMovie' in _genres:
		if 'Thriller' in _genres:
			toRemove.add('Thriller')
		if 'Action' in _genres:
			toRemove.add('Action')
		toRemove.add('Crime')
	if 'ChildrenAnimation' in _genres:
		toRemove.add('Children')
		toRemove.add('Animation')
	if 'Supernatural' in _genres:
		toRemove.add('Horror')
		toRemove.add('Fantasy')
	if 'RomCom' in _genres:
		toRemove.add('Romance')
		toRemove.add('Comedy')
	if 'SpaceOpera' in _genres:
		toRemove.add('Adventure')
		toRemove.add('Sci-Fi')
	if 'AsianComedy' in _genres:
		toRemove.add('Comedy')
	if 'MartialArts' in _genres:
		toRemove.add('Action')
	for entry in toRemove:
		_genres.remove(entry)


def get_movie_infos_for(id, preEncoded: bool, limit: bool):
	movie_info = []
	if movie_arff_info_dict.get(id) is None:
		movie = movie_info_dict.get(id)
		year = movie.get('year')
		director = movie.get('director')
		country = movie.get('country')
		regions = movie.get('regions')
		genres = movie.get('genres')
		if len(genres)> 5 and limit:
			filter_genres(genres)
		traits = movie.get('traits')
		if preEncoded:
			movie_info.append(year_encoding_dict.get(year))
			movie_info.append(country_encoding_dict.get(country))
			movie_info.append(director_encoding_dict.get(director))
			for region in regions:
				movie_info.append(region_encoding_dict.get(region))
			for genre in genres:
				movie_info.append(genre_encoding_dict.get(genre))
			for trait in traits:
				if trait is not None:
					movie_info.append(trait_encoding_dict.get(trait))
		else:
			movie_info.append(get_encoding_of(year_encoding_dict, year))
			movie_info.append(get_encoding_of(country_encoding_dict, country))
			movie_info.append(get_encoding_of(director_encoding_dict, director))
			for region in regions:
				movie_info.append(get_encoding_of(region_encoding_dict,region))
			for genre in genres:
				movie_info.append(get_encoding_of(genre_encoding_dict, genre))
			for trait in traits:
				if trait is not None:
					movie_info.append(get_encoding_of(trait_encoding_dict, trait))
		movie_arff_info_dict[id] = movie_info
	return movie_arff_info_dict.get(id)

def get_user_likes_for(id, preEncoded: bool, limit: bool):
	likes = []
	if limit:
		regions = topk_likes_dict.get(id).get('regions')
		genres = topk_likes_dict.get(id).get('genres')
		directors = topk_likes_dict.get(id).get('directors')
	else:
		regions = user_likes_region_dict.get(id)
		directors = user_likes_director_dict.get(id)
		genres = user_likes_genre_dict.get(id)
	if preEncoded:
		if regions is not None:
			for region in regions:
				likes.append(region_encoding_dict.get(region))
		if directors is not None:
			for director in directors:
				likes.append(director_encoding_dict.get(director))
		if genres is not None:
			for genre in genres:
				likes.append(genre_encoding_dict.get(genre))
	else:
		if regions is not None:
			for region in regions:
				likes.append(get_encoding_of(region_encoding_dict, region))
		if directors is not None:
			for director in directors:
				likes.append(get_encoding_of(director_encoding_dict, director))
		if genres is not None:
			for genre in genres:
				likes.append(get_encoding_of(genre_encoding_dict, genre))
	return likes

def write_arff_file(preEncoded: bool, limit: bool):
	if preEncoded:
		path = '../movielens-2k-arff-extended/records_semantic_preencoded.arff'
	else:
		path = '../movielens-2k-arff-extended/records_semantic.arff'
	f = open(path, 'w')
	f.write(get_arff_header())
	insert_line = '{u}, {m}, {rat}, {rev}\n'
	for userId in user_rating_dict:
		user_likes = None
		user = user_rating_dict.get(userId)
		for movieId in user:
			rating = user.get(movieId).get('rating')
			movie_infos = get_movie_infos_for(movieId, preEncoded, limit)
			if user_likes is None:
				user_likes = get_user_likes_for(userId, preEncoded, limit)
			# movie_infos.extend(user_likes)
			print(len(user_likes), len(movie_infos), len(movie_infos + user_likes))
			# f.write(insert_line.format(u=userId, m=movieId, rat = rating, rev=make_review_string(movie_infos)))
			f.write(insert_line.format(u=userId, m=movieId, rat = rating, rev=make_review_string(movie_infos + user_likes)))
	f.close()


def encoding():
	encoding.cnt += 1
	if encoding.cnt % 1000 == 0:
		print('genres',len(genre_encoding_dict))
		print('directors',len(director_encoding_dict))
		print('regions',len(region_encoding_dict))
		# print(region_encoding_dict)
		# print(genre_encoding_dict)
		# exit(5)
	return encoding.cnt
encoding.cnt = -1

def get_genre_likes():
	endpoint = SPARQLWrapper(SPARQL_ENDPOINT_QUERY_GENRE)
	query = 'SELECT ?user ?genre WHERE {?user jt:interestedInGenre ?genre} ORDER BY ?user'
	endpoint.setQuery(QUERY_HEADER.format(query))
	endpoint.setReturnFormat(JSON)
	results = endpoint.query().convert()
	for result in results["results"]["bindings"]:
		userId = result.get('user').get('value').split('/')[-1]
		genre = result.get('genre').get('value').split('/')[-1]
		if user_likes_genre_dict.get(userId) is None:
			user_likes_genre_dict[userId] = [genre]
		else:
			user_likes_genre_dict.get(userId).append(genre)


def get_region_likes():
	endpoint = SPARQLWrapper(SPARQL_ENDPOINT_QUERY_REGION)
	query = 'SELECT ?user ?region WHERE {?user jt:likesMoviesOfRegion ?region} ORDER BY ?user'
	endpoint.setQuery(QUERY_HEADER.format(query))
	endpoint.setReturnFormat(JSON)
	results = endpoint.query().convert()
	for result in results["results"]["bindings"]:
		userId = result.get('user').get('value').split('/')[-1]
		region = result.get('region').get('value').split('/')[-1]
		if user_likes_region_dict.get(userId) is None:
			user_likes_region_dict[userId] = [region]
		else:
			user_likes_region_dict.get(userId).append(region)


def get_director_likes():
	endpoint = SPARQLWrapper(SPARQL_ENDPOINT_QUERY_DIRECTOR)
	query = 'SELECT ?user ?director WHERE {?user jt:likesMoviesOfDirector ?director} ORDER BY ?user'
	endpoint.setQuery(QUERY_HEADER.format(query))
	endpoint.setReturnFormat(JSON)
	results = endpoint.query().convert()
	for result in results["results"]["bindings"]:
		userId = result.get('user').get('value').split('/')[-1]
		director = result.get('director').get('value').split('/')[-1]
		if user_likes_director_dict.get(userId) is None:
			user_likes_director_dict[userId] = [director]
		else:
			user_likes_director_dict.get(userId).append(director)


def get_movie_info():
	endpoint = SPARQLWrapper(SPARQL_ENDPOINT_QUERY_ALL)
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
		genre_set.add(genre)
		country_set.add(country)
		region_set.add(region)
		director_set.add(director)
		year_set.add(year)
		if trait is not None:
			trait_set.add(trait)
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

def fill_dicts():
	read_ratings_file(user_rating_dict)
	get_movie_info()
	get_genre_likes()
	get_region_likes()
	get_director_likes()

def main():
	args = sys.argv
	mode, limit = None, None
	if len(args) > 1: 
		mode = args[1]
	if len(args) > 2: 
		limit = args[2]
	if mode is not None:
		if mode == '1':
			mode = True
		else:
			mode = False
	if limit is not None:
		if limit == '1':
			limit = True
		else:
			limit = False
	print(mode, limit)
	get_preference_values(limit)
	fill_dicts()
	print('dicts filled')
	if mode:
		preencode()
		print('received preferences')
	write_arff_file(mode, limit)
	print('arff file written')
	write_encoding_file(mode, limit)
	print('encoding table written')
	print('done')


if __name__ == "__main__":
	main()
