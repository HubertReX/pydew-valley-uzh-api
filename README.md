# PyDew Valley UZH API

A **mockup** of an API based on [these requirements](https://github.com/users/sloukit/projects/1/views/1?pane=issue&itemId=67455851) for a [mod of PyDew Valley](https://github.com/sloukit/pydew-valley-uzh).

## Starting server

```bash

start_server.sh

```

## Testing API

```bash

run_client_test.sh

```

## Manual API call

```bash

# root endpoint
curl -i -H "Accept: application/json" \
    -H "Content-Type: application/json" \
    -H "x-api-key: 123" \
    http://localhost:5000/

# authenticate user
curl --request POST \
    --data '{"play_token":"321"}' \
    -H "Accept: application/json" \
    -H "Content-Type: application/json" \
    -H "x-api-key: 123" \
    http://localhost:5000/authn

# send telemetry
# substitute AAAAAAAAAAAA.BBBBBBBBBBBB.CCCCCCCCCCCC" with jwt token returned from authn endpoint
# if jwt was empty, the authentication failed
curl --request POST \
    --data '{"telemetry_data":{"self_assessment": "ok"}}' \
    -H "Accept: application/json" \
    -H "Content-Type: application/json" \
    -H "x-api-key: 123" \
    -H "Authorization: Bearer AAAAAAAAAAAA.BBBBBBBBBBBB.CCCCCCCCCCCC" \
    http://localhost:5000/telemetry

```
