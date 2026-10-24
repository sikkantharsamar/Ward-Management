---
name: Clinical Ward Operations
colors:
  surface: '#f8f9ff'
  surface-dim: '#cbdbf5'
  surface-bright: '#f8f9ff'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#eff4ff'
  surface-container: '#e5eeff'
  surface-container-high: '#dce9ff'
  surface-container-highest: '#d3e4fe'
  on-surface: '#0b1c30'
  on-surface-variant: '#44474d'
  inverse-surface: '#213145'
  inverse-on-surface: '#eaf1ff'
  outline: '#74777e'
  outline-variant: '#c4c6ce'
  surface-tint: '#4a5f7f'
  primary: '#001229'
  on-primary: '#ffffff'
  primary-container: '#0f2744'
  on-primary-container: '#798fb1'
  inverse-primary: '#b2c8ed'
  secondary: '#1d4ed8'
  on-secondary: '#ffffff'
  secondary-container: '#4069f2'
  on-secondary-container: '#fffbff'
  tertiary: '#001323'
  on-tertiary: '#ffffff'
  tertiary-container: '#002942'
  on-tertiary-container: '#2c94d8'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#d4e3ff'
  primary-fixed-dim: '#b2c8ed'
  on-primary-fixed: '#021c39'
  on-primary-fixed-variant: '#324866'
  secondary-fixed: '#dce1ff'
  secondary-fixed-dim: '#b7c4ff'
  on-secondary-fixed: '#001551'
  on-secondary-fixed-variant: '#0039b5'
  tertiary-fixed: '#cce5ff'
  tertiary-fixed-dim: '#93ccff'
  on-tertiary-fixed: '#001d31'
  on-tertiary-fixed-variant: '#004b73'
  background: '#f8f9ff'
  on-background: '#0b1c30'
  surface-variant: '#d3e4fe'
typography:
  headline-xl:
    fontFamily: Plus Jakarta Sans
    fontSize: 36px
    fontWeight: '700'
    lineHeight: 44px
    letterSpacing: -0.02em
  headline-xl-mobile:
    fontFamily: Plus Jakarta Sans
    fontSize: 28px
    fontWeight: '700'
    lineHeight: 36px
    letterSpacing: -0.01em
  headline-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 28px
    fontWeight: '700'
    lineHeight: 36px
    letterSpacing: -0.01em
  headline-lg-mobile:
    fontFamily: Plus Jakarta Sans
    fontSize: 22px
    fontWeight: '700'
    lineHeight: 30px
    letterSpacing: 0em
  headline-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 22px
    fontWeight: '600'
    lineHeight: 28px
    letterSpacing: -0.01em
  headline-sm:
    fontFamily: Plus Jakarta Sans
    fontSize: 18px
    fontWeight: '600'
    lineHeight: 24px
    letterSpacing: 0em
  body-lg:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-lg-medium:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '500'
    lineHeight: 24px
  body-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  body-md-medium:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '500'
    lineHeight: 20px
  body-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '400'
    lineHeight: 16px
  label-lg:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '600'
    lineHeight: 20px
    letterSpacing: 0.01em
  label-md:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '600'
    lineHeight: 16px
    letterSpacing: 0.02em
  label-sm:
    fontFamily: Inter
    fontSize: 11px
    fontWeight: '700'
    lineHeight: 14px
    letterSpacing: 0.04em
  data-metric:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '700'
    lineHeight: 28px
    letterSpacing: -0.02em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  gutter: 1rem
  gutter-desktop: 1.5rem
  margin: 1rem
  margin-tablet: 1.5rem
  margin-desktop: 2rem
  space-xs: 0.25rem
  space-sm: 0.5rem
  space-md: 1rem
  space-lg: 1.5rem
  space-xl: 2rem
---

## Brand & Style

This design system is engineered specifically for acute healthcare and inpatient ward environments. The interface directly serves charge nurses, attending physicians, unit coordinators, and allied health staff who make rapid, safety-critical decisions under cognitive strain and ambient visual distractions.

The design philosophy combines **Clean Clinical Minimalism** with **High-Legibility Modernism**:
- **Clarity over Decoration:** Zero extraneous ornamentation, non-functional animations, or low-contrast stylistic flourishes. Visual structures must be parsed in sub-second glances from bedside monitors or centralized nursing station dashboards.
- **Cognitive Relief:** Dominant clean whites and structured cool grays establish a serene, sterile backdrop that minimizes eye fatigue during extended 12-hour shifts.
- **Uncompromised Hierarchy:** High optical contrast (conforming to WCAG AAA standards for critical text and actionable controls) guarantees readability across varying light conditions, from dimmed night-shift recovery wards to brightly lit trauma bays.
- **Emotional Calibration:** The aesthetic evokes surgical precision, institutional trust, institutional stability, and rapid legibility.

