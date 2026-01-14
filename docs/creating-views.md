# Creating Views

This guide walks through creating new views in WuLims, from simple pages to HTMX-powered interactions.

## Overview

A view in Django:
1. Receives an HTTP request
2. Processes data (query database, validate forms, etc.)
3. Returns an HTTP response (usually rendered HTML)

We use **function-based views** (not class-based) for simplicity.

---

## Step-by-Step: Creating a New View

### Step 1: Write the View Function

Create or edit `views.py` in your app:

```python
# samples/views.py
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Sample

@login_required
def sample_list(request):
    """Display all samples."""
    samples = Sample.objects.all().order_by("-received_at")
    return render(request, "samples/sample_list.html", {
        "samples": samples,
    })
```

**Key components:**
- `@login_required` - Redirects to login if not authenticated
- `request` - Contains HTTP request data (GET params, POST data, user, etc.)
- `render()` - Combines template with context data

### Step 2: Create the URL Pattern

Add the URL in your app's `urls.py`:

```python
# samples/urls.py
from django.urls import path
from . import views

app_name = "samples"  # Namespace for URL reversing

urlpatterns = [
    path("", views.sample_list, name="list"),
]
```

**URL pattern syntax:**
- `""` - Matches `/samples/` (because this file is included at `/samples/`)
- `<int:pk>/` - Captures an integer named `pk`
- `<str:slug>/` - Captures a string named `slug`
- `name="list"` - Allows reversing with `{% url 'samples:list' %}`

### Step 3: Create the Template

Create `templates/samples/sample_list.html`:

```html
{% extends "lims_core/base.html" %}

{% block title %}Samples - WuLims{% endblock %}

{% block content %}
<h1>Samples</h1>

<table class="table">
    <thead>
        <tr>
            <th>Sample ID</th>
            <th>Client</th>
            <th>Status</th>
            <th>Received</th>
        </tr>
    </thead>
    <tbody>
        {% for sample in samples %}
        <tr>
            <td>
                <a href="{% url 'samples:detail' sample.pk %}">
                    {{ sample.sample_id }}
                </a>
            </td>
            <td>{{ sample.client_name }}</td>
            <td>{{ sample.get_status_display }}</td>
            <td>{{ sample.received_at|date:"M d, Y" }}</td>
        </tr>
        {% empty %}
        <tr>
            <td colspan="4">No samples found.</td>
        </tr>
        {% endfor %}
    </tbody>
</table>
{% endblock %}
```

---

## View Types

### 1. List View

Display multiple objects:

```python
@login_required
def sample_list(request):
    samples = Sample.objects.all()
    return render(request, "samples/sample_list.html", {"samples": samples})
```

### 2. Detail View

Display a single object:

```python
@login_required
def sample_detail(request, pk):
    sample = get_object_or_404(Sample, pk=pk)
    return render(request, "samples/sample_detail.html", {"sample": sample})
```

**URL pattern:**
```python
path("<int:pk>/", views.sample_detail, name="detail"),
```

### 3. Create View

Handle form submission to create objects:

```python
from django.shortcuts import redirect
from .forms import SampleForm

@login_required
def sample_create(request):
    if request.method == "POST":
        form = SampleForm(request.POST)
        if form.is_valid():
            sample = form.save()
            return redirect("samples:detail", pk=sample.pk)
    else:
        form = SampleForm()

    return render(request, "samples/sample_form.html", {"form": form})
```

### 4. Update View

Edit existing objects:

```python
@login_required
def sample_update(request, pk):
    sample = get_object_or_404(Sample, pk=pk)

    if request.method == "POST":
        form = SampleForm(request.POST, instance=sample)
        if form.is_valid():
            form.save()
            return redirect("samples:detail", pk=sample.pk)
    else:
        form = SampleForm(instance=sample)

    return render(request, "samples/sample_form.html", {
        "form": form,
        "sample": sample,
    })
```

### 5. Delete View

Remove objects:

```python
@login_required
def sample_delete(request, pk):
    sample = get_object_or_404(Sample, pk=pk)

    if request.method == "POST":
        sample.delete()
        return redirect("samples:list")

    return render(request, "samples/sample_confirm_delete.html", {"sample": sample})
```

---

## HTMX Views

HTMX views return HTML fragments instead of full pages.

### HTMX Partial View

