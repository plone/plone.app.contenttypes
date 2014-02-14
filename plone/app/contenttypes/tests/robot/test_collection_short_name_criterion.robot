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
    Click Edit In Edit Bar
    Wait Until Page Contains Element  xpath=//select[@name="addindex"]
    Select From List  xpath=//select[@name="addindex"]  Short name (id)
    Wait Until Page Contains Element  xpath=//select[@class='queryoperator']
    Wait Until Page Contains Element  xpath=//input[@name='form.widgets.ICollection.query.v:records']
    Input Text  name=form.widgets.ICollection.query.v:records  ${criterion}
    Click Button  Save
    Wait until page contains  Changes saved
