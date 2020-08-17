def make_bracket_ttl(mvId: int, rating: float, time: str):
	entry_line = 'jt:hasRated ex:m_{};\n\t jt:withRating {};\n\t jt:atTime {}'.format(mvId, rating, time)
	entry = '\tjt:ratedMovie [\n\t{}];\n'.format(entry_line)
	return entry
    
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
    str += '@prefix movie:   <http://movie.example.org/>.\n'
    str += '@prefix user:   <http://user.example.org/>.\n'
    str += '@prefix director:   <http://director.example.org/>.\n'
    str += '@prefix country:   <http://country.example.org/>.\n'
    str += '@prefix genre:   <http://genre.example.org/>.\n'
    str += '@prefix region:   <http://region.example.org/>.\n'
    str += '@prefix fr:   <http://filmrating.example.org/>.\n'
    str += '@prefix dr:   <http://directorrating.example.org/>.\n'
    str += '@prefix rr:   <http://regionrating.example.org/>.\n'
    str += '@prefix gr:   <http://genrerating.example.org/>.\n'
    str += '@prefix ex:   <http://example.org/>.\n\n'
    return str
	
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