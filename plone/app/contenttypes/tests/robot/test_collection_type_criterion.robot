*** Settings ***

Resource  plone/app/robotframework/keywords.robot
Resource  plone/app/contenttypes/tests/robot/keywords.txt

Test Setup  Run keywords  Open test browser
Test Teardown  Close all browsers

*** Variables ***

*** Test cases ***

Test Type Criterion
    Given I am logged in as site owner
      And a document  Test Document
      And a news_item  Test News Item
      And a collection  My Collection
     When I set the collection's type criterion to  News Item
     Then the collection should contain  Test News Item
      And the collection should not contain  Test Document


*** Keywords ***

I set the collection's type criterion to
    [Arguments]  ${criterion}
    Click Edit

    I set the criteria index in row 1 to the option 'Type'
    I set the criteria operator in row 1 to the option 'Is'
    I set the criteria value in row 1 to the options '${criterion}'

    Sleep  1
    Click Button  Save
    Wait until page contains  Changes saved
