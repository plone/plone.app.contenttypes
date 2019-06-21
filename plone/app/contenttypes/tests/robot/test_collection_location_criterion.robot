# ============================================================================
# Tests for the Collection Location Criterion
# ============================================================================
#
# $ bin/robot-server --reload-path src/plone.app.contenttypes plone.app.contenttypes.testing.PLONE_APP_CONTENTTYPES_ROBOT_TESTING
#
# $ bin/robot src/plone.app.contenttypes/plone/app/contenttypes/tests/robot/test_collection_location_criterion.robot
#
# ============================================================================

*** Settings *****************************************************************

Resource  plone/app/robotframework/keywords.robot
Resource  plone/app/robotframework/saucelabs.robot
Resource  plone/app/robotframework/selenium.robot
Resource  plone/app/contenttypes/tests/robot/keywords.txt

Variables  plone/app/contenttypes/tests/robot/variables.py

Test Setup  Run Keywords  Plone test setup
Test Teardown  Run keywords  Plone test teardown


*** Test cases ***************************************************************

Scenario: Test Relative Location Criterion
    [Documentation]  This sometimes fails with:
    ...              Element locator 'css=#select2-drop input' did not match any elements after 30 seconds
    Given I am logged in as site owner
      And a document   Document outside Folder
      And a folder 'my-folder' with a document 'Document within Folder'
      And a collection  My Collection
     When I set the collection's relative location criterion to  ../my-folder
     Then the collection should contain  Document within Folder
      And the collection should not contain  Document outside Folder


Scenario: Test Absolute Location Criterion
    [Documentation]  This sometimes fails with:
    ...              Element locator 'css=#select2-drop input' did not match any elements after 30 seconds
    ...              Or with: Element 'id=content' should not contain text 'Document outside Folder' but it did.
    Given I am logged in as site owner
      And a document   Document outside Folder
      And a folder 'my-folder' with a document 'Document within Folder'
      And a collection  My Collection
     When I set the collection's absolute location criterion to  /my-folder/
     Then the collection should contain  Document within Folder
      And the collection should not contain  Document outside Folder


*** Keywords *****************************************************************

a folder '${folder-id}' with a document '${document-title}'
    Go to  ${PLONE_URL}/++add++Folder
    Wait until page contains element  name=form.widgets.IDublinCore.title
    Input text  name=form.widgets.IDublinCore.title  ${folder-id}
    Click Button  Save
    Go to  ${PLONE_URL}/${folder-id}/++add++Document
    Wait until page contains element  name=form.widgets.IDublinCore.title
    Input text  name=form.widgets.IDublinCore.title  ${document-title}
    Click Button  Save
    Wait until page contains  Item created

I set the collection's location criterion to Advanced Mode
    I set the criteria operator in row 1 to the option 'Advanced Mode'

I set the collection's relative location criterion to
    [Arguments]  ${criterion}
    Go to  ${PLONE_URL}/my-collection/edit
    Wait until page contains  Edit Collection

    I set the criteria index in row 1 to the option 'Location'

    I set the collection's location criterion to Advanced Mode

    I set the criteria operator in row 1 to the option 'Relative path'
    I set the criteria value in row 1 to the text '${criterion}'

    Click Button  Save
    Wait until page contains  Changes saved

I set the collection's absolute location criterion to
    [Arguments]  ${criterion}
    Go to  ${PLONE_URL}/my-collection/edit
    Wait until page contains  Edit Collection

    I set the criteria index in row 1 to the option 'Location'

    I set the collection's location criterion to Advanced Mode

    I set the criteria operator in row 1 to the option 'Absolute path'
    I set the criteria value in row 1 to the text '${criterion}'

    Click Button  Save
    Wait until page contains  Changes saved