```python
@login_required
def sample_table(request):
    """HTMX endpoint - returns table HTML only."""
    samples = Sample.objects.all()

    # Apply filters from query params
    status = request.GET.get("status")
    if status:
        samples = samples.filter(status=status)

    # Return partial template (no base.html)
    return render(request, "samples/partials/sample_table.html", {
        "samples": samples,
    })
```

**Partial template (`partials/sample_table.html`):**
```html
<!-- No {% extends %} - this is a fragment -->
<table class="table">
    <tbody>
        {% for sample in samples %}
        <tr id="sample-row-{{ sample.pk }}">
            <td>{{ sample.sample_id }}</td>
            <td>{{ sample.client_name }}</td>
        </tr>
        {% endfor %}
    </tbody>
</table>
```

**Usage in full page:**
```html
<div hx-get="{% url 'samples:table' %}"
     hx-trigger="load"
     hx-target="#table-container">
</div>
<div id="table-container">
    <!-- Table loaded here -->
</div>
```

### HTMX POST Action

```python
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils import timezone

@login_required
def approve_sample(request, pk):
    """HTMX POST endpoint - approves a sample."""
    if request.method != "POST":
        return HttpResponse("Method not allowed", status=405)

    sample = get_object_or_404(Sample, pk=pk)

    # Business logic
    sample.status = Sample.Status.APPROVED
    sample.approved_by = request.user
    sample.approved_at = timezone.now()
    sample.save()

    # Return updated row HTML
    return render(request, "samples/partials/sample_row.html", {"sample": sample})
```

**Trigger from button:**
```html
<button hx-post="{% url 'samples:approve' sample.pk %}"
        hx-target="#sample-row-{{ sample.pk }}"
        hx-swap="outerHTML">
    Approve
</button>
```

### HTMX with Multiple Updates (Out-of-Band)

```python
@login_required
def approve_sample(request, pk):
    sample = get_object_or_404(Sample, pk=pk)
    sample.status = Sample.Status.APPROVED
    sample.approved_by = request.user
    sample.approved_at = timezone.now()
    sample.save()

    # Main response: updated row
    row_html = render_to_string(
        "samples/partials/sample_row.html",
        {"sample": sample}
    )

    # Out-of-band: toast notification
    toast_html = render_to_string(
        "lims_core/partials/toast.html",
        {"message": "Sample approved!", "level": "success"}
    )

    # Combine responses
    return HttpResponse(
        row_html +
        f'<div id="toast-target" hx-swap-oob="beforeend">{toast_html}</div>'
    )
```

---

## Forms

### Creating a Form

```python
# samples/forms.py
from django import forms
from .models import Sample

class SampleForm(forms.ModelForm):
    class Meta:
        model = Sample
        fields = ["sample_id", "client_name", "status"]
        widgets = {
            "sample_id": forms.TextInput(attrs={"class": "form-control"}),
            "client_name": forms.TextInput(attrs={"class": "form-control"}),
            "status": forms.Select(attrs={"class": "form-select"}),
        }
```

### Filter Form (Non-Model)

```python
class SampleFilterForm(forms.Form):
    q = forms.CharField(required=False, label="Search")
    status = forms.ChoiceField(
        required=False,
        choices=[("", "Any")] + list(Sample.Status.choices)
    )
```

### Using Forms in Templates

```html
<form method="post">
    {% csrf_token %}

    {% for field in form %}
    <div class="mb-3">
        <label class="form-label">{{ field.label }}</label>
        {{ field }}
        {% if field.errors %}
        <div class="text-danger">{{ field.errors }}</div>
        {% endif %}
    </div>
    {% endfor %}

    <button type="submit" class="btn btn-primary">Save</button>
</form>
```

---

## Decorators

### Common Decorators

```python
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test

# Require login
@login_required
def my_view(request):
    pass

# Require specific permission
@permission_required("samples.approve_sample")
def approve_view(request):
    pass

# Custom check
@user_passes_test(lambda u: u.groups.filter(name="Reviewers").exists())
def reviewer_only_view(request):
    pass

# Require POST method
from django.views.decorators.http import require_POST

@require_POST
def action_view(request):
    pass
```

### Stacking Decorators

```python
@login_required
@require_POST
def approve_sample(request, pk):
    # User must be logged in AND request must be POST
    pass
```

---

## Querysets

### Common Query Patterns

