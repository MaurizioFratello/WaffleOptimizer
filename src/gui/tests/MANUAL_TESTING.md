# UI Standardization Manual Testing Guide

This document provides a systematic approach to manually verify the consistent implementation of UI standards across the Waffle Optimizer application.

## Setup

1. Run the application by executing `python -m src.gui.main` from the project root
2. Alternatively, run the style verification test directly with `python -m src.gui.tests.style_verification`

## General UI Standards Verification

For each view in the application, verify that:

### Headers and Descriptions
- [ ] All view headers use the same font size (24px) and weight (bold)
- [ ] All view descriptions use the same font size (14px) and color (#7f8c8d)
- [ ] Headers and descriptions have consistent spacing between them

### Button Placement and Styling
- [ ] Primary action buttons are consistently placed in the top-right corner of views
- [ ] Primary action buttons have the same styling (blue background, white text)
- [ ] Secondary buttons have consistent styling (white background, border)
- [ ] Button sizes are consistent throughout the application

### Group Box Styling
- [ ] All group boxes have consistent title styling (16px, semi-bold)
- [ ] All group boxes have the same border color and radius
- [ ] All group boxes have consistent internal padding and margin

### Spacing and Margins
- [ ] All views have consistent outer margins (20px)
- [ ] Spacing between elements is consistent (15px)
- [ ] Form layouts have consistent label and field alignment

### Card Widget Styling
- [ ] All cards have consistent styling (background, border, corner radius)
- [ ] Status-colored cards (in validation view) have consistent status indicators

## View-Specific Verification

### Data View
- [ ] Proper header and description
- [ ] Group boxes with standardized styling
- [ ] File selectors with consistent padding and spacing
- [ ] Preview tabs with consistent styling

### Validation Dashboard View
- [ ] "Run Validation" button properly positioned in the top-right
- [ ] Status cards using standardized card styling
- [ ] Recommendations box positioned below status cards
- [ ] Chart tabs with consistent styling

### Optimization View
- [ ] "Run Optimization" button properly positioned in the top-right
- [ ] Settings form with consistent label and field spacing
- [ ] Output settings group with consistent styling
- [ ] Status display with consistent styling

### Results View
- [ ] Metric cards with standardized card styling
- [ ] Results tabs with consistent styling
- [ ] Export options with consistent form layout

### Model Description View
- [ ] Content area with consistent styling and scrolling behavior

## Verification Process

1. Start with the Data View and systematically navigate through each view
2. For each view, check all the applicable items in the lists above
3. Take screenshots of any inconsistencies found
4. Note any variations in the styling that may need correction

## Known Variations

Some widgets may have specific styling needs that differ from the standard. These are documented below:

- Matplotlib charts in the Validation view use their own styling system
- Card widgets in the Results view have specific styling for metric display

## Reporting Issues

When reporting standardization issues, please include:

1. The view/component where the issue was found
2. A screenshot of the issue
3. A description of the expected styling based on this guide
4. The specific elements that need adjustment

This testing process will help ensure a consistent and professional user experience across the entire application. 