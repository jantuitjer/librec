import os
import sys
from datetime import datetime
os.chdir(os.path.dirname(sys.argv[0]))

librec_arff_mode = True
if not(os.path.isdir("out")):   #check if 'out dir exists
    os.mkdir("out")


def addToDict(dicty:dict, feature: str):
    
    num = len(dicty)
    dicty.update({feature: num})
    return dicty.get(feature)

def init_file_header(filename: str, MOVIE_MODE: bool):
    file = "out/"+filename
    if MOVIE_MODE:
        file+='_movie'
    else:
        file+='_user'
    with open(file+".arff","a+") as out:
        out.write('@Relation '+ filename+'\n')
        out.write('\n')
        if MOVIE_MODE:
            out.write('@Attribute item string\n')
            out.write('@Attribute user string\n')
        else:    
            out.write('@Attribute user string\n')
            out.write('@Attribute item string\n')
        out.write('@Attribute rating NUMERIC\n')
        if not librec_arff_mode:
            out.write('@Attribute timestamp numeric\n')
            # redundant movie information
            out.write('@Attribute genre string\n')
            out.write('@Attribute director string\n')
            out.write('@Attribute country string\n')
            out.write('@Attribute year integer\n')
        else:
            out.write('@Attribute review string\n')
        out.write('\n')
        out.write('@Data\n')
        out.close()

def get_arff_header(filename:str):
	header = '@Relation {}\n\n'.format(filename)
	header += '@Attribute user string\n'
	header += '@Attribute item string\n'
	header += '@Attribute rating NUMERIC\n'
	header += '@Attribute review string\n'
	header += '\n@Data\n'
	return header


def fill_file(filename:str, entry_dict: dict, MOVIE_MODE: bool, limit: int):
	out_file = open('out/{}_no_encoding.arff'.format(filename), 'w')
	out_file.write(get_arff_header(filename))
	for user_id in entry_dict:
		user = entry_dict.get(user_id)
		for movie_id in user:
			movie = user.get(movie_id)
			rating = movie.get('rating')
			director = movie.get('director')
			director_none = director is None
			director = director.strip().replace(' ','') if not director_none else 'unknown'
			genre = movie.get('genre')
			genre_none = genre is None
			genre = genre.strip().replace(' ','') if not genre_none else 'unknown'
			country = movie.get('country')
			country_none = country is None
			country = country.strip().replace(' ','') if not country_none else 'unknown'
			
			year = movie.get('year').strip()
			review_str = '{}:{}:{}:{}:'.format(director, genre, country, year)
			line_str = '{}, {}, {}, {}\n'.format(user_id, movie_id, rating, review_str)
			out_file.write(line_str)
	out_file.close()


