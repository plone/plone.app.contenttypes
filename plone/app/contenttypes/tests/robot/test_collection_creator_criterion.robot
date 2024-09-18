*** Settings ***

Resource  plone/app/robotframework/browser.robot
Resource  plone/app/robotframework/user.robot
Resource  keywords.txt

Library  Remote  ${PLONE_URL}/RobotRemote

Test Setup  Run Keywords  Plone test setup
Test Teardown  Run keywords  Plone test teardown

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
    Get Text  body  contains  Edit Collection

    I set the criteria index in row 1 to the option 'Creator'
    I set the criteria operator in row 1 to the option 'Current'

    Click  "Save"
    Get Text  body  contains  Changes saved