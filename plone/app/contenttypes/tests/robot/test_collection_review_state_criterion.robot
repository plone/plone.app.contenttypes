# ============================================================================
# Tests for the Collection Type Criterion
# ============================================================================
#
# $ bin/robot-server --reload-path src/plone.app.contenttypes plone.app.contenttypes.testing.PLONE_APP_CONTENTTYPES_ROBOT_TESTING
#
# $ bin/robot src/plone.app.contenttypes/plone/app/contenttypes/tests/robot/test_collection_review_state_criterion.robot
#
# ============================================================================

*** Settings *****************************************************************

Resource  plone/app/robotframework/keywords.robot
Resource  plone/app/contenttypes/tests/robot/keywords.txt

Test Setup  Run keywords  Open test browser
Test Teardown  Close all browsers


*** Test cases ***************************************************************

Scenario: Test Review state Criterion
    Given I am logged in as site owner
      And a published document  Published Document
      And a private document  Private Document
      And a collection  My Collection
     When I set the collection's review state criterion to  private
     Then the collection should contain  Private Document
      And the collection should not contain  Published Document


*** Keywords *****************************************************************

a published document
    [Arguments]  ${title}
    ${uid} =  a document  ${title}
    Fire transition  ${uid}  publish

a private document
    [Arguments]  ${title}
    a document  ${title}

I set the collection's review state criterion to
    [Arguments]  ${criterion}
    Go to  ${PLONE_URL}/my-collection/edit
    Wait until page contains  Edit Collection

    I set the criteria index in row 1 to the option 'Review state'
    I set the criteria operator in row 1 to the option 'Any'
    I set the criteria value in row 1 to the options '${criterion}'

    Sleep  1
    Click Button  Save
    Wait until page contains  Changes saved
