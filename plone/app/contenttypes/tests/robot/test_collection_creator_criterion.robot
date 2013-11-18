*** Settings ***

Variables  plone/app/testing/interfaces.py
Variables  plone/app/contenttypes/tests/robot/variables.py

Library  Selenium2Library  timeout=${SELENIUM_TIMEOUT}  implicit_wait=${SELENIUM_IMPLICIT_WAIT}

Resource  plone/app/contenttypes/tests/robot/keywords.txt

Suite Setup  Suite Setup
Suite Teardown  Suite Teardown


*** Test Cases ***

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
    a document  ${title}

a test user document
    [Arguments]  ${title}
    Log in as test user
    a document  ${title}
    Log out
    Log in as site owner

I set the collection's creator criterion to
    [Arguments]  ${criterion}
    Click Link  Edit
    Wait Until Page Contains Element  xpath=//select[@name="addindex"]
    Select From List  xpath=//select[@name="addindex"]  Creator
    Wait Until Page Contains Element  xpath=//select[@class='queryoperator']
    Select From List  xpath=//select[@class='queryoperator']  Is
    Input Text  name=form.widgets.ICollection.query.v:records  ${criterion}
    Click Button  Save
    Wait until page contains  Changes saved
