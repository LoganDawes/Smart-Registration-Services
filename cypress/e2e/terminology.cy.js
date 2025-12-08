/**
 * E2E Tests for Terminology Changes
 * Verifies that "Cart" has been completely replaced with "Added Courses"
 */

describe('Terminology Verification Tests', () => {
  beforeEach(() => {
    cy.loginAsAdmin()
    cy.wait(1000)
  })

  it('should not contain "Cart" terminology in registration page', () => {
    cy.visit('/registration/register/')
    cy.wait(1000)
    
    // Check that "Cart" is not visible in the page (excluding URLs and technical terms)
    cy.get('body').should('not.contain', 'Registration Cart')
    cy.get('body').should('not.contain', 'Your Cart is Empty')
    cy.get('body').should('not.contain', 'Add to Cart')
  })

  it('should contain "Added Courses" terminology in registration page', () => {
    cy.visit('/registration/register/')
    cy.wait(1000)
    
    // Verify "Added Courses" appears in heading
    cy.get('[data-testid="added-courses-heading"]').should('contain', 'Added Courses')
    
    // Check for other Added Courses references
    cy.contains('Added Courses').should('be.visible')
  })

  it('should contain "Added Courses" in course details modal', () => {
    cy.visit('/courses/catalog/')
    cy.wait(1000)
    
    // Open course details
    cy.get('[data-course-id]').first().click()
    cy.wait(500)
    
    // Check button text
    cy.get('[data-testid="add-to-added-courses-btn"]').should('contain', 'Add to Added Courses')
  })

  it('should contain "Added Courses" in load plan modal', () => {
    cy.visit('/registration/register/')
    cy.wait(1000)
    
    // Open load plan modal
    cy.contains('button', 'Load Plan').click()
    cy.wait(500)
    
    // Check modal title and text
    cy.get('#load-plan-modal').should('contain', 'Added Courses')
  })

  it('should not have Create a Plan button on registration page', () => {
    cy.visit('/registration/register/')
    cy.wait(1000)
    
    // Verify the button doesn't exist
    cy.contains('button', 'Create a Plan').should('not.exist')
  })

  it('should have Browse Course Catalog button', () => {
    cy.visit('/registration/register/')
    cy.wait(1000)
    
    // Verify button exists
    cy.get('[data-testid="browse-course-catalog-btn"]').should('contain', 'Browse Course Catalog')
  })
})
