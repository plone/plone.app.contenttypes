# ============================================================================
# Tests for the Collection Creator Criterion
# ============================================================================
#
# $ bin/robot-server --reload-path src/plone.app.contenttypes plone.app.contenttypes.testing.PLONE_APP_CONTENTTYPES_ROBOT_TESTING
#
# $ bin/robot src/plone.app.contenttypes/plone/app/contenttypes/tests/robot/test_collection_creator_criterion.robot
#
# ============================================================================

*** Settings *****************************************************************

Resource  plone/app/robotframework/keywords.robot
Resource  plone/app/robotframework/saucelabs.robot
Resource  plone/app/contenttypes/tests/robot/keywords.txt

Library  Remote  ${PLONE_URL}/RobotRemote

Test Setup  Open SauceLabs test browser
Test Teardown  Run keywords  Report test status  Close all browsers


*** Test cases ***************************************************************

Scenario: Test Creator Criterions
    Given a site owner document  Site Owner Document
      And a test user document  Test User Document
      and a logged in Site Owner
      and a collection  My Collection
     When I set the collection's creator criterion to the current logged in user
     Then the collection should not contain  Test User Document
      And the collection should contain  Site Owner Document


*** Keywords *****************************************************************

a site owner document
    [Arguments]  ${title}
    a logged in site owner
    a document  ${title}
    Disable autologin

a test user document
    [Arguments]  ${title}
    a logged in test user
    a document  ${title}
    Disable autologin

I set the collection's creator criterion to the current logged in user
    Go to  ${PLONE_URL}/my-collection/edit
    Wait until page contains  Edit Collection

    I set the criteria index in row 1 to the option 'Creator'
    I set the criteria operator in row 1 to the option 'Current'

    Sleep  1
    Click Button  Save
    Wait until page contains  Changes saved
