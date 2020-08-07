import os
import sys
os.chdir(os.path.dirname(sys.argv[0]))


if not(os.path.isdir("out")):   #check if 'out dir exists
    os.mkdir("out")

with open("user_ratedmovies-timestamps.dat") as file:
        with open("out/ratings-timestamps.txt","a+") as out:
            next(file)
            for line in file:
                params = line.split("\t")
                #userId=params[0]
                #movieId=params[1]
                #rating=params[2]
                out.write(params[0] + " " + params[1] + " " +params[2]+ " " +params[3])
print("done")
