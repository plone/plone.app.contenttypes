# ============================================================================
# Tests for the Collection Type Criterion
# ============================================================================
#
# $ bin/robot-server --reload-path src/plone.app.contenttypes plone.app.contenttypes.testing.PLONE_APP_CONTENTTYPES_ROBOT_TESTING
#
# $ bin/robot src/plone.app.contenttypes/plone/app/contenttypes/tests/robot/test_collection_type_criterion.robot
#
# ============================================================================

*** Settings *****************************************************************

Resource  plone/app/robotframework/keywords.robot
Resource  plone/app/robotframework/saucelabs.robot
Resource  plone/app/robotframework/selenium.robot
Resource  plone/app/contenttypes/tests/robot/keywords.txt

Test Setup  Run Keywords  Plone test setup
Test Teardown  Run keywords  Plone test teardown


*** Test cases ***************************************************************

Test Type Criterion
    Given I am logged in as site owner
      And a document  Test Document
      And a news_item  Test News Item
      And a collection  My Collection
     When I set the collection's type criterion to  News Item
     Then the collection should contain  Test News Item
      And the collection should not contain  Test Document


*** Keywords *****************************************************************

I set the collection's type criterion to
    [Arguments]  ${criterion}
    Go to  ${PLONE_URL}/my-collection/edit
    Wait until page contains  Edit Collection

    I set the criteria index in row 1 to the option 'Type'
    I set the criteria operator in row 1 to the option 'Any'
    I set the criteria value in row 1 to the options '${criterion}'

    Sleep  1
    Click Button  Save
    Wait until page contains  Changes saved
