def get_arff_header():
    header = '@Relation user_movie_rating\n'
    header += '@Attribute user string\n'
    header += '@Attribute item string\n'
    header += '@Attribute rating NUMERIC\n'
    header += '@Attribute review string\n'
    header += '\n@Data\n'
    return header
