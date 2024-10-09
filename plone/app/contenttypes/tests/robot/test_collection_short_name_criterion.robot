*** Settings ***

Resource  plone/app/robotframework/browser.robot
Resource  keywords.robot

Variables  variables.py

Test Setup  Run Keywords  Plone test setup
Test Teardown  Run keywords  Plone test teardown


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
    Go to  ${PLONE_URL}/my-collection/edit

    I set the criteria index in row 1 to the option 'Short name'
    #I set the criteria operator in row 1 to the option 'Is'

    ${criteria_row} =  Convert to String  .querystring-criteria-wrapper:nth-child(1)
    Click  css=${criteria_row} .querystring-criteria-operator .select2-choice
    Fill Text  css=#select2-drop input  Is
    Click  css=.select2-highlighted


    I set the criteria value in row 1 to the text '${criterion}'
    [Documentation]  Chrome needs some more time
    Sleep  .1s

    Click  "Save"
    Get text  body  contains  Changes saved