def fill_file_encoded(filename:str, entry_dict: dict, MOVIE_MODE: bool, limit: int):
    #TODO: change for write mode param
    
    movies_with_no_ratings = list()
    cnt = 1
    file = "out/"+filename
    director_dict = dict()
    genre_dict= dict()
    country_dict = dict()
    movie_dict = dict()
    user_dict = dict()
    user_num = 0
    movie_num =0
    director_num = 0
    country_num = 0
    genre_num = 0
    feature_dict = dict()
    if MOVIE_MODE:
        file+='_movie'
    else:
        file+='_user'
    with open(file+".arff","a+") as out:
        if MOVIE_MODE:
            for movieId in entry_dict:
                movie = entry_dict.get(movieId)
                if movie.get('genre') is not None:
                    genre = movie.get('genre')
                    if '\n' in genre:
                        genre = movie.get('genre').rsplit()[0]
                else:
                    genre = 'unknown'

                if movie.get('director') is not None:
                    director = movie.get('director')
                    if '\n' in director:
                        director = movie.get('director').rsplit()[0]
                else:
                    director = 'unknown'

                if movie.get('country') is not None and movie.get('country') is not '\n':
                    country = movie.get('country')
                    if '\n' in country:
                        country = movie.get('country').rsplit()[0]
                        
                    else:
                        country = 'unknown'

                if  movie.get('year') is not None:
                    year = movie.get('year')
                    if '\n' in year:
                        year = movie.get('year').rsplit()[0]
                else:
                    year = '9999'
                users = movie.get('users')
                if users is not None:
                    for user in users:
                        rating = users.get(user)[0]
                        time = users.get(user)[1]
                        # movie user rating time genre director country year
                        output = '{}, {}, {}, {}, {}, {}, {}, {}\n'.format(movieId, user, rating, time, genre, director, country, year)
                        if cnt % limit == 0:
                            out.write(output)
                            cnt = 1
                        cnt += 1 
                else:
                    record = '{}, {}, {}, {}, {}\n'.format(movieId, genre, director, country, year)
                    movies_with_no_ratings.append(record)
                        
                    
        else: 
            for user_entry in entry_dict:
                user = entry_dict.get(user_entry)
                for movieId in user:
                    movie = user.get(movieId)
                    if movie.get('genre') is not None:
                        genre = movie.get('genre')
                        if '\n' in genre:
                            genre = movie.get('genre').rsplit()[0]
                    else:
                        genre = 'unknown'

                    if movie.get('director') is not None:
                        director = movie.get('director')
                        if '\n' in director:
                            director = movie.get('director').rsplit()[0]
                    else:
                        director = 'unknown'

                    if movie.get('country') is not None and movie.get('country') is not '\n':
                        country = movie.get('country')
                        if '\n' in country:
                            try:
                                country = movie.get('country').rsplit()[0]
                            except:
                                print(user_entry, movieId)
                                print(entry_dict.get(user_entry).get(movieId))
                    else:
                        country = 'unknown'
                    if  movie.get('year') is not None:
                        year = movie.get('year')
                        if '\n' in year:
                            year = movie.get('year').rsplit()[0]
                    else:
                        year = '9999'
                    rating = movie.get('rating').rsplit()[0]
                    time = movie.get('time').rsplit()[0]
                    if not librec_arff_mode:
                        output = '{}, {}, {}, {}, {}, {}, {}, {}\n'.format(user_entry, movieId, rating, time, genre, director, country, year)
                    else:
                        #features = '{}:{}:{}:{}:{}:'.format(time, genre, director, country, year)
                        movie_mapping = movie_dict.get(movieId)
                        if movie_mapping is None:
                            movie_num += 1
                            movie_dict.update({movieId: movie_num})
                            movie_mapping = movie_dict.get(movieId)
                        user_mapping = user_dict.get(user_entry)
                        if user_mapping is None:
                            user_num += 1
                            user_dict.update({user_entry: user_num})
                            user_mapping = user_dict.get(user_entry)


                        genreId = genre_dict.get(genre)
                        genreId = feature_dict.get(genre)
                        if genreId is None:
                        #    genreId = addToDict(feature_dict, genre)
                            genre_num += 1
                            genre_dict.update({genre :'0' + str(genre_num) + '0'})
                            genreId = genre_dict.get(genre)
                        directorId = director_dict.get(director)
                        #directorId = feature_dict.get(director)
                        if directorId is None:
                        #    directorId = addToDict(feature_dict, director)
                            director_num += 1
                            director_dict.update({director: '1' + str(director_num) + '1'})
                            directorId = director_dict.get(director)
                        countryId = country_dict.get(country)
                        #countryId = feature_dict.get(country)
                        if countryId is None:
                        #    countryId = addToDict(feature_dict, country)
                            country_num +=1 
                            country_dict.update({country: '2' + str(country_num)+'2'})
                            countryId = country_dict.get(country)
                        yearId = feature_dict.get(year)
                        if yearId is None:
                            yearId = addToDict(feature_dict, year)
                        #features = '{}:{}:{}:{}:'.format(genreId, directorId, countryId, yearId)
                        #output ='{}, {}, {}, {}\n'.format(user_entry, movieId, rating, features)
                        #output ='{}, {}, {}, {}\n'.format(user_mapping, movie_mapping, rating, features)
                        features = '{}:{}:{}:{}:'.format(genre, director, country, year)
                        output ='{}, {}, {}, {}\n'.format(user_entry, movieId, rating, features)
                        
                    out.write(output)
                    cnt += 1 
    print(len(country_dict), len(genre_dict), len(director_dict))
    print(len(country_dict)+len(genre_dict)+len(director_dict))

    with open('out/moviesWithNoRatings.txt','a+') as nrf:
        for movie in movies_with_no_ratings:
            nrf.write(movie)
    


