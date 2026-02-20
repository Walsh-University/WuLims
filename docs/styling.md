# Styling (SCSS + Bootstrap)

WuLims uses Bootstrap as a base and layers a custom SCSS theme on top.

## Core Rule

- Edit SCSS in `assets/scss/`.
- Do not edit generated CSS in `static/css/` by hand.
- Do not add inline styles or `<style>` blocks in templates.

SCSS is the source. CSS is the build output.

## Where Styles Live

SCSS source (edit these files):

```text
assets/
└── scss/
    ├── _variables.scss      # Theme tokens and Bootstrap variable overrides
    ├── _overrides.scss      # Component overrides and custom utilities
    ├── wulims.scss          # Main app stylesheet entrypoint
    └── admin.wulims.scss    # Admin-specific stylesheet entrypoint
```

Generated CSS (committed output used at runtime):

```text
static/
└── css/
    ├── bootstrap.wulims.min.css
    └── admin.wulims.min.css
```

## Build Order

`wulims.scss` follows this flow:

1. Import variables/tokens.
2. Import Bootstrap source SCSS.
3. Import local overrides.

This keeps theme decisions (`_variables.scss`) separate from component tweaks (`_overrides.scss`).

## Rebuild CSS

From the repository root:

```bash
make css
```

This compiles both app and admin stylesheets into `static/css/`.

## If You Need Sass

If Sass is not installed locally:

```bash
gem install sass
```

Most contributors do not need to run this often because compiled CSS is already committed.
