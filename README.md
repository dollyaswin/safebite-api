# Safebite Tensorflow App

This is a Flask App who run Tensorflow model

## Build

Need to build the docker image first

```
docker build -t safebite-tf .
```

If there is no error, you can continue to run a container for this.
This app run in port `5000` as defined [here](https://github.com/dollyaswin/safebite-api/blob/main/Dockerfile#L22), and on this example we will run the container at port `5001`


```
docker run  --name safebite-tf-flask -p 5001:5000 safebite-tf
```

If there is no error, you can test the Flask app by sending HTTP Request 

```  
 curl -X POST --header 'Content-Type: application/json' \
      --data  '{"text": "carrot"}' http://localhost:5001/process_input
```

It will give response like this

```
{
  "result": {
    "Allergies Prediction": "Sorry we can't detect it",
    "Data": "carrot",
    "Diseases Prediction": "Sorry we can't detect it",
    "Halal/Haram Prediction": "Sorry we can't detect it"
  },
  "status": "success"
}
```
