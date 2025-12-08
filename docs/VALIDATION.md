# Validation Guide

This document provides step-by-step instructions for validating the UX and terminology changes implemented in this PR.

## Prerequisites

- Python 3.8+
- Node.js 14+
- Django and dependencies installed
- Cypress installed (`npm install`)

## Setup Steps

### 1. Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install Node.js dependencies
npm install
```

### 2. Setup Database

```bash
# Run migrations
python manage.py migrate

# Create default admin user
python manage.py create_default_admin

# Create large sample dataset (60+ courses)
python manage.py create_large_sample_data --clear
```

This will create:
- Admin user with username: `admin`, password: `admin123`
- 60+ courses across multiple departments
- Varied schedules (morning, afternoon, evening, M/W/F, T/Th, lab sessions)
- Prerequisites relationships between courses
- Multiple sections per course

### 3. Start Development Server

```bash
python manage.py runserver
```

The server will be available at `http://localhost:8000`

### 4. Login as Admin

Navigate to `http://localhost:8000/admin/login/` and login with:
- Username: `admin`
- Password: `admin123`

## Manual Validation Checklist

### ✓ Complete Registration Workflow

**1. Add Courses from Catalog (Two Entry Points)**

a. From catalog row:
1. Navigate to `/courses/catalog/`
2. Click "Add to Added Courses" button in any course row
3. Verify button changes to "✓ Added" and is disabled
4. Navigate to `/registration/register/`
5. Verify course appears in "Added Courses" list

b. From course details modal:
1. Navigate to `/courses/catalog/`
2. Click "Details" button on any course
3. In the modal, click "Add to Added Courses" button
4. Verify success message appears
5. Verify button becomes disabled with success state
6. Navigate to `/registration/register/`
7. Verify course appears in "Added Courses" list

**2. Added Courses on Schedule Page**
1. Add at least one course to Added Courses
2. Navigate to `/planning/schedule/`
3. Verify legend shows "Registered Courses" (green) and "Added Courses" (blue)
4. Verify added courses appear in calendar in blue
5. Hover over course blocks to see tooltips with full details
6. Take screenshot for validation

**3. Register Courses and Verify Notification**
1. Navigate to `/registration/register/`
2. Ensure you have courses in "Added Courses" list
3. Click "Confirm Registration" button
4. Confirm the registration when prompted
5. Wait for success message
6. Navigate to home page (`/`)
7. Verify "Unread Messages" count increased
8. Click on "Unread Messages" box
9. Verify you're redirected to `/notifications/notifications/`
10. Verify "Enrollment Confirmed" notification is visible
11. Take screenshot showing the notification

**4. Verify Registered Courses**
1. Navigate to `/registration/register/`
2. Verify courses now appear in "Currently Enrolled" section (not in Added Courses)
3. Verify total credits are calculated correctly
4. Take screenshot

**5. Drop Registered Courses**
1. On registration page, find a registered course
2. Click "Drop Course" button
3. Confirm the drop action
4. Verify course is removed or marked as dropped
5. Verify total credits updated
6. Take screenshot

**6. Notifications System**
1. Navigate to `/notifications/notifications/`
2. Verify all notifications are displayed
3. Click on a notification to mark as read
4. Verify read/unread states update correctly
5. Navigate back to home page
6. Verify unread count decreased
7. Test notification buttons (admin only) to create test notifications
8. Take screenshot

### ✓ Terminology Changes (Cart → Added Courses)

1. Navigate to `/registration/register/`
2. Verify page shows "Added Courses" heading (NOT "Registration Cart")
3. Verify empty state says "Your Added Courses List is Empty" (NOT "Your Cart is Empty")
4. Browse to Course Catalog and open a course details modal
5. Verify button says "Add to Added Courses" (NOT "Add to Cart")
6. Click "Load Plan" button
7. Verify modal says "Load Plan to Added Courses" (NOT "Load Plan to Cart")

### ✓ Create a Plan Button Removal

1. Navigate to `/registration/register/`
2. Verify "Create a Plan" button is NOT visible in Quick Actions section
3. Verify layout looks correct with remaining buttons (Browse Course Catalog, Load Plan, View My Schedule)

### ✓ Modal Close Functionality

**Course Details Modal:**
1. Navigate to Course Catalog
2. Click on any course to open modal
3. Test close via X button (top right) - modal should close
4. Open modal again, test close via "Close" button in footer - should close
5. Open modal again, press ESC key - should close
6. Verify body scroll is restored after closing
7. Verify focus is restored to triggering element

**Load Plan Modal:**
1. Navigate to Registration page
2. Click "Load Plan" button
3. Test close via X button - modal should close
4. Open modal again, press ESC key - should close

### ✓ Schedule Page Updates

1. Navigate to `/planning/schedule/`
2. Verify legend is visible showing:
   - Green box: "Registered Courses"
   - Blue box: "Added Courses"
3. Verify schedule calendar shows courses in appropriate colors:
   - Registered courses: green
   - Added courses: blue
4. Hover over course blocks to see tooltip with details
5. Verify "Browse Course Catalog" button is present
6. Verify "View All Courses" button is NOT present
7. Verify "Browse Catalog" button is NOT present

