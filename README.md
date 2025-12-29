
# WebSockets + Django (ASGI) — How to use views and sockets simultaneously

This project demonstrates using a regular Django HTTP view and an ASGI WebSocket consumer together. The HTTP view triggers a message that is forwarded to a WebSocket group — so clients connected over WebSocket receive the update pushed from an HTTP request.

## Quick overview

- HTTP view endpoint (adds/forwards data): POST /add/
- WebSocket endpoint (clients connect): ws://<host>:<port>/ws/somepath/
- Group name used by both sides: `demo` (the view sends to this group; the consumer joins it)

The flow:
1. A client sends an HTTP POST to `/add/` with a JSON body containing a `data` field.
2. The view reads that JSON and calls the channel layer to group-send a message to group `demo`.
3. Any connected WebSocket client (connected to `/ws/somepath/`) will receive that message via the consumer's `add_function` handler.

## Files / routing (what's in the project)

- `myapp/views.py` exposes the `add` view at `path('add/', add)` which expects POST JSON and sends group messages using `channels`.
- `myapp/consumers.py` defines `MyConsumer` which joins the `demo` group and implements `add_function` to forward messages to the WebSocket client.
- `myapp/routing.py` maps the WebSocket route:

		re_path(r'ws/somepath/$', MyConsumer.as_asgi()),

- `myproject/asgi.py` registers both `http` and `websocket` protocols with Channels' `ProtocolTypeRouter`.

## Run the project (development)

Install dependencies (basic):

```bash
python -m pip install django channels uvicorn
```

Run migrations (if your project uses models):

```bash
python manage.py migrate
```

Start the ASGI server with Uvicorn (recommended for development with auto-reload):

```bash
uvicorn myproject.asgi:application --reload
```

By default, Uvicorn serves on port 8000 so the base URL is http://127.0.0.1:8000/ and the WebSocket URL is ws://127.0.0.1:8000/ws/somepath/

## HTTP: how to call the `add` endpoint

The `add` view expects a POST with a JSON body. Example using curl:

```bash
curl -X POST http://127.0.0.1:8000/add/ \
	-H "Content-Type: application/json" \
	-d '{"data": "hello from http"}'
```

Response (JSON) will include the same `data` value echoed back by the view. The view will also forward that value to the `demo` group via the channel layer.

Note: The view is decorated with `@csrf_exempt` for convenience/testing. In production, replace this with proper CSRF handling or use session/token authentication for your API.

## WebSocket: how to connect and receive the forwarded messages

WebSocket endpoint: ws://127.0.0.1:8000/ws/somepath/

1) Using `wscat` (npm package) from a terminal:

```bash
# install once (if needed)
npm install -g wscat

# connect
wscat -c ws://127.0.0.1:8000/ws/somepath/

# After connecting, any POST to /add/ will cause the server to send a JSON message to your socket. The consumer also sends a greeting on connect.
```

2) Using a browser JavaScript example:

```html
<script>
	const ws = new WebSocket('ws://127.0.0.1:8000/ws/somepath/');

	ws.onopen = () => console.log('socket open');
	ws.onmessage = (evt) => {
		try {
			const data = JSON.parse(evt.data);
			console.log('received', data);
		} catch (err) {
			console.log('non-json msg', evt.data);
		}
	};

	ws.onclose = () => console.log('socket closed');
	ws.onerror = (e) => console.error('socket error', e);
</script>
```

After opening the socket in the browser, run the `curl` POST example above — you'll see the forwarded message appear in the browser console (delivered by `add_function` in the consumer).

## Example: what the messages look like

- On connect, the consumer sends this greeting:

```json
{"message": "hello bibek"}
```

- When the `add` view forwards a value (for example `{"data": "x"}`), the consumer's `add_function` will send to clients:

```json
{"added": "x"}
```

Also, the consumer echoes any message it receives from the client back as `You said: <raw-text>`.

## Notes and production considerations

- The project currently uses `@csrf_exempt` on the `add` view — this is convenient for local testing but insecure for production. Replace with proper CSRF or token-based protection.
- Channel layer backend: by default Channels uses an in-memory layer which is not suitable for multiple workers. For production, configure Redis (or another supported backend) and update `CHANNEL_LAYERS` in `myproject/settings.py`.
- Use authentication/permission checks on both the HTTP view and WebSocket consumer if required by your application.

## Troubleshooting

- If WebSocket connections fail, check the server logs printed by `uvicorn`/ASGI. Ensure `myproject/asgi.py` is loaded (the file prints a startup message in this repo).
- If messages do not arrive to connected clients, confirm the `group_send` call uses the same group name the consumer joins (`demo`).

## Quick summary

1. Start the ASGI server: `uvicorn myproject.asgi:application --reload`.
2. Connect a WebSocket client to `ws://127.0.0.1:8000/ws/add_path/`.
3. POST JSON to `http://127.0.0.1:8000/add/` (e.g. `{ "data": "..." }`).
4. See the forwarded message appear in any connected WebSocket clients.

---
If you'd like, I can also add a short example test or a simple Web UI page in this repo that shows both the HTTP request and the live WebSocket updates together. Would you like that next?

