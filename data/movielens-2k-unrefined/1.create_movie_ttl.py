import os
import sys
from datetime import datetime
from ttl_util import make_ttl_string, get_header 
os.chdir(os.path.dirname(sys.argv[0]))

super_region_dict = {
'CentralAsia': 'Asia',
'EastAsia' : 'Asia',
'SouthEastAsia' : 'Asia',
'WesternAsia' : 'Asia',
'NorthEurope': 'Europe',
'CentralEurope': 'Europe',
'SouthEasternEurope': 'Europe',
'EasternEurope': 'Europe',
'WesternEurope': 'Europe',
'SouthernEurope': 'Europe',
}

region_dict = {
'Afghanistan': 'CentralAsia',
'Kazakhstan' : 'CentralAsia',
'China' : 'EastAsia',
'HongKong': 'EastAsia',
'Japan' : 'EastAsia',
'SoutKorea' : 'EastAsia',
'Taiwan': 'EastAsia', 
'Bhutan': 'SouthAsia',
'India': 'SouthAsia',
'Philippines' : 'SouthEastAsia',
'Singapore' : 'SouthEastAsia',
'Thailand': 'SouthEastAsia',
'Vietnam': 'SouthEastAsia',
'OccupiedPalestinianTerritory': 'WesternAsia',
'Iran': 'WesternAsia',
'Israel': 'WesternAsia',
'Turkey': 'WesternAsia',
'Algeria' : 'Africa',
'BurkinaFaso' : 'Africa',
'Botswana' : 'Africa',
'IvoryCoast': 'Africa',
'Libya': 'Africa',
'Senegal': 'Africa',
'SouthAfrica': 'Africa',
'Tunisia': 'Africa',
'Denmark': 'NorthEurope',
'Finland': 'NorthEurope',
'Iceland': 'NorthEurope',
'Norway': 'NorthEurope',
'Sweden': 'NorthEurope',
'Austria': 'CentralEurope',
'Croatia': 'CentralEurope',
'CzechRepublic': 'CentralEurope',
'Czechoslovakia': 'CentralEurope',
'EastGermany': 'CentralEurope',
'FederalRepublicofYugoslavia': 'CentralEurope',
'Germany': 'CentralEurope',
'Hungary': 'CentralEurope',
'Poland': 'CentralEurope',
'Switzerland': 'CentralEurope',
'WestGermany': 'CentralEurope',
'Yugoslavia': 'CentralEurope',
'Russia': 'EasternEurope',
'SovietUnion': 'EasternEurope',
'Bulgaria': 'SouthEasternEurope',
'Romania': 'SouthEasternEurope',
'BosniaandHerzegovina': 'SouthEasternEurope',
'RepublicofMacedonia': 'SouthEasternEurope',
'Greece': 'SouthEasternEurope',
'Belgium': 'WesternEurope',
'France': 'WesternEurope',
'Ireland': 'WesternEurope',
'Netherlands': 'WesternEurope',
'UK': 'WesternEurope',
'Italy': 'SouthernEurope',
'Portugal': 'SouthernEurope',
'Spain': 'SouthernEurope',
'Aruba': 'Caribbean',
'Cuba': 'Caribbean',
'Jamaica': 'Caribbean',
'Canada': 'NorthAmerica',
'Mexico': 'NorthAmerica',
'USA': 'NorthAmerica',
'Argentina': 'SouthAmerica',
'Brazil': 'SouthAmerica',
'Chile': 'SouthAmerica',
'Colombia': 'SouthAmerica',
'Peru': 'SouthAmerica',
'Venezuela': 'SouthAmerica',
'Australia': 'Oceania',
'NewZealand': 'Oceania',
'\t': 'Unknown',
'\n': 'Unknown',
None: 'Unknown',
'': 'Unknown'}

movie_info_dict = dict()
country_dict = dict()
user_rating_dict = dict()

def read_movie_file():
    f = open('movies.dat')
    next(f)
    pos_id = 0
    pos_year = 5
    for line in f:
        entries = line.split('\t')
        movie_id = entries[pos_id]
        year = entries[pos_year]
        movie_info_dict[movie_id] ={'year': year}
    f.close()
    
def read_genre_file():
    f = open('movie_genres.dat')
    next(f)
    for line in f:
        movie_id, genre = line.split('\t')
        genre = genre.strip()
        if movie_info_dict.get(movie_id).get('genres') is None:
            movie_info_dict.get(movie_id)['genres'] = [genre]
        else:
            movie_info_dict.get(movie_id).get('genres').append(genre)
    f.close()
    
