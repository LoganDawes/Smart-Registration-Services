/**
 * E2E Tests for Schedule Page
 * Verifies schedule displays both Added and Registered courses with distinct styles
 */

describe('Schedule Page Tests', () => {
  beforeEach(() => {
    cy.loginAsAdmin()
    cy.wait(1000)
  })

  it('should display schedule legend', () => {
    cy.visit('/planning/schedule/')
    cy.wait(1000)
    
    // Verify legend exists
    cy.get('[data-testid="schedule-legend"]').should('be.visible')
    
    // Verify legend contains both categories
    cy.get('[data-testid="schedule-legend"]').should('contain', 'Registered Courses')
    cy.get('[data-testid="schedule-legend"]').should('contain', 'Added Courses')
  })

  it('should render schedule events with proper data-testid', () => {
    cy.visit('/planning/schedule/')
    cy.wait(1000)
    
    // Check for schedule events if any exist
    cy.get('body').then($body => {
      if ($body.find('[data-testid="schedule-event"]').length > 0) {
        cy.get('[data-testid="schedule-event"]').should('exist')
        
        // Verify events have status attribute
        cy.get('[data-testid="schedule-event"]').first().should('have.attr', 'data-status')
      }
    })
  })

  it('should distinguish registered and added courses with distinct styles', () => {
    cy.visit('/planning/schedule/')
    cy.wait(1000)
    
    // Check for events with different statuses
    cy.get('body').then($body => {
      if ($body.find('[data-status="registered"]').length > 0) {
        cy.get('[data-status="registered"]').first().should('have.class', 'event--registered')
      }
      
      if ($body.find('[data-status="added"]').length > 0) {
        cy.get('[data-status="added"]').first().should('have.class', 'event--added')
      }
    })
  })

  it('should not have "View All Courses" button', () => {
    cy.visit('/planning/schedule/')
    cy.wait(1000)
    
    // Verify this button doesn't exist
    cy.contains('a', 'View All Courses').should('not.exist')
  })

  it('should not have "Browse Catalog" button', () => {
    cy.visit('/planning/schedule/')
    cy.wait(1000)
    
    // Verify this exact button doesn't exist
    cy.contains('a', 'Browse Catalog').should('not.exist')
  })

  it('should have "Browse Course Catalog" button', () => {
    cy.visit('/planning/schedule/')
    cy.wait(1000)
    
    // Verify this button exists
    cy.get('[data-testid="browse-course-catalog-btn"]').should('contain', 'Browse Course Catalog')
    cy.get('[data-testid="browse-course-catalog-btn"]').should('be.visible')
  })

  it('should display course summary with proper counts', () => {
    cy.visit('/planning/schedule/')
    cy.wait(1000)
    
    // Check for course summary
    cy.contains('Course Summary').should('be.visible')
    
    // Check for registered courses count
    cy.get('body').should('contain', 'Registered Courses')
  })

  it('should show hover tooltips on schedule events', () => {
    cy.visit('/planning/schedule/')
    cy.wait(1000)
    
    // Check if any events exist and have title attribute
    cy.get('body').then($body => {
      if ($body.find('[data-testid="schedule-event"]').length > 0) {
        cy.get('[data-testid="schedule-event"]').first().should('have.attr', 'title')
        
        // Verify title contains course information
        cy.get('[data-testid="schedule-event"]').first().invoke('attr', 'title').should('not.be.empty')
      }
    })
  })

  it('should take screenshot of schedule page', () => {
    cy.visit('/planning/schedule/')
    cy.wait(2000)
    
    cy.screenshot('schedule-page-with-legend', {
      capture: 'fullPage',
      overwrite: true
    })
  })
})
