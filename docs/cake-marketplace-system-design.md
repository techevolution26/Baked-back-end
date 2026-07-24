# Cake Design Marketplace — System Design

**Status:** Proposed
**Date:** 2026-07-22
**Deciders:** John Alfred (Tech Resolute)

## 1. Requirements

**Functional**
- Marketplace dashboard: browse designs across multiple bakeries
- Customer flow: buy a design as-is, OR customize color / stickers / whole design
- Visual, icon-first interaction (tap, drag, drop) — no reliance on reading/writing descriptions
- Assembled design becomes a structured "blueprint" sent to the bakery for baking
- Optional: printable elements (toppers, stencils, molds) exported for a 3D printer
- Bakery owner dashboard: receive blueprint + order, accept/reject, track to delivery
- Payment via M-Pesa

**Non-functional**
- Multi-tenant (many bakeries, isolated inventory/pricing, shared customer base)
- Low-bandwidth friendly (East Africa mobile networks) — compress previews, cache aggressively
- Works on web (PWA) and native mobile from day one
- Literacy-independent UX as a hard constraint, not a nice-to-have

**Constraints**
- Solo/small team, existing stack fluency: Next.js (App Router), React, TypeScript, FastAPI, PostgreSQL, M-Pesa Daraja
- Physical 3D printing hardware is bakery-side, not something the platform controls directly

## 2. Core Concept: The Blueprint

Every customization — bought as-is or fully custom — resolves to one portable JSON document. This is what gets rendered as a preview, sent to the bakery, and (optionally) used to generate a printable file.

```json
{
  "template_id": "tpl_204",
  "base": { "shape": "round", "tiers": 2, "size_inches": 10 },
  "layers": [
    { "type": "color_fill", "target": "tier_1_body", "swatch_id": "sw_012" },
    { "type": "sticker", "asset_id": "sticker_042", "x": 0.5, "y": 0.3, "scale": 1.2, "rotation": 15 },
    { "type": "reference_photo", "url": "https://.../inspo.jpg" },
    { "type": "text", "value": "Happy Birthday", "font": "handwritten" }
  ],
  "printable_elements": [ { "layer_index": 1, "exportable": true, "kind": "topper" } ]
}
```

Layers are the unit of both editing (drag-and-drop) and rendering (2D preview) and, later, fabrication (STL export for flagged elements only).

## 3. High-Level Architecture

```
┌──────────────────┐      ┌───────────────────┐
│  Next.js Web PWA  │      │ React Native (Expo)│
│  customers + owners│      │ customers + owners │
└─────────┬─────────┘      └──────────┬─────────┘
          │      shared TS types/DTOs  │
          └──────────────┬─────────────┘
                          │ REST/JSON (BFF)
                 ┌────────▼─────────┐
                 │  FastAPI Backend  │
                 │ auth · orders ·   │
                 │ blueprints ·      │
                 │ pricing engine    │
                 └───┬─────────┬─────┘
                     │         │
         ┌───────────▼──┐   ┌──▼──────────────┐
         │ PostgreSQL    │   │ Object Storage   │
         │ (row-scoped   │   │ stickers, photos,│
         │  multi-tenant)│   │ rendered previews│
         └───────────────┘   └──────────────────┘
                     │
         ┌───────────▼────────────┐
         │  M-Pesa Daraja (STK)    │
         └─────────────────────────┘
                     │  (phase 2)
         ┌───────────▼────────────┐
         │  STL Export Service     │
         │  (topper/mold geometry) │
         └─────────────────────────┘
```

## 4. Data Model (core tables)

