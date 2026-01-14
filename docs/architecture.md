# Architecture

This document explains the architectural patterns used in WuLims, focusing on HTMX integration.

## Overview

WuLims uses a **server-rendered architecture with HTMX** for dynamic interactions. This approach:

- Avoids JavaScript framework complexity (no React/Vue/Angular)
- Keeps logic on the server (Python, not JavaScript)
- Provides fast, responsive UIs without page reloads
- Is easier to learn and debug

## The HTMX Pattern

Traditional web apps reload the entire page. Single Page Apps (SPAs) use JavaScript to update parts of the page. **HTMX is a middle ground**: it lets the server return HTML fragments that replace parts of the page.

```
Traditional:  Click → Full page reload → Entire HTML response
SPA:          Click → JavaScript → JSON API → JavaScript renders HTML
HTMX:         Click → HTMX request → Server returns HTML fragment → Replace element
```

### How HTMX Works

1. Add `hx-*` attributes to HTML elements
2. HTMX intercepts events (clicks, form submits, etc.)
3. HTMX makes an AJAX request to the server
4. Server returns HTML (not JSON)
5. HTMX swaps the HTML into the page

```html
<!-- When clicked, fetch /samples/_table/ and put the response in #table-target -->
<button hx-get="/samples/_table/"
        hx-target="#table-target"
        hx-swap="innerHTML">
    Refresh Table
</button>

<div id="table-target">
    <!-- Table content will be inserted here -->
</div>
```

---

## Key HTMX Attributes

| Attribute | Purpose | Example |
|-----------|---------|---------|
| `hx-get` | Make GET request | `hx-get="/samples/"` |
| `hx-post` | Make POST request | `hx-post="/samples/1/approve/"` |
| `hx-target` | Where to put response | `hx-target="#result"` |
| `hx-swap` | How to insert response | `hx-swap="innerHTML"` |
| `hx-trigger` | When to send request | `hx-trigger="click"` |
| `hx-include` | Include form data | `hx-include="#filter-form"` |

### Swap Options

```html
hx-swap="innerHTML"     <!-- Replace inner content (default) -->
hx-swap="outerHTML"     <!-- Replace entire element -->
hx-swap="beforeend"     <!-- Append inside element -->
hx-swap="afterend"      <!-- Insert after element -->
hx-swap="delete"        <!-- Delete the target -->
```

### Trigger Options

```html
hx-trigger="click"                      <!-- On click (default for buttons) -->
hx-trigger="load"                       <!-- When element loads -->
hx-trigger="change"                     <!-- When input changes -->
hx-trigger="keyup changed delay:300ms"  <!-- Debounced keyup -->
hx-trigger="submit"                     <!-- On form submit -->
```

---

## Our HTMX Patterns

### Pattern 1: Live Filtering

The sample list filters without page reload:

```html
<!-- Filter form -->
<form id="filter-form">
    <input type="text" name="q" placeholder="Search...">
    <select name="status">
        <option value="">Any</option>
        <option value="RECEIVED">Received</option>
    </select>
</form>

<!-- Table container - loads on page load and when filters change -->
<div hx-get="/samples/_table/"
     hx-trigger="load, keyup changed delay:300ms from:#filter-form, change from:#filter-form"
     hx-target="#table-target"
     hx-include="#filter-form">

    <div id="table-target">
        <!-- Table rows loaded here -->
    </div>
</div>
```

**How it works:**
1. `hx-trigger="load"` - Loads table when page loads
2. `keyup changed delay:300ms` - Reloads when typing (debounced)
3. `change from:#filter-form` - Reloads when dropdown changes
4. `hx-include="#filter-form"` - Sends form data with each request

**Server view (`views.py`):**
```python
def sample_table(request):
    """HTMX endpoint - returns table HTML fragment."""
    samples = Sample.objects.all()

    # Apply filters from request
    q = request.GET.get("q", "")
    if q:
        samples = samples.filter(
            Q(sample_id__icontains=q) | Q(client_name__icontains=q)
        )

    status = request.GET.get("status", "")
    if status:
        samples = samples.filter(status=status)

    return render(request, "samples/partials/sample_table.html", {"samples": samples})
```

### Pattern 2: Tab Switching

Sample detail page switches tabs without reload:

```html
<!-- Tab navigation -->
<ul class="nav nav-tabs">
    <li class="nav-item">
        <a class="nav-link active"
           hx-get="/samples/{{ sample.pk }}/?tab=overview"
           hx-target="#tab-content"
           hx-swap="innerHTML">
            Overview
        </a>
    </li>
    <li class="nav-item">
        <a class="nav-link"
           hx-get="/samples/{{ sample.pk }}/?tab=coc"
           hx-target="#tab-content"
           hx-swap="innerHTML">
            Chain of Custody
        </a>
    </li>
</ul>

<!-- Tab content -->
<div id="tab-content">
    <!-- Active tab content loaded here -->
</div>
```

**Server view:**
```python
def sample_detail(request, pk):
    sample = get_object_or_404(Sample, pk=pk)
    tab = request.GET.get("tab", "overview")

    # Return partial for HTMX requests
    if tab == "overview":
        return render(request, "samples/partials/sample_overview.html", {"sample": sample})
    elif tab == "coc":
        return render(request, "samples/partials/sample_chain_of_custody.html", {"sample": sample})

    # Full page for initial load
    return render(request, "samples/sample_detail.html", {"sample": sample})
```

### Pattern 3: Modal Dialogs

Approval modal loads dynamically:

```html
<!-- Button triggers modal load -->
<button hx-get="/samples/{{ sample.pk }}/_approve_modal/"
        hx-target="#modal-container"
        hx-swap="innerHTML">
    Approve
</button>

<!-- Modal container -->
<div id="modal-container"></div>
```

