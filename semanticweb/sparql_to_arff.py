import os
import sys
from datetime import datetime
os.chdir(os.path.dirname(sys.argv[0]))

num_of_users =- 1
user_rating_dict = dict()
movie_dict = dict()
user_favorite_dict = dict()
country_dict = dict()
director_dict = dict()
genre_dict = dict()
year_dict = dict()
trait_dict = dict()
favorite_movie_dict = dict()
movie_trait_dict= dict()
trait_encoding_dict = dict()
test_favorite_dict = dict()
favorite_movie_encoding_dict = dict()


if not(os.path.isdir("out_ttl")):   #check if 'out dir exists
    os.mkdir("out_ttl")


def inc_counter():
    inc_counter.counter += 1
    return inc_counter.counter
inc_counter.counter = -1


def read_ratings_file():
    f = open('../data/movielens-2k-unrefined/user_ratedmovies-timestamps.dat','r')
    next(f)
    for line in f:
        userId, movieId, rating, time = line.split('\t')
        user_entry = user_rating_dict.get(userId)
        if user_entry is None:
            user_rating_dict[userId] = {movieId: rating}
        else:
            user_entry.update({movieId: rating})
    num_of_users = len(user_rating_dict)


def read_movie_file():
    id_pos = 0
    year_pos = 5
    f = open('../data/movielens-2k-unrefined/movies.dat','r')
    next(f)
    for line in f:
        elem = line.strip().split('\t')
        id = elem[id_pos]
        year = int(elem[year_pos])
        if year_dict.get(year) is None:
            year_dict[year] = inc_counter()
        movie_entry = movie_dict.get(id)
        movie_dict[id] = {'year': year}


def read_country_file():
    f = open('../data/movielens-2k-unrefined/movie_countries.dat','r')
    next(f)
    for line in f:
        movieId, country = line.split('\t')
        if country =='\n':
            country = 'unknown'
        country = country.replace(' ','').strip()
        if country_dict.get(country) is None:
            country_dict[country] = inc_counter()
        movie_record = movie_dict.get(movieId)
        movie_record['country']=country


def read_director_file():
    f = open('../data/movielens-2k-unrefined/movie_directors.dat','r')
    next(f)
    for line in f:
        movieId, directorId, director_name = line.strip().split('\t')
        if director_dict.get(directorId) is None:
            director_dict[directorId]= inc_counter()
        movie_record = movie_dict.get(movieId)
        movie_record['director']=directorId


def read_genre_file():
    f = open('../data/movielens-2k-unrefined/movie_genres.dat','r')
    next(f)
    for line in f:
        movieId, genre = line.strip().split('\t')
        if genre_dict.get(genre) is None:
            genre_dict[genre] = inc_counter()
        movie_record = movie_dict.get(movieId)
        if movie_record.get('genres') is None:
            movie_record['genres']=[genre]
        else:
            movie_record.get('genres').append(genre)


def read_user_info_file():
    f = open('queries/results/user_info.dat','r')
    for line in f:
        line= line.replace('(','').replace(')','').replace(' ','')
        line_entries = line.split('?')
        list = []
        for i in range(1, len(line_entries)):
            record =line_entries[i].split('=')[1]
            list.append(record.strip().split('_')[1][:-1])
        userId, favmovieId, favgenre = list
        if favorite_movie_dict.get(favmovieId) is None:
            favorite_movie_dict[favmovieId]= inc_counter()
        #user_favorite_dict[userId] = {'favorite_movie':favmovieId, 'favorite_genre':favgenre}
        test_favorite_dict[userId] = {'favorite_movie':favmovieId,'favorite_genre': favgenre}
       # user_rating_dict.get(userId)['favorite_movie'] = favmovieId
        # user_rating_dict.get(userId)['favorite_genre'] = favgenre
        # print(user_rating_dict.get(userId).get('favorite_movie'))
        # print(user_rating_dict.get(userId).get('favorite_genre'))
        # exit(89)

def read_movie_trait_file():
    f = open('queries/results/movie_trait_info.dat','r')
    for line in f:
        line= line.replace('(','').replace(')','').replace(' ','')
        line_entries = line.split('?')
        list = []
        movieId = line_entries[1].split('_')[1][:-1]
        trait = line_entries[2].split('=')[1].strip().replace('"','')
        if movie_trait_dict.get(trait) is None:
            movie_trait_dict[trait] = inc_counter()
        movie_entry = movie_dict.get(movieId)
        if movie_entry.get('traits') is None:
            movie_entry['traits']=[trait]
        else:
            movie_entry.get('traits').append(trait)


