*** Settings ***

Resource  plone/app/robotframework/keywords.robot
Resource  plone/app/contenttypes/tests/robot/keywords.txt

Test Setup  Run keywords  Open test browser
Test Teardown  Close all browsers

*** Variables ***

*** Test cases ***

Test Short name (id) Criterion
    Given I am logged in as site owner
      And a document  First Document
      And a document  Second Document
      And a collection  My Collection
     When I set the collection short name (id) criterion to  first-document
     Then the collection should contain  First Document
      And the collection should not contain  Second Document


*** Keywords ***

I set the collection short name (id) criterion to
    [Arguments]  ${criterion}
    Click Edit

    I set the criteria index in row 1 to the option 'Short name (id)'
    I set the criteria operator in row 1 to the option 'Is'
    I set the criteria value in row 1 to the text '${criterion}'

    Sleep  1
    Click Button  Save
    Wait until page contains  Changes saved
