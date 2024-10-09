*** Settings ***

Resource  plone/app/robotframework/browser.robot
Resource  keywords.robot

Variables  variables.py

Test Setup  Run Keywords  Plone test setup
Test Teardown  Run keywords  Plone test teardown

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
    Go to  ${PLONE_URL}/my-collection/edit

    I set the criteria index in row 1 to the option 'Type'
    I set the criteria operator in row 1 to the option 'Any'
    I set the criteria value in row 1 to the options '${criterion}'

    Click  "Save"
    Get text  body  contains  Changes saved