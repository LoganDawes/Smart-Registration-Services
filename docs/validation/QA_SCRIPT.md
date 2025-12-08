# QA Testing Script for Registration Workflow

This script provides step-by-step instructions for manually validating the course registration workflow fixes.

## Prerequisites

1. Access to the Smart Registration Services application
2. Admin/test account credentials
3. Sample data populated (courses with and without prerequisites)
4. Browser with developer tools available

## Test Environment Setup

```bash
# 1. Start the development server
python manage.py runserver

# 2. Populate sample data (if needed)
python manage.py create_sample_data

# 3. Create test user (if needed)
python manage.py createsuperuser --username testadmin --email test@example.com
```

---

## Test Suite 1: Layout Consistency

### Test 1.1: Catalog Layout Reference
**Goal**: Establish baseline for comparison

**Steps**:
1. Navigate to `/courses/catalog/`
2. Observe the row structure:
   - Course code (left, ~96px wide)
   - Course title (expanding)
   - Subject badge (center, ~128px)
   - Credits (center, ~80px)
   - Instructor (right, ~160px)
   - Action buttons (far right)

**Screenshot**: Save as `docs/validation/catalog-layout.png`

**Expected**: Rows are evenly spaced, columns aligned, readable typography

---

### Test 1.2: Registration Page Layout
**Goal**: Verify Added Courses matches catalog format

**Steps**:
1. Add 2-3 courses to Added Courses from catalog
2. Navigate to `/registration/register/`
3. Inspect the Added Courses section rows
4. Compare with catalog layout

**Verification Checklist**:
- [ ] Course code column width matches (~96px)
- [ ] Title column expands to fill space
- [ ] Subject badges are centered and styled consistently
- [ ] Credits column is centered (~80px)
- [ ] Instructor column is right-aligned (~160px)
- [ ] Action buttons (Register/Remove) are in consistent location
- [ ] Row spacing and padding matches catalog
- [ ] Hover effects work properly
- [ ] Alternate row colors (if applicable) match

**Screenshot**: Save as `docs/validation/register-layout.png`

**Expected**: ✅ Visual parity between catalog and registration page

---

### Test 1.3: Responsive Layout
**Goal**: Verify layout adapts to different screen sizes

**Steps**:
1. Open browser dev tools (F12)
2. Toggle device toolbar
3. Test at:
   - Desktop: 1280x720
   - Tablet: 768x1024
   - Mobile: 375x667
4. Verify layout adapts gracefully

**Verification Checklist**:
- [ ] Desktop: All columns visible, proper spacing
- [ ] Tablet: Columns may stack, but remain readable
- [ ] Mobile: Columns stack vertically, buttons accessible
- [ ] No horizontal scrolling required
- [ ] Text remains readable at all sizes

**Screenshot**: Save as `docs/validation/responsive-layout.png`

**Expected**: ✅ Layout works on all screen sizes

---

## Test Suite 2: Enrollment Logic

### Test 2.1: Registration Without Removal Prompt
**Goal**: Verify registration doesn't show second confirmation

**Steps**:
1. Add course "CS101" to Added Courses
2. Click "Register" button for CS101
3. **Observe**: First confirmation dialog appears ("Register for this course now?")
4. Click "OK"
5. **Count confirmations**: Should be exactly 1
6. **Observe**: Success message appears
7. **Verify**: CS101 disappears from Added Courses
8. **Verify**: CS101 appears in "Currently Enrolled" section

**Verification Checklist**:
- [ ] Only ONE confirmation dialog appears
- [ ] No "Remove this course..." prompt appears
- [ ] Success message: "Successfully registered!"
- [ ] Course moves from Added to Enrolled
- [ ] Page reloads to show updated state

**Screenshot Series**:
- `docs/validation/before-register.png` - Added Courses view
- `docs/validation/register-confirm.png` - Single confirmation dialog
- `docs/validation/after-register.png` - Updated view with enrolled course

**Expected**: ✅ Single confirmation, automatic removal, success message

**❌ If Test Fails**: Document behavior and number of confirmations

---

### Test 2.2: Manual Removal With Confirmation
**Goal**: Verify manual removal still shows confirmation

