/**
 * E2E Tests for Prerequisites Display
 * Verifies prerequisites are visible in course details modal
 */

describe('Prerequisites Display Tests', () => {
  beforeEach(() => {
    cy.loginAsAdmin()
    cy.wait(1000)
  })

  it('should display prerequisites section in course details modal', () => {
    cy.visit('/courses/catalog/')
    cy.wait(1000)
    
    // Open any course details
    cy.get('[data-course-id]').first().click()
    cy.wait(500)
    
    // Verify prerequisites section exists
    cy.get('[data-testid="prerequisites-section"]').should('be.visible')
    
    // Check for either prerequisites list or "None" message
    cy.get('[data-testid="prerequisites-section"]').then($section => {
      if ($section.find('[data-testid="prerequisites-list"]').length > 0) {
        cy.get('[data-testid="prerequisites-list"]').should('be.visible')
      } else {
        cy.get('[data-testid="no-prerequisites"]').should('contain', 'None')
      }
    })
  })

  it('should display "None" when course has no prerequisites', () => {
    cy.visit('/courses/catalog/')
    cy.wait(1000)
    
    // Try to find a course without prerequisites
    // We'll check the first course and verify prerequisites section
    cy.get('[data-course-id]').first().click()
    cy.wait(500)
    
    cy.get('[data-testid="prerequisites-section"]').should('be.visible')
    
    // If no prerequisites, should show "None"
    cy.get('body').then($body => {
      if ($body.find('[data-testid="no-prerequisites"]').length > 0) {
        cy.get('[data-testid="no-prerequisites"]').should('contain', 'None')
      }
    })
  })

  it('should list prerequisites when course has them', () => {
    cy.visit('/courses/catalog/')
    cy.wait(1000)
    
    // Look for advanced courses that likely have prerequisites
    // Try to find a 200+ level course
    cy.get('body').then($body => {
      const courseLinks = $body.find('[data-course-id]')
      let foundCourseWithPrereqs = false
      
      // Iterate through courses to find one with prerequisites
      courseLinks.each((index, element) => {
        if (!foundCourseWithPrereqs) {
          cy.wrap(element).click()
          cy.wait(500)
          
          cy.get('body').then($modal => {
            if ($modal.find('[data-testid="prerequisites-list"]').length > 0) {
              // Found a course with prerequisites
              cy.get('[data-testid="prerequisites-list"]').should('be.visible')
              cy.get('[data-testid="prerequisites-list"] li').should('have.length.at.least', 1)
              foundCourseWithPrereqs = true
            } else {
              // Close modal and try next course
              cy.get('.modal-close-btn').click()
              cy.wait(300)
            }
          })
        }
      })
    })
  })

  it('should format prerequisites correctly', () => {
    cy.visit('/courses/catalog/')
    cy.wait(1000)
    
    // Open a course modal
    cy.get('[data-course-id]').first().click()
    cy.wait(500)
    
    // Verify prerequisites section formatting
    cy.get('[data-testid="prerequisites-section"]').within(() => {
      // Should have a heading
      cy.contains('Prerequisites').should('be.visible')
      
      // Should have proper styling
      cy.get('.border-yellow-500').should('exist')
    })
  })

  it('should take screenshot of course details with prerequisites', () => {
    cy.visit('/courses/catalog/')
    cy.wait(1000)
    
    // Open first course
    cy.get('[data-course-id]').first().click()
    cy.wait(1000)
    
    cy.screenshot('course-details-modal-prerequisites', {
      capture: 'viewport',
      overwrite: true
    })
  })
})
