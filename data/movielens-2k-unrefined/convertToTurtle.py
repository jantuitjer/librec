import os
import sys
from datetime import datetime
os.chdir(os.path.dirname(sys.argv[0]))

user_dict = dict()
movie_dict = dict()
genre_dict = dict()
director_dict = dict()
country_dict = dict()
rated_movie_dict = dict()
if not(os.path.isdir("out_ttl")):   #check if 'out dir exists
    os.mkdir("out_ttl")


def get_header():
	str = '@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .\n'
	str += '@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .\n'
	str += '@prefix foaf: <http://xmlns.com/foaf/0.1/> .\n'
	str += '@prefix dbo: <http://dbpedia.org/ontology/> .\n'
	str += '@prefix dbc: <http://dbpedia.org/resource/Category:> . \n'
	str += '@prefix owl: <http://www.w3.org/2002/07/owl#> .\n'
	str += '@prefix dcterms: <http://dublincore.org/documents/2012/06/14/dcmi-terms/> .\n'
	str += '@prefix schema: <https://schema.org/place> .\n'
	str += '@prefix jt: <http://schema.example.org/> .\n'
	str += '@prefix xsd: <https://www.w3.org/2011/rdf-wg/wiki/XSD_Datatypes> .\n'
	str += '@prefix ex:   <http://example.org/>.\n\n'
	return str

def make_ttl_string(_statements):
	ttl = ''
	if len(_statements) < 3:
		print('to few elements to form statement')
		exit(-9)
	for i in range(1, len(_statements), 2):
		if i == 1:
			ttl = '{}\t{}\t{}'.format(_statements[i-1], _statements[i], _statements[i+1])
			continue
		ttl = '{};\n\t{}\t{}'.format(ttl, _statements[i], _statements[i+1])
	ttl += '.\n\n'
	return ttl


def read_user_rating_file():
	f = open('user_ratedmovies-timestamps.dat')
	next(f)
	for line in f:
		user, movie, rating, time = line.strip().split('\t')
		user_entry = user_dict.get(user)
		rating = float(rating)
		#print(user, movie, rating)
		#exit(-9)
		if user_entry is None:
			user_dict[user] = {'has_rated' : [movie], 'avgRating' : rating}
		else:
			user_entry.get('has_rated').append(movie)
			user_entry['avgRating'] = user_entry.get('avgRating') + rating
		movie_entry = movie_dict.get(movie)
		if movie_entry is None:
			movie_dict[movie] = {'was_rated' : [user], 'avgRating' : rating}
		else:
			movie_entry.get('was_rated').append(user)
			movie_entry['avgRating'] = movie_entry.get('avgRating') + rating
		rated_movie_dict[user+'_'+movie] ={'rating' : rating, 'time': time}

def read_genre_file():
	f = open('movie_genres.dat')
	next(f)
	for line in f:
		id, genre = line.strip().split('\t')
		genre_dict[id] = genre
		movie = movie_dict.get(id)
		if movie is None:
			movie_dict[id]={'genre': [genre]}
		else:
			if movie.get('genre') is None:
				movie['genre'] = [genre]
			else:
				movie_dict.get(id).get('genre').append(genre)

def read_country_file():
	f = open('movie_countries.dat')
	next(f)
	for line in f:
		id, country = line.split('\t')
		country_dict[id] = country.strip()
		movie_dict.get(id).update({'country':country_dict.get(id)})
		
		
def read_movie_file():
	id_pos = 0
	year_pos = 5
	f = open('movies.dat')
	next(f)
	for line in f:
		elem = line.strip().split('\t')
		id = elem[id_pos]
		year = int(elem[year_pos])
		movie_entry = movie_dict.get(id)
		if movie_entry is None:
			movie_dict[id] = {'year': year}
		else:
			movie_dict.get(id).update({'year': year})
			
def read_director_file():
	id_pos = 0
	f = open('movie_directors.dat')
	next(f)
	for line in f:
		id, directorId, director = line.strip().split('\t')
		movie_dict.get(id).update({'director': directorId})
		cur_dir = director_dict.get(directorId)
		if cur_dir is None:
			director_dict['directorId'] = director

def refine_data():
#user related refinement
	for user_id in user_dict:
		user = user_dict.get(user_id)
		user['avgRating'] = user.get('avgRating') / len(user.get('has_rated'))
		rated_dict = dict()
		for mId in user.get('has_rated'):
			mGenres = movie_dict.get(mId).get('genre')
			for currentGenre in mGenres:
				if rated_dict.get(currentGenre) is None:
				## maybe add rating into account to estimate favorite rating
					rated_dict[currentGenre] = 1
				else:
					rated_dict[currentGenre] = rated_dict.get(currentGenre) + 1
		favorite_genre = max(rated_dict, key=rated_dict.get)	#extract genre with most ratings by this user
		user.update({'favorite_genre': favorite_genre})	
#movie related refinement
	for movie_id in movie_dict:
		movie = movie_dict.get(movie_id)
		if (movie.get('was_rated') is None) or (movie.get('avgRating') is None):
			movie['numOfRatings'] = 0
			movie['avgRating'] = 0
		else:
			tmp_avg = movie.get('avgRating')
			movie['numOfRatings'] = len(movie.get('was_rated'))
			movie['avgRating'] = movie.get('avgRating') / len(movie.get('was_rated'))