```python
# Get all objects
Sample.objects.all()

# Filter by field
Sample.objects.filter(status="APPROVED")

# Multiple filters (AND)
Sample.objects.filter(status="APPROVED", client_name="ACME")

# OR queries
from django.db.models import Q
Sample.objects.filter(Q(status="APPROVED") | Q(status="IN_REVIEW"))

# Exclude
Sample.objects.exclude(status="REJECTED")

# Order by
Sample.objects.order_by("-received_at")  # Descending
Sample.objects.order_by("received_at")   # Ascending

# Limit
Sample.objects.all()[:10]  # First 10

# Get single object (raises DoesNotExist if not found)
sample = Sample.objects.get(pk=1)

# Get or 404
sample = get_object_or_404(Sample, pk=1)

# Check if exists
if Sample.objects.filter(sample_id="ABC123").exists():
    pass

# Count
count = Sample.objects.filter(status="APPROVED").count()

# Related objects (ForeignKey)
sample.approved_by.username  # Access related User
User.objects.get(pk=1).sample_set.all()  # Reverse relation
```

---

## Complete Example: Adding a Notes Feature

Let's add a notes feature to samples.

### 1. Create the Model

```python
# samples/models.py
class SampleNote(models.Model):
    sample = models.ForeignKey(Sample, on_delete=models.CASCADE, related_name="notes")
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Note on {self.sample.sample_id} by {self.author}"
```

### 2. Create Migration

```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. Create the Form

```python
# samples/forms.py
class SampleNoteForm(forms.ModelForm):
    class Meta:
        model = SampleNote
        fields = ["content"]
        widgets = {
            "content": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Add a note..."
            })
        }
```

### 4. Create Views

```python
# samples/views.py

@login_required
def sample_notes(request, pk):
    """HTMX endpoint - returns notes list."""
    sample = get_object_or_404(Sample, pk=pk)
    return render(request, "samples/partials/sample_notes.html", {
        "sample": sample,
        "notes": sample.notes.all(),
    })

@login_required
@require_POST
def add_note(request, pk):
    """HTMX POST - adds a note to sample."""
    sample = get_object_or_404(Sample, pk=pk)
    form = SampleNoteForm(request.POST)

    if form.is_valid():
        note = form.save(commit=False)
        note.sample = sample
        note.author = request.user
        note.save()

    # Return updated notes list
    return render(request, "samples/partials/sample_notes.html", {
        "sample": sample,
        "notes": sample.notes.all(),
        "form": SampleNoteForm(),  # Fresh form
    })
```

### 5. Add URLs

```python
# samples/urls.py
urlpatterns = [
    # ... existing paths ...
    path("<int:pk>/_notes/", views.sample_notes, name="notes"),
    path("<int:pk>/add-note/", views.add_note, name="add_note"),
]
```

### 6. Create Templates

**`partials/sample_notes.html`:**
```html
<div id="notes-section">
    <h5>Notes</h5>

    <!-- Add note form -->
    <form hx-post="{% url 'samples:add_note' sample.pk %}"
          hx-target="#notes-section"
          hx-swap="outerHTML">
        {% csrf_token %}
        <div class="mb-2">
            <textarea name="content" class="form-control" rows="2"
                      placeholder="Add a note..."></textarea>
        </div>
        <button type="submit" class="btn btn-sm btn-primary">Add Note</button>
    </form>

    <!-- Notes list -->
    <div class="mt-3">
        {% for note in notes %}
        <div class="card mb-2">
            <div class="card-body py-2">
                <small class="text-muted">
                    {{ note.author.display_name }} - {{ note.created_at|timesince }} ago
                </small>
                <p class="mb-0">{{ note.content }}</p>
            </div>
        </div>
        {% empty %}
        <p class="text-muted">No notes yet.</p>
        {% endfor %}
    </div>
</div>
```

### 7. Include in Detail Page

Add to `sample_detail.html`:
```html
<div hx-get="{% url 'samples:notes' sample.pk %}"
     hx-trigger="load"
     hx-target="this">
    Loading notes...
</div>
```

---

## Checklist for New Views

- [ ] Create view function in `views.py`
- [ ] Add `@login_required` decorator
- [ ] Add URL pattern in `urls.py`
- [ ] Create template in `templates/app_name/`
- [ ] For HTMX: use `partials/` folder, no `{% extends %}`
- [ ] Test the view manually
- [ ] Add any needed forms to `forms.py`

---

## Next Steps

- Read [Migrations](migrations.md) to learn about database changes
- Look at existing views in `samples/views.py` for examples