| Table | Key fields |
|---|---|
| `users` | id, role (customer/bakery_owner/admin), phone, name |
| `bakeries` | id, owner_user_id, name, location, mpesa_till, verified, rating |
| `design_templates` | id, bakery_id, base_shape, base_price, tags[], cover_image_url, customizable_fields (jsonb) |
| `sticker_assets` | id, bakery_id (nullable = global library), thumbnail_url, category |
| `color_palettes` | id, bakery_id (nullable = global), hex, swatch_image |
| `blueprints` | id, template_id (nullable for from-scratch), customer_id, bakery_id, layers (jsonb), preview_render_url, status |
| `orders` | id, blueprint_id, customer_id, bakery_id, price, payment_status, order_status, mpesa_transaction_id |
| `print_jobs` (phase 2) | id, blueprint_id, layer_ref, stl_url, print_status |

## 5. Key Decisions

### ADR-1: 2D Layered Canvas vs. Full 3D Web Preview
**Decision:** Ship a 2D layered canvas (react-konva) rendering a stylized tiered/isometric view. Defer true 3D rendering.
| | react-konva (2D) | Three.js (3D) |
|---|---|---|
| Complexity | Low | High |
| Time to ship | Fast | Slow |
| Fits drag/drop editing | Directly | Needs extra abstraction |
| Fits low-bandwidth mobile | Yes | Heavier |

A convincing 2D layered mockup validates the flow far faster than a real-time 3D renderer, and the blueprint JSON is renderer-agnostic — you can swap in Three.js later without changing the data model.

### ADR-2: Scope of "3D Printing"
**Decision:** Phase 1 delivers the blueprint as a visual spec only — the bakery reads the rendered preview and layer list and builds the cake by hand. Phase 2 adds *optional* STL generation, but only for flagged `printable_elements` (toppers, stencils, cutter molds) — never the cake itself, which isn't something a consumer 3D printer produces.

This keeps the MVP shippable and avoids an open-ended geometry/fabrication problem up front.

### ADR-3: Web + Mobile Strategy
**Decision:** Next.js PWA (web) + React Native/Expo (mobile), sharing a TypeScript types/DTO package and API client layer against the same FastAPI backend. This reuses your existing React/TS depth instead of adding a second language/framework (Flutter, native Swift/Kotlin).

### ADR-4: Multi-Tenancy
**Decision:** Single shared PostgreSQL database, row-scoped by `bakery_id`, with an admin-gated onboarding flow (business info + sample photos) before a bakery can list designs. Schema-per-tenant or DB-per-tenant is unnecessary complexity at this scale and would slow down cross-bakery marketplace browsing.

## 6. Literacy-Barrier UX Principles (apply everywhere, not just the builder)
- Swatches instead of color names/hex, thumbnails instead of text lists
- Drag-and-drop placement instead of typed positioning/descriptions
- Photo upload or voice note as the "describe what you want" fallback, instead of a text box
- Relative visual size comparisons (small/medium/large shown as actual scaled circles) instead of numeric-only sizes
- Icon-based order status stepper (submitted → accepted → baking → ready → delivered)
- Swahili/English toggle — but the icon-first design keeps translation surface area small

## 7. Order Flow
1. Customer browses marketplace (photo/rating/price driven, minimal text)
2. Picks a template or starts blank → customizes in the layer editor
3. Live preview + price recalculates per bakery pricing rules
4. Customer submits → M-Pesa STK push
5. Blueprint + order land on bakery dashboard → accept/reject/counter
6. If printable elements exist, STL auto-generated and queued (phase 2)
7. Status updates flow back to customer via the icon stepper

## 8. Phased Roadmap
- **Phase 1 (MVP):** marketplace browsing, template + layer customization, M-Pesa payment, bakery dashboard, visual-spec-only blueprint
- **Phase 2:** STL export for toppers/molds, printer queue, ratings/reviews, bakery analytics
- **Phase 3:** real-time 3D preview (Three.js), "match this reference photo" suggestion engine, bakery-to-bakery template marketplace

## 9. Open Questions to Revisit
- M-Pesa: full payment upfront vs. deposit/escrow until bakery accepts
- Sticker/photo upload moderation policy for the shared asset library
- Bakery verification requirements (KYC-lite) before listing
- Whether design templates are bakery-exclusive or shareable marketplace assets