def write_movie_ttl():
	f = open('out_ttl/movies.ttl', 'w')
	f.write(get_header())
	for movId in movie_dict:
		#c_movie = movie_dict.get(movId)
		#mlist = ['ex:m_'+movId, 'a', 'dbo:Film']
		#mlist.extend(['schema:datePublished', c_movie.get('year')])
		#mlist.extend(['schema:countryOfOrigin', 'ex:c_' + c_movie.get('country').replace(" ","")])
		#director = c_movie.get('director')
		#if director is None:
		#	director = 'Unknown'
		#mlist.extend(['schema:director', 'ex:d_' + director])
		#mlist.extend(['jt:avgRating', c_movie.get('avgRating')])
		#mlist.extend(['jt:numberOfRatings', c_movie.get('numOfRatings')])
		#for genre in c_movie.get('genre'):
		#	mlist.extend(['jt:ofGenre', 'ex:g_'+genre])
		#for userId in movie.get('was_rated'):
		#	mlist.extend(['jt:filmedInConuntry', movie.get('country')])
		#f.write(make_ttl_string(mlist))
		f.write(get_movie_ttl(movId))
	f.close()
	
def get_movie_ttl(movId:int):
	c_movie = movie_dict.get(movId)
	mlist = ['ex:m_'+movId, 'a', 'dbo:Film']
	mlist.extend(['schema:datePublished', c_movie.get('year')])
	mlist.extend(['schema:countryOfOrigin', 'ex:c_' + c_movie.get('country').replace(" ","")])
	director = c_movie.get('director')
	if director is None:
		director = 'Unknown'
	mlist.extend(['schema:director', 'ex:d_' + director])
	mlist.extend(['jt:avgRating', c_movie.get('avgRating')])
	mlist.extend(['jt:numberOfRatings', c_movie.get('numOfRatings')])
	for genre in c_movie.get('genre'):
		mlist.extend(['jt:ofGenre', 'ex:g_'+genre])
	#for userId in movie.get('was_rated'):
	#	mlist.extend(['jt:filmedInConuntry', movie.get('country')])
	return make_ttl_string(mlist)
	
	
def write_user_ttl():
	f = open('out_ttl/users.ttl', 'w')
	f.write(get_header())
	for user_id in user_dict:
		user = user_dict.get(user_id)
		list = ['ex:u_' + user_id, 'a', 'foaf:Person']
		list.append('jt:favoriteGenre')
		list.append('ex:g_{}'.format(user.get('favorite_genre')))
		for mId in user.get('has_rated'):
			list.extend(['jt:hasRated', 'ex:m_'+mId])
		f.write(make_ttl_string(list))
	f.close()
		
		
def make_bracket_ttl(mvId: int, rating: float, time: str):
	entry_line = 'jt:hasRated ex:m_{};\n\t jt:withRating {};\n\t jt:atTime {}'.format(mvId, rating, time)
	entry = '\tjt:ratedMovie [\n\t{}];\n'.format(entry_line)
	return entry
	
		
def write_ttl_extended():
	f = open('out_ttl/abox_extended.ttl', 'w')
	f.write(get_header())
	rf = None
	user_movie_rating_dict = dict()
	for userId in user_dict:
		user = user_dict.get(userId)
		list = ['ex:u_' + userId, 'a', 'foaf:Person']
		list.extend(['jt:favoriteGenre', 'ex:g_{}'.format(user.get('favorite_genre'))])
		#tmp_ttl = make_ttl_string(list).strip().replace('.', ';')
		#tmp_ttl += '\n\t'
		for mId in user.get('has_rated'):
			list.extend(['jt:ratedMovie', 'ex:r_{}_{}'.format(userId, mId)])
			rating_obj = rated_movie_dict.get(userId+'_'+mId)
			user_movie_rating_dict[userId+'_'+mId]={'rating': rating_obj.get('rating'),'time': rating_obj.get('time'),'user':userId, 'movie':mId}
			#tmp_ttl += make_bracket_ttl(mId, rating_obj.get('rating'), rating_obj.get('time'))
		#tmp_ttl = tmp_ttl[:-2]+'.\n'
		f.write(make_ttl_string(list))
	for movId in movie_dict:
		f.write(get_movie_ttl(movId))
	prev_user = -1
	cur_user = -1
	for umr in user_movie_rating_dict:
		record = user_movie_rating_dict.get(umr)
		user = record.get('user')
		if prev_user != user:
			prev_user = user
			cur_user += 1
			rf = open('out_ttl/abox_rating_{}_extended.ttl'.format(cur_user), 'w')
			rf.write(get_header())
		umr_list = ['ex:r_{}'.format(umr), 'a', 'jt:UserFilmRating']
		umr_list.extend(['jt:wasGivenBy', 'ex:u_{}'.format(record.get('user'))])
		umr_list.extend(['jt:hasRated', 'ex:m_{}'.format(record.get('movie'))])
		umr_list.extend(['jt:withRating', record.get('rating')])
		umr_list.extend(['jt:atTime', record.get('time')])
		rf.write(make_ttl_string(umr_list))
	f.close()
	rf.close()

	
def test():
	#print(os.path.dirname(sys.argv[0]))
	print('TESTING_TTL')
	test = ('tdasdsd', 'a', 'letter', 'das', 'ds')
	print(make_ttl_string(test))


def get_data():
	read_user_rating_file()
	read_movie_file()
	read_genre_file()
	read_country_file()
	read_director_file()

def main():
	#test()
	get_data()
	refine_data()
	#write_user_ttl()
	#write_movie_ttl()
	write_ttl_extended()

if __name__ == "__main__":
    main()