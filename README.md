# Utility to answer/check for valid ens addresses used by caddy ask

runs on :80 
its intended to run on a domain. so add your root domain in -b .example.com  so when a request comes for ensdomain.example.com example.com will be stripped and provider will be queried if ensdomain.eth exists. If it does it Returns 200 OK and caddy will resume with cert request.

## usage:
```
python3 app.py -h
```
## test example
```
curl 0:80/?domain=somedomain.eth
```

## docker image:
```
darkobas/enschecker:latest
```

## docker usage:
```
command: -b .my.link.domain -p https://myrpc.provider/
```

## caddy usage:
in global
```
  on_demand_tls {
      ask http://docker_enschecker/
      interval 1m
      burst    15
  }
```
