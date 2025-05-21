
# NDT7 python port for local testing

## Setup
```
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
```

## Setup local ndt server
```
git clone https://github.com/m-lab/ndt-server.git
mkdir certs datadir
docker-compose run ndt-server ./gen_local_test_certs.bash
docker-compose up
```

## To Run
```
python3 ndt7_test.py --local    
```

# Sample output
```
Starting NDT7 tests ...

Server: localhost:4443
Client: 192.168.1.9

Download Started
Download: 2672.52 Mb/s 
Download: Complete
Upload Started
Upload: 2796.75 Mb/s 
Upload Completed

Finshed NDT7 tests

```

## Extending 
Use serverconfig after discovery for upload download test

# License
This project is licensed under the [MIT License][License].

[License]: ./LICENSE

