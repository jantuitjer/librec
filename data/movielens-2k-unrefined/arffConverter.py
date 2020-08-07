import os
import sys
from datetime import datetime
os.chdir(os.path.dirname(sys.argv[0]))


if not(os.path.isdir("out")):   #check if 'out dir exists
    os.mkdir("out")


#with open("user_ratedmovies-timestamps.dat") as file:
#        with open("out/ratings_timestamp.txt","a+") as out:
#            next(file)
#            for line in file:
#                params = line.split("\t")
#                #userId=params[0]
#                #movieId=params[1]
#                #rating=params[2]
#                out.write(params[0] + " " + params[1] + " " +params[2]+ " " + params[3]+"\n")
#print("done")
type_dict = { 'id': 'numeric',
 'title': 'string',
 'imdbID': 'numeric',
 'spanishTitle': 'string',
 'imdbPictureURL': 'string',
 'year': 'numeric',
 'rtID': 'string',
 'rtAllCriticsRating': 'numeric',
 'rtAllCriticsNumReviews': 'numeric',
 'rtAllCriticsNumFresh': 'numeric',
 'rtAllCriticsNumRotten': 'numeric',
 'rtAllCriticsScore': 'numeric',
 'rtTopCriticsRating': 'numeric',
 'rtTopCriticsNumReviews': 'numeric',
 'rtTopCriticsNumFresh': 'numeric',
 'rtTopCriticsNumRotten': 'numeric',
 'rtTopCriticsScore': 'numeric',
 'rtAudienceRating': 'numeric',
 'rtAudienceNumRatings': 'numeric',
 'rtAudienceScore': 'numeric',
 'rtPictureURL': 'string',
 'movieID': 'numeric',
 'actorID': 'string',
 'actorName': 'string',
 'ranking': 'numeric',
 'country': 'string',
 'directorID': 'string',
 'directorName': 'numeric',
 'genre': 'string',
 'location1': 'string',
 'location2': 'string',
 'location3': 'string',
 'location4': 'string',
 'tagID': 'numeric',
 'tagWeight': 'numeric',
 'value': 'string',
 'userID': 'numeric',
 'rating': 'numeric',
 'timestamp': 'date',
 'date_day': 'numeric',
 'date_month': 'numeric',
 'date_year': 'numeric',
 'date_hour': 'numeric',
 'date_minute': 'numeric', 
 'date_second': 'numeric'         
}
#now = datetime.now()
#print(now)
#print(datetime.timestamp(now))
#datetime.fromtimestamp(timestamp)
seen_header = dict()
for filename in os.listdir(os.getcwd()):
    if filename.endswith('dat'):
        print(filename)
        with open(filename) as data:
            filename = filename.split('.')[0]     
            with open("out/"+filename+".arff","a+") as out:
                out.write('@Relation '+ filename+'\n')
                header = next(data)
                header_arr = header.split("\t")
                contains_time = False
                contains_escape = False
                cnt = -1
                t_pos = -1
                imdbURL_pos = -1
                picURL_pos = -1
                title_pos = -1
                sTitle_pos = -1
                for entry in header_arr:
                    cnt += 1
                    entry = entry.rstrip()
                    if entry == 'timestamp':
                        contains_time = True
                        t_pos = cnt
                    if entry == 'imdbPictureURL':
                        imdbURL_pos = cnt
                        contains_escape = True
                    if entry == 'rtPictureURL':
                        picURL_pos = cnt
                        contains_escape = True
                    if entry == 'title':
                        title_pos = cnt
                        contains_escape = True
                    if entry == 'spanishTitle':
                        sTitle_pos = cnt
                        contains_escape = True
                    out.write('@ATTRIBUTE ' + entry +"\t" + type_dict.get(entry)+'\n')
                out.write('\n@Data\n')
                for line in data:
                    str_line = ''
                    line_arr = line.split('\t')
                    if not contains_time and not contains_escape:
                        for e in line_arr:
                            str_line += e + ', '
                    else:
                        if contains_time:
                            for i in range(len(line_arr)):
                                if i != t_pos:
                                    str_line += line_arr[i].rstrip() + ', '
                                else:
                                    timestamp = int(line_arr[i].rstrip())/1000 #convert into seconds from milliseconds
                                    time = datetime.fromtimestamp(timestamp) 
                                    str_line += str(time) + ', '
                        if contains_escape:
                            for i in range(len(line_arr)):
                                if i != imdbURL_pos and i != picURL_pos and i != title_pos and i != sTitle_pos:
                                     str_line += line_arr[i].rstrip() + ', '
                                else:
                                    val = line_arr[i].rstrip()
                                    if '"' in val:
                                        str_line += val + ", "
                                    else:    
                                        escaped ='"' + line_arr[i].rstrip() + '"'
                                        str_line += escaped + ", "
                    str_line = str_line[:-2]
                    
                    if contains_time or contains_escape:
                        out.write(str_line+'\n')
                    else:
                        out.write(str_line)
print('done')