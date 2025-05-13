## SSE to Streamable-HTTP proxy
See https://gofastmcp.com/
- easy to migrate from SSE to Streamable-HTTP
  
## Adding auth
Simple testing using NGROK
```
   server_b = MCPServerSse(
        name="Server B",
        params={
            "url": "https://bd20-2a02-1810-b41d-b600-8c37-1e56-75c1-3035.ngrok-free.app/sse",
            "headers": {"Authorization": f"Basic dXNlcjpwYXNzd29yZDE="}
        },
    )
```
```
ngrok http http://localhost:8001 --traffic-policy-file policy.yml
```
```
on_http_request:
  - actions:
      - type: basic-auth
        config:
          realm: sample-realm
          credentials:
            - user:password1
            - admin:password2
          enforce: true
```
