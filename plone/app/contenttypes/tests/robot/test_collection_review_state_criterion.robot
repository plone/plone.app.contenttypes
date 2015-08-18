*** Settings ***

Resource  plone/app/robotframework/keywords.robot
Resource  plone/app/contenttypes/tests/robot/keywords.txt

Test Setup  Run keywords  Open test browser
Test Teardown  Close all browsers

*** Variables ***

*** Test cases ***

Scenario: Test Review state Criterion
    Given I am logged in as site owner
      And a published document  Published Document
      And a private document  Private Document
      And a collection  My Collection
     When I set the collection's review state criterion to  private
     Then the collection should contain  Private Document
      And the collection should not contain  Published Document


*** Keywords ***

a published document
    [Arguments]  ${title}
    a document  ${title}
    Click link  css=dl#plone-contentmenu-workflow dt.actionMenuHeader a
    Click Link  workflow-transition-publish

a private document
    [Arguments]  ${title}
    a document  ${title}

I set the collection's review state criterion to
    [Arguments]  ${criterion}
    Click Link  Edit
    Wait Until Page Contains Element  xpath=//select[@name="addindex"]
    Select From List  xpath=//select[@name="addindex"]  Review state
    Wait Until Page Contains Element  xpath=//select[@class='queryoperator']
    Click Element  xpath=//span[@class='arrowDownAlternative']
    Select Checkbox  ${criterion}
    Click Button  Save
    Wait until page contains  Changes saved
