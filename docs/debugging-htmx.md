## Debugging HTMX

Debugging HTMX can be challenging due to its asynchronous nature.

You can use the following snippet; paste it into lims_core/base.html near the bottom.

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

That will add console logging to your browser.  You can see the htmx events by opening your browser's developer tools
and watching the console.
