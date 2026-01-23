# WuLims UI Conventions (Read Before Building Pages)

This document defines **how UI elements should look and behave** in WuLims.

The goal is **consistency**, not creativity.  
A consistent UI is easier to learn, easier to maintain, and feels professional.

When in doubt: **copy an existing pattern**.

---

## General Principles

- Use **Bootstrap components and utilities first**
- Prefer **clarity over cleverness**
- Avoid visual noise (too many colors, borders, icons)
- If two pages solve the same problem, they should look the same

---

## Buttons

Buttons communicate **intent**. Use them consistently.

### Button Types

| Purpose | Class | Example |
|------|------|------|
| Primary action | `btn btn-primary` | Save, Create, Submit |
| Secondary action | `btn btn-outline-secondary` | Cancel, Back |
| Destructive action | `btn btn-danger` | Delete |
| Neutral / admin | `btn btn-outline-secondary` | Admin tools |

### Rules

- Every page should have **one primary action**
- Destructive actions should be:
    - visually distinct
    - confirmed (modal or prompt)
- Avoid custom colors for buttons

### Example

```html
<div class="d-flex gap-2">
  <button class="btn btn-primary">Save</button>
  <a href="{% url 'samples:list' %}" class="btn btn-outline-secondary">Cancel</a>
</div>
```

## Tables

Tables are the heart of WuLims. Keep them readable and predictable.

Required Classes
```html
<table class="table table-hover align-middle">
```
Use:
- table-hover → helps scanning rows
- align-middle → vertical alignment for mixed content

Table Headers
- Use <thead>
- Keep headers short and descriptive
- Avoid icons in headers unless necessary

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

Actions Column
- Actions go on the right
- Use buttons or icon buttons
- Align actions right

```html
<td class="text-end">
  <a class="btn btn-sm btn-outline-secondary">View</a>
</td>

```

## Forms

Forms should be boring and predictable.

**Layout Rules**
- One column by default
- Group related fields 
- Labels always above inputs

**Required Structure**
```html
<div class="mb-3">
  <label class="form-label">Sample Name</label>
  <input type="text" class="form-control">
</div>
```
**Validation**
Validation
- Use Bootstrap validation styles
- Error messages should be specific and actionable

```html
<div class="invalid-feedback">
  Sample name is required.
</div>
```


## Page Layout

Page Header Pattern (Recommended)

```html
<div class="d-flex justify-content-between align-items-center mb-3">
  <h1 class="h3 mb-0">Samples</h1>
  <button class="btn btn-primary">New Sample</button>
</div>
```

- Page title on the left
- Primary action on the right
- Use h3 for page titles (consistent scale)

## Badges & Status Indicators

Use badges to communicate state, not decoration.

**Approved Uses**
- Status (Complete, Pending, Error)
- Connectivity (Connected, Offline)
- Counts or alerts

Example
```html
<span class="badge text-bg-success">Complete</span>
<span class="badge text-bg-warning text-dark">Pending</span>
<span class="badge badge-accent">Connected</span>
```
Avoid inventing new colors or meanings.

## Icons (If Used)

- Use Bootstrap Icons (https://icons.getbootstrap.com/)
- Icons should support text, not replace it
- Never rely on color alone to communicate meaning (hurts colorblind users)
- Prefer text + icon, not icon-only buttons

## Modals

**Use modals for:**
- confirmation (delete, destructive actions)
- focused data entry
- short, self-contained tasks

**Avoid:**
- large workflows
- long forms
- critical navigation

## What NOT to Do

- Inline styles
- Custom colors in templates
- One-off CSS fixes
- Overusing icons
- Multiple primary buttons on one page

If you feel tempted to do one of these, stop and ask.

## Final Reminder

WuLims is lab software, not a marketing site.

- Clear > pretty
- Consistent > clever
- Boring UI = good UI

If a user doesn’t notice the interface, you did it right.