## Colors

The color architecture is built around an unambiguous, clinical taxonomy. Tinting and saturation indicate operational state rather than mere decoration.

### Primary Palette & Neutrals
- **Deep Navy Blue (`#0F2744`):** Primary base. Used for primary interactive actions, high-level navigation chrome, table headers, and structural anchoring.
- **Royal Blue (`#1D4ED8` default, `#2563EB` active/hover):** Operational interactive blue for standard CTAs, active tab indicators, and primary data highlights.
- **Clinical/Sky Blue (`#0284C7` / tint `#E0F2FE`):** Diagnostic accents, patient bed state indicators, and soft badge backgrounds.
- **Backgrounds & Canvas:** Baseline canvas relies on Crisp Light Gray (`#F8FAFC`), while structural containers and card divisions use `#F1F5F9`. Surface tiles and primary elevation cards are pure Clean White (`#FFFFFF`).
- **Neutral Typography:** Primary text uses Deep Slate/Navy (`#0F172A`) for high contrast against white and light gray tiles. Secondary metadata uses `#475569`, never dropping below WCAG AAA contrast ratios.

### Strict Semantic Rules
Color coding in ward management is life-critical; semantic tokens are strictly reserved and may never be repurposed for general branding or decorative accents:
- **Emergency Crimson (`#DC2626` base, `#EF4444` active highlight, `#FEF2F2` tint):** Strictly reserved for life-safety events, Code Blue indicators, severe allergy alerts, critical abnormal lab results, and destructive actions.
- **Clinical Green (`#16A34A` base, `#22C55E` bright, `#F0FDF4` tint):** Reserved for normal vitals, discharged/available beds, stable patient parameters, and verified medication administration.
- **Caution Amber (`#D97706` base, `#F59E0B` bright, `#FFFBEB` tint):** Reserved for unassigned beds, fall-risk flags, pending physician sign-offs, and cautionary vitals deviations.
- **Clinical Info Blue (`#2563EB` base, `#EFF6FF` tint):** General administrative notes, shift transfer logs, and neutral clinical metadata.

## Typography

The typographic system utilizes **Plus Jakarta Sans** for display headers and ward titles to grant structural authority, paired with **Inter** for dense tabular records, patient data charts, telemetry figures, and form components.

- **Tabular Figures & Numbers:** All numeric readouts (heart rate, blood pressure, oxygen saturation, medical record numbers) must employ open-type tabular numbers (`font-variant-numeric: tabular-nums;`) to preserve vertical column alignment across rapidly updating vitals streams.
- **Hierarchy Enforcement:** Headers establish immediate context (`headline-sm` to `headline-xl`), while `label-sm` (all-caps with wide tracking) is strictly deployed for metric category tags (e.g., `HR BPM`, `SPO2`, `BED #`).
- **Readability Rules:** Continuous body copy maintains a 1.5 line-height ratio, while dense telemetry and bed-grid metrics compress to a strict 1.15 to 1.25 ratio to prevent vertical bloat on dashboard panels.

## Layout & Spacing

The layout model balances dense information capacity with spatial cleanliness. Medical software fails when high density degrades into visual noise; thus, a rigorous mathematical grid governs the canvas.

### Grid & Density Modes
- **Central Ward Grid:** Desktop and widescreen displays employ a 12-column responsive grid with a standard `1.5rem` (24px) gutter. Ward layouts (e.g., ICU Bed Matrix, Triage Board) can switch between **Standard View** (relaxed spacing for ward rounds) and **Dense Telemetry View** (compact spacing for central monitoring desks).
- **Responsive Adaptation:**
  - **Mobile (< 768px):** 4 columns, single-card bed list view, fixed bottom action tray for quick triage tagging. Outer margin: `1rem`.
  - **Tablet (768px - 1024px):** 8 columns, 2-column card layout for bedside tablet checks. Outer margin: `1.5rem`.
  - **Desktop / Wall Displays (> 1024px):** 12 columns, multi-column patient matrices with persistent left-hand ward filters and right-hand drawer inspector. Outer margin: `2rem`.

### Internal Element Rhythm
Component padding follows strict 4px/8px increments:
- Tight inputs and micro badges leverage `space-xs` (4px) and `space-sm` (8px).
- Ward bed cards leverage `space-md` (16px) for interior padding.
- Major canvas panel separations utilize `space-lg` (24px) to `space-xl` (32px).

## Elevation & Depth

In a medical workstation UI, elevation communicates modal priority and urgency levels without visually disconnecting related data. Heavy, dark shadows are prohibited; instead, depth is conveyed through **crisp micro-borders coupled with diffused clinical ambient shadows**.