def read_country_file():
    f = open('movie_countries.dat')
    next(f)
    for line in f:
        movie_id, country = line.split('\t')
        if country == '\n':
            country = 'Unknown'
        country = country.strip().replace(' ','')
        movie_info_dict.get(movie_id)['country'] = country
        if country_dict.get(country) is None:
            country_dict[country] = country
    f.close()
def read_director_file():
    f = open('movie_directors.dat')
    next(f)
    for line in f:
        movie_id, director, director_name = line.split('\t')
        director = director.strip()
        movie_info_dict.get(movie_id)['director'] = director

def read_ratings_file():
    f = open('user_ratedmovies-timestamps.dat')
    next(f)
    for line in f:
        user_id, movie_id, rating, timestamp = line.split('\t')
        timestamp = timestamp.strip()
        if movie_info_dict.get(movie_id).get('sum_ratings') is None:
            movie_info_dict.get(movie_id).update({'sum_ratings' : float(rating), 'amt_ratings' : 1})
        else:
            new_rating_val = movie_info_dict.get(movie_id).get('sum_ratings') + float(rating)
            new_rating_amt = movie_info_dict.get(movie_id).get('amt_ratings') + 1
            movie_info_dict.get(movie_id).update({'sum_ratings' : new_rating_val, 'amt_ratings' : new_rating_amt})
    for movie_id in movie_info_dict:
        amt_ratings = movie_info_dict.get(movie_id).get('amt_ratings')
        val_ratings = movie_info_dict.get(movie_id).get('sum_ratings')
        if val_ratings is None and amt_ratings is None:
            pass
        else:
            avg_rating = val_ratings / amt_ratings
            movie_info_dict.get(movie_id)['avg_rating'] = avg_rating
    f.close()

def read_ratings_file():
	f = open('user_ratedmovies-timestamps.dat')
	next(f)
	for line in f:
		user, movie, rating, time = line.split('\t')
		insert_dict = {'rating': rating, 'time': time.strip()}
		if user_rating_dict.get(user) is None:
			user_rating_dict[user] = {movie: insert_dict}
		else:
			user_rating_dict.get(user)[movie] = insert_dict



def write_movie_info(f):
	for movie_id in movie_info_dict:
		movie = movie_info_dict.get(movie_id)
		list = ['movie:{}'.format(movie_id), 'a', 'dbo:Film']
		list.extend(['schema:datePublished', movie.get('year')])
		list.extend(['schema:countryOfOrigin', 'country:{}'.format(movie.get('country'))])
		list.extend(['schema:director', 'director:{}'.format(movie.get('director'))])
		if movie.get('amt_ratings') is not None:
			list.extend(['jt:numberOfRatings', movie.get('amt_ratings')])
			list.extend(['jt:avgRating', movie.get('avg_rating')])
		for genre in movie.get('genres'):
			list.extend(['jt:ofGenre', 'genre:{}'.format(genre)])
		f.write(make_ttl_string(list))


def write_country_region_info(f):
	for country in country_dict:
		f.write(make_ttl_string(['country:{}'.format(country),'jt:partOf', 
			'region:{}'.format(region_dict.get(country))]))
	for subRegion in super_region_dict:
		f.write(make_ttl_string(['region:{}'.format(subRegion), 'jt:subRegionOf','region:{}'.format(super_region_dict.get(subRegion))]))


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


def write_user_info(f):
	for userId in user_rating_dict:
		user = user_rating_dict.get(userId)
		favorite_movie = get_favorite_movie_for_user(userId)
		record = ['user:{}'.format(userId), 'jt:favoriteMovie', 'fr:{}_{}'.format(userId, favorite_movie)]
		for movieId in user:
			record.extend(['jt:hasGiven', 'fr:{}_{}'.format(userId, movieId)])
		f.write(make_ttl_string(record))


def write_ttl():
	f = open('../../semanticweb/abox/movie_info.ttl', 'w')
	f.write(get_header())
	write_movie_info(f)
	write_country_region_info(f)
	write_user_info(f)
	f.close()

def get_data():
    read_movie_file()
    read_genre_file()
    read_country_file()
    read_director_file()
    read_ratings_file()

def main():
    get_data()
    write_ttl()

if __name__ == "__main__":
    main()