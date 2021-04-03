---
title: Working with API
---

> This functionality requires an experimental `server` plugin. [Read More](../references/plugins-reference.md)

It's possible to start Frictionless API as a standalone server. This capability is highly experimental at the moment and **it's not tested to be secure**. Please don't use the server in production environment.

## Install

The API server are shipped as plugin so you need to install it with the core framework:

```bash title="CLI"
pip install frictionless[server]
```

## Server

It's simple to start the API server:

```bash title="CLI"
frictionless api
```

Not you can make HTTP calls to:

```
http://localhost:8000
```

The API is the same as Python and Command-Line interfaces use.

## Inputs

All input data is expected to be in JSON format, for exmaple:

> [POST] http://localhost:8000/extract

```json title="API"
{
	"source": "data/table.csv"
}
```

## Ouputs

All output data will be in JSON format, for example:

```json title="API"
[
    {
        "id": 1,
        "name": "english"
    },
    {
        "id": 2,
        "name": "中国人"
    }
]
```

## Debug

Watch the command-line session when you ran `frictionless api` to get the server's logs.