def read_movie_popular_file():
    f = open('queries/results/movie_popular_info.dat','r')
    for line in f:
        line= line.replace('(','').replace(')','').replace(' ','')
        entry = line.split('?')[1].strip().split('_')[1][:-1]
        movie_entry = movie_dict.get(entry)
        if movie_trait_dict.get('popular') is None:
            movie_trait_dict['popular'] = inc_counter()
        if movie_entry.get('traits') is None:
            movie_entry['traits']=['popular']
        else:
            movie_entry.get('traits').append('popular')


def test():
    print(user_rating_dict.get('75'))
    print(user_favorite_dict.get('75'))
    print(genre_dict.get(user_favorite_dict.get('75').get('favorite_genre')))
    print(movie_dict.get('6'))
    print(genre_dict.get(movie_dict.get('6').get('genres')[0]))


def insert_pos_info():
    line_entries = ['year', 'country', 'director', 'genres', 'favmovie', 'movie_traits']
    dicts = [year_dict, country_dict, director_dict, genre_dict, favorite_movie_dict, movie_trait_dict]
    info_line = ''
    format_line = '%{} from: {} to {}\n'
    for i in range(len(line_entries)):
        min_value = min(dicts[i].values())
        max_value = max(dicts[i].values())
        info_line += format_line.format(line_entries[i], min_value, max_value)
    return info_line


def get_arff_header():
    header = '@Relation user_movie_rating\n'
    header += '@Attribute user string\n'
    header += '@Attribute item string\n'
    header += '@Attribute rating NUMERIC\n'
    header += '@Attribute review string\n'
    header += insert_pos_info()
    header += '\n@Data\n'
    return header


def dump_arff_file():
    f = open('records_working_new.arff','w')
    f.write(get_arff_header())
    output_line_format = '{user}, {movie}, {rating}, {review}\n'
    dicts = [year_dict, country_dict, director_dict, genre_dict, favorite_movie_dict, movie_trait_dict]
    inc_counter.counter = -1
    for dict in dicts:
        dict.clear()
    for userId in user_rating_dict:
        user_record = user_rating_dict.get(userId)
        for rated_movieId in user_record:
            rating = user_record.get(rated_movieId)
            movie_info = movie_dict.get(rated_movieId)
            record_list = []
            year = year_dict.get(movie_info.get('year'))
            if year is None:
                year = inc_counter()
                year_dict[movie_info.get('year')] = year
            record_list.append(year)
            director = director_dict.get(movie_info.get('director'))
            if director is None:
                director = inc_counter()
                director_dict[movie_info.get('director')] = director
            record_list.append(director)
            country = country_dict.get(movie_info.get('country'))
            if country is None:
                country = inc_counter()
                country_dict[movie_info.get('country')] = country
            record_list.append(country)
            for genre_entry in movie_info.get('genres'):
                genre = genre_dict.get(genre_entry)
                if genre is None:
                    genre = inc_counter()
                    genre_dict[genre_entry] = genre
                record_list.append(genre)
            fav_genre = genre_dict.get(test_favorite_dict.get(userId).get('favorite_genre'))
            
            traits = movie_info.get('traits')
            if traits is not None:
                for trait_entry in traits:
                    trait = trait_encoding_dict.get(trait_entry)
                    if trait is None:
                        trait = inc_counter()
                        trait_encoding_dict[trait_entry] = trait
                record_list.append(trait)
            
            if fav_genre is None:
                fav_genre = inc_counter()
                genre_dict[test_favorite_dict.get(userId).get('favorite_genre')] = fav_genre
            record_list.append(fav_genre)
            fav_movie = favorite_movie_encoding_dict.get(test_favorite_dict.get(userId).get('favorite_movie'))
            if fav_movie is None:
                fav_movie = inc_counter()
                favorite_movie_encoding_dict[test_favorite_dict.get(userId).get('favorite_movie')] = fav_movie
            record_list.append(fav_movie)
            record_line = ''
            for entry in record_list:
                record_line += str(entry)+':'
            f.write(output_line_format.format(user=userId, movie=rated_movieId, rating=rating, review=record_line))
            

def dump_encoding():
    f = open('encoding_table.txt', 'w')
    f.write('encoded, decoded, type\n')
    dicts = [year_dict, director_dict, country_dict, genre_dict, trait_encoding_dict, favorite_movie_encoding_dict]
    dict_names = ['year', 'director', 'country', 'genre','movie_trait', 'favorite_movie']
    entry_line = '{encoded}, {decoded}, {type}\n'
    for i in range(len(dicts)):
        for key in dicts[i]:
            encoded = dicts[i].get(key)
            decoded = key
            f.write(entry_line.format(encoded=encoded, decoded=decoded, type=dict_names[i]))

def main():
    read_ratings_file()
    read_movie_file()
    read_country_file()
    read_genre_file()
    read_director_file()
    read_user_info_file()
    read_movie_trait_file()
    read_movie_popular_file()
    #test()
    dump_arff_file()
    dump_encoding()
    print('extended arff file was written.')
    
if __name__ == "__main__":
    main()