to run the stat tracker:

export FLASK_APP=statsCollector

python -m flask run



viewing / on the flask server will display summary page
GET /cluster will cause it to find new clusters for the data it has been given
your chatbat should POST to /record with json {intent: str, count: int, input: str, score: str(that will parse to float)}

where input is the user question, count is how many instances of this were recorded, intent is the label for the answer picked, and score is the confidence in that result. 

the clustering will only use sentences with a confidence below .85

intentCounts.json records how many times each intent was triggered
inputs.json records all of the inputs that have been sent
labeledClusters stores the results of the latest clustering
