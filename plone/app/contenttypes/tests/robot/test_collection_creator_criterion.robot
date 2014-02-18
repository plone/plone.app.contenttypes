*** Settings ***

Resource  plone/app/robotframework/keywords.robot
Resource  plone/app/contenttypes/tests/robot/keywords.txt

Test Setup  Run keywords  Open test browser
Test Teardown  Close all browsers

*** Variables ***

*** Test cases ***

Scenario: Test Creator Criterion
    Given a site owner document  Site Owner Document
      And a test user document  Test User Document
      And a collection  My Collection
     When I set the collection's creator criterion to  ${TEST_USER_ID}
     Then the collection should contain  Test User Document
      And the collection should not contain  Site Owner Document


*** Keywords ***

a site owner document
    [Arguments]  ${title}
    Log in as site owner
    a document  ${title}

a test user document
    [Arguments]  ${title}
    Log in as test user
    a document  ${title}
    Log out
    Log in as site owner

I set the collection's creator criterion to
    [Arguments]  ${criterion}
    Click Edit

    I set the criteria index in row 1 to the option 'Creator'
    I set the criteria operator in row 1 to the option 'Is'
    I set the criteria value in row 1 to the text '${criterion}'

    Click Button  Save
    Wait until page contains  Changes saved
