# Debugging HTMX

HTMX replaces parts of the page with server responses, which makes network requests harder to trace than a traditional page load. This guide covers tools for diagnosing broken requests, unexpected swaps, and response errors.

## Browser Console Snippet

Paste this snippet into `lims_core/base.html` just before the closing `</body>` tag. **Remove it when you're done debugging** — it is not meant for production.

```html
<script>
  (function () {
    if (window.WuLimsHtmxDebug) return;
    window.WuLimsHtmxDebug = true;
    // eslint-disable-next-line no-console
    console.log("[HTMX] debug enabled");

    function logEvent(name, evt) {
      try {
        const detail = evt.detail || {};
        const xhr = detail.xhr || {};
        const info = {
          event: name,
          target: (detail.target && detail.target.id) || null,
          status: xhr.status || null,
          successful: detail.successful ?? null,
          path: (detail.pathInfo && detail.pathInfo.requestPath) || null,
        };
        // eslint-disable-next-line no-console
        console.log("[HTMX]", info);
      } catch (e) {
        // eslint-disable-next-line no-console
        console.log("[HTMX] log failed", e);
      }
    }

    document.body.addEventListener("htmx:beforeRequest", (evt) => logEvent("beforeRequest", evt));
    document.body.addEventListener("htmx:afterRequest", (evt) => logEvent("afterRequest", evt));
    document.body.addEventListener("htmx:afterOnLoad", (evt) => logEvent("afterOnLoad", evt));
    document.body.addEventListener("htmx:responseError", (evt) => logEvent("responseError", evt));
    document.body.addEventListener("htmx:afterSwap", (evt) => logEvent("afterSwap", evt));
    document.body.addEventListener("htmx:swapError", (evt) => {
      logEvent("swapError", evt);
      try {
        const xhr = evt.detail && evt.detail.xhr;
        if (xhr) {
          const preview = (xhr.responseText || "").slice(0, 300);
          // eslint-disable-next-line no-console
          console.log("[HTMX] swapError response preview:", preview);
        }
      } catch (e) {
        // eslint-disable-next-line no-console
        console.log("[HTMX] swapError preview failed", e);
      }
    });
  })();
</script>
```

Open your browser's **Developer Tools → Console** tab to see the output.

## What Each Event Means

| Event | When it fires | What to look for |
|-------|--------------|-----------------|
| `beforeRequest` | Just before HTMX sends the request | Confirm the correct `path` is being called |
| `afterRequest` | After the server responds | Check `status` (200 = ok, 403 = CSRF/auth, 500 = server error) and `successful` flag |
| `afterOnLoad` | After the response body is loaded | Fires even on error responses |
| `responseError` | Server returned a non-2xx status | `status` shows the HTTP error code |
| `afterSwap` | HTML was successfully swapped into the DOM | Confirm `target` is the element you expected |
| `swapError` | HTMX could not perform the swap | Response preview shows what the server actually returned |

## Common Problems

### 403 on POST requests

HTMX POST requests require a CSRF token. Make sure `base.html` includes:

```html
<body hx-headers='{"X-CSRFToken": "{{ csrf_token }}"}'>
```

Without this, Django returns 403 and the `afterRequest` log will show `status: 403, successful: false`.

### Swap targets the wrong element

The `target` field in the log shows the element ID being updated. If it is `null` or wrong, check that:

- The element exists on the page before the request fires
- The `hx-target` selector matches an actual ID or CSS selector in the DOM

### Server returns an error page instead of a partial

If `swapError` fires and the response preview contains `<!DOCTYPE html>`, the view is returning a full HTML page (usually Django's debug error page) instead of a fragment. Check the Django terminal output for the traceback.

### Request never fires

If no `beforeRequest` log appears after clicking a button:

- Confirm HTMX is loaded — check the Network tab for `htmx.min.js`
- Confirm the element has `hx-get` or `hx-post` (not just `hx-target`)
- Check for JavaScript errors earlier in the console that may have prevented HTMX from initializing

## Built-in HTMX Logging

HTMX also has a built-in logger you can enable from the console without editing any files:

```js
htmx.logger = function(elt, event, data) {
    console.log(event, elt, data);
}
```

This is more verbose than the snippet above and useful for inspecting the full event payload.

## Removing the Debug Snippet

When debugging is complete, delete the `<script>` block from `lims_core/base.html`. The `window.WuLimsHtmxDebug` guard prevents the listeners from being registered twice if the script is accidentally included more than once, but it should not ship to production.

## Related

- [Architecture](architecture.md) — HTMX patterns used in WuLims
- [Creating Views](creating-views.md) — How HTMX endpoints are structured
