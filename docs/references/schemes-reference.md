---
title: Schemes Reference
---

It's a schemes reference supported by the main Frictionless package. If you have installed external plugins, there can be more schemes available. Below we're listing a scheme group name (or a loader name) like Remote, which is used, for example, for `http`, `https` etc schemes. Options can be used for creating controls, for example, `control = RemoteControl(http_timeout=1)`.


## S3


### Options

#### Endpoint Url

> Type: string

Endpoint url



## Filelike


There are no options available.


## Local


There are no options available.


## Remote


### Options

#### Http Session

> Type: requests.Session

User defined http session

#### Http Preload

> Type: bool

Don't use http streaming and preload all the data

#### Http Timeout

> Type: int

User defined http timeout in minutes



## Text


There are no options available.
