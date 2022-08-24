---
title: Server Guide
---

The Server concept is quite simple. A server needs to have a two functions:
- `server.start`
- `server.stop`

## Server Example

```python script title="Python"
from frictionless import Server

class ApiServer(Server):

    # Start

    def start(self, *, port):
        app = create_api()
        # This function create a Flask app
        server = create_server(app, port=port)
        # This functio runs it
        server.run()
```
