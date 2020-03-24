# Ascii server converter
Converts image to an ascii

## Implementation 
Server is implemented in [fastapi](https://github.com/tiangolo/fastapi). It
uses asyncio. Server only uploads an image and queues the image for processing.
Processing is done asynchronously and server can still get requests.
Converting images is a separate file and could be easily switched for another
faster implementation for example in C or Rust.

It took me around 10 hours to finish it. Mainly because I decide to learn more
about fastpi and new python typing and playing with different ascii conversion
implementations.

1. **What would you monitor during the initial rollout of this service? What tools would you setup?
   Would you make any changes to the code, or packaging of the container?**

   I would monitor basic metric CPU, disk IO, disk space and network. Next would be number
   of errors in logs and histogram of conversion times per picture. The service
   provides a status page with some basic metrics.

   Tools for monitoring - for example: Prometheus for metrics or datadog.
   Splunk or ElasticSearch for logs.

   I would put the config from the server itself into a separate file.

2. **Customers are wild about this new capability and we find out usage is growing fast with
   thousands of simultaneous customers who are each submitting large workloads! How would you scale
   up the service to respond? Are there any bottlenecks you anticipate? Are there any API changes
   you'd make for v2?**

   * **Scaling**  
   Right now conversion and web server are in the same container. It would make
   sense to split it up. Web server is ready for it. Instead of starting up the
   conversion it would just store the image and queue the image id into another
   service (could kafka if it's already setup). Conversion service would pick
   up ids and work on the conversion.
   
   * **Bottlenecks**
       * speed of conversion - mainly CPU and some IO
       * upload speed and store speed  


   * **v2 version**  
   I would not add anything to the v2, but it would make sense to include
   richer search API and some kind of security. Username and password.

3. **One morning, you get a rushed email from a product manager saying customers are emailing telling
   them the service is "broken" but they're short on details. What followup questions would you
   ask? What would you investigate?** 

    What is the exact error they are getting and in what phase (uploading or
    getting results). Is it only one customer or multiple. If it's just one are
    there more customers complaining.  I would check logs of the service and metrics. Speed of
    conversion is the service overloaded, disk full or if it's larger outage in
    our system.

## Upload an image
`curl -X POST -F 'file=@test.png' localhost:8080/ascii?size=100`  
`curl -X POST -F 'file=@test.png' localhost:8080/upload`  

The converted image keeps size ration. The size paramater is x-axis of the
image. y-axis will be computed based on it.

The call returns an image id in the format `{"image_id":"c39b32fc-6d59-11ea-8fd6-40a3cc6050d6"}`

## Get an image
`curl -f --show-error http://127.0.0.1:8080/image/<imageid>/ascii`


Returns an ascii image for the id.

## Get an metadata
`curl -f --show-error http://127.0.0.1:8080/image/<imageid>/ascii`

```
{
    "filename": "test.png",
    "created": 1585004288.9470613,
    "state": "ready",
    "image_type": "PNG",
    "image_size": [560, 560],
    "convert_time": 0.007903814315795898
}
```

## Get an original
`curl -f --show-error http://127.0.0.1:8080/image/<imageid>/original`

## List all stored images
`curl -f --show-error http://127.0.0.1:8080/list`


## Show status
`curl -f --show-error http://127.0.0.1:8080/status`

```
{
    "errors":0,
    "uploaded_count":2
}
```


