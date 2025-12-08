/**
 * E2E Tests for Course Registration UI/UX Improvements
 * Tests list spacing, modal behavior, create plan flow, and accessibility features
 */

describe('Course Registration UI/UX Tests', () => {
  beforeEach(() => {
    // Login as admin/student before each test
    cy.visit('/admin/login/')
    cy.get('input[name="username"]').type('admin')
    cy.get('input[name="password"]').type('admin123')
    cy.get('input[type="submit"]').click()
    cy.wait(1000)
  })

  describe('1. List Row Spacing and Alignment', () => {
    it('should have uniform spacing in registration cart list', () => {
      cy.visit('/registration/register/')
      
      // Check if list rows exist
      cy.get('.list-row').should('exist')
      
      // Verify consistent height and padding
      cy.get('.list-row').first().then($el => {
        const padding = window.getComputedStyle($el[0]).padding
        const minHeight = window.getComputedStyle($el[0]).minHeight
        
        expect(padding).to.not.be.empty
        expect(minHeight).to.equal('60px')
      })
    })

    it('should have proper column alignment across all rows', () => {
      cy.visit('/registration/register/')
      
      // Check course code column
      cy.get('.list-row-course-code').first().should('have.css', 'width', '96px')
      
      // Check that title column grows
      cy.get('.list-row-title').first().should('have.css', 'flex', '1 1 0%')
      
      // Check credits column alignment
      cy.get('.list-row-credits').first().should('have.css', 'text-align', 'center')
    })

    it('should maintain alignment on enrolled courses list', () => {
      cy.visit('/registration/register/')
      
      // Check enrolled courses section if it exists
      cy.get('body').then($body => {
        if ($body.find('.list-row').length > 0) {
          // Verify list rows have consistent structure
          cy.get('.list-row').each($row => {
            cy.wrap($row).find('.list-row-course-code').should('exist')
            cy.wrap($row).find('.list-row-title').should('exist')
            cy.wrap($row).find('.list-row-actions').should('exist')
          })
        }
      })
    })

    it('should be responsive at different viewport widths', () => {
      cy.visit('/registration/register/')
      
      // Test desktop view
      cy.viewport(1280, 720)
      cy.get('.list-row').first().should('have.css', 'display', 'flex')
      
      // Test tablet view
      cy.viewport(768, 1024)
      cy.get('.list-row').first().should('be.visible')
      
      // Test mobile view
      cy.viewport(375, 667)
      cy.get('.list-row').first().should('be.visible')
    })
  })

  describe('2. Modal Scrolling Behavior', () => {
    it('should allow vertical scrolling in course details modal', () => {
      cy.visit('/courses/catalog/')
      
      // Open a course details modal (assuming there's a button/link)
      cy.get('body').then($body => {
        if ($body.find('[data-course-id]').length > 0) {
          cy.get('[data-course-id]').first().click()
          
          // Check modal is visible
          cy.get('#course-details-modal').should('be.visible')
          
          // Check modal body is scrollable
          cy.get('.modal-body').should('have.css', 'overflow-y', 'auto')
          
          // Verify body scroll is locked
          cy.get('body').should('have.class', 'modal-open')
        }
      })
    })

    it('should lock body scroll when modal is open', () => {
      cy.visit('/registration/register/')
      
      // Click Create a Plan button
      cy.contains('button', 'Create a Plan').click()
      cy.wait(500)
      
      // Verify modal is visible
      cy.get('#create-plan-modal').should('be.visible')
      
      // Verify body has modal-open class
      cy.get('body').should('have.class', 'modal-open')
      
      // Verify body overflow is hidden
      cy.get('body').should('have.css', 'overflow', 'hidden')
    })

    it('should unlock body scroll when modal closes', () => {
      cy.visit('/registration/register/')
      
      // Open modal
      cy.contains('button', 'Create a Plan').click()
      cy.wait(500)
      
      // Close modal
      cy.get('.modal-close-btn').click()
      cy.wait(500)
      
      // Verify body scroll is restored
      cy.get('body').should('not.have.class', 'modal-open')
    })
  })

  describe('3. Create a Plan Flow', () => {
    it('should open create plan modal without changing route', () => {
      cy.visit('/registration/register/')
      
      // Get current URL
      cy.url().then(url => {
        // Click Create a Plan button
        cy.contains('button', 'Create a Plan').click()
        cy.wait(500)
        
        // Verify modal opened
        cy.get('#create-plan-modal').should('be.visible')
        
        // Verify URL hasn't changed
        cy.url().should('equal', url)
      })
    })

    it('should allow creating a plan from registration page', () => {
      cy.visit('/registration/register/')
      
      // Click Create a Plan
      cy.contains('button', 'Create a Plan').click()
      cy.wait(500)
      
      // Fill in form
      cy.get('input[name="name"]').type('Test Plan Fall 2025')
      cy.get('select[name="term"]').select('Fall')
      cy.get('select[name="year"]').select('2025')
      
      // Submit form
      cy.get('button[type="submit"]').contains('Create Plan').click()
      
      // Wait for success (modal should close)
      cy.wait(1000)
      
      // Verify we're still on registration page
      cy.url().should('include', '/registration/register/')
    })

    it('should close modal and stay on registration page after cancel', () => {
      cy.visit('/registration/register/')
      
      // Open modal
      cy.contains('button', 'Create a Plan').click()
      cy.wait(500)
      
      // Click cancel
      cy.contains('button', 'Cancel').click()
      cy.wait(500)
      
      // Verify modal is closed
      cy.get('#create-plan-modal').should('not.exist')
      
      // Verify we're still on registration page
      cy.url().should('include', '/registration/register/')
    })
  })

  describe('4. Modal Close Button Behavior', () => {
    it('should close course details modal via X button', () => {
      cy.visit('/courses/catalog/')
      
      // Open course details if available
      cy.get('body').then($body => {
        if ($body.find('[data-course-id]').length > 0) {
          cy.get('[data-course-id]').first().click()
          cy.wait(500)
          
          // Click X button
          cy.get('#course-details-modal .modal-close-btn').click()
          cy.wait(500)
          
          // Verify modal is closed
          cy.get('#course-details-modal').should('not.exist')
        }
      })
    })

    it('should close create plan modal via X button', () => {
      cy.visit('/registration/register/')
      
      // Open modal
      cy.contains('button', 'Create a Plan').click()
      cy.wait(500)
      
      // Click X button
      cy.get('#create-plan-modal .modal-close-btn').click()
      cy.wait(500)
      
      // Verify modal is closed
      cy.get('#create-plan-modal').should('not.exist')
    })

    it('should close modal on backdrop click', () => {
      cy.visit('/registration/register/')
      
      // Open modal
      cy.contains('button', 'Create a Plan').click()
      cy.wait(500)
      
      // Click on backdrop
      cy.get('.modal-overlay').click(-10, -10, { force: true })
      cy.wait(500)
      
      // Verify modal is closed
      cy.get('#create-plan-modal').should('not.exist')
    })

    it('should close modal on Escape key', () => {
      cy.visit('/registration/register/')
      
      // Open modal
      cy.contains('button', 'Create a Plan').click()
      cy.wait(500)
      
      // Press Escape
      cy.get('body').type('{esc}')
      cy.wait(500)
      
      // Verify modal is closed
      cy.get('#create-plan-modal').should('not.exist')
    })
  })

  describe('5. Focus Management', () => {
    it('should restore focus to opener after closing modal', () => {
      cy.visit('/registration/register/')
      
      // Focus on Create a Plan button
      cy.contains('button', 'Create a Plan').focus().click()
      cy.wait(500)
      
      // Close modal
      cy.get('.modal-close-btn').click()
      cy.wait(500)
      
      // Verify focus is restored to button
      cy.contains('button', 'Create a Plan').should('have.focus')
    })

    it('should trap focus within modal', () => {
      cy.visit('/registration/register/')
      
      // Open modal
      cy.contains('button', 'Create a Plan').click()
      cy.wait(500)
      
      // Get all focusable elements
      cy.get('#create-plan-modal').within(() => {
        // Tab through elements
        cy.get('input[name="name"]').focus().tab()
        cy.get('select[name="term"]').should('have.focus')
      })
    })
  })

  describe('6. Accessibility Features', () => {
    it('should have proper ARIA attributes on modals', () => {
      cy.visit('/registration/register/')
      
      // Open modal
      cy.contains('button', 'Create a Plan').click()
      cy.wait(500)
      
      // Check ARIA attributes
      cy.get('#create-plan-modal')
        .should('have.attr', 'role', 'dialog')
        .and('have.attr', 'aria-modal', 'true')
        .and('have.attr', 'aria-labelledby')
    })

    it('should have aria-label on close button', () => {
      cy.visit('/registration/register/')
      
      // Open modal
      cy.contains('button', 'Create a Plan').click()
      cy.wait(500)
      
      // Check close button has aria-label
      cy.get('.modal-close-btn').should('have.attr', 'aria-label', 'Close modal')
    })
  })
})