### Elevation Hierarchy
- **Level 0 (Canvas):** Crisp Light Gray (`#F8FAFC`). No shadow. Holds static background layout elements.
- **Level 1 (Clinical Cards & Data Surfaces):** Clean White (`#FFFFFF`) bounded by a subtle outline border (`#E2E8F0`). Supported by an ambient clinical shadow: `0 1px 3px 0 rgba(15, 39, 68, 0.05), 0 1px 2px -1px rgba(15, 39, 68, 0.05)`.
- **Level 2 (Active/Hover Cards, Table Row Selects):** Elevated bed cards or focused medical orders: `0 4px 6px -1px rgba(15, 39, 68, 0.07), 0 2px 4px -2px rgba(15, 39, 68, 0.05)`, with border color darkening to `#CBD5E1`.
- **Level 3 (Popovers, Dropdowns, Flyout Drawers):** `0 10px 15px -3px rgba(15, 39, 68, 0.08), 0 4px 6px -4px rgba(15, 39, 68, 0.04)`.
- **Level 4 (Stat/Code Blue Modals & Emergency Overlays):** Emergency interrupt layer: `0 20px 25px -5px rgba(15, 39, 68, 0.12), 0 8px 10px -6px rgba(15, 39, 68, 0.08)`, paired with a tinted backdrop scrim (`rgba(15, 23, 42, 0.6)`).

## Shapes

The design system enforces a balanced curvature model (`roundedness: 2`). Sharp corners (`0px`) evoke brittle legacy terminal systems, while fully rounded pill layouts across cards feel overly informal for serious healthcare interfaces.

- **Base Radius (`0.5rem` / 8px):** Standard inputs, dropdown triggers, primary/secondary buttons, telemetry containers, and patient alert banners.
- **Large Radius (`rounded-lg`, `1rem` / 16px):** Ward bed cards, diagnostic overview panels, and modal containers.
- **Specialized Pill Shapes:** Reserved exclusively for small semantic status chips, triage score tags, and bed occupancy badges to distinguish them immediately from rectangular interactive buttons and input fields.

## Components

### Buttons
- **Primary Action:** Solid Deep Navy (`#0F2744`) or Royal Blue (`#1D4ED8`) background, white text, 8px corner radius, minimum touch target of 44x44px. Hover state brightens to `#2563EB`. Active state settles at `#1E40AF`.
- **Emergency Button:** High-visibility Crimson (`#DC2626`) fill with pure white label. Used exclusively for "Trigger Code", "Stat Lab", or critical discharge cancellations.
- **Secondary / Ghost:** White background, 1px solid border (`#CBD5E1`), text in `#0F2744`. Hover state tints to `#F1F5F9`.

### Badges & Semantic Chips
- Always paired with full-height contrast: light pastel background with bold, high-contrast text.
  - **Emergency/Critical:** `#FEF2F2` background, `#991B1B` text, 1px `#FCA5A5` border. Optional pulse indicator dot (`#DC2626`).
  - **Normal/Stable:** `#F0FDF4` background, `#166534` text, 1px `#86EFAC` border.
  - **Pending/Observation:** `#FFFBEB` background, `#92400E` text, 1px `#FCD34D` border.
  - **Informational/Scheduled:** `#EFF6FF` background, `#1E40AF` text, 1px `#93C5FD` border.

### Input Fields & Controls
- **Inputs:** Clean white container, 1px `#CBD5E1` border, 8px radius, text in `#0F172A`. In-focus state introduces a 2px Royal Blue (`#2563EB`) ring with an offset. Error states immediately flip the border and focus ring to `#DC2626`.
- **Checkboxes & Radios:** High-contrast 20x20px targets. Checked state uses solid Royal Blue (`#1D4ED8`) with crisp white interior iconography.

### Patient & Ward Bed Cards
- The foundational building block of the ward management system:
  - **Card Header:** Bed Identifier (`#0F2744`, bold) anchored alongside the patient's room status badge and primary attending physician.
  - **Card Body:** Patient demographics, Medical Record Number (monospaced Inter), diagnosis summary, and allergy tags (high-contrast Crimson).
  - **Telemetry Strip:** Inline display for Vitals (Pulse, BP, SpO2, Temp). Normal vitals appear in deep slate; values outside reference ranges automatically format in Caution Amber or Emergency Crimson with prominent directional arrows.
  - **Card Border Coding:** A vertical 4px left-hand indicator bar visually reinforces the patient's clinical tier (Green: Ready for Discharge; Amber: Pending Results; Red: Stat Attention Required).

### Tables & Ward Census Lists
- Alternating row styling using `#FFFFFF` and `#F8FAFC`. Header rows styled with `#F1F5F9` background, `#475569` uppercase 11px typography, and sticky vertical placement for long ward rosters.