**Steps**:
1. Add course "CS102" to Added Courses
2. Click "Remove" button for CS102
3. **Observe**: Confirmation dialog appears ("Remove this course from your Added Courses list?")
4. Click "Cancel"
5. **Verify**: CS102 remains in Added Courses
6. Click "Remove" again
7. Click "OK"
8. **Verify**: CS102 removed from Added Courses

**Verification Checklist**:
- [ ] Confirmation dialog appears when clicking Remove
- [ ] Cancel button works (keeps course)
- [ ] OK button removes course
- [ ] No error messages appear
- [ ] Page updates correctly

**Screenshot**: Save as `docs/validation/manual-removal-confirm.png`

**Expected**: ✅ Confirmation shows, removal works correctly

---

### Test 2.3: Bulk Registration
**Goal**: Verify "Confirm Registration" button works correctly

**Steps**:
1. Add 3 courses to Added Courses: CS101, CS102, CS103
2. Click "Confirm Registration" button at top of Added Courses section
3. **Observe**: Confirmation dialog ("Register for all 3 courses...")
4. Click "OK"
5. **Observe**: Success message with count
6. **Verify**: All courses moved to Currently Enrolled
7. **Verify**: Added Courses list is now empty

**Verification Checklist**:
- [ ] Confirmation shows correct count
- [ ] Success message shows: "Successfully registered for 3 course(s)!"
- [ ] All courses enrolled
- [ ] Added Courses list cleared
- [ ] No removal prompts appear during process

**Screenshot**: Save as `docs/validation/bulk-registration.png`

**Expected**: ✅ Bulk registration works without individual removal prompts

---

## Test Suite 3: Prerequisite Bypass

### Test 3.1: Register Without Prerequisites
**Goal**: Verify students can register for courses without meeting prerequisites

**Steps**:
1. Identify a course with prerequisites:
   - Open course catalog
   - Click "Details" on an advanced course (e.g., CS201)
   - Note prerequisites section shows "CS101" required
2. Verify student has NOT completed CS101:
   - Check Currently Enrolled section
   - Confirm CS101 is not listed
3. Add CS201 to Added Courses
4. Click "Register" for CS201
5. **Verify**: Registration succeeds
6. **Verify**: NO "Prerequisites not met" error appears

**Verification Checklist**:
- [ ] Course details show prerequisites (view-only)
- [ ] Student has not completed prerequisites
- [ ] Registration succeeds anyway
- [ ] No error messages about prerequisites
- [ ] Course appears in Currently Enrolled

**Screenshot Series**:
- `docs/validation/prerequisites-display.png` - Course details showing prerequisites
- `docs/validation/prerequisite-bypass-success.png` - Successful registration

**Expected**: ✅ Registration succeeds despite unmet prerequisites

**Note**: This is intentional behavior per requirements

---

### Test 3.2: Bulk Registration With Prerequisites
**Goal**: Verify bulk registration bypasses prerequisites

**Setup**:
- Ensure student has NO prior enrollments
- Add courses with prerequisites:
  - CS201 (requires CS101)
  - CS301 (requires CS201)
  - CS302 (requires CS201)

**Steps**:
1. Add all three courses to Added Courses
2. Click "Confirm Registration"
3. Confirm when prompted
4. **Verify**: All courses register successfully
5. **Verify**: Success message shows "Successfully registered for 3 course(s)!"
6. **Verify**: No failure messages about prerequisites

**Verification Checklist**:
- [ ] All courses added to Added Courses
- [ ] Bulk registration initiated
- [ ] All 3 courses register successfully
- [ ] No prerequisite errors in response
- [ ] Failed count is 0

**Expected**: ✅ All courses register regardless of prerequisite chain

---

## Test Suite 4: State Transitions

### Test 4.1: Complete Workflow
**Goal**: Verify smooth state transitions from catalog to enrolled

**Steps**:
1. **State: Unadded**
   - Navigate to `/courses/catalog/`
   - Locate CS101 in list
   - Note: Only "Details", "Add to Plan", "Add to Added Courses" buttons visible

2. **Transition: Unadded → Added**
   - Click "Add to Added Courses" for CS101
   - **Verify**: Success alert appears
   - **Verify**: Button changes to "✓ Added" or disabled state