### ✓ Prerequisites Display

1. Navigate to Course Catalog
2. Open a 100-level course modal (e.g., CS101, MATH101)
3. Verify "Prerequisites" section shows "None"
4. Close and open a 200+ level course modal (e.g., CS201, MATH201)
5. Verify "Prerequisites" section lists prerequisite courses
6. Verify prerequisites are formatted as a list with course code and title

## Running Automated Tests

### Run All Cypress Tests

```bash
# Headless mode (CI)
npm run test:e2e

# Interactive mode
npm run cypress:open
```

### Run Specific Test Suites

```bash
# Complete workflow tests (NEW)
npx cypress run --spec "cypress/e2e/complete-workflow.cy.js"

# Modal functionality tests
npx cypress run --spec "cypress/e2e/modal-functionality.cy.js"

# Added Courses tests
npx cypress run --spec "cypress/e2e/added-courses.cy.js"

# Terminology tests
npx cypress run --spec "cypress/e2e/terminology.cy.js"

# Schedule tests
npx cypress run --spec "cypress/e2e/schedule.cy.js"

# Prerequisites tests
npx cypress run --spec "cypress/e2e/prerequisites.cy.js"
```

## Screenshots

After running tests, screenshots will be available in:
- `cypress/screenshots/` - Test screenshots
- The tests automatically capture key screens:
  - Course details modal with prerequisites
  - Schedule page with legend and both course types
  - Registration page with Added Courses
  - Empty Added Courses state
  - Catalog with "Add to Added Courses" buttons (both row and modal)
  - Enrollment Confirmed notification
  - Notifications page
  - After dropping courses

## Test Coverage

The automated tests verify:

1. **Complete Registration Workflow** (NEW)
   - Adding courses from catalog row button
   - Adding courses from modal button
   - Consistent state between both entry points
   - Added courses appearing on schedule page
   - Schedule conflict detection
   - Registration process with notification
   - Dropping registered courses
   - Notifications system functionality
   - Read/unread state management

2. **Modal Close Functionality**
   - X button closes both modals
   - Close button in footer closes modal
   - ESC key closes modals
   - Focus restoration works correctly
   - Body scroll is restored

3. **Terminology Changes**
   - No "Cart" references in UI
   - "Added Courses" appears in all relevant places
   - "Create a Plan" button is removed

4. **Added Courses Functionality**
   - Adding courses from modal updates list
   - Adding courses from catalog row updates list
   - Badge count updates
   - Button state changes after adding
   - Removing courses works correctly

5. **Schedule Page**
   - Legend is visible
   - Both course types render with distinct colors
   - Correct buttons are present/absent
   - Hover tooltips work

6. **Prerequisites Display**
   - Prerequisites section always visible
   - Shows "None" when no prerequisites
   - Lists prerequisites when they exist
   - Proper formatting and styling

## Expected Results

All tests should pass with:
- ✓ 0 failing tests
- ✓ All terminology changed from "Cart" to "Added Courses"
- ✓ Modals close properly via all methods
- ✓ Schedule shows both Added and Registered courses
- ✓ Prerequisites display correctly
- ✓ Add to Added Courses works from both catalog row and modal
- ✓ Registration creates "Enrollment Confirmed" notification
- ✓ Notifications system functional with read/unread states
- ✓ Dropping courses works correctly
- ✓ Screenshots captured successfully

## Troubleshooting

### Tests Fail Due to Missing Data
- Run `python manage.py create_large_sample_data --clear` again
- Ensure admin user exists: `python manage.py create_default_admin`

### Modal Tests Fail
- Ensure JavaScript is enabled
- Check browser console for errors
- Verify modals load from correct endpoints

### Schedule Tests Fail
- Add at least one course to Added Courses manually
- Register for at least one course as admin user
- Check session storage is working

### Notification Tests Fail
- Ensure migrations are run: `python manage.py migrate`
- Check that notifications app is in INSTALLED_APPS
- Verify notification creation in registration view

## Visual Confirmation

For final validation, compare screenshots in `cypress/screenshots/` with the following expected states:

1. **course-details-modal-prerequisites.png**: Modal showing either prerequisites list or "None"
2. **schedule-page-with-legend.png**: Schedule with visible legend and color-coded courses
3. **catalog-add-to-added-courses-row.png**: Catalog with working "Add to Added Courses" buttons
4. **enrollment-confirmed-notification.png**: Notification showing enrollment confirmation
5. **notifications-page.png**: Full notifications page with test notifications

## Success Criteria

✅ All automated tests pass  
✅ No "Cart" terminology visible in UI  
✅ "Added Courses" consistently used throughout  
✅ Modals close via X, Close button, and ESC  
✅ Schedule shows both course types with legend  
✅ Prerequisites display correctly  
✅ "Create a Plan" button removed from registration page  
✅ Correct buttons present on schedule page  
✅ Add to Added Courses works from catalog row and modal  
✅ Registration creates notification  
✅ Notifications system fully functional  
✅ Dropping courses works correctly  
✅ Unread messages box shows accurate count  
✅ Clicking unread messages box opens notifications page  

---

For any issues or questions, please refer to the main README.md or open an issue.
