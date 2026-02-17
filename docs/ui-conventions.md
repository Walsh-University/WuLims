# WuLims UI Conventions

This document defines how UI elements should look and behave in WuLims.

Goal: consistency over creativity.

## General Principles

- Use Bootstrap components and utilities first.
- Prefer clarity over cleverness.
- Avoid visual noise (too many colors, borders, or icons).
- If two pages solve the same problem, they should look the same.

## Buttons

Buttons should communicate intent clearly.

| Purpose | Class | Example |
|---|---|---|
| Primary action | `btn btn-primary` | Save, Create, Submit |
| Secondary action | `btn btn-outline-secondary` | Cancel, Back |
| Destructive action | `btn btn-danger` | Delete |
| Neutral/admin | `btn btn-outline-secondary` | Admin tools |

Rules:
- Use one primary action per page.
- Make destructive actions visually distinct and confirm them (modal or prompt).
- Avoid custom button colors in templates.

Example:

```html
<div class="d-flex gap-2">
  <button class="btn btn-primary">Save</button>
  <a href="{% url 'samples:list' %}" class="btn btn-outline-secondary">Cancel</a>
</div>
```

## Tables

Use predictable table patterns:

```html
<table class="table table-hover align-middle">
```

- `table-hover` improves scanability.
- `align-middle` keeps mixed-content rows aligned.
- Keep action buttons right-aligned in the last column.

Header example:

```html
<thead class="table-light">
  <tr>
    <th>Sample ID</th>
    <th>Status</th>
    <th>Received</th>
    <th class="text-end">Actions</th>
  </tr>
</thead>
```

## Forms

Forms should be simple and predictable.

- One column by default.
- Group related fields.
- Keep labels above inputs.
- Use Bootstrap validation styles and actionable error text.

Example:

```html
<div class="mb-3">
  <label class="form-label">Sample Name</label>
  <input type="text" class="form-control">
  <div class="invalid-feedback">Sample name is required.</div>
</div>
```

## Page Layout

Recommended page header pattern:

```html
<div class="d-flex justify-content-between align-items-center mb-3">
  <h1 class="h3 mb-0">Samples</h1>
  <button class="btn btn-primary">New Sample</button>
</div>
```

- Title on the left.
- Primary action on the right.
- Use consistent heading scale (`h3` for page titles).

## Badges and Status

Use badges for state, not decoration.

```html
<span class="badge text-bg-success">Complete</span>
<span class="badge text-bg-warning text-dark">Pending</span>
```

Do not invent one-off status colors in templates.

## Icons

- Use Bootstrap Icons.
- Prefer icon + text over icon-only actions.
- Do not rely on color alone to communicate meaning.

## Modals

Use modals for:
- Confirmations for destructive actions.
- Short, focused tasks.

Avoid modals for:
- Long forms.
- Multi-step workflows.
- Core navigation.

## Avoid

- Inline styles.
- `<style>` blocks in templates.
- One-off CSS fixes in templates.
- Multiple primary buttons on one page.

When in doubt, copy an existing pattern from the same feature area.
