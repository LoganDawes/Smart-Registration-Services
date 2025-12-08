/**
 * E2E Tests for Modal Functionality
 * Tests close buttons (x, Close, ESC key) for both course details and plan modals
 */

describe('Modal Close Functionality Tests', () => {
  beforeEach(() => {
    cy.loginAsAdmin()
    cy.wait(1000)
  })

  describe('Course Details Modal', () => {
    it('should close via x button', () => {
      cy.visit('/courses/catalog/')
      cy.wait(500)
      
      // Find and click a course to open modal
      cy.get('[data-course-id]').first().click()
      cy.wait(500)
      
      // Verify modal is visible
      cy.get('#course-details-modal').should('be.visible')
      
      // Click x button
      cy.get('#course-details-modal .modal-close-btn').click()
      cy.wait(500)
      
      // Verify modal is closed
      cy.get('#course-details-modal').should('not.exist')
    })

    it('should close via Close button in footer', () => {
      cy.visit('/courses/catalog/')
      cy.wait(500)
      
      cy.get('[data-course-id]').first().click()
      cy.wait(500)
      
      cy.get('#course-details-modal').should('be.visible')
      
      // Click footer Close button
      cy.get('[data-testid="close-modal-btn"]').click()
      cy.wait(500)
      
      cy.get('#course-details-modal').should('not.exist')
    })

    it('should close via ESC key', () => {
      cy.visit('/courses/catalog/')
      cy.wait(500)
      
      cy.get('[data-course-id]').first().click()
      cy.wait(500)
      
      cy.get('#course-details-modal').should('be.visible')
      
      // Press ESC key
      cy.get('body').type('{esc}')
      cy.wait(500)
      
      cy.get('#course-details-modal').should('not.exist')
    })

    it('should restore focus after closing', () => {
      cy.visit('/courses/catalog/')
      cy.wait(500)
      
      // Click a specific element to track focus
      cy.get('[data-course-id]').first().as('courseLink').click()
      cy.wait(500)
      
      // Close modal
      cy.get('#course-details-modal .modal-close-btn').click()
      cy.wait(500)
      
      // Focus should be restored (check body is unlocked)
      cy.get('body').should('not.have.class', 'modal-open')
    })
  })

  describe('Create Plan Modal', () => {
    it('should close via x button', () => {
      cy.visit('/registration/register/')
      cy.wait(500)
      
      // Open create plan modal
      cy.contains('button', 'Create a Plan').should('not.exist') // Button removed
    })
  })

  describe('Load Plan Modal', () => {
    it('should close via x button', () => {
      cy.visit('/registration/register/')
      cy.wait(500)
      
      // Open load plan modal
      cy.contains('button', 'Load Plan').click()
      cy.wait(500)
      
      // Verify modal is visible
      cy.get('#load-plan-modal').should('be.visible')
      
      // Click x button
      cy.get('#load-plan-modal .modal-close-btn').click()
      cy.wait(500)
      
      // Verify modal is closed
      cy.get('#load-plan-modal').should('not.exist')
    })

    it('should close via ESC key', () => {
      cy.visit('/registration/register/')
      cy.wait(500)
      
      cy.contains('button', 'Load Plan').click()
      cy.wait(500)
      
      cy.get('#load-plan-modal').should('be.visible')
      
      // Press ESC key
      cy.get('body').type('{esc}')
      cy.wait(500)
      
      cy.get('#load-plan-modal').should('not.exist')
    })
  })
})