3. **State: Added**
   - Navigate to `/registration/register/`
   - **Verify**: CS101 appears in Added Courses section
   - **Verify**: "Register" and "Remove" buttons visible

4. **Transition: Added → Registered**
   - Click "Register" for CS101
   - Confirm when prompted
   - **Verify**: Success message appears
   - **Verify**: CS101 disappears from Added Courses
   - **Verify**: CS101 appears in Currently Enrolled section

5. **State: Registered**
   - **Verify**: CS101 in Currently Enrolled with "Drop" button
   - **Verify**: Total credits updated

**Verification Checklist**:
- [ ] Each state displays correctly
- [ ] Transitions happen smoothly
- [ ] No duplicate entries
- [ ] No stale data across pages
- [ ] UI updates without manual refresh (or auto-refreshes)

**Screenshot**: Save as `docs/validation/state-transitions.png`

**Expected**: ✅ Clean, predictable state transitions

---

## Test Suite 5: Edge Cases

### Test 5.1: Empty Added Courses
**Goal**: Verify empty state handling

**Steps**:
1. Remove all courses from Added Courses
2. Navigate to `/registration/register/`
3. **Verify**: Empty state message displays
4. **Verify**: "Browse Catalog" and "Load Plan" buttons visible

**Expected**: ✅ Helpful empty state with clear next actions

---

### Test 5.2: Duplicate Registration Prevention
**Goal**: Verify system prevents duplicate enrollments

**Steps**:
1. Register for CS101
2. Add CS101 to Added Courses again (from catalog)
3. Try to register for CS101 again
4. **Verify**: Error message: "Already enrolled in this section"

**Expected**: ✅ Duplicate prevention works

---

### Test 5.3: Full Section Handling
**Goal**: Verify waitlist behavior (if applicable)

**Steps**:
1. Identify a section at capacity
2. Attempt to register
3. **Verify**: Either enrollment fails with capacity message, or student is waitlisted

**Expected**: ✅ Capacity limits enforced

---

## Test Suite 6: Cross-Browser Testing

### Browsers to Test
- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Edge (latest)

### For Each Browser
1. Run Test Suite 1 (Layout)
2. Run Test Suite 2 (Enrollment Logic)
3. Document any browser-specific issues

---

## Test Results Summary

### Layout Tests
- [ ] Test 1.1: Catalog Layout Reference
- [ ] Test 1.2: Registration Page Layout
- [ ] Test 1.3: Responsive Layout

### Enrollment Logic Tests
- [ ] Test 2.1: Registration Without Removal Prompt
- [ ] Test 2.2: Manual Removal With Confirmation
- [ ] Test 2.3: Bulk Registration

### Prerequisite Bypass Tests
- [ ] Test 3.1: Register Without Prerequisites
- [ ] Test 3.2: Bulk Registration With Prerequisites

### State Transition Tests
- [ ] Test 4.1: Complete Workflow

### Edge Case Tests
- [ ] Test 5.1: Empty Added Courses
- [ ] Test 5.2: Duplicate Registration Prevention
- [ ] Test 5.3: Full Section Handling

### Cross-Browser Tests
- [ ] Chrome
- [ ] Firefox
- [ ] Safari
- [ ] Edge

---

## Issue Reporting

If any test fails, document:

1. **Test Number**: (e.g., Test 2.1)
2. **Expected Behavior**: What should happen
3. **Actual Behavior**: What actually happened
4. **Steps to Reproduce**: Exact sequence
5. **Screenshots**: Visual evidence
6. **Browser/Version**: If browser-specific
7. **Console Errors**: Any JavaScript errors

**Format**:
```
## Issue: [Brief Description]
- Test: 2.1
- Severity: High/Medium/Low
- Expected: Single confirmation dialog
- Actual: Two confirmation dialogs appeared
- Screenshot: docs/validation/issue-2.1.png
- Browser: Chrome 120.0.6099.109
```

---

## Sign-Off

**Tester Name**: ___________________________  
**Date**: ___________________________  
**Overall Result**: ☐ Pass ☐ Pass with Notes ☐ Fail  
**Notes**:
_____________________________________________
_____________________________________________
_____________________________________________

**Signature**: ___________________________
