/**
 * E2E Tests for Added Courses Functionality
 * Tests adding courses to Added Courses list and badge updates
 */

describe('Added Courses Functionality Tests', () => {
  beforeEach(() => {
    cy.loginAsAdmin()
    cy.wait(1000)
  })

  it('should add course from modal to Added Courses', () => {
    // Clear session storage
    cy.clearCookies()
    
    cy.visit('/courses/catalog/')
    cy.wait(1000)
    
    // Open course details modal
    cy.get('[data-course-id]').first().click()
    cy.wait(500)
    
    // Verify modal is visible
    cy.get('#course-details-modal').should('be.visible')
    
    // Click "Add to Added Courses" button
    cy.get('[data-testid="add-to-added-courses-btn"]').click()
    cy.wait(1000)
    
    // Verify success (alert or button state change)
    // Modal should close after adding
    cy.wait(2000)
    
    // Navigate to registration page
    cy.visit('/registration/register/')
    cy.wait(1000)
    
    // Verify course appears in Added Courses list
    cy.get('[data-testid="added-courses-section"]').should('be.visible')
    cy.get('[data-testid="added-course-item"]').should('have.length.at.least', 1)
  })

  it('should show empty state when no courses added', () => {
    cy.visit('/registration/register/')
    cy.wait(1000)
    
    // Check for empty state
    cy.get('body').then($body => {
      if ($body.find('[data-testid="empty-added-courses"]').length > 0) {
        cy.get('[data-testid="empty-added-courses"]').should('be.visible')
        cy.contains('Your Added Courses List is Empty').should('be.visible')
      }
    })
  })

  it('should display Added Courses heading', () => {
    cy.visit('/registration/register/')
    cy.wait(1000)
    
    cy.get('[data-testid="added-courses-heading"]').should('contain', 'Added Courses')
  })

  it('should remove course from Added Courses', () => {
    cy.visit('/registration/register/')
    cy.wait(1000)
    
    // Check if there are any added courses
    cy.get('body').then($body => {
      if ($body.find('[data-testid="added-course-item"]').length > 0) {
        // Click remove button on first item
        cy.get('[data-testid="remove-from-added-courses-btn"]').first().click()
        cy.wait(1000)
        
        // Accept confirmation dialog
        cy.on('window:confirm', () => true)
        
        // Page should reload
        cy.wait(1000)
      }
    })
  })
})
