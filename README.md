# Web Server
Homework #4 (OTUS. Python Developer. Professional)

Python Web Server from scratch.

## Run dev
`docker-compose up`

## Run tests and linters
`docker-compose -f docker-compose.ci.yml up --build`

## Architecture
Multithreading socket server. Processes HTTP requests and serves static files

## Load test results
Command to run benchmarking: ` ab -n 50000 -c 100 -r http://localhost:8080/`

### Results of 50k requests
```
Server Software:        python
Server Hostname:        localhost
Server Port:            8080

Document Path:          /
Document Length:        74 bytes

Concurrency Level:      100
Time taken for tests:   5.592 seconds
Complete requests:      50000
Failed requests:        0
Non-2xx responses:      50000
Total transferred:      5900000 bytes
HTML transferred:       3700000 bytes
Requests per second:    8941.57 [#/sec] (mean)
Time per request:       11.184 [ms] (mean)
Time per request:       0.112 [ms] (mean, across all concurrent requests)
Transfer rate:          1030.38 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    0   0.3      0       9
Processing:     2   11   0.6     11      19
Waiting:        1   11   0.6     11      18
Total:          9   11   0.6     11      21

Percentage of the requests served within a certain time (ms)
  50%     11
  66%     11
  75%     11
  80%     11
  90%     12
  95%     12
  98%     13
  99%     13
 100%     21 (longest request)
```
