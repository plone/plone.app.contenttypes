*** Settings ***

Library  Selenium2Library  timeout=2  implicit_wait=0.1

Resource  plone/app/contenttypes/tests/robot/keywords.txt
Variables  plone/app/testing/interfaces.py
Variables  plone/app/contenttypes/tests/robot/variables.py

Suite Setup  Suite Setup
Suite Teardown  Suite Teardown


*** Test Cases ***

Scenario: Test Review state Criterion
    Given a published document  Published Document
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
