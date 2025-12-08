// ***********************************************
// This file contains custom Cypress commands for the Smart Registration Services project
//
// For more comprehensive examples of custom commands please read more here:
// https://on.cypress.io/custom-commands
// ***********************************************

/**
 * Login as admin user
 */
Cypress.Commands.add('loginAsAdmin', () => {
  // Navigate to login page
  cy.visit('/admin/login/')
  
  // Fill in admin credentials
  cy.get('input[name="username"]').type('admin')
  cy.get('input[name="password"]').type('admin123')
  
  // Submit login form
  cy.get('input[type="submit"]').click()
  
  // Verify successful login
  cy.url().should('not.include', '/login')
})

/**
 * Login as student user
 */
Cypress.Commands.add('loginAsStudent', () => {
  // Navigate to login page
  cy.visit('/admin/login/')
  
  // Fill in student credentials
  cy.get('input[name="username"]').type('student')
  cy.get('input[name="password"]').type('student123')
  
  // Submit login form
  cy.get('input[type="submit"]').click()
  
  // Verify successful login
  cy.url().should('not.include', '/login')
})

/**
 * Check if element has specific computed CSS property value
 */
Cypress.Commands.add('shouldHaveComputedStyle', { prevSubject: true }, (subject, property, value) => {
  cy.wrap(subject).then($el => {
    const computedStyle = window.getComputedStyle($el[0])
    expect(computedStyle.getPropertyValue(property)).to.equal(value)
  })
})

/**
 * Get CSRF token from cookies
 */
Cypress.Commands.add('getCsrfToken', () => {
  return cy.getCookie('csrftoken').then((cookie) => {
    return cookie ? cookie.value : null
  })
})
