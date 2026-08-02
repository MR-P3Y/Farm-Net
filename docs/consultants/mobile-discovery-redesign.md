# Mobile Consultant Discovery Redesign

Status: completed and manually approved on 2026-08-02.

## Delivered

- specialty-first consultant discovery with compact, overflow-safe cards;
- shared Persian/English and light/dark presentation;
- debounced text search and rating/newest/relevance sorting;
- real province/city filters backed by Geo identifiers;
- one-step filter sheet with explicit apply and clear actions;
- active-filter indicator and a visible clear-filters action;
- collapsible discovery hero and specialties while scrolling results;
- responsive consultant cards and decimal rating parsing;
- redesigned consultant profile with shared back navigation, glass sections,
  persistent consultation CTA, performance metrics, specialties, biography,
  and public reviews placed at the end of the profile;
- empty, loading, API-error, large-text, and narrow-screen handling.

## Verification

- focused Flutter analyze: passed;
- consultant model/state tests: 4 passed;
- Flutter web build: passed;
- manual Persian mobile UI verification: approved;
- manual specialty, province/city, scrolling, filter clearing, profile, and
  responsive button verification: approved.

The local development database contains eight active specialties and seven
approved consultant fixtures across multiple specialties and Geo-backed
province/city combinations for manual discovery testing. These are development
fixtures and are not part of production migrations.