def process_movie_file(entry_dict:dict):
    pos_id = 0
    pos_year = 5
    with open('movies.dat') as file:
        next(file)
        for line in file:
            entries = line.split('\t')
            entry_dict.update({entries[pos_id]:{'year': entries[pos_year]}})

                

def process_genres(entry_dict:dict):
    pos_id = 0
    pos_genre = 1
    with open('movie_genres.dat') as file:
        next(file)
        for line in file:
            entries = line.split('\t')
            genre = entries[pos_genre]
            entry_dict.get(entries[pos_id]).update({'genre': genre})


def process_directors(entry_dict:dict):
    pos_id = 0
    pos_director = 1
    with open('movie_directors.dat') as file:
        next(file)
        for line in file:
            entries = line.split('\t')
            entry_dict.get(entries[pos_id]).update({'director': entries[pos_director]})


def process_countries(entry_dict:dict):
    pos_id = 0
    pos_countries = 1
    with open('movie_countries.dat') as file:
        next(file)
        for line in file:
            entries = line.split('\t')
            entry_dict.get(entries[pos_id]).update({'country': entries[pos_countries]})


def process_ratings(entry_dict:dict, MOVIE_MODE: bool):
    pos_user = 0
    pos_movie = 1
    pos_rating = 2
    pos_time = 3
    new_dict = dict()
    if not MOVIE_MODE:
        new_dict.update(entry_dict)
        entry_dict.clear()

    with open('user_ratedmovies-timestamps.dat') as file:
        next(file)
        for line in file:
            entries = line.split('\t')
            if MOVIE_MODE:
                if entry_dict.get(entries[pos_movie]).get('users') is None:
                    entry_dict.get(entries[pos_movie]).update({'users': {entries[pos_user]: (entries[pos_rating], entries[pos_time].rstrip())}})
                else:
                    entry_dict.get(entries[pos_movie]).get('users').update({entries[pos_user]: (entries[pos_rating], entries[pos_time].rstrip())})
            else:                
                t_dict = {'rating': entries[pos_rating],
                          'time': entries[pos_time],
                          'year': new_dict.get(entries[pos_movie]).get('year'),
                          'director': new_dict.get(entries[pos_movie]).get('director'),
                          'country': new_dict.get(entries[pos_movie]).get('country'),
                          'genre' : new_dict.get(entries[pos_movie]).get('genre')
                          }
                if entry_dict.get(entries[pos_user]) is None:
                    entry_dict.update({entries[pos_user]: {entries[pos_movie]: t_dict}})
                else:
                    entry_dict.get(entries[pos_user]).update({entries[pos_movie]: t_dict})
    # write encoded rating file
    user_num = 0
    movie_num = 0
    user_dict = dict()
    movie_dict = dict()
    ratings_file = open('out/ratings_encoded.txt', 'w')
    ratings_file_timestamp = open('out/ratings_timestamp_encoded.txt', 'w')
    with open('user_ratedmovies-timestamps.dat') as file:
        next(file)
        for line in file:
            entries = line.split('\t')
            user = entries[0]
            movie = entries[1]
            rating = entries[2]
            timestamp = entries[3]
            userId = user_dict.get(user)
            
            if userId is None:
                user_num += 1
                user_dict.update({user: user_num})
                userId = user_dict.get(user)
            movieId = movie_dict.get(movie)
            if movieId is None:
                movie_num += 1
                movie_dict.update({movie: movie_num})
                movieId = movie_dict.get(movie)
            out = '{}, {}, {}\n'.format(userId, movieId, rating)
            out_time = '{}, {}, {}, {}\n'.format(userId, movieId, rating, timestamp)
            ratings_file.write(out)
            ratings_file_timestamp.write(out_time)
    ratings_file.close()
    ratings_file_timestamp.close()
            


def main():
    MOVIE_MODE = False
    file_name = 'extended_ratings'
    entry_dict = dict()
    process_movie_file(entry_dict)
    process_genres(entry_dict)
    process_directors(entry_dict)
    process_countries(entry_dict)
    process_ratings(entry_dict, MOVIE_MODE)
    init_file_header(file_name, MOVIE_MODE)
    fill_file(file_name, entry_dict, MOVIE_MODE, 10)     
    print('done')

if __name__ == "__main__":
    main()