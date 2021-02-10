# ============================================================================
# Tests for the Collection Short Name Criterion
# ============================================================================
#
# $ bin/robot-server --reload-path src/plone.app.contenttypes plone.app.contenttypes.testing.PLONE_APP_CONTENTTYPES_ROBOT_TESTING
#
# $ bin/robot src/plone.app.contenttypes/plone/app/contenttypes/tests/robot/test_collection_short_name_criterion.robot
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

Test Short name (id) Criterion
    Given I am logged in as site owner
      And a document  First Document
      And a document  Second Document
      And a collection  My Collection
     When I set the collection short name (id) criterion to  first-document
     Then the collection should contain  First Document
      And the collection should not contain  Second Document


*** Keywords *****************************************************************

I set the collection short name (id) criterion to
    [Arguments]  ${criterion}
    Go to  ${PLONE_URL}/my-collection/edit
    Wait until page contains  Edit Collection

    I set the criteria index in row 1 to the option 'Short name'
    I set the criteria operator in row 1 to the option 'Is'
    I set the criteria value in row 1 to the text '${criterion}'

    Sleep  1
    Click Button  Save
    Wait until page contains  Changes saved
