# PlanetREST

A demo REST service that uses the Flask framework.

## Details

I actually implemented this twice. I was learning Flask during the first pass so I aimed to keep it fairly simple and wrote raw SQL.

Second pass, I used [Flask-Restless](http://flask-restless.readthedocs.org/en/stable/) which basically generates a REST API from SQLAlchemy models. Less code, and less to worry about in terms of correctly implementing REST. Sadly though, the Flask TestClient doesn't play too nicely with it so I wrote tests against the live service using Request.

## Running it

I included a Vagrantfile in each directory to get it working quickly on most major OSes.

Make sure you have [vagrant](https://vagrantup.com) and [virtualbox](https://virtualbox.org) (or some other hypervisor) installed.

### Flask-restless version
```
$ cd planetrest/2
$ vagrant up
```

### Flask version
```
$ cd planetrest/1
$ vagrant up
```

In either version, the service should be available at http://localhost:5000/ on the *host* after a few minutes when vagrant has finished spinning up the VM and installing dependencies.

## Shut down / Clean up

Run `vagrant destroy` from the `1/` or `2/ directory to shut down and remove the VMs
