*** Settings ***

Resource  plone/app/robotframework/browser.robot
Resource  keywords.txt

Variables  variables.py

Test Setup  Run Keywords  Plone test setup
Test Teardown  Run keywords  Plone test teardown


*** Test cases ***

Scenario: Test Review state Criterion
    Given I am logged in as site owner
      And a published document  Published Document
      And a private document  Private Document
      And a collection  My Collection
     When I set the collection's review state criterion to  private
     Then the collection should contain  Private Document
      And the collection should not contain  Published Document


*** Keywords *****************************************************************

a published document
    [Arguments]  ${title}
    ${uid} =  a document  ${title}
    Fire transition  ${uid}  publish

a private document
    [Arguments]  ${title}
    a document  ${title}

I set the collection's review state criterion to
    [Arguments]  ${criterion}
    Go to  ${PLONE_URL}/my-collection/edit

    I set the criteria index in row 1 to the option 'Review state'
    I set the criteria operator in row 1 to the option 'Any'
    I set the criteria value in row 1 to the options '${criterion}'

    Click  "Save"