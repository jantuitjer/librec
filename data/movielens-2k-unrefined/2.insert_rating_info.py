import rdflib
import rdfextras
from SPARQLWrapper import SPARQLWrapper, TURTLE, RDF, JSON

SPARQL_ENDPOINT = 'http://localhost:3030/movielens-2k'
RDF_FILE = 'movie_info_extended.xml'	#file which contains the rdf data
URI = 'r_75_3'
rdfextras.registerplugins() 
QUERY_HEADER = """
prefix schema: <https://schema.org/place> 
prefix rr:    <http://regionrating.example.org/> 
prefix country: <http://country.example.org/> 
prefix dbc:   <http://dbpedia.org/resource/Category:> 
prefix movie: <http://movie.example.org/> 
prefix owl:   <http://www.w3.org/2002/07/owl#> 
prefix director: <http://director.example.org/> 
prefix xsd:   <https://www.w3.org/2011/rdf-wg/wiki/XSD_Datatypes> 
prefix rdfs:  <http://www.w3.org/2000/01/rdf-schema#> 
prefix jt:    <http://schema.example.org/> 
prefix gr:    <http://genrerating.example.org/> 
prefix fr:    <http://filmrating.example.org/> 
prefix dr:    <http://directorrating.example.org/> 
prefix dbo:   <http://dbpedia.org/ontology/> 
prefix ex:    <http://example.org/>
prefix rdf:   <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
prefix genre: <http://genre.example.org/> 
prefix dcterms: <http://dublincore.org/documents/2012/06/14/dcmi-terms/> 
prefix region: <http://region.example.org/>
prefix user:  <http://user.example.org/> 
prefix foaf:  <http://xmlns.com/foaf/0.1/> 

{}"""

user_rating_dict = dict()
movie_info_dict = dict()

def load_all_movie_info():
	endpoint = SPARQLWrapper(SPARQL_ENDPOINT)
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
			movie_info_dict[movieId] = {'genres': [genre], 'year':year, 'country': country, 'region':[region], 'director': director, 'traits':[trait]}
		else:
			movie = movie_info_dict.get(movieId)
			if not genre in movie.get('genres'):
				movie_info_dict.get(movieId).get('genres').append(genre)
			if not region in movie.get('region'):
				movie_info_dict.get(movieId).get('region').append(region)
			if trait is not None and not trait in movie.get('traits'):
				movie_info_dict.get(movieId).get('traits').append(trait)
			
	print(movie_info_dict.get('75'))
	exit(9)
		# entry = ''
		#for var in result:
			# entry += '{}: {} '.format(var, result.get(var).get('value'))
		# print(entry)

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

def main():
	load_all_movie_info()
	exit(9)
	load_rdf_graph()
	read_ratings_file()

if __name__ == "__main__":
	main()