**Modal template (`approve_modal.html`):**
```html
<div class="modal fade show" style="display: block;">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h5>Approve Sample</h5>
                <button type="button" class="btn-close"
                        hx-get="/samples/_clear_modal/"
                        hx-target="#modal-container">
                </button>
            </div>
            <div class="modal-body">
                <p>Approve sample {{ sample.sample_id }}?</p>
            </div>
            <div class="modal-footer">
                <button hx-post="/samples/{{ sample.pk }}/approve/"
                        hx-target="#sample-row-{{ sample.pk }}"
                        hx-swap="outerHTML">
                    Confirm
                </button>
            </div>
        </div>
    </div>
</div>
<div class="modal-backdrop fade show"></div>
```

### Pattern 4: Out-of-Band Swaps

Update multiple elements with one response using `hx-swap-oob`:

```python
def approve_sample(request, pk):
    sample = get_object_or_404(Sample, pk=pk)
    sample.status = Sample.Status.APPROVED
    sample.approved_by = request.user
    sample.approved_at = timezone.now()
    sample.save()

    # Return multiple HTML fragments
    html = render_to_string("samples/partials/sample_row.html", {"sample": sample})

    # Toast notification (out-of-band swap)
    toast_html = render_to_string("lims_core/partials/toast.html", {
        "message": f"Sample {sample.sample_id} approved",
        "level": "success"
    })

    # Clear modal (out-of-band swap)
    return HttpResponse(
        html +
        f'<div id="toast-target" hx-swap-oob="beforeend">{toast_html}</div>' +
        '<div id="modal-container" hx-swap-oob="innerHTML"></div>'
    )
```

**How `hx-swap-oob` works:**
- The main response replaces the target (`#sample-row-X`)
- Elements with `hx-swap-oob` are swapped to their matching IDs
- This allows updating the row, showing a toast, AND closing the modal in one response

---

## Template Organization

### Full Page vs Partial Templates

**Full pages** extend `base.html` and render complete HTML:

```html
{% extends "lims_core/base.html" %}

{% block content %}
<h1>Sample List</h1>
<!-- Page content -->
{% endblock %}
```

**Partials** are HTML fragments for HTMX (no `{% extends %}`):

```html
<!-- samples/partials/sample_table.html -->
<table class="table">
    <thead>
        <tr>
            <th>Sample ID</th>
            <th>Client</th>
            <th>Status</th>
        </tr>
    </thead>
    <tbody>
        {% for sample in samples %}
        <tr id="sample-row-{{ sample.pk }}">
            <td>{{ sample.sample_id }}</td>
            <td>{{ sample.client_name }}</td>
            <td>{{ sample.get_status_display }}</td>
        </tr>
        {% endfor %}
    </tbody>
</table>
```

### Naming Conventions

| Type | Location | Example |
|------|----------|---------|
| Full pages | `templates/app/` | `sample_list.html` |
| Partials | `templates/app/partials/` | `sample_table.html` |
| HTMX endpoints | URL with `_` prefix | `/_table/`, `/_modal/` |

---

## URL Design for HTMX

```python
# samples/urls.py
urlpatterns = [
    # Full page views
    path("", views.sample_list, name="list"),
    path("<int:pk>/", views.sample_detail, name="detail"),

    # HTMX endpoints (prefixed with _)
    path("_table/", views.sample_table, name="table"),
    path("<int:pk>/_approve_modal/", views.approve_modal, name="approve_modal"),
    path("<int:pk>/approve/", views.approve_sample, name="approve"),
]
```

The underscore prefix (`_table/`) indicates HTMX-only endpoints that return partials.

---

## Bootstrap Integration

Bootstrap is loaded via CDN in `base.html`. Use Bootstrap classes directly:

```html
<div class="card">
    <div class="card-header">Sample Details</div>
    <div class="card-body">
        <button class="btn btn-primary">Submit</button>
    </div>
</div>
```

See [Bootstrap 5 documentation](https://getbootstrap.com/docs/5.3/) for available components.

---

## Alpine.js (Optional)

Alpine.js is included for simple client-side interactivity when HTMX isn't enough:

```html
<div x-data="{ open: false }">
    <button @click="open = !open">Toggle</button>
    <div x-show="open">Content</div>
</div>
```

Use Alpine.js for:
- Simple show/hide toggles
- Client-side validation feedback
- Dropdown menus

Use HTMX for:
- Loading data from server
- Form submissions
- Any server interaction

---

## Common Gotchas

### 1. CSRF Tokens

Django requires CSRF tokens for POST requests. HTMX handles this automatically if you include:

```html
<body hx-headers='{"X-CSRFToken": "{{ csrf_token }}"}'>
```

Or include the token in forms:

```html
<form hx-post="/submit/">
    {% csrf_token %}
    <!-- form fields -->
</form>
```

### 2. ID Conflicts

Every HTMX target needs a unique ID:

```html
<!-- Bad: duplicate IDs -->
{% for sample in samples %}
<div id="sample-row">...</div>  <!-- All have same ID! -->
{% endfor %}

<!-- Good: unique IDs -->
{% for sample in samples %}
<div id="sample-row-{{ sample.pk }}">...</div>
{% endfor %}
```

### 3. Loading States

Show loading indicators with `hx-indicator`:

```html
<button hx-get="/slow-endpoint/"
        hx-indicator="#spinner">
    Load Data
</button>
<span id="spinner" class="htmx-indicator">Loading...</span>
```

---

## Next Steps

- Read [Creating Views](creating-views.md) for hands-on view creation
- See the `samples/` app for working examples of all these patterns
