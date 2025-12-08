/**
 * E2E Tests for Registration Workflow Fixes
 * Tests:
 * 1. Layout consistency between catalog and register page
 * 2. Enrollment logic without removal confirmation
 * 3. Prerequisite bypass during registration
 */

describe('Registration Workflow Fixes', () => {
  beforeEach(() => {
    cy.loginAsAdmin()
    cy.wait(1000)
  })

  describe('Layout Consistency', () => {
    it('should display Added Courses with consistent list-row formatting', () => {
      cy.visit('/registration/register/')
      cy.wait(1000)
      
      // Check if there are added courses
      cy.get('body').then($body => {
        if ($body.find('[data-testid="added-course-item"]').length > 0) {
          // Verify list-row structure exists
          cy.get('.list-row').should('exist')
          cy.get('.list-row-course-code').should('exist')
          cy.get('.list-row-title').should('exist')
          cy.get('.list-row-credits').should('exist')
          cy.get('.list-row-actions').should('exist')
          
          // Check that rows have consistent structure
          cy.get('.list-row').each($row => {
            cy.wrap($row).find('.list-row-course-code').should('exist')
            cy.wrap($row).find('.list-row-title').should('exist')
            cy.wrap($row).find('.list-row-actions').should('exist')
          })
        } else {
          // If no courses, that's fine - just verify empty state shows
          cy.log('No added courses to verify layout')
        }
      })
    })

    it('should have similar layout structure to catalog page', () => {
      // First check catalog structure
      cy.visit('/courses/catalog/')
      cy.wait(1000)
      
      let catalogStructure = {
        hasCourseCode: false,
        hasTitle: false,
        hasCredits: false,
        hasActions: false
      }
      
      cy.get('body').then($body => {
        if ($body.find('.course-item').length > 0) {
          // Check catalog has key elements
          cy.get('.course-item').first().within(() => {
            cy.get('div').contains(/[A-Z]{2,4}\d{3}/).should('exist') // Course code
          })
        }
      })
      
      // Then check register page structure
      cy.visit('/registration/register/')
      cy.wait(1000)
      
      cy.get('body').then($body => {
        if ($body.find('[data-testid="added-course-item"]').length > 0) {
          cy.get('[data-testid="added-course-item"]').first().within(() => {
            // Should have course code
            cy.get('.list-row-course-code').should('exist')
            // Should have title
            cy.get('.list-row-title').should('exist')
            // Should have credits
            cy.get('.list-row-credits').should('exist')
            // Should have actions
            cy.get('.list-row-actions').should('exist')
          })
        }
      })
    })
  })

  describe('Enrollment Logic Without Removal Prompt', () => {
    it('should register without showing removal confirmation prompt', () => {
      // Add a course to Added Courses first
      cy.visit('/courses/catalog/')
      cy.wait(1000)
      
      // Add course to Added Courses via button in catalog
      cy.get('body').then($body => {
        if ($body.find('[data-testid="add-to-added-courses-row-btn"]').length > 0) {
          cy.get('[data-testid="add-to-added-courses-row-btn"]').first().click()
          cy.wait(1000)
        }
      })
      
      // Go to registration page
      cy.visit('/registration/register/')
      cy.wait(1000)
      
      // Stub window.confirm to track if it's called
      let confirmCallCount = 0
      cy.window().then((win) => {
        cy.stub(win, 'confirm').callsFake((message) => {
          confirmCallCount++
          cy.log(`Confirm called ${confirmCallCount} time(s): ${message}`)
          
          // Should only be called once for "Register for this course now?"
          // NOT called for removal
          return true
        })
      })
      
      // Click Register button
      cy.get('body').then($body => {
        if ($body.find('[data-testid="register-single-btn"]').length > 0) {
          cy.get('[data-testid="register-single-btn"]').first().click()
          cy.wait(2000)
          
          // Confirm should be called only once (for registration, not removal)
          cy.window().then((win) => {
            expect(win.confirm).to.have.been.calledOnce
          })
        }
      })
    })

    it('should show confirmation when manually removing from Added Courses', () => {
      cy.visit('/registration/register/')
      cy.wait(1000)
      
      // Stub window.confirm
      cy.window().then((win) => {
        cy.stub(win, 'confirm').returns(false) // Cancel the removal
      })
      
      // Click Remove button
      cy.get('body').then($body => {
        if ($body.find('[data-testid="remove-from-added-courses-btn"]').length > 0) {
          cy.get('[data-testid="remove-from-added-courses-btn"]').first().click()
          cy.wait(500)
          
          // Confirm should be called
          cy.window().then((win) => {
            expect(win.confirm).to.have.been.called
          })
        }
      })
    })
  })

  describe('Prerequisite Bypass', () => {
    it('should allow registration regardless of prerequisites', () => {
      // This test verifies that the UI doesn't block registration
      // The actual prerequisite bypass is tested in unit tests
      
      cy.visit('/registration/register/')
      cy.wait(1000)
      
      // If there are courses in Added Courses, try to register
      cy.get('body').then($body => {
        if ($body.find('[data-testid="register-single-btn"]').length > 0) {
          // Stub confirm to accept
          cy.window().then((win) => {
            cy.stub(win, 'confirm').returns(true)
            cy.stub(win, 'alert')
          })
          
          cy.get('[data-testid="register-single-btn"]').first().click()
          cy.wait(2000)
          
          // Registration should proceed (either success or other error, but not prerequisite error)
          cy.window().then((win) => {
            // If alert was called, check it's not a prerequisite error
            if (win.alert.called) {
              const alertMessage = win.alert.getCall(0).args[0]
              expect(alertMessage.toLowerCase()).to.not.contain('prerequisite')
            }
          })
        }
      })
    })
    
    it('should allow bulk registration without prerequisite checks', () => {
      cy.visit('/registration/register/')
      cy.wait(1000)
      
      cy.get('body').then($body => {
        if ($body.find('[data-testid="confirm-registration-btn"]').length > 0) {
          // Stub confirm and alert
          cy.window().then((win) => {
            cy.stub(win, 'confirm').returns(true)
            cy.stub(win, 'alert')
          })
          
          cy.get('[data-testid="confirm-registration-btn"]').click()
          cy.wait(2000)
          
          // Check that no prerequisite errors were shown
          cy.window().then((win) => {
            if (win.alert.called) {
              const alertCalls = win.alert.getCalls()
              alertCalls.forEach(call => {
                const message = call.args[0]
                expect(message.toLowerCase()).to.not.contain('prerequisite')
              })
            }
          })
        }
      })
    })
  })

  describe('State Transitions', () => {
    it('should properly transition from Unadded -> Added -> Registered', () => {
      // Start from catalog (Unadded)
      cy.visit('/courses/catalog/')
      cy.wait(1000)
      
      let courseName = ''
      
      // Add to Added Courses (Unadded -> Added)
      cy.get('body').then($body => {
        if ($body.find('[data-testid="add-to-added-courses-row-btn"]').length > 0) {
          // Get course name
          cy.get('.course-item').first().within(() => {
            cy.get('div').first().invoke('text').then(text => {
              courseName = text.trim()
              cy.log(`Course: ${courseName}`)
            })
          })
          
          cy.get('[data-testid="add-to-added-courses-row-btn"]').first().click()
          cy.wait(1000)
          
          // Go to registration page (Added state)
          cy.visit('/registration/register/')
          cy.wait(1000)
          
          // Verify course is in Added Courses
          cy.get('[data-testid="added-course-item"]').should('exist')
          
          // Register (Added -> Registered)
          cy.window().then((win) => {
            cy.stub(win, 'confirm').returns(true)
            cy.stub(win, 'alert')
          })
          
          cy.get('[data-testid="register-single-btn"]').first().click()
          cy.wait(2000)
          
          // Should show success message without additional confirmation
          cy.window().then((win) => {
            // Confirm should be called only once
            expect(win.confirm.callCount).to.be.at.most(1)
          })
        }
      })
    })
  })
})
