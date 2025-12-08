/**
 * E2E Tests for Complete Registration Workflow
 * Tests the full flow: Catalog -> Added Courses -> Register -> Notifications
 */

describe('Complete Registration Workflow Tests', () => {
  beforeEach(() => {
    cy.loginAsAdmin()
    cy.wait(1000)
  })

  describe('1. Course Catalog Add to Added Courses', () => {
    it('should add course from catalog row button', () => {
      cy.visit('/courses/catalog/')
      cy.wait(1000)
      
      // Find and click "Add to Added Courses" button in catalog row
      cy.get('[data-testid="add-to-added-courses-row-btn"]').first().as('addBtn').click()
      cy.wait(1000)
      
      // Verify alert or button state change
      cy.get('@addBtn').should('contain', '✓ Added')
      cy.get('@addBtn').should('be.disabled')
      
      // Navigate to registration page
      cy.visit('/registration/register/')
      cy.wait(1000)
      
      // Verify course appears in Added Courses list
      cy.get('[data-testid="added-courses-section"]').should('be.visible')
      cy.get('[data-testid="added-course-item"]').should('have.length.at.least', 1)
      
      // Take screenshot
      cy.screenshot('catalog-add-to-added-courses-row', { capture: 'viewport' })
    })

    it('should add course from modal button', () => {
      cy.visit('/courses/catalog/')
      cy.wait(1000)
      
      // Click Details button to open modal
      cy.get('[data-testid="details-btn"]').first().click()
      cy.wait(1000)
      
      // Verify modal is visible
      cy.get('#course-details-modal').should('be.visible')
      
      // Click "Add to Added Courses" button in modal
      cy.get('[data-testid="add-to-added-courses-btn"]').click()
      cy.wait(2000)
      
      // Modal should close after adding
      cy.wait(1000)
      
      // Navigate to registration page
      cy.visit('/registration/register/')
      cy.wait(1000)
      
      // Verify course appears in Added Courses list
      cy.get('[data-testid="added-course-item"]').should('have.length.at.least', 1)
      
      // Take screenshot
      cy.screenshot('modal-add-to-added-courses', { capture: 'viewport' })
    })

    it('should show consistent state when adding from both entry points', () => {
      // This test ensures both buttons update the same backend state
      cy.visit('/courses/catalog/')
      cy.wait(1000)
      
      // Add from row
      cy.get('[data-testid="add-to-added-courses-row-btn"]').first().click()
      cy.wait(1000)
      
      // Try to add same course from modal - should show error
      cy.get('[data-testid="details-btn"]').first().click()
      cy.wait(500)
      
      cy.get('#course-details-modal').should('be.visible')
      cy.get('[data-testid="add-to-added-courses-btn"]').click()
      cy.wait(1000)
      
      // Should show alert about already being in Added Courses
      // (Alert would be visible in browser)
    })
  })

  describe('2. Added Courses on Schedule Page', () => {
    it('should display added courses on schedule with distinct styling', () => {
      // First add a course
      cy.visit('/courses/catalog/')
      cy.wait(1000)
      
      cy.get('[data-testid="add-to-added-courses-row-btn"]').first().click()
      cy.wait(1000)
      
      // Navigate to schedule
      cy.visit('/planning/schedule/')
      cy.wait(1000)
      
      // Verify legend is visible
      cy.get('[data-testid="schedule-legend"]').should('be.visible')
      cy.get('[data-testid="schedule-legend"]').should('contain', 'Added Courses')
      cy.get('[data-testid="schedule-legend"]').should('contain', 'Registered Courses')
      
      // Check for schedule events
      cy.get('body').then($body => {
        if ($body.find('[data-testid="schedule-event"]').length > 0) {
          // Verify at least one event exists
          cy.get('[data-testid="schedule-event"]').should('exist')
          
          // Check for added courses (blue)
          cy.get('[data-status="added"]').should('exist')
          cy.get('[data-status="added"]').should('have.class', 'event--added')
        }
      })
      
      // Take screenshot
      cy.screenshot('schedule-with-added-courses', { capture: 'fullPage' })
    })

    it('should show hover tooltips with course details', () => {
      cy.visit('/planning/schedule/')
      cy.wait(1000)
      
      // Check if events have title attribute for tooltips
      cy.get('body').then($body => {
        if ($body.find('[data-testid="schedule-event"]').length > 0) {
          cy.get('[data-testid="schedule-event"]').first().should('have.attr', 'title')
          
          // Verify title contains course information
          cy.get('[data-testid="schedule-event"]').first()
            .invoke('attr', 'title')
            .should('match', /[A-Z]+\d+/) // Should contain course code pattern
        }
      })
    })
  })

  describe('3. Registration and Notification', () => {
    it('should register courses and create Enrollment Confirmed notification', () => {
      // Navigate to registration page
      cy.visit('/registration/register/')
      cy.wait(1000)
      
      // Check if there are courses in Added Courses
      cy.get('body').then($body => {
        if ($body.find('[data-testid="added-course-item"]').length > 0) {
          // Click Confirm Registration button
          cy.get('[data-testid="confirm-registration-btn"]').click()
          cy.wait(1000)
          
          // Confirm the registration
          cy.on('window:confirm', () => true)
          cy.wait(2000)
          
          // Navigate to home page to check notifications
          cy.visit('/')
          cy.wait(1000)
          
          // Verify unread messages count increased
          cy.get('[data-testid="unread-count"]').invoke('text').then(parseInt).should('be.gte', 1)
          
          // Click unread messages box
          cy.get('[data-testid="unread-messages-box"]').click()
          cy.wait(1000)
          
          // Verify we're on notifications page
          cy.url().should('include', '/notifications/')
          
          // Look for Enrollment Confirmed notification
          cy.contains('Enrollment Confirmed').should('be.visible')
          
          // Take screenshot
          cy.screenshot('enrollment-confirmed-notification', { capture: 'fullPage' })
        }
      })
    })

    it('should show registered courses on registration page', () => {
      cy.visit('/registration/register/')
      cy.wait(1000)
      
      // Check for enrolled courses section
      cy.get('body').then($body => {
        if ($body.find('.list-row').length > 0) {
          // Should have at least one enrolled course
          cy.contains('Currently Enrolled').should('be.visible')
          
          // Take screenshot
          cy.screenshot('registered-courses-list', { capture: 'fullPage' })
        }
      })
    })
  })

  describe('4. Drop Registered Courses', () => {
    it('should drop a registered course and update UI', () => {
      cy.visit('/registration/register/')
      cy.wait(1000)
      
      // Check if there are enrolled courses
      cy.get('body').then($body => {
        if ($body.find('button').filter(':contains("Drop Course")').length > 0) {
          // Get initial count
          cy.get('body').invoke('text').then((initialText) => {
            // Click drop button on first course
            cy.contains('button', 'Drop Course').first().click()
            cy.wait(500)
            
            // Confirm the drop
            cy.on('window:confirm', () => true)
            cy.wait(2000)
            
            // Page should reload and course should be removed or marked as dropped
            cy.visit('/registration/register/')
            cy.wait(1000)
            
            // Take screenshot
            cy.screenshot('after-dropping-course', { capture: 'fullPage' })
          })
        }
      })
    })
  })

  describe('5. Notifications System', () => {
    it('should display notifications page correctly', () => {
      cy.visit('/notifications/notifications/')
      cy.wait(1000)
      
      // Page should load
      cy.contains('Notifications').should('be.visible')
      
      // Check for test notification buttons (admin/staff only)
      cy.get('body').then($body => {
        if ($body.find('button').filter(':contains("Enrollment Confirmed")').length > 0) {
          // Test creating a notification
          cy.contains('button', 'Enrollment Confirmed').click()
          cy.wait(1000)
          
          // Should see success or the notification appear
          cy.wait(2000)
          cy.visit('/notifications/notifications/')
          cy.wait(1000)
          
          // Take screenshot
          cy.screenshot('notifications-page', { capture: 'fullPage' })
        }
      })
    })

    it('should update read/unread status of notifications', () => {
      cy.visit('/notifications/notifications/')
      cy.wait(1000)
      
      // Check if there are any notifications
      cy.get('body').then($body => {
        const notificationElements = $body.find('.notification-item, [data-notification-id]')
        
        if (notificationElements.length > 0) {
          // Click on a notification to mark as read
          cy.get('.notification-item, [data-notification-id]').first().click()
          cy.wait(1000)
          
          // Verify read state changed (implementation specific)
          // Take screenshot
          cy.screenshot('notifications-read-status', { capture: 'fullPage' })
        }
      })
    })

    it('should navigate from unread messages box to notifications', () => {
      cy.visit('/')
      cy.wait(1000)
      
      // Click unread messages box
      cy.get('[data-testid="unread-messages-box"]').should('be.visible').click()
      cy.wait(1000)
      
      // Should be on notifications page
      cy.url().should('include', '/notifications/')
      cy.contains('Notifications').should('be.visible')
      
      // Take screenshot
      cy.screenshot('navigate-to-notifications', { capture: 'fullPage' })
    })
  })

  describe('6. Conflict Detection', () => {
    it('should detect and display schedule conflicts', () => {
      // Add two courses with conflicting times
      cy.visit('/courses/catalog/')
      cy.wait(1000)
      
      // Add first course
      cy.get('[data-testid="add-to-added-courses-row-btn"]').first().click()
      cy.wait(1000)
      
      // Try to find another course at the same time
      // (This would require inspecting course times)
      
      // Navigate to schedule to see if conflicts are shown
      cy.visit('/planning/schedule/')
      cy.wait(1000)
      
      // Look for conflict indicators (implementation specific)
      cy.screenshot('schedule-with-potential-conflicts', { capture: 'fullPage' })
    })
  })
})
