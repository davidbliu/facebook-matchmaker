mydata = read.csv("c:/Users/david/Desktop/share/facebook-matchmaker/comments/speech_vectors.csv")
names = t(read.csv("c:/Users/david/Desktop/share/facebook-matchmaker/comments/people.csv"))
frame = as.data.frame(t(mydata))

colnames(frame) = names

result = kmeans(mydata, 10)
centers = result$centers
length(centers)

for(j in 1:length(centers[,1])){
  print(j)
  for(name in names){
  #   name = "David Liu"
    person_vec = frame[[name]]
    maxdist = 2147483647
    group = -1
    for(i in 1:length(centers[,1])){
      dist = dist(rbind(person_vec, centers[i,]))
      if(dist<maxdist){
        maxdist = dist
        group = i
      }
    }
    if(group == j){
      print(name)
    }
  }
}
