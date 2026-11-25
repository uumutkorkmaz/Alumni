# Brand Guide

> Back to [README.md](README.md)

How the Alumni Tracking System looks and speaks: its place under Istanbul University, logo, colours, type, layout, components and tone. The palette comes from the colours Istanbul University and its Faculty of Economics really use on their websites, tuned into a calm, premium dark theme that is easy on the eyes.

> **Status:** applied. Every page uses this identity; [section 11](#11-applying-the-palette) records what changed from the earlier sky/violet palette.

> **Rule:** when a colour, the logo, a font or a shared component changes in the code, update this file in the same commit, as `ddd.md` is updated for the database.

> **Design system:** this file says *who we are and why*; [DESIGN.md](DESIGN.md) turns it into tokens, component recipes and the motion system for people and AI agents building pages. The two always agree; change them together.

## 1. The brand in one line

**Alumni Tracking** keeps the graduates of Management Information Systems (MIS, Yönetim Bilişim Sistemleri) in one place, with their announcements, job postings and applications. It is a working tool for the department and its graduates: calm, clear and trustworthy, with the quiet confidence of a university, not the noise of a marketing site.

| | |
| --- | --- |
| Full name | Alumni Tracking System |
| Short name (navbar, titles) | Alumni Tracking |
| Belongs to | İstanbul Üniversitesi → İktisat Fakültesi → Yönetim Bilişim Sistemleri |
| Course | Web Programming (YBSB3001) |
| Audience | Department staff and MIS graduates |
| Personality | Academic, calm, precise, premium; never loud |

### Relationship to Istanbul University

The site is an **endorsed** brand: it has its own name and mark, and it shows where it belongs through **Istanbul University's colours** and a plain text line ("İstanbul Üniversitesi · İktisat Fakültesi · YBS"), not through the university's own marks.

- Do **not** copy, redraw or imitate the Istanbul University logo or emblem, or the faculty's. Their use is governed by the university's own corporate identity guide (not public), and this project is a student project, not an official university site.
- Write the university's name in full and correctly: **İstanbul Üniversitesi** (Turkish), **Istanbul University** (English).

## 2. Where the colours come from

The university's corporate identity guide is not public, so the palette is based on the colours its official websites actually use. They were read from the theme stylesheets of **[istanbul.edu.tr](https://www.istanbul.edu.tr/)** and **[iktisat.istanbul.edu.tr](https://iktisat.istanbul.edu.tr/)** on 2026-11-18:

| Source colour | Where it is used on the university sites | Role in our brand |
| --- | --- | --- |
| `#439c86` green | The most used colour of both sites (118 times); the Faculty of Economics names it `--secilen-yesil` (headings, active menu) | **Primary**: links, focus, highlights, logo mark |
| `#2c7a64` deep green | Faculty of Economics `--yesil-koyu`: end of the green underline gradient, active language | **Primary buttons**, end of the brand gradient |
| `#006a4e` forest green | Footer headings and footer links | Quiet tints (selected rows, success backgrounds) |
| `#b8860b` gold | Tab icons, active and hovered tabs | **Accent**: the one premium highlight per screen |
| `#1a3a5a` navy | Dialog header, subscription button | Information tint; base of the "in progress" blue |
| `#dc3545` red | Error states | Danger (borders and fills; softened for text) |
| `#0d9488` / `#0f766e` teal | University management menu and banner | Not used: too close to the primary green |

## 3. Logo

The logo is the **AT mark** next to the **wordmark**, optionally followed by the **endorsement line**:

| Part | Specification |
| --- | --- |
| Mark | The letters **AT**, weight 800, colour `--ink` (`#0d1614`), in a 32 × 32 px square with 9 px rounded corners, filled with **İÜ green** `#439c86`, with a 1 px inner hairline of gold at 45 % opacity (`rgba(184, 134, 11, 0.45)`). Contrast of the letters: 5.55 : 1. |
| Wordmark | "Alumni Tracking", weight 700, 17 px, colour `--text`, 10 px to the right of the mark. |
| Endorsement line | "İstanbul Üniversitesi · İktisat Fakültesi · YBS", 12 px, `--muted`, upper case with 0.08em spacing. Used on the home page and the About page, not in the navbar. |
| Favicon | The mark alone: **AT** in `#0d1614` on a `#439c86` square with rounded corners (inline SVG in `layout.py`). |
| Where | Top left of every page, always a link to the home page (`/`). |

Do:
- Keep the mark and the wordmark together in the navbar.
- Keep the mark square, green, with dark letters.

Don't:
- Recolour, stretch, outline or rotate the mark; put white letters on it (white on `#439c86` is only 3.31 : 1).
- Put the mark on a light or busy background.
- Write the name in another way ("AlumniTracking", "ALUMNI TRACKING", "AT System").

## 4. Colours

The site is **dark only** (`color-scheme: dark`). The colours are CSS variables in `:root` of `app/static/app.css`; use the variables, never a new hex code.

### 4.1 Surfaces and text

A deep ink with a slight green tint instead of pure black, and a soft off-white instead of pure white: strong enough to read, never glaring.

| Token | Hex | Use |
| --- | --- | --- |
| `--bg` / `--ink` | `#0d1614` | Page background; dark text on green (logo mark, light buttons). |
| `--panel` | `#141f1c` | Cards, tables, ghost buttons. |
| `--panel-2` | `#1a2824` | Table headers, hover, the active navbar link. |
| `--field` | `#111b19` | Form inputs, selects, text areas. |
| `--border` | `#273732` | Every border and divider (1.35 : 1 against a panel: visible, not harsh). |
| `--text` | `#e3e9e6` | Body text and headings. |
| `--muted` | `#98a7a1` | Secondary text: labels, dates, notes, subtitles. |

### 4.2 Brand colours

| Token | Hex | Source | Use |
| --- | --- | --- | --- |
| `--primary` | `#439c86` | İÜ green | Links, focus ring, active states, highlighted words, logo mark, "Open" and "accepted". |
| `--primary-light` | `#6cbca6` | tint of İÜ green | Link hover; green text on small sizes. |
| `--primary-deep` | `#2c7a64` | İktisat `--yesil-koyu` | Primary button background (white text 5.15 : 1); hover `#26705b` (5.91 : 1). |
| `--forest` | `#006a4e` | İÜ footer green | Background tints only, e.g. `rgba(0, 106, 78, 0.15)` behind a selected row or a success badge. |
| `--gold` | `#b8860b` | İÜ gold | The accent: one highlight per screen (hero word, active navbar underline, "interview" status, the pill). |
| `--gold-light` | `#d4a64a` | tint of İÜ gold | Gold text below 14 px. |
| `--navy` | `#1a3a5a` | İÜ navy | Background tint of information and "in progress" badges. |
| `--navy-light` | `#86aed6` | tint of İÜ navy | Text of "in progress" states (submitted, under review). |
| `--danger` | `#dc3545` | İÜ red | Borders and fills of danger elements only (as text it is 3.73 : 1, too weak). |
| `--danger-soft` | `#e8857c` | tint of İÜ red | Error text, delete button text, "rejected" / "Closed" badges. |

**Brand gradient:** `linear-gradient(90deg, #439c86, #2c7a64)`, the same green line the Faculty of Economics draws under its headings. Used only as a **decoration**: a 3 px line under a hero or section title, or the top edge of a featured card. Never put text on it.

**Background:** the `--bg` colour with two very soft glows at the top: green `rgba(67, 156, 134, 0.10)` on the left and gold `rgba(184, 134, 11, 0.05)` on the right (they replace the sky and violet glows).

### 4.3 Status colours

Badges always mean the same thing:

| Meaning | Text | Background | Statuses |
| --- | --- | --- | --- |
| In progress | `--navy-light` | `--navy` at 35 % | submitted, under review |
| Next step | `--gold-light` | `--gold` at 12 % | interview |
| Good outcome | `--primary-light` | `--forest` at 18 % | accepted, Open |
| Ended / refused | `--danger-soft` | `--danger` at 10 % | rejected, withdrawn, Closed |

## 5. Easy on the eyes

"Premium" here means restraint. These rules keep long sessions comfortable:

1. **No pure white, no pure black.** Text `#e3e9e6` on `#0d1614` (14.9 : 1) instead of white on black (21 : 1), which glares on a dark screen.
2. **Colour is for small things.** Green and gold together cover at most about a tenth of a screen: links, one button, badges, thin lines. Large areas stay ink and panel.
3. **One gold element per screen.** Gold marks the single thing that matters most there; used twice it stops meaning anything.
4. **Soft edges, no glow.** Borders are low contrast (1.35 : 1); no neon shadows, no glowing text.
5. **Readable text blocks.** Body 15 px, line height 1.6, paragraphs at most about 72 characters wide.
6. **Calm motion.** Things ease into place once and then stay still: colour changes 150 ms, hover lift 2 px at most, entrances under 1 second; respect `prefers-reduced-motion` (no movement at all when the user asks for it). The one exception is the home page's scroll film (the walk from the main gate to the Rectorate), which moves only while the user scrolls, runs on desktops only, and becomes a still picture on phones and under reduced motion. The full motion system is in [DESIGN.md §7](DESIGN.md#7-motion--animation).
7. **Every pair checked.** All text colours pass WCAG AA (4.5 : 1) on the surfaces they are used on (section 6).

## 6. Contrast table

WCAG 2 contrast ratios, computed for the pairs the site uses:

| Foreground | Background | Ratio | WCAG |
| --- | --- | --- | --- |
| `--text` `#e3e9e6` | `--bg` `#0d1614` | 14.94 : 1 | AAA |
| `--text` | `--panel` `#141f1c` | 13.73 : 1 | AAA |
| `--text` | `--panel-2` `#1a2824` | 12.43 : 1 | AAA |
| `--muted` `#98a7a1` | `--bg` | 7.34 : 1 | AAA |
| `--muted` | `--panel` | 6.74 : 1 | AA |
| `--muted` | `--panel-2` | 6.10 : 1 | AA |
| `--muted` | `--field` `#111b19` | 7.01 : 1 | AAA |
| `--primary` `#439c86` | `--bg` | 5.55 : 1 | AA |
| `--primary` | `--panel` | 5.10 : 1 | AA |
| `--primary-light` `#6cbca6` | `--panel` | 7.55 : 1 | AAA |
| `--ink` `#0d1614` | `--primary` (logo mark) | 5.55 : 1 | AA |
| white | `--primary-deep` `#2c7a64` (button) | 5.15 : 1 | AA |
| white | `#26705b` (button hover) | 5.91 : 1 | AA |
| `--gold` `#b8860b` | `--bg` | 5.65 : 1 | AA |
| `--gold` | `--panel` | 5.19 : 1 | AA |
| `--gold-light` `#d4a64a` | `--bg` | 8.19 : 1 | AAA |
| `--navy-light` `#86aed6` | `--panel-2` | 6.58 : 1 | AA |
| `--danger-soft` `#e8857c` | `--panel-2` | 5.88 : 1 | AA |
| Alert text `#f3d9d6` | Alert background `#2a1714` | 12.76 : 1 | AAA |
| *Not allowed:* white | `--primary` | 3.31 : 1 | fails |
| *Not allowed:* `--danger` `#dc3545` as text | `--panel` | 3.73 : 1 | fails |

## 7. Typography

| Element | Style |
| --- | --- |
| Fonts | Three Google Fonts with full Turkish glyphs: **Source Serif 4** (headings and numbers: the university's voice), **Inter** (interface and reading text), **IBM Plex Mono** (labels, ids, dates: what the system records). Fallbacks: Georgia, the system sans (`Segoe UI`, Roboto), Consolas. |
| Body | Inter 15 px, line height 1.6, `--text`. Tables 14 px. |
| Page title (`h1`) | Source Serif 4, 36 px, weight 600, letter spacing −0.01em. |
| Hero title (home) | Source Serif 4, 40–64 px, weight 500, line height 1.05, letter spacing −0.02em; one word or phrase may be **gold** (the screen's single gold element). |
| Section heading | Source Serif 4, 28 px, weight 600. Card titles: Inter 16 px, weight 600. |
| Labels and table headers | IBM Plex Mono 11–12 px, `--muted`, upper case with 0.06–0.08em spacing. |
| Numbers | Counters, dates and ids use tabular figures (`font-variant-numeric: tabular-nums`), so columns line up. Stat numbers in Source Serif 4, 44 px. |
| Code and ids | IBM Plex Mono, e.g. the error id and requested paths on error pages. |

The full type scale and the font link are in [DESIGN.md §3](DESIGN.md#3-typography-rules).

## 8. Layout and spacing

| Item | Value |
| --- | --- |
| Page width | 1120 px (`.container`); 780 px for focused pages such as forms, details and errors (`.container.narrow`). |
| Side padding | 24 px; 16 px on phones. |
| Corner radius | 14 px for cards, tables and panels (`--radius`); 10 px for buttons, inputs and alerts; 8 px for small buttons; fully round for badges and pills. |
| Card padding | 24 px. |
| Gaps | 16 px between cards in a grid, 24–32 px between sections. |
| Phones | Below 720 px forms and grids become one column and the navbar scrolls sideways; tables scroll inside their card. |

Every page is built by `render_page` in `app/views/layout.py`: the same navbar, the same footer ("YBSB3001 — Web Programming") and the same stylesheet. A new page uses it instead of writing its own `<html>`.

## 9. Components

| Component | Class | Rule |
| --- | --- | --- |
| Primary button | `.btn .btn-primary` | Solid `--primary-deep` with white text, hover `#26705b`. The one main action of a screen ("Create", "Save changes", "Apply"). No gradient behind text. |
| Ghost button | `.btn .btn-ghost` | `--panel` with a `--border` line, `--text`. Secondary actions and navigation ("Edit", "Back", "Home"). |
| Danger button | `.btn .btn-danger` | `--danger-soft` text on `--danger` at 10 %, border at 35 %. Only for deleting; always asks for confirmation first. |
| Small button | `.btn-sm` | Inside table rows. |
| Navbar link | `.nav-links a` | `--muted`; hover `--text` on `--panel`; the active page `--text` with a 2 px gold underline that slides in from the left. |
| Badge | `.badge` (+ status class) | Short status words with the colours of section 4.3. |
| Register button | `.nav-cta` | The navbar's one call to action for guests: "Register" with a gold hairline, next to "Giriş yap". |
| Navbar account | `.nav-user` | For a signed-in user: avatar, first name and role in a pill, and a "Çıkış" button (see DESIGN.md §4). |
| Role card | `.role-card` | The role choice on the registration page: a radio card with the role and the email it needs; the chosen one gets a green border and a gold underline. |
| Role badge | `.badge.role-<role>` | A user's role: student (navy), graduate (green), academic (gold), staff (neutral), admin (soft red); see DESIGN.md §4. |
| Alert | `.alert .alert-error` | Text `#f3d9d6` on `#2a1714`, border `--danger` at 40 %: a refused action at the top of the page, the reason in plain words. |
| Card | `.card` | Groups one form, one detail or one list. A featured card may have the brand gradient as a 3 px top edge. |
| Table | `.table-wrap` + `table` | Lists; a filter box above, the actions on the right of each row; a selected or hovered row gets a `--forest` tint. |
| Pill | `.pill` | Small upper-case label above the hero title of every page, gold text with a gold hairline. |
| Page hero | `.hero.hero--page` / `.hero--compact` | The home hero on every other page: pill, serif title with one gold italic phrase, Faculty Line, lead, buttons; built by `page_hero()` in `layout.py` (see DESIGN.md §4). |
| Album card | `.album-card` | One graduate on the Users page: a tilted, frameless campus photo with the initials, name, class and department on it, tossed among the others under a large outlined "Graduates" (see DESIGN.md §4). The pictures are campus places, never invented portraits. |
| Kicker | `.kicker` | Small mono label with a green dot, used inside the home film captions. |
| Focus | `:focus-visible` | 2 px `--primary` outline with 2 px offset on every interactive element. Never remove it. |

## 10. Voice and tone

- **Plain and short.** Say what happened and what to do next: "This posting is closed, so nobody can apply to it."
- **Reason first.** Errors always give a reason, never just a code: "User not found (user_id=999)."
- **Own server mistakes.** A 5xx says it is our fault, not the user's: "This is our mistake, not yours", with an error id to report.
- **No internals for users.** No stack traces, SQL or file paths on a page; those go to `logs/error.logs`.
- **Academic, not salesy.** No exclamation marks, no hype ("amazing", "revolutionary"); the tone of a well-run department office.
- **Language.** The management pages, the API and the error messages are in English. The public pages (home, About and the registration pages) are in Turkish, including the registration's field messages. Inside one page, do not mix the two.
- **Numbers and dates.** Dates as `YYYY-MM-DD`, times as `HH:MM`; counts with their noun ("3 postings · 2 open").

## 11. Applying the palette

What changed in the code to move from the earlier sky/violet palette to this identity (done; kept as a record).

| Current token | Current value | New token | New value |
| --- | --- | --- | --- |
| `--bg` | `#0b1120` | `--bg` / `--ink` | `#0d1614` |
| `--panel` | `#151f38` | `--panel` | `#141f1c` |
| `--panel-2` | `#1a2644` | `--panel-2` | `#1a2824` |
| `--field` | `#0f1830` | `--field` | `#111b19` |
| `--border` | `#24314f` | `--border` | `#273732` |
| `--text` | `#e2e8f0` | `--text` | `#e3e9e6` |
| `--muted` | `#94a3b8` | `--muted` | `#98a7a1` |
| `--accent` | `#38bdf8` (sky) | `--primary` | `#439c86` |
| `--accent-2` | `#a78bfa` (violet) | `--gold` (accent) and `--primary-deep` (buttons) | `#b8860b` / `#2c7a64` |
| `--ok` | `#4ade80` | `--primary-light` | `#6cbca6` |
| `--danger` | `#f87171` | `--danger` (fills) and `--danger-soft` (text) | `#dc3545` / `#e8857c` |
| (none) | | `--forest`, `--gold-light`, `--navy`, `--navy-light` | `#006a4e`, `#d4a64a`, `#1a3a5a`, `#86aed6` |

Also:
- `.btn-primary`: from the sky→violet gradient with dark text to solid `--primary-deep` with white text.
- `.brand-mark`: from the gradient to solid `--primary` with the gold hairline; the favicon fill in `layout.py` to `#439c86` and its letters to `#0d1614`.
- The two background glows (section 4.2), the badge colours (section 4.3), the alert colours and the active navbar underline (section 9).
- The three fonts, `prefers-reduced-motion` and tabular figures (sections 5 and 7), and the motion tokens and keyframes from the [DESIGN.md Quick Start](DESIGN.md#quick-start).
- Check every page once more against the contrast table after the change.

## 12. Where the brand lives in the code

| What | Where |
| --- | --- |
| Colour tokens, type sizes, spacing, components | `app/static/app.css` (`:root` and the sections below it) |
| Logo mark, wordmark, favicon, navbar, footer, page skeleton | `app/views/layout.py` |
| Error pages (404, 5xx) | `app/views/error_view.py` |
