*** Settings ***

Variables  plone/app/testing/interfaces.py
Variables  plone/app/contenttypes/tests/robot/variables.py

Library  Selenium2Library  timeout=${SELENIUM_TIMEOUT}  implicit_wait=${SELENIUM_IMPLICIT_WAIT}

Resource  library-settings.txt
Resource  plone/app/contenttypes/tests/robot/keywords.txt

Suite Setup  Suite Setup
Suite Teardown  Suite Teardown


*** Test Cases ***

Test Short name (id) Criterion
    Given a document  First Document
      And a document  Second Document
      And a collection  My Collection
     When I set the collection short name (id) criterion to  first-document
     Then the collection should contain  First Document
      And the collection should not contain  Second Document


*** Keywords ***

I set the collection short name (id) criterion to
    [Arguments]  ${criterion}
    Click Link  Edit
    Wait Until Page Contains Element  xpath=//select[@name="addindex"]
    Select From List  xpath=//select[@name="addindex"]  Short name (id)
    Wait Until Page Contains Element  xpath=//select[@class='queryoperator']
    Input Text  name=form.widgets.query.v:records  ${criterion}
    Click Button  Save
